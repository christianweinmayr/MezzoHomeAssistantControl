"""
The Powersoft Mezzo integration.

This integration provides control and monitoring of Powersoft Mezzo amplifiers
via the PBus protocol over UDP.
"""
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    PLATFORMS,
    COORDINATOR,
    CLIENT,
    SCENE_MANAGER,
    ACTIVE_SCENE_ID,
    CONF_HOST,
    CONF_PORT,
    CONF_TIMEOUT,
    CONF_SCAN_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
)
from .mezzo_client import MezzoClient
from .scene_manager import SceneManager

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Powersoft Mezzo from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    timeout = entry.options.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    _LOGGER.info("Setting up Powersoft Mezzo integration for %s:%d", host, port)

    # Create client
    client = MezzoClient(host, port, timeout)

    # Try to connect
    try:
        await client.connect()
    except Exception as err:
        _LOGGER.error("Failed to connect to amplifier at %s:%d: %s", host, port, err)
        raise ConfigEntryNotReady(f"Unable to connect to amplifier: {err}") from err

    # Create coordinator
    coordinator = MezzoDataUpdateCoordinator(
        hass,
        client,
        update_interval=timedelta(seconds=scan_interval),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Create and load scene manager
    scene_manager = SceneManager(hass, entry.entry_id)
    await scene_manager.async_load()
    _LOGGER.info(
        "Scene manager initialized: %d default + %d custom scenes",
        len(scene_manager.get_all_scenes()) - scene_manager.get_custom_scene_count(),
        scene_manager.get_custom_scene_count()
    )

    # Store coordinator, client, scene manager, and active scene tracking
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        COORDINATOR: coordinator,
        CLIENT: client,
        SCENE_MANAGER: scene_manager,
        ACTIVE_SCENE_ID: None,  # Track currently active scene
    }

    # Register services (only once for the domain)
    if not hass.services.has_service(DOMAIN, "save_scene"):
        await async_register_services(hass)

    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register options update listener
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    _LOGGER.info("Successfully set up Powersoft Mezzo integration")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading Powersoft Mezzo integration")

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Disconnect client
        data = hass.data[DOMAIN].pop(entry.entry_id)
        client: MezzoClient = data[CLIENT]
        await client.disconnect()
        _LOGGER.info("Successfully unloaded Powersoft Mezzo integration")

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    _LOGGER.info("Reloading Powersoft Mezzo integration due to options update")
    await hass.config_entries.async_reload(entry.entry_id)


