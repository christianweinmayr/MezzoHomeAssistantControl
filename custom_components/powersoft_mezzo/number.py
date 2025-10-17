"""Number platform for Powersoft Mezzo integration."""
import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    COORDINATOR,
    CLIENT,
    UID_VOLUME,
    CHANNEL_NUMBERS,
)
from .mezzo_client import MezzoClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Mezzo number entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    client = hass.data[DOMAIN][entry.entry_id][CLIENT]

    entities = []

    # Add volume controls for each channel
    for channel in CHANNEL_NUMBERS:
        entities.append(MezzoVolumeNumber(coordinator, client, entry, channel))

    async_add_entities(entities)


class MezzoVolumeNumber(CoordinatorEntity, NumberEntity):
    """Representation of a channel volume control."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:volume-high"
    _attr_native_min_value = 0.0
    _attr_native_max_value = 100.0
    _attr_native_step = 1.0
    _attr_native_unit_of_measurement = "%"
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        coordinator,
        client: MezzoClient,
        entry: ConfigEntry,
        channel: int,
    ):
        """Initialize the volume number entity."""
        super().__init__(coordinator)
        self._client = client
        self._channel = channel
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Powersoft",
            "model": "Mezzo 602 AD",
        }
        self._attr_unique_id = f"{entry.entry_id}_{UID_VOLUME}{channel}"
        self._attr_name = f"Volume Channel {channel}"

    @property
    def native_value(self) -> float | None:
        """Return the current volume (0-100%)."""
        if self.coordinator.data and "volumes" in self.coordinator.data:
            # Convert linear gain (0.0-1.0) to percentage (0-100)
            linear_gain = self.coordinator.data["volumes"].get(self._channel)
            if linear_gain is not None:
                return linear_gain * 100.0
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the volume (0-100%)."""
        try:
            # Convert percentage (0-100) to linear gain (0.0-1.0)
            linear_gain = value / 100.0
            await self._client.set_volume(self._channel, linear_gain)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(
                "Failed to set volume for channel %d: %s", self._channel, err
            )
            raise
