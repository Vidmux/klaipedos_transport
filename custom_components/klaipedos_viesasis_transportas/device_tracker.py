import logging
import requests
from datetime import timedelta

from homeassistant.components.device_tracker import SOURCE_TYPE_GPS
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.core import callback

DOMAIN = "klaipedos_transport"
API_URL = "https://www.stops.lt/klaipeda/gps_full.php"
SCAN_INTERVAL = timedelta(seconds=15)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up bus GPS trackers filtered by specific route."""
    
    route_filter = str(config.get("route_id"))
    if not route_filter:
        _LOGGER.error("Route ID missing in config!")
        return

    coordinator = BusGPSCoordinator(hass, route_filter)
    await coordinator.async_config_entry_first_refresh()

    trackers = []

    for bus in coordinator.data:
        trackers.append(
            BusGPSEntity(
                coordinator,
                bus_id=bus["bus_id"],
                route=bus["route"],
                lat=bus["lat"],
                lon=bus["lon"],
            )
        )

    async_add_entities(trackers, True)


class BusGPSCoordinator(DataUpdateCoordinator):
    """Fetch filtered bus GPS location for one specific route."""

    def __init__(self, hass, route_id):
        super().__init__(
            hass,
            _LOGGER,
            name=f"klaipeda_bus_route_{route_id}",
            update_interval=SCAN_INTERVAL,
        )
        self.route_filter = route_id

    async def _async_update_data(self):
        """Fetch and filter GPS markers."""

        try:
            r = requests.get(API_URL, timeout=5)
            data = r.json()

            gps_list = []

            for m in data.get("markers", []):
                if str(m.get("route_id")) != self.route_filter:
                    continue  # skip other routes

                gps_list.append(
                    {
                        "bus_id": m.get("code"),
                        "route": m.get("route_id"),
                        "lat": float(m.get("lat")),
                        "lon": float(m.get("lng")),
                    }
                )

            return gps_list

        except Exception as e:
            _LOGGER.error("GPS fetch error: %s", e)
            return []


class BusGPSEntity(CoordinatorEntity, TrackerEntity):
    """GPS entity for each moving bus on selected route."""

    def __init__(self, coordinator, bus_id, route, lat, lon):
        super().__init__(coordinator)

        self._bus_id = bus_id
        self._route = route
        self._lat = lat
        self._lon = lon

        self._attr_name = f"Bus {route} #{bus_id}"
        self._attr_unique_id = f"klaipeda_route_{route}_bus_{bus_id}".lower()
        self._attr_source_type = SOURCE_TYPE_GPS

    @property
    def latitude(self):
        return self._lat

    @property
    def longitude(self):
        return self._lon

    @callback
    def _handle_coordinator_update(self):
        """Update GPS coords from coordinator."""
        for bus in self.coordinator.data:
            if bus["bus_id"] == self._bus_id:
                self._lat = bus["lat"]
                self._lon = bus["lon"]
                break

        self.async_write_ha_state()

    @property
    def device_info(self):
        """Each bus is its own device."""
        return {
            "identifiers": {(DOMAIN, f"bus_{self._bus_id}")},
            "name": f"Klaipėdos autobusas #{self._bus_id}",
            "manufacturer": "Klaipėdos transportas",
            "model": f"Route {self._route}",
        }
