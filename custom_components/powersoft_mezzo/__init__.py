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
    CONF_HOST,
    CONF_PORT,
    CONF_TIMEOUT,
    CONF_SCAN_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
)
from .mezzo_client import MezzoClient

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

    # Store coordinator and client
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        COORDINATOR: coordinator,
        CLIENT: client,
    }

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
