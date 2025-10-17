"""Number platform for Powersoft Mezzo integration."""
import logging
import math

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
from .mezzo_memory_map import NUM_EQ_BANDS

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

    # Add EQ parameter controls for each channel and band
    for channel in CHANNEL_NUMBERS:
        for band in range(1, NUM_EQ_BANDS + 1):
            entities.append(MezzoEQFrequencyNumber(coordinator, client, entry, channel, band))
            entities.append(MezzoEQGainNumber(coordinator, client, entry, channel, band))
            entities.append(MezzoEQQNumber(coordinator, client, entry, channel, band))

    async_add_entities(entities)
    _LOGGER.info("Added %d number entities (volumes, EQ frequency/gain/Q)", len(entities))


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


class MezzoEQFrequencyNumber(CoordinatorEntity, NumberEntity):
    """Representation of an EQ band frequency control."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:sine-wave"
    _attr_native_min_value = 20.0
    _attr_native_max_value = 20000.0
    _attr_native_step = 1.0
    _attr_native_unit_of_measurement = "Hz"
    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        coordinator,
        client: MezzoClient,
        entry: ConfigEntry,
        channel: int,
        band: int,
    ):
        """Initialize the EQ frequency number entity."""
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
        self._attr_unique_id = f"{entry.entry_id}_eq_ch{channel}_band{band}_frequency"
        self._attr_name = f"EQ Channel {channel} Band {band} Frequency"

    @property
    def native_value(self) -> float | None:
        """Return the current frequency."""
        if self._eq_data:
            return float(self._eq_data.get("frequency", 1000))
        return None

    async def async_update(self) -> None:
        """Fetch current EQ band state."""
        try:
            self._eq_data = await self._client.get_eq_band(self._channel, self._band)
        except Exception as err:
            _LOGGER.debug("Failed to read EQ CH%d Band%d: %s", self._channel, self._band, err)
            self._eq_data = None

    async def async_set_native_value(self, value: float) -> None:
        """Set the frequency."""
        try:
            # Read current settings
            current = await self._client.get_eq_band(self._channel, self._band)

            # Write back with new frequency
            await self._client.set_eq_band(
                self._channel,
                self._band,
                enabled=current["enabled"],
                filt_type=current["type"],
                q=current["q"],
                slope=current["slope"],
                frequency=int(value),
                gain=current["gain"],
            )
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(
                "Failed to set EQ frequency for CH%d Band%d: %s",
                self._channel, self._band, err
            )
            raise


class MezzoEQGainNumber(CoordinatorEntity, NumberEntity):
    """Representation of an EQ band gain control."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:amplifier"
    _attr_native_min_value = -12.0
    _attr_native_max_value = 12.0
    _attr_native_step = 0.1
    _attr_native_unit_of_measurement = "dB"
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        coordinator,
        client: MezzoClient,
        entry: ConfigEntry,
        channel: int,
        band: int,
    ):
        """Initialize the EQ gain number entity."""
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
        self._attr_unique_id = f"{entry.entry_id}_eq_ch{channel}_band{band}_gain"
        self._attr_name = f"EQ Channel {channel} Band {band} Gain"

    @property
    def native_value(self) -> float | None:
        """Return the current gain in dB."""
        if self._eq_data:
            linear_gain = self._eq_data.get("gain", 1.0)
            if linear_gain > 0:
                return 20 * math.log10(linear_gain)
            else:
                return -12.0
        return None

    async def async_update(self) -> None:
        """Fetch current EQ band state."""
        try:
            self._eq_data = await self._client.get_eq_band(self._channel, self._band)
        except Exception as err:
            _LOGGER.debug("Failed to read EQ CH%d Band%d: %s", self._channel, self._band, err)
            self._eq_data = None

    async def async_set_native_value(self, value: float) -> None:
        """Set the gain in dB."""
        try:
            # Convert dB to linear gain: gain = 10^(dB/20)
            linear_gain = 10 ** (value / 20)

            # Read current settings
            current = await self._client.get_eq_band(self._channel, self._band)

            # Write back with new gain
            await self._client.set_eq_band(
                self._channel,
                self._band,
                enabled=current["enabled"],
                filt_type=current["type"],
                q=current["q"],
                slope=current["slope"],
                frequency=current["frequency"],
                gain=linear_gain,
            )
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(
                "Failed to set EQ gain for CH%d Band%d: %s",
                self._channel, self._band, err
            )
            raise


class MezzoEQQNumber(CoordinatorEntity, NumberEntity):
    """Representation of an EQ band Q factor control."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:chart-bell-curve"
    _attr_native_min_value = 0.1
    _attr_native_max_value = 10.0
    _attr_native_step = 0.1
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        coordinator,
        client: MezzoClient,
        entry: ConfigEntry,
        channel: int,
        band: int,
    ):
        """Initialize the EQ Q number entity."""
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
        self._attr_unique_id = f"{entry.entry_id}_eq_ch{channel}_band{band}_q"
        self._attr_name = f"EQ Channel {channel} Band {band} Q"

    @property
    def native_value(self) -> float | None:
        """Return the current Q factor."""
        if self._eq_data:
            return self._eq_data.get("q", 1.0)
        return None

    async def async_update(self) -> None:
        """Fetch current EQ band state."""
        try:
            self._eq_data = await self._client.get_eq_band(self._channel, self._band)
        except Exception as err:
            _LOGGER.debug("Failed to read EQ CH%d Band%d: %s", self._channel, self._band, err)
            self._eq_data = None

    async def async_set_native_value(self, value: float) -> None:
        """Set the Q factor."""
        try:
            # Read current settings
            current = await self._client.get_eq_band(self._channel, self._band)

            # Write back with new Q
            await self._client.set_eq_band(
                self._channel,
                self._band,
                enabled=current["enabled"],
                filt_type=current["type"],
                q=value,
                slope=current["slope"],
                frequency=current["frequency"],
                gain=current["gain"],
            )
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(
                "Failed to set EQ Q for CH%d Band%d: %s",
                self._channel, self._band, err
            )
            raise
