"""Select platform for Powersoft Mezzo integration."""
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    COORDINATOR,
    CLIENT,
    SCENE_MANAGER,
    ACTIVE_SCENE_ID,
    UID_SOURCE,
    UID_SCENE,
    CHANNEL_NUMBERS,
    SOURCE_OPTIONS,
)
from .mezzo_client import MezzoClient
from .scene_manager import SceneManager
from .mezzo_memory_map import (
    NUM_EQ_BANDS,
    NUM_SOURCE_EQ_BANDS,
    EQ_TYPE_PEAKING,
    EQ_TYPE_LOW_SHELVING,
    EQ_TYPE_HIGH_SHELVING,
)

_LOGGER = logging.getLogger(__name__)

# EQ Filter Type Options
EQ_TYPE_OPTIONS = {
    0: "Peaking",
    11: "Low Shelving",
    12: "High Shelving",
    13: "Low Pass",
    14: "High Pass",
    15: "Band Pass",
    16: "Band Stop",
    17: "All Pass",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Mezzo select entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    client = hass.data[DOMAIN][entry.entry_id][CLIENT]
    scene_manager: SceneManager = hass.data[DOMAIN][entry.entry_id][SCENE_MANAGER]

    entities = []

    # Add scene selector (dropdown)
    entities.append(MezzoSceneSelect(coordinator, client, scene_manager, entry, hass))

    # Add input source selectors for each channel
    for channel in CHANNEL_NUMBERS:
        entities.append(MezzoSourceSelect(coordinator, client, entry, channel))

    # Add User EQ filter type selectors for each channel and band
    for channel in CHANNEL_NUMBERS:
        for band in range(1, NUM_EQ_BANDS + 1):
            entities.append(MezzoEQTypeSelect(coordinator, client, entry, channel, band))

    # Add Source EQ filter type selectors for each band
    for band in range(1, NUM_SOURCE_EQ_BANDS + 1):
        entities.append(MezzoSourceEQTypeSelect(coordinator, client, entry, band))

    async_add_entities(entities)
    _LOGGER.info("Added %d select entities (scenes, sources, User EQ, Source EQ)", len(entities))


class MezzoSceneSelect(CoordinatorEntity, SelectEntity):
    """Representation of a scene selector."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:palette"

    def __init__(
        self,
        coordinator,
        client: MezzoClient,
        scene_manager: SceneManager,
        entry: ConfigEntry,
        hass: HomeAssistant,
    ):
        """Initialize the scene select entity."""
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
        self._attr_unique_id = f"{entry.entry_id}_{UID_SCENE}_selector"
        self._attr_name = "Scene"

        # Build options list from all scenes
        self._scenes = scene_manager.get_all_scenes()
        self._attr_options = [scene["name"] for scene in self._scenes]

    @property
    def current_option(self) -> str | None:
        """Return the currently active scene name."""
        active_scene_id = self._hass.data[DOMAIN][self._entry.entry_id][ACTIVE_SCENE_ID]

        if active_scene_id is None:
            return None

        # Find the scene with this ID
        for scene in self._scenes:
            if scene["id"] == active_scene_id:
                return scene["name"]

        return None

    async def async_select_option(self, option: str) -> None:
        """Select and apply a scene."""
        try:
            # Find the scene by name
            scene_to_apply = None
            for scene in self._scenes:
                if scene["name"] == option:
                    scene_to_apply = scene
                    break

            if scene_to_apply is None:
                _LOGGER.error("Scene not found: %s", option)
                return

            _LOGGER.info("Applying scene from selector: %s", scene_to_apply["name"])

            # Apply the scene
            await self._client.apply_scene(scene_to_apply)

            # Update active scene tracking
            self._hass.data[DOMAIN][self._entry.entry_id][ACTIVE_SCENE_ID] = scene_to_apply["id"]

            # Force immediate coordinator refresh
            await self.coordinator.async_request_refresh()

        except Exception as err:
            _LOGGER.error("Failed to apply scene %s: %s", option, err)
            raise


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

            _LOGGER.warning(
                "Setting channel %d source to %d (%s)",
                self._channel, source_id, option
            )
            await self._client.set_source(self._channel, source_id)
            await self.coordinator.async_request_refresh()
            _LOGGER.warning("Source change completed for channel %d", self._channel)
        except Exception as err:
            _LOGGER.error(
                "Failed to set source for channel %d: %s", self._channel, err
            )
            raise


class MezzoEQTypeSelect(CoordinatorEntity, SelectEntity):
    """Representation of an EQ filter type selector."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:waveform"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator,
        client: MezzoClient,
        entry: ConfigEntry,
        channel: int,
        band: int,
    ):
        """Initialize the EQ type select entity."""
        super().__init__(coordinator)
        self._client = client
        self._channel = channel
        self._band = band
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Powersoft",
            "model": "Mezzo 602 AD",
        }
        self._attr_unique_id = f"{entry.entry_id}_eq_ch{channel}_band{band}_type"
        self._attr_name = f"EQ Channel {channel} Band {band} Type"
        self._attr_options = list(EQ_TYPE_OPTIONS.values())

    @property
    def current_option(self) -> str | None:
        """Return the current filter type."""
        if (self.coordinator.data and
            'eq' in self.coordinator.data and
            self._channel in self.coordinator.data['eq'] and
            self._band in self.coordinator.data['eq'][self._channel]):
            filt_type = self.coordinator.data['eq'][self._channel][self._band].get("type", 0)
            return EQ_TYPE_OPTIONS.get(filt_type, f"Type {filt_type}")
        return None

    async def async_select_option(self, option: str) -> None:
        """Select the filter type."""
        try:
            # Find type ID from option label
            type_id = None
            for tid, label in EQ_TYPE_OPTIONS.items():
                if label == option:
                    type_id = tid
                    break

            if type_id is None:
                _LOGGER.error("Unknown EQ type option: %s", option)
                return

            # Read current settings
            current = await self._client.get_eq_band(self._channel, self._band)

            # Write back with new type
            await self._client.set_eq_band(
                self._channel,
                self._band,
                enabled=current["enabled"],
                filt_type=type_id,
                q=current["q"],
                slope=current["slope"],
                frequency=current["frequency"],
                gain=current["gain"],
            )
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(
                "Failed to set EQ type for CH%d Band%d: %s", self._channel, self._band, err
            )
            raise


