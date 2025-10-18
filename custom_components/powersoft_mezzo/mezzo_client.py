"""
Powersoft Mezzo Amplifier Client.

High-level API for controlling and monitoring Powersoft Mezzo amplifiers.
Provides convenient methods for all control functions.
"""
import logging
import struct
from typing import Optional, Dict, Any, List
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
    get_priority_source_address,
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
    # EQ
    get_user_eq_biquad_address,
    NUM_EQ_BANDS,
    EQ_BIQUAD_SIZE,
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

        # Try both approaches: priority source AND manual source selection
        # Priority source address
        addr_priority = get_priority_source_address(channel)
        # Manual source selection global address
        from .mezzo_memory_map import ADDR_MANUAL_SOURCE_SELECTION

        commands = [
            WriteCommand(addr_priority, int32_to_bytes(source_id)),
            WriteCommand(ADDR_MANUAL_SOURCE_SELECTION, int32_to_bytes(source_id)),
        ]

        _LOGGER.warning(
            "Setting channel %d source to %d - writing to 0x%08x and 0x%08x",
            channel, source_id, addr_priority, ADDR_MANUAL_SOURCE_SELECTION
        )
        responses = await self._udp.send_request(commands)

        for i, resp in enumerate(responses):
            if resp.is_nak():
                _LOGGER.warning("Command %d NAK'd when setting source", i)

        _LOGGER.warning("Source set complete for channel %d", channel)

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

    async def set_eq_band(
        self,
        channel: int,
        band: int,
        enabled: int,
        filt_type: int,
        q: float,
        slope: float,
        frequency: int,
        gain: float
    ) -> None:
        """
        Write EQ band configuration to amplifier.

        Args:
            channel: Channel number (1-4)
            band: Band number (1-4)
            enabled: 1 if enabled, 0 if disabled
            filt_type: Filter type (0=peaking, 11=low shelf, etc.)
            q: Quality factor
            slope: Filter slope
            frequency: Center frequency in Hz
            gain: Linear gain value

        Raises:
            ValueError: If channel or band out of range
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        if not 1 <= channel <= NUM_CHANNELS:
            raise ValueError(f"Channel must be 1-{NUM_CHANNELS}")
        if not 1 <= band <= NUM_EQ_BANDS:
            raise ValueError(f"Band must be 1-{NUM_EQ_BANDS}")

        # Pack BiQuad structure (24 bytes)
        biquad_data = struct.pack(
            '<IIffIf',  # Little-endian
            enabled,
            filt_type,
            q,
            slope,
            frequency,
            gain,
        )

        addr = get_user_eq_biquad_address(channel, band)
        cmd = WriteCommand(addr, biquad_data)

        _LOGGER.debug("Setting EQ CH%d Band%d: enabled=%d, type=%d, freq=%dHz, gain=%.2f",
                     channel, band, enabled, filt_type, frequency, gain)
        responses = await self._udp.send_request([cmd])

        if responses[0].is_nak():
            raise ValueError(f"Failed to write EQ band {band} for channel {channel}")

    async def get_eq_band(self, channel: int, band: int) -> Dict[str, Any]:
        """
        Read EQ band configuration from amplifier.

        Args:
            channel: Channel number (1-4)
            band: Band number (1-4)

        Returns:
            Dictionary with EQ band configuration:
            - enabled: 1 if enabled, 0 if disabled
            - type: Filter type (0=peaking, 11=low shelf, etc.)
            - q: Quality factor
            - slope: Filter slope
            - frequency: Center frequency in Hz
            - gain: Linear gain

        Raises:
            ValueError: If channel or band out of range
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        if not 1 <= channel <= NUM_CHANNELS:
            raise ValueError(f"Channel must be 1-{NUM_CHANNELS}")
        if not 1 <= band <= NUM_EQ_BANDS:
            raise ValueError(f"Band must be 1-{NUM_EQ_BANDS}")

        addr = get_user_eq_biquad_address(channel, band)
        cmd = ReadCommand(addr, EQ_BIQUAD_SIZE)
        responses = await self._udp.send_request([cmd])

        if responses[0].is_nak():
            raise ValueError(f"Failed to read EQ band {band} for channel {channel}")

        # Parse BiQuad structure
        data = responses[0].data
        enabled, filt_type, q, slope, frequency, gain = struct.unpack('<IIffIf', data)

        return {
            "enabled": enabled,
            "type": filt_type,
            "q": q,
            "slope": slope,
            "frequency": frequency,
            "gain": gain,
        }

    async def get_all_eq(self) -> List[List[Dict[str, Any]]]:
        """
        Read all EQ configurations from amplifier.

        Returns:
            List of 4 channels, each containing list of 4 bands with EQ config

        Raises:
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        # Build multicommand to read all EQ bands at once
        commands = []
        for ch in range(1, NUM_CHANNELS + 1):
            for band in range(1, NUM_EQ_BANDS + 1):
                addr = get_user_eq_biquad_address(ch, band)
                commands.append(ReadCommand(addr, EQ_BIQUAD_SIZE))

        _LOGGER.debug("Reading all EQ settings (16 bands)...")
        responses = await self._udp.send_request(commands)

        # Parse responses into nested structure
        eq_config = []
        resp_idx = 0

        for ch in range(NUM_CHANNELS):
            channel_bands = []
            for band in range(NUM_EQ_BANDS):
                resp = responses[resp_idx]
                resp_idx += 1

                if resp.is_nak():
                    _LOGGER.warning("Failed to read EQ CH%d Band%d", ch+1, band+1)
                    # Use default flat EQ
                    channel_bands.append({
                        "enabled": 0,
                        "type": 0,
                        "q": 1.0,
                        "slope": 1.0,
                        "frequency": 1000,
                        "gain": 1.0,
                    })
                else:
                    # Parse BiQuad structure
                    data = resp.data
                    enabled, filt_type, q, slope, frequency, gain = struct.unpack('<IIffIf', data)
                    channel_bands.append({
                        "enabled": enabled,
                        "type": filt_type,
                        "q": q,
                        "slope": slope,
                        "frequency": frequency,
                        "gain": gain,
                    })

            eq_config.append(channel_bands)

        return eq_config

    async def capture_current_state(self) -> Dict[str, Any]:
        """
        Capture complete current amplifier state for scene creation.

        Reads all volumes, mutes, sources, EQ settings, and standby state.

        Returns:
            Dictionary with complete scene configuration ready to save

        Raises:
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        _LOGGER.info("Capturing current amplifier state...")

        # Get basic state
        state = await self.get_all_state()

        # Get EQ settings
        eq_config = await self.get_all_eq()

        # Build scene configuration
        scene_config = {
            "volumes": [state['volumes'].get(i, 0.5) for i in range(1, NUM_CHANNELS + 1)],
            "mutes": [state['mutes'].get(i, False) for i in range(1, NUM_CHANNELS + 1)],
            "sources": [state['sources'].get(i, 0) for i in range(1, NUM_CHANNELS + 1)],
            "eq": eq_config,
            "standby": state.get('standby', False),
        }

        _LOGGER.info("Captured state: %d channels with full EQ", NUM_CHANNELS)
        return scene_config

    async def apply_scene(self, scene_config: Dict[str, Any]) -> None:
        """
        Apply a complete scene configuration via multicommand.

        This is the recommended way to load scenes/presets. It applies all
        configuration changes (volumes, mutes, sources, power) in a single
        PBus packet for maximum efficiency and atomicity.

        Args:
            scene_config: Dictionary with scene configuration:
                - volumes: List[float] - Volume levels 0.0-1.0 for channels 1-4
                - mutes: List[bool] - Mute states for channels 1-4
                - sources: List[int] - Source IDs for channels 1-4
                - eq: List[List[Dict]] - EQ settings (4 channels x 4 bands) (optional)
                - standby: bool - Standby state (optional)

        Raises:
            ValueError: If configuration is invalid
            ConnectionError: If not connected
            TimeoutError: If request times out

        Example:
            scene = {
                "volumes": [0.7, 0.7, 0.5, 0.5],
                "mutes": [False, False, False, False],
                "sources": [1, 1, 2, 2],
                "standby": False
            }
            await client.apply_scene(scene)
        """
        commands = []

        # Validate configuration
        if 'volumes' not in scene_config or len(scene_config['volumes']) != NUM_CHANNELS:
            raise ValueError(f"Scene must contain 'volumes' list with {NUM_CHANNELS} entries")
        if 'mutes' not in scene_config or len(scene_config['mutes']) != NUM_CHANNELS:
            raise ValueError(f"Scene must contain 'mutes' list with {NUM_CHANNELS} entries")
        if 'sources' not in scene_config or len(scene_config['sources']) != NUM_CHANNELS:
            raise ValueError(f"Scene must contain 'sources' list with {NUM_CHANNELS} entries")

        # Build write commands for all channels
        for ch in range(1, NUM_CHANNELS + 1):
            # Volume
            volume = scene_config['volumes'][ch - 1]
            if not 0.0 <= volume <= 1.0:
                raise ValueError(f"Volume for channel {ch} must be between 0.0 and 1.0")
            addr = get_user_gain_address(ch)
            commands.append(WriteCommand(addr, float_to_bytes(volume)))

            # Mute
            muted = scene_config['mutes'][ch - 1]
            addr = get_user_mute_address(ch)
            value = MUTE_ON if muted else MUTE_OFF
            commands.append(WriteCommand(addr, uint8_to_bytes(value)))

            # Source
            source = scene_config['sources'][ch - 1]
            if not SOURCE_MIN <= source <= SOURCE_MAX:
                raise ValueError(f"Source ID for channel {ch} must be {SOURCE_MIN}-{SOURCE_MAX}")
            addr = get_source_id_address(ch)
            commands.append(WriteCommand(addr, int32_to_bytes(source)))

        # EQ settings (optional)
        if 'eq' in scene_config:
            eq_channels = scene_config['eq']
            if len(eq_channels) != NUM_CHANNELS:
                raise ValueError(f"Scene EQ must contain {NUM_CHANNELS} channel configurations")

            for ch in range(1, NUM_CHANNELS + 1):
                eq_bands = eq_channels[ch - 1]
                if len(eq_bands) != NUM_EQ_BANDS:
                    raise ValueError(f"Channel {ch} EQ must contain {NUM_EQ_BANDS} band configurations")

                for band in range(1, NUM_EQ_BANDS + 1):
                    band_config = eq_bands[band - 1]

                    # Build BiQuad structure (24 bytes):
                    # +0x00: Enabled (uint32, 4 bytes)
                    # +0x04: Type (uint32, 4 bytes)
                    # +0x08: Q (Float, 4 bytes)
                    # +0x0C: Slope (Float, 4 bytes)
                    # +0x10: Frequency (uint32, 4 bytes)
                    # +0x14: Gain (Float, 4 bytes)
                    biquad_data = struct.pack(
                        '<IIffIf',  # Little-endian: 2x uint32, 2x float, uint32, float
                        band_config.get('enabled', 0),
                        band_config.get('type', 0),
                        band_config.get('q', 1.0),
                        band_config.get('slope', 1.0),
                        band_config.get('frequency', 1000),
                        band_config.get('gain', 1.0),
                    )

                    addr = get_user_eq_biquad_address(ch, band)
                    commands.append(WriteCommand(addr, biquad_data))

        # Power state (optional)
        if 'standby' in scene_config:
            standby = scene_config['standby']
            value = STANDBY_ACTIVATE if standby else STANDBY_DEACTIVATE
            commands.append(WriteCommand(ADDR_STANDBY_TRIGGER, uint32_to_bytes(value)))

        # Send commands in batches for better performance
        # We can batch commands efficiently now that write response parsing is fixed
        scene_name = scene_config.get('name', 'Unknown')
        _LOGGER.info("Applying scene '%s' with %d commands", scene_name, len(commands))

        try:
            # Split into reasonable batch sizes (12 commands per batch = volumes + mutes + sources)
            # This way we can send basic controls, then EQ, then power
            batch_size = 12
            failed_count = 0

            for batch_start in range(0, len(commands), batch_size):
                batch = commands[batch_start:batch_start + batch_size]
                try:
                    responses = await self._udp.send_request(batch, timeout=3.0)
                    # Check for NAKs
                    for i, resp in enumerate(responses):
                        if resp.is_nak():
                            cmd_idx = batch_start + i
                            _LOGGER.warning("Command %d/%d NAK (addr=0x%08x)",
                                          cmd_idx+1, len(commands), commands[cmd_idx].address)
                            failed_count += 1
                except Exception as batch_err:
                    _LOGGER.warning("Batch %d-%d failed: %s",
                                  batch_start+1, min(batch_start+batch_size, len(commands)), batch_err)
                    failed_count += len(batch)

            if failed_count > 0:
                _LOGGER.warning("Scene '%s' applied with %d/%d failures", scene_name, failed_count, len(commands))
            else:
                _LOGGER.info("Scene '%s' applied successfully", scene_name)

        except Exception as err:
            _LOGGER.error("Failed to apply scene '%s': %s", scene_name, err)
            raise

    async def load_preset(self, speaker: int, preset_id: int) -> None:
        """
        DEPRECATED: Load preset for speaker using old preset type addresses.

        Note: This method uses the deprecated ADDR_PRESET_TYPE_SPK addresses
        which may not work on newer firmware. Use apply_scene() instead.

        Args:
            speaker: Speaker number (1-4)
            preset_id: Preset ID to load

        Raises:
            ValueError: If speaker out of range
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        _LOGGER.warning("load_preset() is deprecated. Use apply_scene() instead.")

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
        DEPRECATED: Get current preset for speaker.

        Note: This method uses the deprecated ADDR_PRESET_TYPE_SPK addresses
        which may not work on newer firmware.

        Args:
            speaker: Speaker number (1-4)

        Returns:
            Current preset ID

        Raises:
            ValueError: If speaker out of range
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        _LOGGER.warning("get_preset() is deprecated.")

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
            Dictionary containing all amplifier state including EQ

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

        # Add EQ band read commands (4 channels × 4 bands)
        for ch in range(1, NUM_CHANNELS + 1):
            for band in range(1, NUM_EQ_BANDS + 1):
                addr = get_user_eq_biquad_address(ch, band)
                commands.append(ReadCommand(addr, EQ_BIQUAD_SIZE))

        responses = await self._udp.send_request(commands)

        state = {
            'standby': bool(bytes_to_uint32(responses[0].data)) if not responses[0].is_nak() else None,
            'volumes': {},
            'mutes': {},
            'sources': {},
            'temperatures': {},
            'fault_code': None,
            'eq': {},  # Store EQ by channel/band: eq[channel][band]
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

        # Parse EQ bands (starting at response index 16)
        resp_idx = 16
        for ch in range(1, NUM_CHANNELS + 1):
            if ch not in state['eq']:
                state['eq'][ch] = {}
            for band in range(1, NUM_EQ_BANDS + 1):
                resp = responses[resp_idx]
                resp_idx += 1

                if not resp.is_nak():
                    # Parse BiQuad structure
                    data = resp.data
                    enabled, filt_type, q, slope, frequency, gain = struct.unpack('<IIffIf', data)
                    state['eq'][ch][band] = {
                        "enabled": enabled,
                        "type": filt_type,
                        "q": q,
                        "slope": slope,
                        "frequency": frequency,
                        "gain": gain,
                    }
                else:
                    # Use default if read failed
                    state['eq'][ch][band] = {
                        "enabled": 0,
                        "type": 0,
                        "q": 1.0,
                        "slope": 1.0,
                        "frequency": 1000,
                        "gain": 1.0,
                    }

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
