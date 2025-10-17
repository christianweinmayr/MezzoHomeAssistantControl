"""
Powersoft Mezzo Amplifier Client.

High-level API for controlling and monitoring Powersoft Mezzo amplifiers.
Provides convenient methods for all control functions.
"""
import logging
from typing import Optional, Dict, Any
import math

from .udp_manager import UDPManager, UDPBroadcaster
from .pbus_protocol import (
    ReadCommand,
    WriteCommand,
    float_to_bytes,
    bytes_to_float,
    uint32_to_bytes,
    bytes_to_uint32,
    uint8_to_bytes,
    bytes_to_uint8,
    int32_to_bytes,
    bytes_to_int32,
)
from .mezzo_memory_map import (
    # Power/Standby
    ADDR_STANDBY_TRIGGER,
    ADDR_STANDBY_STATE,
    STANDBY_ACTIVATE,
    STANDBY_DEACTIVATE,
    # Volume/Gain
    get_user_gain_address,
    get_zone_gain_address,
    # Mute
    get_user_mute_address,
    get_zone_mute_address,
    MUTE_ON,
    MUTE_OFF,
    # Source
    get_source_id_address,
    SOURCE_MIN,
    SOURCE_MAX,
    SOURCE_MUTED,
    # Presets
    ADDR_PRESET_TYPE_SPK1,
    # Temperatures
    ADDR_TEMP_TRANSFORMER,
    ADDR_TEMP_HEATSINK,
    get_temp_channel_address,
    # Faults
    ADDR_FAULT_CODE,
    ADDR_ALARM_GENERIC_FAULT,
    get_mute_code_flags_address,
    FAULT_CODES,
    MUTE_CODES,
    # Misc
    NUM_CHANNELS,
)

_LOGGER = logging.getLogger(__name__)


