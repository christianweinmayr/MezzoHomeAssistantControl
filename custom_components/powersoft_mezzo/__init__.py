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

            # Source EQ - output channels 1-4, 2 bands each (192 bytes total)
            output_lines.append("\n2. SOURCE EQ (0x0000f100-0x0000f1c0):")
            output_lines.append("   Status: Source EQ per output channel - 2 bands each")

            import struct
            for ch in range(1, 5):
                output_lines.append(f"\n   Output Channel {ch}:")
                for band in range(1, 3):  # Only 2 bands per channel
                    offset = ((ch - 1) * 2 + (band - 1)) * 24
                    if offset + 24 <= len(eq_data['source_eq']):
                        biquad_data = eq_data['source_eq'][offset:offset + 24]
                        enabled, filt_type, q, slope, frequency, gain = struct.unpack('<IIffIf', biquad_data)
                        type_name = {0: "Peaking", 11: "Low Shelving", 12: "High Shelving",
                                    13: "Low Pass", 14: "High Pass", 15: "Band Pass",
                                    16: "Band Stop", 17: "All Pass"}.get(filt_type, f"Type {filt_type}")
                        output_lines.append(
                            f"     Band {band}: enabled={enabled}, type={type_name}, "
                            f"freq={frequency}Hz, gain={gain:.2f}, q={q:.2f}"
                        )

            # Zone EQ - output channels 1-4, 4 bands each (384 bytes, offset at 192)
            output_lines.append("\n3. ZONE EQ (0x0000f1c0-0x0000f340):")
            output_lines.append("   Status: Zone EQ per output channel - 4 bands each")

            zone_eq_offset = 192  # Source EQ is 4 channels × 2 bands × 24 bytes = 192 bytes
            for ch in range(1, 5):
                output_lines.append(f"\n   Output Channel {ch}:")
                for band in range(1, 5):  # 4 bands per channel
                    offset = zone_eq_offset + ((ch - 1) * 4 + (band - 1)) * 24
                    if offset + 24 <= len(eq_data['source_eq']):
                        biquad_data = eq_data['source_eq'][offset:offset + 24]
                        enabled, filt_type, q, slope, frequency, gain = struct.unpack('<IIffIf', biquad_data)
                        type_name = {0: "Peaking", 11: "Low Shelving", 12: "High Shelving",
                                    13: "Low Pass", 14: "High Pass", 15: "Band Pass",
                                    16: "Band Stop", 17: "All Pass"}.get(filt_type, f"Type {filt_type}")
                        output_lines.append(
                            f"     Band {band}: enabled={enabled}, type={type_name}, "
                            f"freq={frequency}Hz, gain={gain:.2f}, q={q:.2f}"
                        )

            # Source Config area
            output_lines.append("\n4. SOURCE CONFIG (0x00002500-0x00002554):")
            output_lines.append(f"   Status: UNKNOWN - {len(eq_data['source_config'])} bytes read")
            output_lines.append(f"   Raw hex: {eq_data['source_config'].hex()}")

            # Ways area (sample only - it's large)
            output_lines.append("\n5. WAYS AREA (0x00007000-0x00007950):")
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

    async def handle_test_quattro_direct(call):
        """Handle test_quattro_direct service call (diagnostic)."""
        host = call.data["host"]
        timeout = call.data.get("timeout", 2.0)

        _LOGGER.warning("Service call: test_quattro_direct - Testing QUATTROCANALI protocol at %s", host)

        try:
            from .quattro_protocol import build_power_command, DEFAULT_PORT as QUATTRO_PORT, QuattroResponse
            from .udp_manager import UDPProtocol
            import asyncio

            # Build formatted output
            output_lines = ["QUATTROCANALI Direct Test Results:"]
            output_lines.append("=" * 60)
            output_lines.append(f"Target: {host}:{QUATTRO_PORT}")
            output_lines.append(f"Timeout: {timeout}s")
            output_lines.append("")

            # Create a simple power query command
            test_cmd = build_power_command(True)
            packet = test_cmd.build_packet()

            output_lines.append(f"Sending QUATTROCANALI packet ({len(packet)} bytes):")
            output_lines.append(f"  Hex: {packet.hex()}")
            output_lines.append("")

            # Create UDP socket and send directly (not broadcast)
            response_data = None
            response_event = asyncio.Event()

            def handle_response(data: bytes, addr):
                nonlocal response_data
                response_data = data
                response_event.set()

            loop = asyncio.get_event_loop()
            transport, protocol = await loop.create_datagram_endpoint(
                lambda: UDPProtocol(handle_response),
                local_addr=('0.0.0.0', 0),
            )

            try:
                # Send directly to the host (unicast, not broadcast)
                _LOGGER.info("Sending QUATTROCANALI packet to %s:%d", host, QUATTRO_PORT)
                transport.sendto(packet, (host, QUATTRO_PORT))

                # Wait for response
                try:
                    await asyncio.wait_for(response_event.wait(), timeout=timeout)

                    output_lines.append("✓ RESPONSE RECEIVED!")
                    output_lines.append(f"  Response size: {len(response_data)} bytes")
                    output_lines.append(f"  Hex: {response_data.hex()}")
                    output_lines.append("")

                    # Try to parse response
                    quattro_resp = QuattroResponse.parse_packet(response_data)
                    if quattro_resp:
                        output_lines.append("✓ VALID QUATTROCANALI PROTOCOL!")
                        output_lines.append(f"  Command: 0x{quattro_resp.cmd:02x}")
                        output_lines.append(f"  Cookie: {quattro_resp.cookie}")
                        output_lines.append(f"  Data: {quattro_resp.data.hex()}")
                        output_lines.append("")
                        output_lines.append("SUCCESS: Device responds to QUATTROCANALI protocol!")
                    else:
                        output_lines.append("⚠ Response received but failed QUATTROCANALI parsing")
                        output_lines.append("  The device may use a different protocol variant")

                except asyncio.TimeoutError:
                    output_lines.append("✗ NO RESPONSE (timeout after {timeout}s)")
                    output_lines.append("")
                    output_lines.append("Troubleshooting:")
                    output_lines.append("- Check device is powered on and network connected")
                    output_lines.append("- Verify IP address is correct")
                    output_lines.append("- Check firewall settings")
                    output_lines.append("- Device may require different command or authentication")

            finally:
                transport.close()

            output_text = "\n".join(output_lines)

            # Log to Home Assistant logs
            _LOGGER.warning("QUATTROCANALI Direct Test Results:\n%s", output_text)

            # Create persistent notification
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "QUATTROCANALI Direct Test",
                    "message": f"```\n{output_text}\n```",
                    "notification_id": f"{DOMAIN}_quattro_direct_test",
                },
            )

        except Exception as err:
            _LOGGER.error("Failed to test QUATTROCANALI direct: %s", err)
            import traceback
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "QUATTROCANALI Direct Test Failed",
                    "message": f"Error: {err}\n\n{traceback.format_exc()}",
                    "notification_id": f"{DOMAIN}_quattro_direct_test_error",
                },
            )
            raise

    async def handle_test_port_scan(call):
        """Handle test_port_scan service call (diagnostic)."""
        host = call.data["host"]
        start_port = call.data.get("start_port", 8000)
        end_port = call.data.get("end_port", 8010)
        timeout = call.data.get("timeout", 0.5)

        _LOGGER.warning(
            "Service call: test_port_scan - Testing %s ports %d-%d (timeout=%.1fs)",
            host, start_port, end_port, timeout
        )

        try:
            from .pbus_protocol import ReadCommand
            from .mezzo_memory_map import ADDR_STANDBY_STATE

            # Simple read command to test connectivity
            test_cmd = ReadCommand(ADDR_STANDBY_STATE, 4)

            # Build formatted output
            output_lines = ["Port Scan Results:"]
            output_lines.append("=" * 60)
            output_lines.append(f"Target: {host}")
            output_lines.append(f"Port range: {start_port}-{end_port}")
            output_lines.append(f"Timeout per port: {timeout}s")
            output_lines.append("")

            responsive_ports = []

            for port in range(start_port, end_port + 1):
                _LOGGER.debug("Testing port %d...", port)

                # Create temporary client for this port
                temp_client = MezzoClient(host, port, timeout)

                try:
                    await temp_client.connect()
                    responses = await temp_client._udp.send_request([test_cmd], timeout=timeout)

                    # Check if we got a valid response
                    if responses and not responses[0].is_nak():
                        output_lines.append(f"Port {port}: ✓ RESPONSE (got valid data)")
                        responsive_ports.append(port)
                        _LOGGER.info("Port %d responded with valid data!", port)
                    else:
                        output_lines.append(f"Port {port}: ⚠ NAK (device responded but rejected command)")
                        _LOGGER.debug("Port %d sent NAK", port)

                except TimeoutError:
                    output_lines.append(f"Port {port}: ✗ No response (timeout)")
                    _LOGGER.debug("Port %d timed out", port)
                except Exception as e:
                    output_lines.append(f"Port {port}: ✗ Error - {e}")
                    _LOGGER.debug("Port %d error: %s", port, e)
                finally:
                    await temp_client.disconnect()

            output_lines.append("")
            output_lines.append("=" * 60)
            if responsive_ports:
                output_lines.append(f"Found {len(responsive_ports)} responsive port(s): {', '.join(map(str, responsive_ports))}")
                output_lines.append("")
                output_lines.append("Next steps:")
                output_lines.append(f"- Use port {responsive_ports[0]} to communicate with this device")
                output_lines.append("- Try read_device_info service with this IP to get more info")
            else:
                output_lines.append("No responsive ports found.")
                output_lines.append("")
                output_lines.append("Troubleshooting:")
                output_lines.append("- Verify the device is powered on and network connected")
                output_lines.append("- Check firewall settings")
                output_lines.append("- Try a wider port range (e.g., 8000-9000)")
                output_lines.append("- The device may use TCP instead of UDP")
                output_lines.append("- The device may use a different protocol entirely")

            output_text = "\n".join(output_lines)

            # Log to Home Assistant logs
            _LOGGER.warning("Port Scan Results:\n%s", output_text)

            # Create persistent notification
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Port Scan Results",
                    "message": f"```\n{output_text}\n```",
                    "notification_id": f"{DOMAIN}_port_scan",
                },
            )

            _LOGGER.warning("Port scan complete. Found %d responsive port(s). Check notifications for details.", len(responsive_ports))

        except Exception as err:
            _LOGGER.error("Failed to perform port scan: %s", err)
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Port Scan Failed",
                    "message": f"Error during port scan: {err}",
                    "notification_id": f"{DOMAIN}_port_scan_error",
                },
            )
            raise

    async def handle_discover_amplifiers(call):
        """Handle discover_amplifiers service call (diagnostic)."""
        timeout = call.data.get("timeout", 5.0)
        _LOGGER.warning("Service call: discover_amplifiers with timeout=%.1fs", timeout)

        try:
            from .mezzo_client import discover_amplifiers

            # Run discovery
            _LOGGER.info("Starting amplifier discovery scan...")
            devices = await discover_amplifiers(timeout=timeout)

            # Build formatted output
            output_lines = ["Amplifier Discovery Results:"]
            output_lines.append("=" * 60)
            output_lines.append(f"Scan timeout: {timeout}s")
            output_lines.append(f"Devices found: {len(devices)}")
            output_lines.append("")

            if devices:
                for ip, info in devices.items():
                    output_lines.append(f"Device at {ip}:")
                    output_lines.append(f"  Model: {info.get('model', 'Unknown')}")
                    standby = info.get('standby', None)
                    standby_str = "ON (standby)" if standby else "OFF (active)" if standby is not None else "Unknown"
                    output_lines.append(f"  Power: {standby_str}")
                    output_lines.append("")
            else:
                output_lines.append("No amplifiers found on network.")
                output_lines.append("")
                output_lines.append("Troubleshooting:")
                output_lines.append("- Ensure amplifiers are powered on")
                output_lines.append("- Check network connectivity")
                output_lines.append("- Verify UDP port 8002 is not blocked")
                output_lines.append("- Try increasing timeout value")
                output_lines.append("- Check if amplifiers are on same network/VLAN")

            output_text = "\n".join(output_lines)

            # Log to Home Assistant logs
            _LOGGER.warning("Amplifier Discovery Results:\n%s", output_text)

            # Create persistent notification
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Amplifier Discovery",
                    "message": f"```\n{output_text}\n```",
                    "notification_id": f"{DOMAIN}_discover_amplifiers",
                },
            )

            _LOGGER.warning("Discovery scan complete. Found %d device(s). Check notifications for details.", len(devices))

        except Exception as err:
            _LOGGER.error("Failed to discover amplifiers: %s", err)
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Amplifier Discovery Failed",
                    "message": f"Error during discovery scan: {err}",
                    "notification_id": f"{DOMAIN}_discover_amplifiers_error",
                },
            )
            raise

    async def handle_read_device_info(call):
        """Handle read_device_info service call (diagnostic)."""
        host = call.data.get("host")

        if host:
            _LOGGER.warning("Service call: read_device_info - Reading device information from %s...", host)
        else:
            _LOGGER.warning("Service call: read_device_info - Reading device information...")

        # Determine which client to use
        if host:
            # Create temporary client for specified host
            temp_client = MezzoClient(host, DEFAULT_PORT, DEFAULT_TIMEOUT)
            client = temp_client
            should_cleanup = True
        else:
            # Use configured client
            entry_id = next(iter(hass.data[DOMAIN].keys()))
            data = hass.data[DOMAIN][entry_id]
            client = data[CLIENT]
            should_cleanup = False

        try:
            # Connect if using temporary client
            if should_cleanup:
                await client.connect()

            from .pbus_protocol import ReadCommand, bytes_to_string, bytes_to_uint32, bytes_to_float
            from .mezzo_memory_map import (
                ADDR_MODEL_NAME,
                ADDR_SERIAL_NUMBER,
                ADDR_FIRMWARE_VERSION,
                ADDR_MAC_ADDRESS,
                ADDR_STANDBY_STATE,
                ADDR_TEMP_TRANSFORMER,
                ADDR_TEMP_HEATSINK,
                ADDR_TEMP_CH1, ADDR_TEMP_CH2, ADDR_TEMP_CH3, ADDR_TEMP_CH4,
                ADDR_FAULT_CODE,
            )

            # Query all device info
            commands = [
                ReadCommand(ADDR_MODEL_NAME, 20),
                ReadCommand(ADDR_SERIAL_NUMBER, 16),
                ReadCommand(ADDR_FIRMWARE_VERSION, 20),
                ReadCommand(ADDR_MAC_ADDRESS, 6),
                ReadCommand(ADDR_STANDBY_STATE, 4),
                ReadCommand(ADDR_TEMP_TRANSFORMER, 4),
                ReadCommand(ADDR_TEMP_HEATSINK, 4),
                ReadCommand(ADDR_TEMP_CH1, 4),
                ReadCommand(ADDR_TEMP_CH2, 4),
                ReadCommand(ADDR_TEMP_CH3, 4),
                ReadCommand(ADDR_TEMP_CH4, 4),
                ReadCommand(ADDR_FAULT_CODE, 1),
            ]

            responses = await client._udp.send_request(commands)

            # Build formatted output
            output_lines = ["Device Information:"]
            output_lines.append("=" * 70)

            # Device Identification
            output_lines.append("\n[DEVICE IDENTIFICATION]")

            # Model name
            if len(responses) > 0 and not responses[0].is_nak() and responses[0].data:
                try:
                    model = bytes_to_string(responses[0].data)
                    output_lines.append(f"  Model Name:       {model}")
                    output_lines.append(f"  Raw Data (hex):   {responses[0].data.hex()}")
                except Exception as e:
                    output_lines.append(f"  Model Name:       ERROR - {e}")
                    output_lines.append(f"  Raw Data (hex):   {responses[0].data.hex()}")
            else:
                output_lines.append(f"  Model Name:       NAK or no response")

            # Serial number
            if len(responses) > 1 and not responses[1].is_nak() and responses[1].data:
                try:
                    serial = bytes_to_string(responses[1].data)
                    output_lines.append(f"  Serial Number:    {serial}")
                    output_lines.append(f"  Raw Data (hex):   {responses[1].data.hex()}")
                except Exception as e:
                    output_lines.append(f"  Serial Number:    ERROR - {e}")
                    output_lines.append(f"  Raw Data (hex):   {responses[1].data.hex()}")
            else:
                output_lines.append(f"  Serial Number:    NAK or no response")

            # Firmware version
            if len(responses) > 2 and not responses[2].is_nak() and responses[2].data:
                try:
                    firmware = bytes_to_string(responses[2].data)
                    output_lines.append(f"  Firmware Version: {firmware}")
                    output_lines.append(f"  Raw Data (hex):   {responses[2].data.hex()}")
                except Exception as e:
                    output_lines.append(f"  Firmware Version: ERROR - {e}")
                    output_lines.append(f"  Raw Data (hex):   {responses[2].data.hex()}")
            else:
                output_lines.append(f"  Firmware Version: NAK or no response")

            # MAC address
            if len(responses) > 3 and not responses[3].is_nak() and responses[3].data:
                mac_bytes = responses[3].data[:6]
                mac_addr = ":".join([f"{b:02x}" for b in mac_bytes])
                output_lines.append(f"  MAC Address:      {mac_addr}")
            else:
                output_lines.append(f"  MAC Address:      NAK or no response")

            # Device Status
            output_lines.append("\n[DEVICE STATUS]")

            # Standby state
            if len(responses) > 4 and not responses[4].is_nak() and responses[4].data:
                standby = bool(bytes_to_uint32(responses[4].data))
                output_lines.append(f"  Standby State:    {'STANDBY' if standby else 'ACTIVE'}")
            else:
                output_lines.append(f"  Standby State:    NAK or no response")

            # Temperatures
            output_lines.append("\n[TEMPERATURES]")

            temp_labels = [
                ("Transformer", 5),
                ("Heatsink", 6),
                ("Channel 1", 7),
                ("Channel 2", 8),
                ("Channel 3", 9),
                ("Channel 4", 10),
            ]

            for label, idx in temp_labels:
                if len(responses) > idx and not responses[idx].is_nak() and responses[idx].data:
                    try:
                        temp = bytes_to_float(responses[idx].data)
                        output_lines.append(f"  {label:12s}:  {temp:.1f}°C")
                    except Exception as e:
                        output_lines.append(f"  {label:12s}:  ERROR - {e}")
                else:
                    output_lines.append(f"  {label:12s}:  NAK or no response")

            # Fault code
            if len(responses) > 11 and not responses[11].is_nak() and responses[11].data:
                from .pbus_protocol import bytes_to_uint8
                fault_code = bytes_to_uint8(responses[11].data)
                output_lines.append(f"\n[FAULT STATUS]")
                output_lines.append(f"  Fault Code:       {fault_code} (0x{fault_code:02x})")
            else:
                output_lines.append(f"\n[FAULT STATUS]")
                output_lines.append(f"  Fault Code:       NAK or no response")

            # Memory addresses for reference
            output_lines.append("\n[MEMORY ADDRESSES QUERIED]")
            output_lines.append(f"  Model Name:       0x{ADDR_MODEL_NAME:08x}")
            output_lines.append(f"  Serial Number:    0x{ADDR_SERIAL_NUMBER:08x}")
            output_lines.append(f"  Firmware Version: 0x{ADDR_FIRMWARE_VERSION:08x}")
            output_lines.append(f"  MAC Address:      0x{ADDR_MAC_ADDRESS:08x}")
            output_lines.append(f"  Standby State:    0x{ADDR_STANDBY_STATE:08x}")

            output_text = "\n".join(output_lines)

            # Log to Home Assistant logs
            _LOGGER.warning("Device Information:\n%s", output_text)

            # Create persistent notification visible in UI
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Device Information",
                    "message": f"```\n{output_text}\n```",
                    "notification_id": f"{DOMAIN}_device_info",
                },
            )

            _LOGGER.warning("Device information query complete. Check notifications for results.")

        except Exception as err:
            _LOGGER.error("Failed to read device information: %s", err)
            import traceback
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Device Information Read Failed",
                    "message": f"Error reading device information: {err}\n\nTraceback:\n{traceback.format_exc()}",
                    "notification_id": f"{DOMAIN}_device_info_error",
                },
            )
            raise
        finally:
            # Disconnect temporary client if we created one
            if should_cleanup:
                await client.disconnect()

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

    hass.services.async_register(
        DOMAIN,
        "read_device_info",
        handle_read_device_info,
        schema=vol.Schema({
            vol.Optional("host"): cv.string,
        }),
    )

    hass.services.async_register(
        DOMAIN,
        "discover_amplifiers",
        handle_discover_amplifiers,
        schema=vol.Schema({
            vol.Optional("timeout", default=5.0): vol.All(vol.Coerce(float), vol.Range(min=1.0, max=30.0)),
        }),
    )

    hass.services.async_register(
        DOMAIN,
        "test_port_scan",
        handle_test_port_scan,
        schema=vol.Schema({
            vol.Required("host"): cv.string,
            vol.Optional("start_port", default=8000): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
            vol.Optional("end_port", default=8010): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
            vol.Optional("timeout", default=0.5): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=5.0)),
        }),
    )

    hass.services.async_register(
        DOMAIN,
        "test_quattro_direct",
        handle_test_quattro_direct,
        schema=vol.Schema({
            vol.Required("host"): cv.string,
            vol.Optional("timeout", default=2.0): vol.All(vol.Coerce(float), vol.Range(min=0.5, max=10.0)),
        }),
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
