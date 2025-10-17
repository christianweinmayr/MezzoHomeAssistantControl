"""
Scene Manager for Powersoft Mezzo Integration.

Manages custom scene storage, loading, and persistence.
"""
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DEFAULT_SCENES
from .mezzo_memory_map import NUM_CHANNELS, NUM_EQ_BANDS

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1
STORAGE_KEY = "powersoft_mezzo_scenes"

# Custom scene IDs start at 1 (no default scenes anymore)
CUSTOM_SCENE_ID_START = 1


class SceneManager:
    """
    Manages scene storage and operations.

    Handles loading, saving, updating, and deleting custom scenes.
    Merges default scenes with custom scenes.
    """

    def __init__(self, hass: HomeAssistant, entry_id: str):
        """
        Initialize the scene manager.

        Args:
            hass: Home Assistant instance
            entry_id: Config entry ID for unique storage
        """
        self.hass = hass
        self.entry_id = entry_id
        self._store = Store(
            hass,
            STORAGE_VERSION,
            f"{STORAGE_KEY}_{entry_id}",
        )
        self._custom_scenes: List[Dict[str, Any]] = []
        self._next_id = CUSTOM_SCENE_ID_START

    async def async_load(self) -> None:
        """Load scenes from storage."""
        data = await self._store.async_load()

        if data is None:
            _LOGGER.info("No custom scenes found, starting fresh")
            self._custom_scenes = []
            self._next_id = CUSTOM_SCENE_ID_START
            return

        self._custom_scenes = data.get("scenes", [])

        # Calculate next available ID
        if self._custom_scenes:
            max_id = max(scene["id"] for scene in self._custom_scenes)
            self._next_id = max(max_id + 1, CUSTOM_SCENE_ID_START)
        else:
            self._next_id = CUSTOM_SCENE_ID_START

        _LOGGER.info("Loaded %d custom scene(s)", len(self._custom_scenes))

    async def async_save(self) -> None:
        """Save scenes to storage."""
        data = {
            "version": STORAGE_VERSION,
            "scenes": self._custom_scenes,
        }
        await self._store.async_save(data)
        _LOGGER.debug("Saved %d custom scene(s)", len(self._custom_scenes))

    def get_all_scenes(self) -> List[Dict[str, Any]]:
        """
        Get all scenes (default + custom).

        Returns:
            List of all scene configurations
        """
        # Combine default scenes with custom scenes
        all_scenes = DEFAULT_SCENES.copy()
        all_scenes.extend(self._custom_scenes)
        return all_scenes

    def get_scene_by_id(self, scene_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific scene by ID.

        Args:
            scene_id: Scene ID to retrieve

        Returns:
            Scene configuration or None if not found
        """
        all_scenes = self.get_all_scenes()
        for scene in all_scenes:
            if scene["id"] == scene_id:
                return scene
        return None

    def validate_scene_config(self, config: Dict[str, Any]) -> None:
        """
        Validate scene configuration.

        Args:
            config: Scene configuration to validate

        Raises:
            ValueError: If configuration is invalid
        """
        # Check required fields
        required_fields = ["name", "volumes", "mutes", "sources"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Scene missing required field: {field}")

        # Validate volumes
        if len(config["volumes"]) != NUM_CHANNELS:
            raise ValueError(f"Scene must have {NUM_CHANNELS} volume entries")
        for i, vol in enumerate(config["volumes"]):
            if not isinstance(vol, (int, float)) or not 0.0 <= vol <= 1.0:
                raise ValueError(f"Volume {i+1} must be between 0.0 and 1.0")

        # Validate mutes
        if len(config["mutes"]) != NUM_CHANNELS:
            raise ValueError(f"Scene must have {NUM_CHANNELS} mute entries")
        for i, mute in enumerate(config["mutes"]):
            if not isinstance(mute, bool):
                raise ValueError(f"Mute {i+1} must be boolean")

        # Validate sources
        if len(config["sources"]) != NUM_CHANNELS:
            raise ValueError(f"Scene must have {NUM_CHANNELS} source entries")
        for i, src in enumerate(config["sources"]):
            if not isinstance(src, int) or not -1 <= src <= 31:
                raise ValueError(f"Source {i+1} must be between -1 and 31")

        # Validate EQ if present
        if "eq" in config:
            eq = config["eq"]
            if len(eq) != NUM_CHANNELS:
                raise ValueError(f"Scene EQ must have {NUM_CHANNELS} channel configurations")

            for ch_idx, channel_eq in enumerate(eq):
                if len(channel_eq) != NUM_EQ_BANDS:
                    raise ValueError(f"Channel {ch_idx+1} EQ must have {NUM_EQ_BANDS} bands")

                for band_idx, band in enumerate(channel_eq):
                    required_band_fields = ["enabled", "type", "q", "frequency", "gain", "slope"]
                    for field in required_band_fields:
                        if field not in band:
                            raise ValueError(
                                f"EQ band {band_idx+1} on channel {ch_idx+1} "
                                f"missing field: {field}"
                            )

        # Validate standby if present
        if "standby" in config:
            if not isinstance(config["standby"], bool):
                raise ValueError("Standby must be boolean")

    async def async_create_scene(
        self,
        name: str,
        config: Dict[str, Any],
        scene_id: Optional[int] = None
    ) -> int:
        """
        Create a new scene.

        Args:
            name: Scene name
            config: Scene configuration (volumes, mutes, sources, eq, standby)
            scene_id: Optional specific ID (for testing or overwrites)

        Returns:
            ID of created scene

        Raises:
            ValueError: If configuration is invalid or scene_id conflicts
        """
        # Validate configuration
        scene_config = config.copy()
        scene_config["name"] = name
        self.validate_scene_config(scene_config)

        # Determine ID
        if scene_id is not None:
            # Check if ID is in default range
            if scene_id < CUSTOM_SCENE_ID_START:
                raise ValueError(
                    f"Cannot use scene_id < {CUSTOM_SCENE_ID_START} "
                    "(reserved for default scenes)"
                )
            # Check if ID already exists
            if any(s["id"] == scene_id for s in self._custom_scenes):
                raise ValueError(f"Scene ID {scene_id} already exists")
            use_id = scene_id
        else:
            use_id = self._next_id
            self._next_id += 1

        # Create scene with metadata
        now = datetime.utcnow().isoformat() + "Z"
        scene = {
            "id": use_id,
            "name": name,
            "volumes": scene_config["volumes"],
            "mutes": scene_config["mutes"],
            "sources": scene_config["sources"],
            "eq": scene_config.get("eq", []),
            "standby": scene_config.get("standby", False),
            "created_at": now,
            "updated_at": now,
        }

        self._custom_scenes.append(scene)
        await self.async_save()

        _LOGGER.info("Created scene '%s' (ID: %d)", name, use_id)
        return use_id

    async def async_update_scene(self, scene_id: int, config: Dict[str, Any]) -> None:
        """
        Update an existing scene.

        Args:
            scene_id: ID of scene to update
            config: New scene configuration

        Raises:
            ValueError: If scene not found
        """
        # Find the scene
        scene = None
        scene_idx = None
        for idx, s in enumerate(self._custom_scenes):
            if s["id"] == scene_id:
                scene = s
                scene_idx = idx
                break

        if scene is None:
            raise ValueError(f"Scene ID {scene_id} not found")

        # Validate new configuration
        updated_config = config.copy()
        updated_config["name"] = scene["name"]  # Preserve name if not provided
        if "name" in config:
            updated_config["name"] = config["name"]
        self.validate_scene_config(updated_config)

        # Update scene
        now = datetime.utcnow().isoformat() + "Z"
        self._custom_scenes[scene_idx].update({
            "name": updated_config["name"],
            "volumes": updated_config["volumes"],
            "mutes": updated_config["mutes"],
            "sources": updated_config["sources"],
            "eq": updated_config.get("eq", []),
            "standby": updated_config.get("standby", False),
            "updated_at": now,
        })

        await self.async_save()
        _LOGGER.info("Updated scene ID %d", scene_id)

    async def async_delete_scene(self, scene_id: int) -> None:
        """
        Delete a scene.

        Args:
            scene_id: ID of scene to delete

        Raises:
            ValueError: If scene not found
        """
        # Find and remove the scene
        initial_count = len(self._custom_scenes)
        self._custom_scenes = [s for s in self._custom_scenes if s["id"] != scene_id]

        if len(self._custom_scenes) == initial_count:
            raise ValueError(f"Scene ID {scene_id} not found")

        await self.async_save()
        _LOGGER.info("Deleted scene ID %d", scene_id)

    def get_custom_scene_count(self) -> int:
        """Get count of custom scenes."""
        return len(self._custom_scenes)

    def get_total_scene_count(self) -> int:
        """Get total count of all scenes (default + custom)."""
        return len(DEFAULT_SCENES) + len(self._custom_scenes)
