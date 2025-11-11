"""
QUATTROCANALI Protocol Implementation.

This module implements the Powersoft QUATTROCANALI UDP protocol
which uses port 1234, CRC16/ARC checksums, and little-endian byte order.

Based on Biamp documentation:
https://support.biamp.com/Biamp_Control/Control_configuration/Developing_a_custom_driver_for_Powersoft
"""
import struct
import logging
from dataclasses import dataclass
from typing import Optional

_LOGGER = logging.getLogger(__name__)

# Protocol constants
STX = 0x02
ETX = 0x03
DEFAULT_PORT = 1234

# Command codes (from official Powersoft Quattrocanali.pdf documentation)
CMD_PING = 0x00   # Ping command - simple connectivity test
CMD_INFO = 0x0B   # Info command - device identification (128 bytes)
CMD_POWER = 0x14  # Standby control command


def crc16_arc(data: bytes) -> int:
    """
    Calculate CRC16/ARC checksum.

    This is the algorithm used by QUATTROCANALI protocol.
    Also known as CRC-16-IBM or CRC-16-ANSI.

    Args:
        data: Bytes to calculate checksum for

    Returns:
        16-bit CRC checksum
    """
    crc = 0x0000
    polynomial = 0xA001  # Reversed polynomial for CRC-16-IBM/ARC

    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ polynomial
            else:
                crc >>= 1

    return crc & 0xFFFF


@dataclass
class QuattroCommand:
    """Represents a QUATTROCANALI protocol command."""
    cmd: int           # Command code
    data: bytes        # Command data payload
    cookie: int = 0    # Optional tag for matching responses
    answer_port: int = 0  # Port for response (0 = default 1234)

    def build_packet(self) -> bytes:
        """
        Build a complete QUATTROCANALI protocol packet.

        Format:
        STX | cmd | cookie | answer_port | count | data | crc16 | ~cmd | ETX

        Returns:
            Complete packet as bytes
        """
        # Calculate data length
        count = len(self.data)

        # Calculate CRC16 of data
        crc = crc16_arc(self.data)

        # Calculate inverse command (~cmd = 255 - cmd)
        cmd_inverse = (255 - self.cmd) & 0xFF

        # Build packet (all multi-byte values in little-endian)
        packet = struct.pack(
            '<BBHHH',
            STX,
            self.cmd,
            self.cookie,
            self.answer_port,
            count
        )
        packet += self.data
        packet += struct.pack('<HBB', crc, cmd_inverse, ETX)

        return packet


@dataclass
class QuattroResponse:
    """Represents a QUATTROCANALI protocol response."""
    cmd: int           # Command code this responds to
    cookie: int        # Cookie from request
    data: bytes        # Response data payload

    @staticmethod
    def parse_packet(packet: bytes) -> Optional['QuattroResponse']:
        """
        Parse a QUATTROCANALI response packet.

        Args:
            packet: Raw packet bytes

        Returns:
            Parsed QuattroResponse or None if invalid
        """
        try:
            # Minimum packet size: STX + cmd + cookie + answer_port + count + crc16 + ~cmd + ETX
            if len(packet) < 10:
                _LOGGER.debug("Packet too short: %d bytes", len(packet))
                return None

            # Check STX
            if packet[0] != STX:
                _LOGGER.debug("Invalid STX: 0x%02x", packet[0])
                return None

            # Check ETX
            if packet[-1] != ETX:
                _LOGGER.debug("Invalid ETX: 0x%02x", packet[-1])
                return None

            # Parse header (little-endian)
            cmd, cookie, answer_port, count = struct.unpack_from('<BHHH', packet, 1)

            # Extract data
            data_start = 7
            data_end = data_start + count

            if data_end + 3 > len(packet):
                _LOGGER.debug("Invalid packet length")
                return None

            data = packet[data_start:data_end]

            # Verify CRC
            crc_received = struct.unpack_from('<H', packet, data_end)[0]
            crc_calculated = crc16_arc(data)

            if crc_received != crc_calculated:
                _LOGGER.warning(
                    "CRC mismatch: received 0x%04x, calculated 0x%04x",
                    crc_received, crc_calculated
                )
                return None

            # Verify inverse command
            cmd_inverse = packet[data_end + 2]
            expected_inverse = (255 - cmd) & 0xFF

            if cmd_inverse != expected_inverse:
                _LOGGER.warning(
                    "Command inverse mismatch: received 0x%02x, expected 0x%02x",
                    cmd_inverse, expected_inverse
                )
                return None

            return QuattroResponse(cmd=cmd, cookie=cookie, data=data)

        except Exception as err:
            _LOGGER.error("Failed to parse QUATTROCANALI packet: %s", err)
            return None


# Command builders for common operations

def build_ping_command() -> QuattroCommand:
    """
    Build a PING command for connectivity testing.

    PING is the simplest command with no data payload,
    perfect for device discovery and connectivity testing.

    Returns:
        QuattroCommand for PING
    """
    return QuattroCommand(cmd=CMD_PING, data=b'')


def build_info_command() -> QuattroCommand:
    """
    Build an INFO command to query device identification.

    Returns device information including:
    - Manufacturer (32 bytes)
    - Family (32 bytes)
    - Model (32 bytes)
    - Serial Number (32 bytes)
    Total: 128 bytes

    Returns:
        QuattroCommand for INFO
    """
    return QuattroCommand(cmd=CMD_INFO, data=b'')


def build_power_command(power_on: bool) -> QuattroCommand:
    """
    Build a power control command.

    Args:
        power_on: True to power on, False to enter standby

    Returns:
        QuattroCommand for power control
    """
    # Power ON: 01 00 00 00 (little-endian)
    # Power OFF: 02 00 00 00 (little-endian)
    data = struct.pack('<I', 1 if power_on else 2)
    return QuattroCommand(cmd=CMD_POWER, data=data)


def parse_info_response(data: bytes) -> Optional[dict]:
    """
    Parse the response from an INFO command.

    Args:
        data: Response data (should be 128 bytes)

    Returns:
        Dictionary with device info or None if invalid
    """
    if len(data) != 128:
        _LOGGER.warning("INFO response has incorrect length: %d (expected 128)", len(data))
        return None

    try:
        # Each field is 32 bytes, null-terminated strings
        manufacturer = data[0:32].split(b'\x00', 1)[0].decode('ascii', errors='ignore').strip()
        family = data[32:64].split(b'\x00', 1)[0].decode('ascii', errors='ignore').strip()
        model = data[64:96].split(b'\x00', 1)[0].decode('ascii', errors='ignore').strip()
        serial = data[96:128].split(b'\x00', 1)[0].decode('ascii', errors='ignore').strip()

        return {
            'manufacturer': manufacturer,
            'family': family,
            'model': model,
            'serial_number': serial,
        }
    except Exception as err:
        _LOGGER.error("Failed to parse INFO response: %s", err)
        return None