async def async_register_services(hass: HomeAssistant) -> None:
    """Register integration services."""
    import voluptuous as vol
    from homeassistant.helpers import config_validation as cv

    _LOGGER.info("Registering Powersoft Mezzo services")

    async def handle_save_scene(call):
        """Handle save_scene service call."""
        name = call.data["name"]
        _LOGGER.info("Service call: save_scene with name='%s'", name)

        # Get the first available entry (services are domain-level, not per-entry)
        entry_id = next(iter(hass.data[DOMAIN].keys()))
        data = hass.data[DOMAIN][entry_id]
        client: MezzoClient = data[CLIENT]
        scene_manager: SceneManager = data[SCENE_MANAGER]

        try:
            # Capture current amplifier state
            config = await client.capture_current_state()

            # Save as new scene
            scene_id = await scene_manager.async_create_scene(name, config)

            _LOGGER.info("Successfully created scene '%s' (ID: %d)", name, scene_id)

            # Reload integration to refresh button entities
            await hass.config_entries.async_reload(entry_id)

        except Exception as err:
            _LOGGER.error("Failed to save scene '%s': %s", name, err)
            raise

    async def handle_update_scene(call):
        """Handle update_scene service call."""
        scene_id = call.data["scene_id"]
        _LOGGER.info("Service call: update_scene with scene_id=%d", scene_id)

        # Get the first available entry
        entry_id = next(iter(hass.data[DOMAIN].keys()))
        data = hass.data[DOMAIN][entry_id]
        client: MezzoClient = data[CLIENT]
        scene_manager: SceneManager = data[SCENE_MANAGER]

        try:
            # Capture current amplifier state
            config = await client.capture_current_state()

            # Update existing scene
            await scene_manager.async_update_scene(scene_id, config)

            _LOGGER.info("Successfully updated scene ID %d", scene_id)

            # Reload integration to refresh button entities
            await hass.config_entries.async_reload(entry_id)

        except Exception as err:
            _LOGGER.error("Failed to update scene %d: %s", scene_id, err)
            raise

    async def handle_delete_scene(call):
        """Handle delete_scene service call."""
        scene_id = call.data["scene_id"]
        _LOGGER.info("Service call: delete_scene with scene_id=%d", scene_id)

        # Get the first available entry
        entry_id = next(iter(hass.data[DOMAIN].keys()))
        data = hass.data[DOMAIN][entry_id]
        scene_manager: SceneManager = data[SCENE_MANAGER]

        try:
            # Delete the scene
            await scene_manager.async_delete_scene(scene_id)

            _LOGGER.info("Successfully deleted scene ID %d", scene_id)

            # Reload integration to refresh button entities
            await hass.config_entries.async_reload(entry_id)

        except Exception as err:
            _LOGGER.error("Failed to delete scene %d: %s", scene_id, err)
            raise

    async def handle_rename_scene(call):
        """Handle rename_scene service call."""
        scene_id = call.data["scene_id"]
        new_name = call.data["name"]
        _LOGGER.info("Service call: rename_scene with scene_id=%d, name='%s'", scene_id, new_name)

        # Get the first available entry
        entry_id = next(iter(hass.data[DOMAIN].keys()))
        data = hass.data[DOMAIN][entry_id]
        scene_manager: SceneManager = data[SCENE_MANAGER]

        try:
            # Rename the scene
            await scene_manager.async_rename_scene(scene_id, new_name)

            _LOGGER.info("Successfully renamed scene ID %d", scene_id)

            # Reload integration to refresh button names
            await hass.config_entries.async_reload(entry_id)

        except Exception as err:
            _LOGGER.error("Failed to rename scene %d: %s", scene_id, err)
            raise

    async def handle_capture_eq(call):
        """Handle capture_eq service call (debugging helper)."""
        _LOGGER.warning("Service call: capture_eq - Reading EQ from amplifier...")

        # Get the first available entry
        entry_id = next(iter(hass.data[DOMAIN].keys()))
        data = hass.data[DOMAIN][entry_id]
        client: MezzoClient = data[CLIENT]

        try:
            # Read EQ from amplifier
            eq_config = await client.get_all_eq()

            # Build formatted output
            output_lines = ["Current EQ Configuration:"]
            output_lines.append("=" * 60)

            for ch_idx, channel_eq in enumerate(eq_config):
                output_lines.append(f"\nChannel {ch_idx + 1}:")
                for band_idx, band in enumerate(channel_eq):
                    enabled_str = "ENABLED" if band["enabled"] else "disabled"
                    gain_db = band["gain"]  # Gain is already in dB
                    output_lines.append(
                        f"  Band {band_idx + 1}: {enabled_str:8s} | "
                        f"Type={band['type']:2d} | "
                        f"Freq={band['frequency']:5d}Hz | "
                        f"Gain={gain_db:+.1f}dB | "
                        f"Q={band['q']:.2f}"
                    )

            output_text = "\n".join(output_lines)

            # Log to Home Assistant logs
            _LOGGER.warning("EQ Capture Results:\n%s", output_text)

            # Create persistent notification visible in UI
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Amplifier EQ Configuration",
                    "message": f"```\n{output_text}\n```",
                    "notification_id": f"{DOMAIN}_eq_capture",
                },
            )

            _LOGGER.warning("EQ capture complete. Check notifications for results.")

        except Exception as err:
            _LOGGER.error("Failed to capture EQ: %s", err)
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "EQ Capture Failed",
                    "message": f"Error reading EQ from amplifier: {err}",
                    "notification_id": f"{DOMAIN}_eq_capture_error",
                },
            )
            raise

    async def handle_disable_manual_source_mode(call):
        """Handle disable_manual_source_mode service call (emergency fix)."""
        _LOGGER.warning("Service call: disable_manual_source_mode - Attempting to restore automatic source routing...")

        # Get the first available entry
        entry_id = next(iter(hass.data[DOMAIN].keys()))
        data = hass.data[DOMAIN][entry_id]
        client: MezzoClient = data[CLIENT]

        try:
            # Disable manual source mode
            await client.disable_manual_source_mode()

            # Create success notification
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Manual Source Mode Disabled",
                    "message": "Successfully disabled manual source mode. Automatic source routing should now be restored. If channel 1 is still silent, please power cycle the amplifier.",
                    "notification_id": f"{DOMAIN}_disable_manual_source_mode",
                },
            )

            _LOGGER.warning("Manual source mode disabled successfully.")

        except Exception as err:
            _LOGGER.error("Failed to disable manual source mode: %s", err)
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Manual Source Mode Disable Failed",
                    "message": f"Error disabling manual source mode: {err}",
                    "notification_id": f"{DOMAIN}_disable_manual_source_mode_error",
                },
            )
            raise

    async def handle_read_source_registers(call):
        """Handle read_source_registers service call (diagnostic)."""
        _LOGGER.warning("Service call: read_source_registers - Reading all source registers...")

        # Get the first available entry
        entry_id = next(iter(hass.data[DOMAIN].keys()))
        data = hass.data[DOMAIN][entry_id]
        client: MezzoClient = data[CLIENT]

        try:
            # Read all source registers
            registers = await client.read_all_source_registers()

            # Build formatted output
            output_lines = ["Source Register Diagnostics:"]
            output_lines.append("=" * 60)

            output_lines.append("\nSource ID Status (read-only, shows current active source):")
            for ch in range(1, 5):
                val = registers["source_id_status"].get(ch, "ERROR")
                output_lines.append(f"  Channel {ch}: {val}")

            output_lines.append("\nPriority Source (writable, sets preferred source):")
            for ch in range(1, 5):
                val = registers["priority_source"].get(ch, "ERROR")
                output_lines.append(f"  Channel {ch}: {val}")

            output_lines.append(f"\nManual Source Selection (global): {registers['manual_source_selection']}")
            output_lines.append("  (0 = automatic routing, other = manual override)")

            output_text = "\n".join(output_lines)

            # Log to Home Assistant logs
            _LOGGER.warning("Source Register Diagnostics:\n%s", output_text)

            # Create persistent notification visible in UI
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Source Register Diagnostics",
                    "message": f"```\n{output_text}\n```",
                    "notification_id": f"{DOMAIN}_source_registers",
                },
            )

            _LOGGER.warning("Source register read complete. Check notifications for results.")

        except Exception as err:
            _LOGGER.error("Failed to read source registers: %s", err)
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Source Register Read Failed",
                    "message": f"Error reading source registers: {err}",
                    "notification_id": f"{DOMAIN}_source_registers_error",
                },
            )
            raise

    async def handle_read_all_eq_registers(call):
        """Handle read_all_eq_registers service call (diagnostic)."""
        _LOGGER.warning("Service call: read_all_eq_registers - Reading all EQ memory areas...")

        # Get the first available entry
        entry_id = next(iter(hass.data[DOMAIN].keys()))
        data = hass.data[DOMAIN][entry_id]
        client: MezzoClient = data[CLIENT]

        try:
            # Read all EQ-related memory areas
            eq_data = await client.read_all_eq_areas()

            # Build formatted output
            output_lines = ["EQ Register Diagnostics:"]
            output_lines.append("=" * 60)

            # User EQ (currently implemented)
            output_lines.append("\n1. USER EQ (0x00004100-0x00004280):")
            output_lines.append("   Status: IMPLEMENTED - 4 bands per channel")
            for ch in range(1, 5):
                output_lines.append(f"\n   Channel {ch}:")
                for band in range(1, 5):
                    band_data = eq_data["user_eq"][ch-1][band-1]
                    output_lines.append(
                        f"     Band {band}: enabled={band_data['enabled']}, "
                        f"type={band_data['type']}, freq={band_data['frequency']}Hz, "
                        f"gain={band_data['gain']:.2f}, q={band_data['q']:.2f}"
                    )

            # Source EQ (active input EQ) - parse first 4 bands
            output_lines.append("\n2. SOURCE EQ (0x0000f100-0x0000f340):")
            output_lines.append(f"   Status: Active input EQ - {len(eq_data['source_eq'])} bytes read")

            # Parse first 4 BiQuads (4 bands × 24 bytes = 96 bytes)
            import struct
            for band in range(1, 5):
                offset = (band - 1) * 24
                if offset + 24 <= len(eq_data['source_eq']):
                    biquad_data = eq_data['source_eq'][offset:offset + 24]
                    enabled, filt_type, q, slope, frequency, gain = struct.unpack('<IIffIf', biquad_data)
                    type_name = {0: "Peaking", 11: "Low Shelving", 12: "High Shelving",
                                13: "Low Pass", 14: "High Pass", 15: "Band Pass",
                                16: "Band Stop", 17: "All Pass"}.get(filt_type, f"Type {filt_type}")
                    output_lines.append(
                        f"   Band {band}: enabled={enabled}, type={type_name}, "
                        f"freq={frequency}Hz, gain={gain:.2f}, q={q:.2f}"
                    )

            output_lines.append(f"   Raw hex (first 256 bytes): {eq_data['source_eq'][:256].hex()}")

            # Source Config area
            output_lines.append("\n3. SOURCE CONFIG (0x00002500-0x00002554):")
            output_lines.append(f"   Status: UNKNOWN - {len(eq_data['source_config'])} bytes read")
            output_lines.append(f"   Raw hex: {eq_data['source_config'].hex()}")

            # Ways area (sample only - it's large)
            output_lines.append("\n4. WAYS AREA (0x00007000-0x00007950):")
            output_lines.append(f"   Status: UNKNOWN - {len(eq_data['ways_area'])} bytes read")
            output_lines.append(f"   Raw hex (first 256 bytes): {eq_data['ways_area'][:256].hex()}")

            output_text = "\n".join(output_lines)

            # Log to Home Assistant logs
            _LOGGER.warning("EQ Register Diagnostics:\n%s", output_text)

            # Create persistent notification visible in UI
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "EQ Register Diagnostics",
                    "message": f"```\n{output_text}\n```",
                    "notification_id": f"{DOMAIN}_eq_registers",
                },
            )

            _LOGGER.warning("EQ register read complete. Check notifications for results.")

        except Exception as err:
            _LOGGER.error("Failed to read EQ registers: %s", err)
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "EQ Register Read Failed",
                    "message": f"Error reading EQ registers: {err}",
                    "notification_id": f"{DOMAIN}_eq_registers_error",
                },
            )
            raise

    async def handle_read_zone_registers(call):
        """Handle read_zone_registers service call (diagnostic)."""
        _LOGGER.warning("Service call: read_zone_registers - Reading Zone control registers...")

        # Get the first available entry
        entry_id = next(iter(hass.data[DOMAIN].keys()))
        data = hass.data[DOMAIN][entry_id]
        client: MezzoClient = data[CLIENT]

        try:
            from .pbus_protocol import ReadCommand, bytes_to_uint8, bytes_to_float, bytes_to_uint32
            from .mezzo_memory_map import (
                ADDR_ZONE_ENABLE_CH1, ADDR_ZONE_MUTE_CH1,
                ADDR_ZONE_GAIN_CH1, ADDR_ZONE_SOURCE_GUID_CH1,
                ADDR_ZONE_GUID_CH1
            )

            # Read Zone control registers
            commands = [
                # Zone Enable (4 bytes, one per channel)
                ReadCommand(ADDR_ZONE_ENABLE_CH1, 4),
                # Zone Mute (4 bytes, one per channel)
                ReadCommand(ADDR_ZONE_MUTE_CH1, 4),
                # Zone Gain (16 bytes, 4 floats)
                ReadCommand(ADDR_ZONE_GAIN_CH1, 16),
                # Zone Source GUIDs (16 bytes, 4 uint32s)
                ReadCommand(ADDR_ZONE_SOURCE_GUID_CH1, 16),
                # Zone GUIDs (16 bytes, 4 uint32s)
                ReadCommand(ADDR_ZONE_GUID_CH1, 16),
            ]

            responses = await client._udp.send_request(commands)

            # Build formatted output
            output_lines = ["Zone Register Diagnostics:"]
            output_lines.append("=" * 60)

            # Zone Enable
            output_lines.append("\nZone Enable (per channel):")
            if not responses[0].is_nak():
                for i in range(4):
                    val = responses[0].data[i] if i < len(responses[0].data) else 0
                    output_lines.append(f"  Channel {i+1}: {val}")

            # Zone Mute
            output_lines.append("\nZone Mute (per channel):")
            if not responses[1].is_nak():
                for i in range(4):
                    val = responses[1].data[i] if i < len(responses[1].data) else 0
                    output_lines.append(f"  Channel {i+1}: {val}")

            # Zone Gain
            output_lines.append("\nZone Gain (linear, per channel):")
            if not responses[2].is_nak():
                import struct
                for i in range(4):
                    offset = i * 4
                    if offset + 4 <= len(responses[2].data):
                        val = struct.unpack('<f', responses[2].data[offset:offset+4])[0]
                        output_lines.append(f"  Channel {i+1}: {val:.4f}")

            # Zone Source GUIDs
            output_lines.append("\nZone Source GUIDs (per channel):")
            if not responses[3].is_nak():
                import struct
                for i in range(4):
                    offset = i * 4
                    if offset + 4 <= len(responses[3].data):
                        val = struct.unpack('<I', responses[3].data[offset:offset+4])[0]
                        output_lines.append(f"  Channel {i+1}: 0x{val:08x}")

            # Zone GUIDs
            output_lines.append("\nZone GUIDs (per channel):")
            if not responses[4].is_nak():
                import struct
                for i in range(4):
                    offset = i * 4
                    if offset + 4 <= len(responses[4].data):
                        val = struct.unpack('<I', responses[4].data[offset:offset+4])[0]
                        output_lines.append(f"  Channel {i+1}: 0x{val:08x}")

            output_text = "\n".join(output_lines)

            # Log to Home Assistant logs
            _LOGGER.warning("Zone Register Diagnostics:\n%s", output_text)

            # Create persistent notification
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Zone Register Diagnostics",
                    "message": f"```\n{output_text}\n```",
                    "notification_id": f"{DOMAIN}_zone_registers",
                },
            )

            _LOGGER.warning("Zone register read complete. Check notifications for results.")

        except Exception as err:
            _LOGGER.error("Failed to read zone registers: %s", err)
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Zone Register Read Failed",
                    "message": f"Error reading zone registers: {err}",
                    "notification_id": f"{DOMAIN}_zone_registers_error",
                },
            )
            raise

    async def handle_enable_manual_source_mode(call):
        """Handle enable_manual_source_mode service call (emergency recovery)."""
        source_id = call.data["source_id"]
        _LOGGER.warning("Service call: enable_manual_source_mode with source_id=%d", source_id)

        # Get the first available entry
        entry_id = next(iter(hass.data[DOMAIN].keys()))
        data = hass.data[DOMAIN][entry_id]
        client: MezzoClient = data[CLIENT]

        try:
            # Enable manual source mode with specific source
            await client.enable_manual_source_mode(source_id)

            # Create success notification
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Manual Source Mode Enabled",
                    "message": f"Successfully enabled manual source mode. ALL channels are now forced to source {source_id}. This overrides per-channel settings.",
                    "notification_id": f"{DOMAIN}_enable_manual_source_mode",
                },
            )

            _LOGGER.warning("Manual source mode enabled successfully with source %d.", source_id)

        except Exception as err:
            _LOGGER.error("Failed to enable manual source mode: %s", err)
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Manual Source Mode Enable Failed",
                    "message": f"Error enabling manual source mode: {err}",
                    "notification_id": f"{DOMAIN}_enable_manual_source_mode_error",
                },
            )
            raise

    # Register services
    hass.services.async_register(
        DOMAIN,
        "save_scene",
        handle_save_scene,
        schema=vol.Schema({
            vol.Required("name"): cv.string,
        }),
    )

    hass.services.async_register(
        DOMAIN,
        "update_scene",
        handle_update_scene,
        schema=vol.Schema({
            vol.Required("scene_id"): cv.positive_int,
        }),
    )

    hass.services.async_register(
        DOMAIN,
        "delete_scene",
        handle_delete_scene,
        schema=vol.Schema({
            vol.Required("scene_id"): cv.positive_int,
        }),
    )

    hass.services.async_register(
        DOMAIN,
        "rename_scene",
        handle_rename_scene,
        schema=vol.Schema({
            vol.Required("scene_id"): cv.positive_int,
            vol.Required("name"): cv.string,
        }),
    )

    hass.services.async_register(
        DOMAIN,
        "capture_eq",
        handle_capture_eq,
        schema=vol.Schema({}),
    )

    hass.services.async_register(
        DOMAIN,
        "disable_manual_source_mode",
        handle_disable_manual_source_mode,
        schema=vol.Schema({}),
    )

    hass.services.async_register(
        DOMAIN,
        "enable_manual_source_mode",
        handle_enable_manual_source_mode,
        schema=vol.Schema({
            vol.Required("source_id"): vol.All(vol.Coerce(int), vol.Range(min=-1, max=31)),
        }),
    )

    hass.services.async_register(
        DOMAIN,
        "read_source_registers",
        handle_read_source_registers,
        schema=vol.Schema({}),
    )

    hass.services.async_register(
        DOMAIN,
        "read_all_eq_registers",
        handle_read_all_eq_registers,
        schema=vol.Schema({}),
    )

    hass.services.async_register(
        DOMAIN,
        "read_zone_registers",
        handle_read_zone_registers,
        schema=vol.Schema({}),
    )


class MezzoDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Mezzo amplifier data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: MezzoClient,
        update_interval: timedelta,
    ):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.client = client

    async def _async_update_data(self):
        """Fetch data from amplifier."""
        try:
            # Get complete state in single batch request
            state = await self.client.get_all_state()
            _LOGGER.debug("Updated amplifier state: %s", state)
            return state

        except TimeoutError as err:
            raise UpdateFailed(f"Timeout communicating with amplifier: {err}") from err
        except ConnectionError as err:
            raise UpdateFailed(f"Connection error: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error updating data: {err}") from err
