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
from .mezzo_memory_map import (
    NUM_EQ_BANDS,
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

    entities = []

    # Add input source selectors for each channel
    for channel in CHANNEL_NUMBERS:
        entities.append(MezzoSourceSelect(coordinator, client, entry, channel))

    # Add EQ filter type selectors for each channel and band
    for channel in CHANNEL_NUMBERS:
        for band in range(1, NUM_EQ_BANDS + 1):
            entities.append(MezzoEQTypeSelect(coordinator, client, entry, channel, band))

    async_add_entities(entities)
    _LOGGER.info("Added %d select entities (sources, EQ types)", len(entities))


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


class MezzoEQTypeSelect(CoordinatorEntity, SelectEntity):
    """Representation of an EQ filter type selector."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:waveform"

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
        self._eq_data = None
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
        if self._eq_data:
            filt_type = self._eq_data.get("type", 0)
            return EQ_TYPE_OPTIONS.get(filt_type, f"Type {filt_type}")
        return None

    async def async_update(self) -> None:
        """Fetch current EQ band state."""
        try:
            self._eq_data = await self._client.get_eq_band(self._channel, self._band)
        except Exception as err:
            _LOGGER.debug("Failed to read EQ CH%d Band%d: %s", self._channel, self._band, err)
            self._eq_data = None

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
