"""Button platform for Powersoft Mezzo integration."""
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    COORDINATOR,
    CLIENT,
    UID_PRESET,
)
from .mezzo_client import MezzoClient

_LOGGER = logging.getLogger(__name__)

# Default presets (can be customized via configuration)
DEFAULT_PRESETS = [
    {"id": 0, "name": "Preset 1"},
    {"id": 1, "name": "Preset 2"},
    {"id": 2, "name": "Preset 3"},
    {"id": 3, "name": "Preset 4"},
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Mezzo button entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    client = hass.data[DOMAIN][entry.entry_id][CLIENT]

    entities = []

    # Add preset buttons
    for preset in DEFAULT_PRESETS:
        entities.append(
            MezzoPresetButton(
                coordinator,
                client,
                entry,
                preset["id"],
                preset["name"],
            )
        )

    async_add_entities(entities)


class MezzoPresetButton(CoordinatorEntity, ButtonEntity):
    """Representation of a preset button."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:numeric-1-box"

    def __init__(
        self,
        coordinator,
        client: MezzoClient,
        entry: ConfigEntry,
        preset_id: int,
        preset_name: str,
    ):
        """Initialize the preset button."""
        super().__init__(coordinator)
        self._client = client
        self._preset_id = preset_id
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Powersoft",
            "model": "Mezzo 602 AD",
        }
        self._attr_unique_id = f"{entry.entry_id}_{UID_PRESET}_{preset_id}"
        self._attr_name = preset_name

    async def async_press(self) -> None:
        """Handle the button press - load the preset."""
        try:
            _LOGGER.info("Loading preset %d", self._preset_id)
            # Load preset for all speakers (channels)
            for speaker in range(1, 5):  # 4 channels
                await self._client.load_preset(speaker, self._preset_id)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to load preset %d: %s", self._preset_id, err)
            raise
