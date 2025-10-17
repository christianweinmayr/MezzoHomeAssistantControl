"""Sensor platform for Powersoft Mezzo integration."""
import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    COORDINATOR,
    CLIENT,
    UID_TEMP_TRANSFORMER,
    UID_TEMP_HEATSINK,
    UID_FAULT_CODE,
    UID_EQ,
)
from .mezzo_memory_map import FAULT_CODES, NUM_CHANNELS, EQ_TYPE_PEAKING, EQ_TYPE_LOW_SHELVING, EQ_TYPE_HIGH_SHELVING
from .mezzo_client import MezzoClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Mezzo sensor entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    client = hass.data[DOMAIN][entry.entry_id][CLIENT]

    entities = []

    # Temperature sensors
    entities.append(MezzoTemperatureSensor(
        coordinator, entry, "transformer", UID_TEMP_TRANSFORMER, "Transformer Temperature"
    ))
    entities.append(MezzoTemperatureSensor(
        coordinator, entry, "heatsink", UID_TEMP_HEATSINK, "Heatsink Temperature"
    ))

    # Fault code sensor
    entities.append(MezzoFaultCodeSensor(coordinator, entry))

    # EQ sensors (one per channel)
    for channel in range(1, NUM_CHANNELS + 1):
        entities.append(MezzoEQSensor(coordinator, client, entry, channel))

    async_add_entities(entities)


class MezzoTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Representation of a temperature sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        temp_key: str,
        uid_suffix: str,
        name: str,
    ):
        """Initialize the temperature sensor."""
        super().__init__(coordinator)
        self._temp_key = temp_key
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Powersoft",
            "model": "Mezzo 602 AD",
        }
        self._attr_unique_id = f"{entry.entry_id}_{uid_suffix}"
        self._attr_name = name
        self._attr_icon = "mdi:thermometer"

    @property
    def native_value(self) -> float | None:
        """Return the temperature value."""
        if self.coordinator.data and "temperatures" in self.coordinator.data:
            return self.coordinator.data["temperatures"].get(self._temp_key)
        return None


class MezzoFaultCodeSensor(CoordinatorEntity, SensorEntity):
    """Representation of the fault code sensor."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:alert-circle"

    def __init__(self, coordinator, entry: ConfigEntry):
        """Initialize the fault code sensor."""
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Powersoft",
            "model": "Mezzo 602 AD",
        }
        self._attr_unique_id = f"{entry.entry_id}_{UID_FAULT_CODE}"
        self._attr_name = "Fault Code"

    @property
    def native_value(self) -> str | None:
        """Return the fault code description."""
        if self.coordinator.data and "fault_code" in self.coordinator.data:
            code = self.coordinator.data["fault_code"]
            if code is not None:
                return FAULT_CODES.get(code, f"Unknown fault: 0x{code:02x}")
        return "No Fault"

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        if self.coordinator.data and "fault_code" in self.coordinator.data:
            code = self.coordinator.data["fault_code"]
            if code is not None:
                return {"fault_code": code}
        return {}


class MezzoEQSensor(CoordinatorEntity, SensorEntity):
    """Representation of EQ configuration sensor for a channel."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:equalizer"

    # Map EQ filter types to human-readable names
    EQ_TYPE_NAMES = {
        0: "Peaking",
        11: "Low Shelving",
        12: "High Shelving",
        13: "Low Pass",
        14: "High Pass",
        15: "Band Pass",
        16: "Band Stop",
        17: "All Pass",
    }

    def __init__(self, coordinator, client: MezzoClient, entry: ConfigEntry, channel: int):
        """Initialize the EQ sensor."""
        super().__init__(coordinator)
        self._client = client
        self._channel = channel
        self._eq_data = None
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Powersoft",
            "model": "Mezzo 602 AD",
        }
        self._attr_unique_id = f"{entry.entry_id}_{UID_EQ}{channel}"
        self._attr_name = f"EQ Channel {channel}"

    @property
    def native_value(self) -> int:
        """Return number of enabled EQ bands."""
        if self._eq_data:
            return sum(1 for band in self._eq_data if band.get("enabled", 0))
        return 0

    @property
    def extra_state_attributes(self) -> dict:
        """Return EQ configuration as attributes."""
        if not self._eq_data:
            return {}

        attrs = {}
        for i, band in enumerate(self._eq_data, 1):
            enabled = bool(band.get("enabled", 0))
            filt_type = band.get("type", 0)
            freq = band.get("frequency", 1000)
            gain = band.get("gain", 1.0)
            q = band.get("q", 1.0)

            # Convert gain to dB
            import math
            gain_db = 20 * math.log10(gain) if gain > 0 else -float('inf')

            band_prefix = f"band_{i}"
            attrs[f"{band_prefix}_enabled"] = enabled
            attrs[f"{band_prefix}_type"] = self.EQ_TYPE_NAMES.get(filt_type, f"Type {filt_type}")
            attrs[f"{band_prefix}_frequency_hz"] = freq
            attrs[f"{band_prefix}_gain_linear"] = round(gain, 3)
            attrs[f"{band_prefix}_gain_db"] = round(gain_db, 2) if gain_db != -float('inf') else -99.0
            attrs[f"{band_prefix}_q"] = round(q, 2)

        return attrs

    async def async_update(self) -> None:
        """Fetch EQ data from amplifier."""
        try:
            # Read EQ for this specific channel (all 4 bands)
            eq_bands = []
            for band in range(1, 5):  # 4 bands per channel
                band_data = await self._client.get_eq_band(self._channel, band)
                eq_bands.append(band_data)
            self._eq_data = eq_bands
        except Exception as err:
            _LOGGER.debug("Failed to update EQ for channel %d: %s", self._channel, err)
            self._eq_data = None
