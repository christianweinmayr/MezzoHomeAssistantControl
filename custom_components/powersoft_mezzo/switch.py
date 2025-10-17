"""Switch platform for Powersoft Mezzo integration."""
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    COORDINATOR,
    CLIENT,
    UID_POWER,
    UID_MUTE,
    CHANNEL_NUMBERS,
)
from .mezzo_client import MezzoClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Mezzo switch entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    client = hass.data[DOMAIN][entry.entry_id][CLIENT]

    entities = []

    # Add power switch
    entities.append(MezzoPowerSwitch(coordinator, client, entry))

    # Add mute switches for each channel
    for channel in CHANNEL_NUMBERS:
        entities.append(MezzoMuteSwitch(coordinator, client, entry, channel))

    async_add_entities(entities)


class MezzoPowerSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of the amplifier power switch."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:power"

    def __init__(self, coordinator, client: MezzoClient, entry: ConfigEntry):
        """Initialize the power switch."""
        super().__init__(coordinator)
        self._client = client
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Powersoft",
            "model": "Mezzo 602 AD",
        }
        self._attr_unique_id = f"{entry.entry_id}_{UID_POWER}"
        self._attr_name = "Power"

    @property
    def is_on(self) -> bool | None:
        """Return true if the amplifier is powered on (not in standby)."""
        if self.coordinator.data and "standby" in self.coordinator.data:
            # Standby = True means powered OFF, so invert
            return not self.coordinator.data["standby"]
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the amplifier on (exit standby)."""
        try:
            await self._client.set_standby(False)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to turn on amplifier: %s", err)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the amplifier off (enter standby)."""
        try:
            await self._client.set_standby(True)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to turn off amplifier: %s", err)
            raise


class MezzoMuteSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a channel mute switch."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:volume-off"

    def __init__(
        self,
        coordinator,
        client: MezzoClient,
        entry: ConfigEntry,
        channel: int,
    ):
        """Initialize the mute switch."""
        super().__init__(coordinator)
        self._client = client
        self._channel = channel
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Powersoft",
            "model": "Mezzo 602 AD",
        }
        self._attr_unique_id = f"{entry.entry_id}_{UID_MUTE}{channel}"
        self._attr_name = f"Mute Channel {channel}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the channel is muted."""
        if self.coordinator.data and "mutes" in self.coordinator.data:
            return self.coordinator.data["mutes"].get(self._channel)
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Mute the channel."""
        try:
            await self._client.set_mute(self._channel, True)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to mute channel %d: %s", self._channel, err)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Unmute the channel."""
        try:
            await self._client.set_mute(self._channel, False)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to unmute channel %d: %s", self._channel, err)
            raise
