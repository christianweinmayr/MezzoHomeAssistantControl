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

    # Store coordinator, client, and scene manager
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        COORDINATOR: coordinator,
        CLIENT: client,
        SCENE_MANAGER: scene_manager,
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
                    gain_db = 20 * __import__('math').log10(band["gain"]) if band["gain"] > 0 else -float('inf')
                    output_lines.append(
                        f"  Band {band_idx + 1}: {enabled_str:8s} | "
                        f"Type={band['type']:2d} | "
                        f"Freq={band['frequency']:5d}Hz | "
                        f"Gain={band['gain']:.2f} ({gain_db:+.1f}dB) | "
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
