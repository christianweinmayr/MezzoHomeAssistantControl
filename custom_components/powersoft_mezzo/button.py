"""Button platform for Powersoft Mezzo integration."""
import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory

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

    # Add "Create Scene" button (always visible)
    entities = [
        MezzoCreateSceneButton(
            coordinator,
            client,
            scene_manager,
            entry,
            hass,
        )
    ]

    # Get all scenes (default + custom)
    scenes = scene_manager.get_all_scenes()

    # Create button entities
    for scene in scenes:
        # Main scene application button
        entities.append(
            MezzoSceneButton(
                coordinator,
                client,
                entry,
                scene,
            )
        )

        # Add update/delete buttons for all scenes (all are custom now)
        entities.append(
            MezzoSceneUpdateButton(
                coordinator,
                client,
                scene_manager,
                entry,
                scene,
            )
        )
        entities.append(
            MezzoSceneDeleteButton(
                scene_manager,
                entry,
                scene,
                hass,
            )
        )

    async_add_entities(entities, update_before_add=True)

    # Count button types for logging
    scene_buttons = len([e for e in entities if isinstance(e, MezzoSceneButton)])
    update_buttons = len([e for e in entities if isinstance(e, MezzoSceneUpdateButton)])
    delete_buttons = len([e for e in entities if isinstance(e, MezzoSceneDeleteButton)])
    create_buttons = len([e for e in entities if isinstance(e, MezzoCreateSceneButton)])

    _LOGGER.info(
        "Added %d total button(s): %d scene, %d update, %d delete, %d create",
        len(entities), scene_buttons, update_buttons, delete_buttons, create_buttons
    )
    _LOGGER.info("Custom scenes: %d", scene_manager.get_custom_scene_count())


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


class MezzoSceneUpdateButton(CoordinatorEntity, ButtonEntity):
    """Button to update a custom scene with current amplifier state."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:content-save-edit"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator,
        client: MezzoClient,
        scene_manager: SceneManager,
        entry: ConfigEntry,
        scene_config: dict,
    ):
        """Initialize the update button."""
        super().__init__(coordinator)
        self._client = client
        self._scene_manager = scene_manager
        self._scene_config = scene_config
        self._entry = entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Powersoft",
            "model": "Mezzo 602 AD",
        }
        self._attr_unique_id = f"{entry.entry_id}_{UID_SCENE}_{scene_config['id']}_update"
        self._attr_name = f"Update {scene_config['name']}"

    async def async_press(self) -> None:
        """Handle button press - update the scene with current amp state."""
        try:
            _LOGGER.info("Updating scene: %s", self._scene_config["name"])

            # Capture current amplifier state
            config = await self._client.capture_current_state()

            # Update the scene
            await self._scene_manager.async_update_scene(
                self._scene_config["id"], config
            )

            _LOGGER.info("Successfully updated scene '%s'", self._scene_config["name"])

            # Reload integration to refresh all buttons
            await self.hass.config_entries.async_reload(self._entry.entry_id)

        except Exception as err:
            _LOGGER.error(
                "Failed to update scene %s: %s", self._scene_config["name"], err
            )
            raise


class MezzoSceneDeleteButton(ButtonEntity):
    """Button to delete a custom scene."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:delete"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        scene_manager: SceneManager,
        entry: ConfigEntry,
        scene_config: dict,
        hass: HomeAssistant,
    ):
        """Initialize the delete button."""
        self._scene_manager = scene_manager
        self._scene_config = scene_config
        self._entry = entry
        self._hass = hass
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Powersoft",
            "model": "Mezzo 602 AD",
        }
        self._attr_unique_id = f"{entry.entry_id}_{UID_SCENE}_{scene_config['id']}_delete"
        self._attr_name = f"Delete {scene_config['name']}"

    async def async_press(self) -> None:
        """Handle button press - delete the scene."""
        try:
            scene_name = self._scene_config["name"]
            scene_id = self._scene_config["id"]

            _LOGGER.warning("Deleting scene '%s' (ID: %d)", scene_name, scene_id)

            # Delete the scene
            await self._scene_manager.async_delete_scene(scene_id)

            _LOGGER.info("Successfully deleted scene '%s'", scene_name)

            # Reload integration to refresh all buttons
            await self._hass.config_entries.async_reload(self._entry.entry_id)

        except Exception as err:
            _LOGGER.error(
                "Failed to delete scene %s: %s", self._scene_config["name"], err
            )
            raise


class MezzoCreateSceneButton(CoordinatorEntity, ButtonEntity):
    """Button to create a new scene from current amplifier state."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:plus-circle"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator,
        client: MezzoClient,
        scene_manager: SceneManager,
        entry: ConfigEntry,
        hass: HomeAssistant,
    ):
        """Initialize the create scene button."""
        super().__init__(coordinator)
        self._client = client
        self._scene_manager = scene_manager
        self._entry = entry
        self._hass = hass
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Powersoft",
            "model": "Mezzo 602 AD",
        }
        self._attr_unique_id = f"{entry.entry_id}_create_scene"
        self._attr_name = "Create Scene from Current State"

    async def async_press(self) -> None:
        """Handle button press - create new scene from current amp state."""
        try:
            from datetime import datetime

            # Generate scene name with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            scene_name = f"Scene {timestamp}"

            _LOGGER.info("Creating new scene: %s", scene_name)

            # Capture current amplifier state
            config = await self._client.capture_current_state()

            # Create the scene
            scene_id = await self._scene_manager.async_create_scene(scene_name, config)

            _LOGGER.info("Successfully created scene '%s' (ID: %d)", scene_name, scene_id)

            # Create notification to inform user
            await self._hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Scene Created",
                    "message": f"Created new scene: '{scene_name}' (ID: {scene_id})\n\n"
                               f"The scene includes current volumes, mutes, sources, EQ settings, and power state.\n\n"
                               f"Use the 'Update {scene_name}' button to modify it later.",
                    "notification_id": f"{DOMAIN}_scene_created_{scene_id}",
                },
            )

            # Reload integration to show new buttons
            await self._hass.config_entries.async_reload(self._entry.entry_id)

        except Exception as err:
            _LOGGER.error("Failed to create scene: %s", err)
            await self._hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Scene Creation Failed",
                    "message": f"Error creating scene: {err}",
                    "notification_id": f"{DOMAIN}_scene_create_error",
                },
            )
            raise
