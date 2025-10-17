"""Button platform for Powersoft Mezzo integration."""
import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import (
    DOMAIN,
    COORDINATOR,
    CLIENT,
    SCENE_MANAGER,
    UID_SCENE,
)
from .mezzo_client import MezzoClient
from .scene_manager import SceneManager

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Mezzo button entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    client = hass.data[DOMAIN][entry.entry_id][CLIENT]
    scene_manager: SceneManager = hass.data[DOMAIN][entry.entry_id][SCENE_MANAGER]

    @callback
    def async_add_scene_buttons():
        """Add or update scene button entities."""
        # Get all scenes (default + custom)
        scenes = scene_manager.get_all_scenes()

        # Create button entities
        entities = []
        for scene in scenes:
            entities.append(
                MezzoSceneButton(
                    coordinator,
                    client,
                    entry,
                    scene,
                )
            )

        async_add_entities(entities, update_before_add=True)
        _LOGGER.info("Added %d scene button(s)", len(entities))

    # Add initial buttons
    async_add_scene_buttons()

    # Listen for scene updates to dynamically add/remove buttons
    entry.async_on_unload(
        async_dispatcher_connect(
            hass,
            f"{DOMAIN}_scenes_updated_{entry.entry_id}",
            async_add_scene_buttons,
        )
    )


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

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {
            "scene_id": self._scene_config["id"],
            "volumes": self._scene_config.get("volumes", []),
            "mutes": self._scene_config.get("mutes", []),
            "sources": self._scene_config.get("sources", []),
            "standby": self._scene_config.get("standby", False),
        }

        # Add timestamps if available (custom scenes only)
        if "created_at" in self._scene_config:
            attrs["created_at"] = self._scene_config["created_at"]
        if "updated_at" in self._scene_config:
            attrs["updated_at"] = self._scene_config["updated_at"]

        # Add EQ info summary
        if "eq" in self._scene_config and self._scene_config["eq"]:
            eq_enabled_count = 0
            for channel_eq in self._scene_config["eq"]:
                for band in channel_eq:
                    if band.get("enabled", 0):
                        eq_enabled_count += 1
            attrs["eq_bands_enabled"] = eq_enabled_count

        return attrs

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
