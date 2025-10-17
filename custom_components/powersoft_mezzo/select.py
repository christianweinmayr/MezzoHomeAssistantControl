"""Select platform for Powersoft Mezzo integration."""
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    COORDINATOR,
    CLIENT,
    UID_SOURCE,
    CHANNEL_NUMBERS,
    SOURCE_OPTIONS,
)
from .mezzo_client import MezzoClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Mezzo select entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    client = hass.data[DOMAIN][entry.entry_id][CLIENT]

    entities = []

    # Add input source selectors for each channel
    for channel in CHANNEL_NUMBERS:
        entities.append(MezzoSourceSelect(coordinator, client, entry, channel))

    async_add_entities(entities)


class MezzoSourceSelect(CoordinatorEntity, SelectEntity):
    """Representation of a channel input source selector."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:import"

    def __init__(
        self,
        coordinator,
        client: MezzoClient,
        entry: ConfigEntry,
        channel: int,
    ):
        """Initialize the source select entity."""
        super().__init__(coordinator)
        self._client = client
        self._channel = channel
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Powersoft",
            "model": "Mezzo 602 AD",
        }
        self._attr_unique_id = f"{entry.entry_id}_{UID_SOURCE}{channel}"
        self._attr_name = f"Input Source Channel {channel}"
        self._attr_options = list(SOURCE_OPTIONS.values())

    @property
    def current_option(self) -> str | None:
        """Return the current selected input source."""
        if self.coordinator.data and "sources" in self.coordinator.data:
            source_id = self.coordinator.data["sources"].get(self._channel)
            if source_id is not None:
                return SOURCE_OPTIONS.get(str(source_id), f"Source {source_id}")
        return None

    async def async_select_option(self, option: str) -> None:
        """Select the input source."""
        try:
            # Find source ID from option label
            source_id = None
            for sid, label in SOURCE_OPTIONS.items():
                if label == option:
                    source_id = int(sid)
                    break

            if source_id is None:
                _LOGGER.error("Unknown source option: %s", option)
                return

            await self._client.set_source(self._channel, source_id)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(
                "Failed to set source for channel %d: %s", self._channel, err
            )
            raise