class MezzoSourceEQTypeSelect(CoordinatorEntity, SelectEntity):
    """Representation of a Source EQ filter type selector."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:waveform"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator,
        client: MezzoClient,
        entry: ConfigEntry,
        band: int,
    ):
        """Initialize the Source EQ type select entity."""
        super().__init__(coordinator)
        self._client = client
        self._band = band
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Powersoft",
            "model": "Mezzo 602 AD",
        }
        self._attr_unique_id = f"{entry.entry_id}_source_eq_band{band}_type"
        self._attr_name = f"Source EQ Band {band} Type"
        self._attr_options = list(EQ_TYPE_OPTIONS.values())

    @property
    def current_option(self) -> str | None:
        """Return the current filter type."""
        # Source EQ values are read on first use and cached after writes
        # Not included in coordinator bulk read to avoid timeout
        return None  # Will show as empty until first write

    async def async_select_option(self, option: str) -> None:
        """Select the filter type."""
        try:
            # Find type ID from option label
            type_id = None
            for tid, label in EQ_TYPE_OPTIONS.items():
                if label == option:
                    type_id = tid
                    break

            if type_id is None:
                _LOGGER.error("Unknown Source EQ type option: %s", option)
                return

            # Read current settings
            current = await self._client.get_source_eq_band(self._band)

            # Write back with new type
            await self._client.set_source_eq_band(
                self._band,
                enabled=current["enabled"],
                filt_type=type_id,
                q=current["q"],
                slope=current["slope"],
                frequency=current["frequency"],
                gain=current["gain"],
            )
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(
                "Failed to set Source EQ type for Band%d: %s", self._band, err
            )
            raise
