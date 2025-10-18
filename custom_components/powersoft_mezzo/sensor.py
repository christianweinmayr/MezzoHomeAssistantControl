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
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Powersoft",
            "model": "Mezzo 602 AD",
        }
        self._attr_unique_id = f"{entry.entry_id}_{UID_EQ}{channel}"
        self._attr_name = f"EQ Channel {channel}"

    @property
    def icon(self) -> str:
        """Return dynamic icon based on EQ state."""
        if (self.coordinator.data and
            'eq' in self.coordinator.data and
            self._channel in self.coordinator.data['eq']):
            channel_eq = self.coordinator.data['eq'][self._channel]
            enabled_count = sum(1 for band_data in channel_eq.values() if band_data.get("enabled", 0))
            if enabled_count == 0:
                return "mdi:equalizer-outline"
            else:
                return "mdi:equalizer"
        return "mdi:equalizer-outline"

    @property
    def native_value(self) -> str:
        """Return description of enabled EQ bands."""
        if (self.coordinator.data and
            'eq' in self.coordinator.data and
            self._channel in self.coordinator.data['eq']):
            channel_eq = self.coordinator.data['eq'][self._channel]
            enabled_bands = [str(band_num) for band_num, band_data in channel_eq.items()
                           if band_data.get("enabled", 0)]

            if not enabled_bands:
                return "No EQ"
            elif len(enabled_bands) == 4:
                return "All bands active"
            else:
                return f"Bands {', '.join(enabled_bands)}"
        return "Unknown"

    @property
    def extra_state_attributes(self) -> dict:
        """Return EQ configuration as attributes."""
        if not (self.coordinator.data and
                'eq' in self.coordinator.data and
                self._channel in self.coordinator.data['eq']):
            return {}

        channel_eq = self.coordinator.data['eq'][self._channel]
        attrs = {}

        # Add summary information
        enabled_bands = [band_num for band_num, band_data in channel_eq.items()
                        if band_data.get("enabled", 0)]
        attrs["enabled_count"] = len(enabled_bands)
        attrs["enabled_bands"] = enabled_bands if enabled_bands else None

        # Add detailed information for each band
        for band_num, band_data in channel_eq.items():
            enabled = bool(band_data.get("enabled", 0))
            filt_type = band_data.get("type", 0)
            freq = band_data.get("frequency", 1000)
            gain_db = band_data.get("gain", 0.0)  # Gain is already in dB
            q = band_data.get("q", 1.0)

            band_prefix = f"band_{band_num}"
            attrs[f"{band_prefix}_enabled"] = enabled
            attrs[f"{band_prefix}_type"] = self.EQ_TYPE_NAMES.get(filt_type, f"Type {filt_type}")
            attrs[f"{band_prefix}_frequency_hz"] = freq
            attrs[f"{band_prefix}_gain_db"] = round(gain_db, 1)
            attrs[f"{band_prefix}_q"] = round(q, 1)

            # Add a human-readable summary for enabled bands
            if enabled:
                type_name = self.EQ_TYPE_NAMES.get(filt_type, f"Type {filt_type}")
                attrs[f"{band_prefix}_summary"] = (
                    f"{type_name}: {freq}Hz, {gain_db:+.1f}dB, Q={q:.1f}"
                )

        return attrs
