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
    UID_SCENE,
    CONF_SCENES,
    DEFAULT_SCENES,
)
from .mezzo_client import MezzoClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Mezzo button entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    client = hass.data[DOMAIN][entry.entry_id][CLIENT]

    entities = []

    # Get scene configurations from entry options or use defaults
    scenes = entry.options.get(CONF_SCENES, DEFAULT_SCENES)

    # Add scene buttons
    for scene in scenes:
        entities.append(
            MezzoSceneButton(
                coordinator,
                client,
                entry,
                scene,
            )
        )

    async_add_entities(entities)


class MezzoSceneButton(CoordinatorEntity, ButtonEntity):
    """Representation of a scene button."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:palette"

    def __init__(
        self,
        coordinator,
        client: MezzoClient,
        entry: ConfigEntry,
        scene_config: dict,
    ):
        """Initialize the scene button."""
        super().__init__(coordinator)
        self._client = client
        self._scene_config = scene_config
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Powersoft",
            "model": "Mezzo 602 AD",
        }
        self._attr_unique_id = f"{entry.entry_id}_{UID_SCENE}_{scene_config['id']}"
        self._attr_name = scene_config["name"]

    async def async_press(self) -> None:
        """Handle the button press - apply the scene."""
        try:
            _LOGGER.info("Applying scene: %s", self._scene_config["name"])
            await self._client.apply_scene(self._scene_config)
            # Force immediate coordinator refresh to show new state
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(
                "Failed to apply scene %s: %s", self._scene_config["name"], err
            )
            raise
