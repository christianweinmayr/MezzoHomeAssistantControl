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
    UID_TEMP_TRANSFORMER,
    UID_TEMP_HEATSINK,
    UID_FAULT_CODE,
)
from .mezzo_memory_map import FAULT_CODES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Mezzo sensor entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id][ COORDINATOR]

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
