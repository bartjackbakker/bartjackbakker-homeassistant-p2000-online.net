from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import Throttle
from datetime import timedelta

SCAN_INTERVAL = timedelta(seconds=5)
from .coordinator import P2000Coordinator
from .const import DOMAIN, CONF_PROVINCIE, CONF_DISCIPLINES

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the P2000 sensor from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    provincie = data[CONF_PROVINCIE]
    discipline = data[CONF_DISCIPLINES]

    coordinator = P2000Coordinator(hass, provincie, discipline)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([P2000Sensor(coordinator)])

class P2000Sensor(SensorEntity):
    """Representation of a P2000 sensor."""

    def __init__(self, coordinator: P2000Coordinator) -> None:
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_name = f"P2000 {coordinator.provincie} {coordinator.discipline}"
        self._attr_unique_id = f"p2000_{coordinator.provincie}_{coordinator.discipline}"

    @property
    def native_value(self):
        """Return the current value of the sensor."""
        return self.coordinator.data["melding"]

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = {}
        data = self.coordinator.data
        if data:
            attrs["time"] = data["datum"]
            attrs["discipline"] = data["discipline"]
            attrs["regio"] = data["regio"]
            attrs["teams"] = data["teams"]
            self.attrs = attrs

        return self.attrs

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        data = self.coordinator.data
        if data:
            if data["discipline"] == "Ambulance":
                return "mdi:ambulance"
            elif data["discipline"] == "Brandweer":
                return "mdi:fire-truck"
            elif data["discipline"] == "Politie":
                return "mdi:car-emergency"
            elif data["discipline"] == "Gereserveerd":
                return "mdi:car-emergency"
            elif data["discipline"] == "Lifeliner":
                return "mdi:helicopter"

        return "mdi:fire-truck"

    @Throttle(timedelta(minutes=1))
    async def async_update(self):
        """Update the sensor data."""
        await self.coordinator.async_request_refresh()
