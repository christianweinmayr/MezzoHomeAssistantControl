"""
Powersoft PBus Protocol Implementation.

This module implements the binary PBus protocol used by Powersoft Mezzo amplifiers
for UDP communication on port 8002.
"""
import struct
import random
from typing import Optional, Tuple, List
from dataclasses import dataclass


# Protocol Constants
STX = 0x02  # Start of frame
ETX = 0x03  # End of frame
ESC = 0x1B  # Escape character
ESCAPE_OFFSET = 0x40  # Offset added to escaped bytes

MAGIC_NUMBER = b'MZO'  # Magic number in response frames
PROTOCOL_ID = 0x0001  # Mezzo protocol identifier

# Opcodes
OPCODE_READ = ord('R')  # 0x52
OPCODE_WRITE = ord('W')  # 0x57
OPCODE_ERASE = ord('E')  # 0x45
OPCODE_CRC = ord('C')  # 0x43

# CRC16-CCITT lookup table
CRC16_TABLE = [
    0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
    0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
    0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
    0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
    0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
    0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
    0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
    0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
    0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
    0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
    0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
    0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
    0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
    0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
    0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
    0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
    0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
    0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
    0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
    0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
    0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
    0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
    0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
    0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
    0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
    0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
    0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
    0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
    0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
    0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
    0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
    0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0
]


def calculate_crc16(data: bytes) -> int:
    """
    Calculate CRC16-CCITT for the given data.

    Uses polynomial x16+x12+x5+1 (0x1021).

    Args:
        data: Bytes to calculate CRC for

    Returns:
        CRC16 value as 16-bit integer
    """
    crc = 0
    for byte in data:
        crc = ((crc << 8) ^ CRC16_TABLE[((crc >> 8) ^ byte) & 0xFF]) & 0xFFFF
    return crc


def escape_data(data: bytes) -> bytes:
    """
    Apply escaping strategy to data.

    Special bytes (STX, ETX, ESC) are escaped by prepending ESC
    and adding 0x40 to the byte value.

    Args:
        data: Raw bytes to escape

    Returns:
        Escaped bytes
    """
    result = bytearray()
    for byte in data:
        if byte in (STX, ETX, ESC):
            result.append(ESC)
            result.append(byte + ESCAPE_OFFSET)
        else:
            result.append(byte)
    return bytes(result)


def unescape_data(data: bytes) -> bytes:
    """
    Remove escaping from data.

    Args:
        data: Escaped bytes

    Returns:
        Unescaped bytes
    """
    result = bytearray()
    i = 0
    while i < len(data):
        if data[i] == ESC and i + 1 < len(data):
            # Next byte is escaped, subtract 0x40 to get original value
            result.append(data[i + 1] - ESCAPE_OFFSET)
            i += 2
        else:
            result.append(data[i])
            i += 1
    return bytes(result)


def generate_tag() -> bytes:
    """
    Generate a random 4-byte TAG for request/response matching.

    Returns:
        4 random bytes
    """
    return random.randbytes(4)


@dataclass
class PBusCommand:
    """Base class for PBus commands."""
    opcode: int
    address: int
    size: int
    data: Optional[bytes] = None

    def to_bytes(self) -> bytes:
        """Convert command to bytes (before escaping)."""
        # OPCODE (1) + ADDR32 (4) + SIZE32 (4) + DATA (variable)
        result = struct.pack('<BII', self.opcode, self.address, self.size)
        if self.data:
            result += self.data
        return result


class ReadCommand(PBusCommand):
    """PBus Read command ('R')."""

    def __init__(self, address: int, size: int):
        """
        Create a read command.

        Args:
            address: 32-bit memory address to read from
            size: Number of bytes to read
        """
        super().__init__(OPCODE_READ, address, size, None)


class WriteCommand(PBusCommand):
    """PBus Write command ('W')."""

    def __init__(self, address: int, data: bytes):
        """
        Create a write command.

        Args:
            address: 32-bit memory address to write to
            data: Bytes to write
        """
        super().__init__(OPCODE_WRITE, address, len(data), data)


@dataclass
class PBusResponse:
    """Parsed PBus command response."""
    opcode: int
    address: int
    size: int
    data: Optional[bytes] = None

    def is_nak(self) -> bool:
        """Check if this is a NAK response (SIZE32 == 0)."""
        return self.size == 0