class MezzoClient:
    """
    High-level client for Powersoft Mezzo amplifiers.

    Provides convenient methods for controlling power, volume, mute,
    input selection, and monitoring amplifier status.
    """

    def __init__(self, host: str, port: int = 8002, timeout: float = 2.0):
        """
        Initialize the Mezzo client.

        Args:
            host: IP address of the amplifier
            port: UDP port (default 8002)
            timeout: Default timeout for requests
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self._udp = UDPManager(host, port, timeout)

    async def connect(self) -> None:
        """Connect to the amplifier."""
        await self._udp.connect()

    async def disconnect(self) -> None:
        """Disconnect from the amplifier."""
        await self._udp.disconnect()

    @property
    def is_connected(self) -> bool:
        """Check if connected to amplifier."""
        return self._udp.is_connected

    # ========================================================================
    # Power Control
    # ========================================================================

    async def set_standby(self, standby: bool) -> None:
        """
        Set amplifier standby state.

        Args:
            standby: True to activate standby (power off), False to deactivate (power on)

        Raises:
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        value = STANDBY_ACTIVATE if standby else STANDBY_DEACTIVATE
        cmd = WriteCommand(ADDR_STANDBY_TRIGGER, uint32_to_bytes(value))

        _LOGGER.info("Setting standby to %s", standby)
        responses = await self._udp.send_request([cmd])

        if responses[0].is_nak():
            raise ValueError("Failed to set standby state")

    async def get_standby_state(self) -> bool:
        """
        Get current standby state.

        Returns:
            True if in standby (powered off), False if powered on

        Raises:
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        cmd = ReadCommand(ADDR_STANDBY_STATE, 4)
        responses = await self._udp.send_request([cmd])

        if responses[0].is_nak():
            raise ValueError("Failed to read standby state")

        value = bytes_to_uint32(responses[0].data)
        return bool(value)

    # ========================================================================
    # Volume/Gain Control
    # ========================================================================

    async def set_volume(self, channel: int, volume: float, use_user_gain: bool = True) -> None:
        """
        Set channel volume/gain.

        Args:
            channel: Channel number (1-4)
            volume: Volume level 0.0-1.0 (linear gain)
            use_user_gain: Use user gain area (True) or zone gain area (False)

        Raises:
            ValueError: If channel or volume out of range
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        if not 1 <= channel <= NUM_CHANNELS:
            raise ValueError(f"Channel must be 1-{NUM_CHANNELS}")
        if not 0.0 <= volume <= 1.0:
            raise ValueError("Volume must be between 0.0 and 1.0")

        addr = get_user_gain_address(channel) if use_user_gain else get_zone_gain_address(channel)
        cmd = WriteCommand(addr, float_to_bytes(volume))

        _LOGGER.debug("Setting channel %d volume to %.2f", channel, volume)
        responses = await self._udp.send_request([cmd])

        if responses[0].is_nak():
            raise ValueError(f"Failed to set volume for channel {channel}")

    async def get_volume(self, channel: int, use_user_gain: bool = True) -> float:
        """
        Get channel volume/gain.

        Args:
            channel: Channel number (1-4)
            use_user_gain: Read from user gain area (True) or zone gain area (False)

        Returns:
            Volume level 0.0-1.0 (linear gain)

        Raises:
            ValueError: If channel out of range
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        if not 1 <= channel <= NUM_CHANNELS:
            raise ValueError(f"Channel must be 1-{NUM_CHANNELS}")

        addr = get_user_gain_address(channel) if use_user_gain else get_zone_gain_address(channel)
        cmd = ReadCommand(addr, 4)
        responses = await self._udp.send_request([cmd])

        if responses[0].is_nak():
            raise ValueError(f"Failed to read volume for channel {channel}")

        return bytes_to_float(responses[0].data)

    @staticmethod
    def volume_to_db(volume: float) -> float:
        """
        Convert linear volume (0.0-1.0) to dB.

        Args:
            volume: Linear volume 0.0-1.0

        Returns:
            Volume in dB (-inf to 0.0)
        """
        if volume <= 0.0:
            return float('-inf')
        return 20 * math.log10(volume)

    @staticmethod
    def db_to_volume(db: float) -> float:
        """
        Convert dB to linear volume (0.0-1.0).

        Args:
            db: Volume in dB (-inf to 0.0)

        Returns:
            Linear volume 0.0-1.0
        """
        if db == float('-inf'):
            return 0.0
        return 10 ** (db / 20)

    # ========================================================================
    # Mute Control
    # ========================================================================

    async def set_mute(self, channel: int, muted: bool, use_user_mute: bool = True) -> None:
        """
        Set channel mute state.

        Args:
            channel: Channel number (1-4)
            muted: True to mute, False to unmute
            use_user_mute: Use user mute area (True) or zone mute area (False)

        Raises:
            ValueError: If channel out of range
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        if not 1 <= channel <= NUM_CHANNELS:
            raise ValueError(f"Channel must be 1-{NUM_CHANNELS}")

        addr = get_user_mute_address(channel) if use_user_mute else get_zone_mute_address(channel)
        value = MUTE_ON if muted else MUTE_OFF
        cmd = WriteCommand(addr, uint8_to_bytes(value))

        _LOGGER.debug("Setting channel %d mute to %s", channel, muted)
        responses = await self._udp.send_request([cmd])

        if responses[0].is_nak():
            raise ValueError(f"Failed to set mute for channel {channel}")

    async def get_mute(self, channel: int, use_user_mute: bool = True) -> bool:
        """
        Get channel mute state.

        Args:
            channel: Channel number (1-4)
            use_user_mute: Read from user mute area (True) or zone mute area (False)

        Returns:
            True if muted, False if unmuted

        Raises:
            ValueError: If channel out of range
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        if not 1 <= channel <= NUM_CHANNELS:
            raise ValueError(f"Channel must be 1-{NUM_CHANNELS}")

        addr = get_user_mute_address(channel) if use_user_mute else get_zone_mute_address(channel)
        cmd = ReadCommand(addr, 1)
        responses = await self._udp.send_request([cmd])

        if responses[0].is_nak():
            raise ValueError(f"Failed to read mute for channel {channel}")

        return bool(bytes_to_uint8(responses[0].data))

    # ========================================================================
    # Source/Input Selection
    # ========================================================================

    async def set_source(self, channel: int, source_id: int) -> None:
        """
        Set input source for channel.

        Args:
            channel: Channel number (1-4)
            source_id: Source ID (-1 for muted, 0-31 for sources)

        Raises:
            ValueError: If channel or source_id out of range
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        if not 1 <= channel <= NUM_CHANNELS:
            raise ValueError(f"Channel must be 1-{NUM_CHANNELS}")
        if not SOURCE_MIN <= source_id <= SOURCE_MAX:
            raise ValueError(f"Source ID must be {SOURCE_MIN}-{SOURCE_MAX}")

        addr = get_source_id_address(channel)
        # Source ID is stored as 4 int8 values, we write to the first one
        cmd = WriteCommand(addr, int32_to_bytes(source_id))

        _LOGGER.debug("Setting channel %d source to %d", channel, source_id)
        responses = await self._udp.send_request([cmd])

        if responses[0].is_nak():
            raise ValueError(f"Failed to set source for channel {channel}")

    async def get_source(self, channel: int) -> int:
        """
        Get current input source for channel.

        Args:
            channel: Channel number (1-4)

        Returns:
            Source ID (-1 for muted, 0-31 for sources)

        Raises:
            ValueError: If channel out of range
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        if not 1 <= channel <= NUM_CHANNELS:
            raise ValueError(f"Channel must be 1-{NUM_CHANNELS}")

        addr = get_source_id_address(channel)
        cmd = ReadCommand(addr, 4)
        responses = await self._udp.send_request([cmd])

        if responses[0].is_nak():
            raise ValueError(f"Failed to read source for channel {channel}")

        return bytes_to_int32(responses[0].data)

    # ========================================================================
    # Preset/Scene Management
    # ========================================================================

    async def load_preset(self, speaker: int, preset_id: int) -> None:
        """
        Load preset for speaker.

        Args:
            speaker: Speaker number (1-4)
            preset_id: Preset ID to load

        Raises:
            ValueError: If speaker out of range
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        if not 1 <= speaker <= NUM_CHANNELS:
            raise ValueError(f"Speaker must be 1-{NUM_CHANNELS}")

        addr = ADDR_PRESET_TYPE_SPK1 + ((speaker - 1) * 4)
        cmd = WriteCommand(addr, int32_to_bytes(preset_id))

        _LOGGER.info("Loading preset %d for speaker %d", preset_id, speaker)
        responses = await self._udp.send_request([cmd])

        if responses[0].is_nak():
            raise ValueError(f"Failed to load preset for speaker {speaker}")

    async def get_preset(self, speaker: int) -> int:
        """
        Get current preset for speaker.

        Args:
            speaker: Speaker number (1-4)

        Returns:
            Current preset ID

        Raises:
            ValueError: If speaker out of range
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        if not 1 <= speaker <= NUM_CHANNELS:
            raise ValueError(f"Speaker must be 1-{NUM_CHANNELS}")

        addr = ADDR_PRESET_TYPE_SPK1 + ((speaker - 1) * 4)
        cmd = ReadCommand(addr, 4)
        responses = await self._udp.send_request([cmd])

        if responses[0].is_nak():
            raise ValueError(f"Failed to read preset for speaker {speaker}")

        return bytes_to_int32(responses[0].data)

    # ========================================================================
    # Status Monitoring
    # ========================================================================

    async def get_temperatures(self) -> Dict[str, float]:
        """
        Get all temperature readings.

        Returns:
            Dictionary with temperature readings in Celsius:
            - transformer: Transformer temperature
            - heatsink: Heatsink temperature
            - ch1, ch2, ch3, ch4: Channel temperatures

        Raises:
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        # Build multicommand to read all temperatures at once
        commands = [
            ReadCommand(ADDR_TEMP_TRANSFORMER, 4),
            ReadCommand(ADDR_TEMP_HEATSINK, 4),
            ReadCommand(get_temp_channel_address(1), 4),
            ReadCommand(get_temp_channel_address(2), 4),
            ReadCommand(get_temp_channel_address(3), 4),
            ReadCommand(get_temp_channel_address(4), 4),
        ]

        responses = await self._udp.send_request(commands)

        temps = {}
        if not responses[0].is_nak():
            temps['transformer'] = bytes_to_float(responses[0].data)
        if not responses[1].is_nak():
            temps['heatsink'] = bytes_to_float(responses[1].data)
        for i in range(NUM_CHANNELS):
            if not responses[2 + i].is_nak():
                temps[f'ch{i+1}'] = bytes_to_float(responses[2 + i].data)

        return temps

    async def get_fault_code(self) -> tuple[int, str]:
        """
        Get current fault code.

        Returns:
            Tuple of (fault_code, fault_description)

        Raises:
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        cmd = ReadCommand(ADDR_FAULT_CODE, 1)
        responses = await self._udp.send_request([cmd])

        if responses[0].is_nak():
            raise ValueError("Failed to read fault code")

        code = bytes_to_uint8(responses[0].data)
        description = FAULT_CODES.get(code, f"Unknown fault code: 0x{code:02x}")
        return code, description

    async def get_mute_codes(self, channel: int) -> Dict[int, str]:
        """
        Get active mute reasons for channel.

        Args:
            channel: Channel number (1-4)

        Returns:
            Dictionary mapping bit positions to mute reasons

        Raises:
            ValueError: If channel out of range
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        if not 1 <= channel <= NUM_CHANNELS:
            raise ValueError(f"Channel must be 1-{NUM_CHANNELS}")

        addr = get_mute_code_flags_address(channel)
        cmd = ReadCommand(addr, 4)
        responses = await self._udp.send_request([cmd])

        if responses[0].is_nak():
            raise ValueError(f"Failed to read mute codes for channel {channel}")

        flags = bytes_to_uint32(responses[0].data)

        # Extract active mute reasons
        active_mutes = {}
        for bit, reason in MUTE_CODES.items():
            if flags & (1 << bit):
                active_mutes[bit] = reason

        return active_mutes

    async def get_all_state(self) -> Dict[str, Any]:
        """
        Get complete amplifier state in a single batch request.

        Returns:
            Dictionary containing all amplifier state

        Raises:
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        # Build multicommand to read all important state
        commands = [
            # Power
            ReadCommand(ADDR_STANDBY_STATE, 4),
            # Volumes (all channels)
            ReadCommand(get_user_gain_address(1), 4),
            ReadCommand(get_user_gain_address(2), 4),
            ReadCommand(get_user_gain_address(3), 4),
            ReadCommand(get_user_gain_address(4), 4),
            # Mutes (all channels)
            ReadCommand(get_user_mute_address(1), 1),
            ReadCommand(get_user_mute_address(2), 1),
            ReadCommand(get_user_mute_address(3), 1),
            ReadCommand(get_user_mute_address(4), 1),
            # Sources (all channels)
            ReadCommand(get_source_id_address(1), 4),
            ReadCommand(get_source_id_address(2), 4),
            ReadCommand(get_source_id_address(3), 4),
            ReadCommand(get_source_id_address(4), 4),
            # Temperatures
            ReadCommand(ADDR_TEMP_TRANSFORMER, 4),
            ReadCommand(ADDR_TEMP_HEATSINK, 4),
            # Fault
            ReadCommand(ADDR_FAULT_CODE, 1),
        ]

        responses = await self._udp.send_request(commands)

        state = {
            'standby': bool(bytes_to_uint32(responses[0].data)) if not responses[0].is_nak() else None,
            'volumes': {},
            'mutes': {},
            'sources': {},
            'temperatures': {},
            'fault_code': None,
        }

        # Parse volumes
        for i in range(NUM_CHANNELS):
            if not responses[1 + i].is_nak():
                state['volumes'][i + 1] = bytes_to_float(responses[1 + i].data)

        # Parse mutes
        for i in range(NUM_CHANNELS):
            if not responses[5 + i].is_nak():
                state['mutes'][i + 1] = bool(bytes_to_uint8(responses[5 + i].data))

        # Parse sources
        for i in range(NUM_CHANNELS):
            if not responses[9 + i].is_nak():
                state['sources'][i + 1] = bytes_to_int32(responses[9 + i].data)

        # Parse temperatures
        if not responses[13].is_nak():
            state['temperatures']['transformer'] = bytes_to_float(responses[13].data)
        if not responses[14].is_nak():
            state['temperatures']['heatsink'] = bytes_to_float(responses[14].data)

        # Parse fault
        if not responses[15].is_nak():
            state['fault_code'] = bytes_to_uint8(responses[15].data)

        return state

    # ========================================================================
    # Context Manager Support
    # ========================================================================

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


async def discover_amplifiers(timeout: float = 5.0) -> Dict[str, Dict[str, Any]]:
    """
    Discover Mezzo amplifiers on the network.

    Args:
        timeout: Time to wait for responses

    Returns:
        Dictionary mapping IP addresses to device information
    """
    # Broadcast a read request for device info
    # We'll try to read the standby state as a simple identify command
    cmd = ReadCommand(ADDR_STANDBY_STATE, 4)

    _LOGGER.info("Starting amplifier discovery...")
    responses_by_host = await UDPBroadcaster.broadcast([cmd], timeout=timeout)

    devices = {}
    for host, responses in responses_by_host.items():
        if responses and not responses[0].is_nak():
            devices[host] = {
                'host': host,
                'standby': bool(bytes_to_uint32(responses[0].data)),
                'model': 'Mezzo 602 AD',  # Could be extended to read actual model
            }
            _LOGGER.info("Discovered amplifier at %s", host)

    _LOGGER.info("Discovery complete: found %d amplifier(s)", len(devices))
    return devices