class PBusPacket:
    """PBus protocol packet builder and parser."""

    @staticmethod
    def build_request(tag: bytes, commands: List[PBusCommand]) -> bytes:
        """
        Build a request packet.

        Args:
            tag: 4-byte TAG for request/response matching
            commands: List of PBus commands to include

        Returns:
            Complete packet ready to send via UDP
        """
        if len(tag) != 4:
            raise ValueError("TAG must be 4 bytes")

        # Build payload (TAG + commands)
        payload = bytearray(tag)
        for cmd in commands:
            payload.extend(cmd.to_bytes())

        # Calculate CRC16 on unescaped payload
        crc = calculate_crc16(bytes(payload))
        payload.extend(struct.pack('<H', crc))

        # Apply escaping to everything except STX and ETX
        escaped = escape_data(bytes(payload))

        # Build final packet: STX + escaped_payload + ETX
        packet = bytearray([STX])
        packet.extend(escaped)
        packet.append(ETX)

        return bytes(packet)

    @staticmethod
    def parse_response(packet: bytes) -> Tuple[bytes, List[PBusResponse]]:
        """
        Parse a response packet.

        Args:
            packet: Complete packet received via UDP

        Returns:
            Tuple of (tag, list of responses)

        Raises:
            ValueError: If packet is malformed or CRC check fails
        """
        if len(packet) < 14:  # Minimum: STX + MZO + ProtID + TAG + CRC + ETX
            raise ValueError("Packet too short")

        if packet[0] != STX:
            raise ValueError(f"Invalid STX: expected 0x02, got 0x{packet[0]:02x}")

        if packet[-1] != ETX:
            raise ValueError(f"Invalid ETX: expected 0x03, got 0x{packet[-1]:02x}")

        # Remove STX and ETX, then unescape
        escaped_payload = packet[1:-1]
        payload = unescape_data(escaped_payload)

        # Verify CRC16 (last 2 bytes)
        if len(payload) < 2:
            raise ValueError("Payload too short for CRC")

        crc_received = struct.unpack('<H', payload[-2:])[0]
        crc_calculated = calculate_crc16(payload[:-2])

        if crc_received != crc_calculated:
            raise ValueError(
                f"CRC mismatch: received 0x{crc_received:04x}, "
                f"calculated 0x{crc_calculated:04x}"
            )

        # Remove CRC from payload
        payload = payload[:-2]

        # Parse header: Magic Number (3) + Protocol ID (2) + TAG (4)
        if len(payload) < 9:
            raise ValueError("Payload too short for header")

        magic = payload[0:3]
        if magic != MAGIC_NUMBER:
            raise ValueError(f"Invalid magic number: {magic}")

        protocol_id = struct.unpack('<H', payload[3:5])[0]
        if protocol_id != PROTOCOL_ID:
            raise ValueError(f"Invalid protocol ID: 0x{protocol_id:04x}")

        tag = payload[5:9]

        # Parse PBus command responses
        responses = []
        offset = 9

        while offset < len(payload):
            if offset + 9 > len(payload):
                raise ValueError("Incomplete PBus response")

            opcode = payload[offset]
            address = struct.unpack('<I', payload[offset+1:offset+5])[0]
            size = struct.unpack('<I', payload[offset+5:offset+9])[0]
            offset += 9

            # Read data if size > 0 (not a NAK)
            # Note: For WRITE responses, the amplifier may set SIZE to the number of
            # bytes written but NOT include the data in the response payload.
            # We only try to read data if it's actually present.
            data = None
            if size > 0:
                # Check if this is a WRITE response
                if opcode == OPCODE_WRITE:
                    # For writes, SIZE indicates bytes written but data is not returned
                    # This is an ACK - don't try to read data
                    pass
                else:
                    # For reads, data should be present
                    if offset + size > len(payload):
                        raise ValueError("Response data extends beyond payload")
                    data = payload[offset:offset+size]
                    offset += size

            responses.append(PBusResponse(opcode, address, size, data))

        return tag, responses


# Convenience functions for data type conversion

def float_to_bytes(value: float) -> bytes:
    """Convert float to 4-byte little-endian representation."""
    return struct.pack('<f', value)


def bytes_to_float(data: bytes) -> float:
    """Convert 4-byte little-endian to float."""
    if len(data) != 4:
        raise ValueError("Float must be 4 bytes")
    return struct.unpack('<f', data)[0]


def uint32_to_bytes(value: int) -> bytes:
    """Convert uint32 to 4-byte little-endian representation."""
    return struct.pack('<I', value)


def bytes_to_uint32(data: bytes) -> int:
    """Convert 4-byte little-endian to uint32."""
    if len(data) != 4:
        raise ValueError("Uint32 must be 4 bytes")
    return struct.unpack('<I', data)[0]


def uint8_to_bytes(value: int) -> bytes:
    """Convert uint8 to 1-byte representation."""
    return struct.pack('<B', value)


def bytes_to_uint8(data: bytes) -> int:
    """Convert 1-byte to uint8."""
    if len(data) != 1:
        raise ValueError("Uint8 must be 1 byte")
    return struct.unpack('<B', data)[0]


def int32_to_bytes(value: int) -> bytes:
    """Convert int32 to 4-byte little-endian representation."""
    return struct.pack('<i', value)


def bytes_to_int32(data: bytes) -> int:
    """Convert 4-byte little-endian to int32."""
    if len(data) != 4:
        raise ValueError("Int32 must be 4 bytes")
    return struct.unpack('<i', data)[0]
