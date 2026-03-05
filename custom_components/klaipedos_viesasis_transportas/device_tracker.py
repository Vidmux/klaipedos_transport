import logging
import urllib.request
import time
from datetime import timedelta
from homeassistant.helpers.event import async_track_time_interval

_LOGGER = logging.getLogger(__name__)
URL = "https://www.stops.lt/klaipeda/gps_full.txt"


async def async_setup_entry(hass, entry, async_add_entities):
    """Paleidžiama kai HA startuoja integraciją."""
    manager = KlaipedaTrackerManager(hass)

    async_track_time_interval(hass, manager.update_data, timedelta(seconds=30))
    await manager.update_data()

    return True


class KlaipedaTrackerManager:
    def __init__(self, hass):
        self.hass = hass
        self.known = set()

    async def update_data(self, now=None):
        try:
            text = await self.hass.async_add_executor_job(self._fetch)
            if not text:
                return

            lines = text.splitlines()
            current = set()

            for line in lines:
                parts = line.split(",")

                if len(parts) < 6:
                    continue

                route = parts[1].upper()
                vehicle_id = parts[3]

                try:
                    lon = int(parts[4]) / 1000000
                    lat = int(parts[5]) / 1000000
                except:
                    continue

                current.add(vehicle_id)

                entity_id = f"device_tracker.klp_bus_{vehicle_id}"

                self.hass.states.async_set(
                    entity_id,
                    "home",
                    {
                        "latitude": lat,
                        "longitude": lon,
                        "source_type": "gps",
                        "friendly_name": route,
                        "icon": "mdi:bus",
                        "route": route,
                        "vehicle_id": vehicle_id,
                    },
                )

            # dingę autobusai
            for old in self.known - current:
                entity_id = f"device_tracker.klp_bus_{old}"
                state = self.hass.states.get(entity_id)

                if state and state.state != "not_home":
                    self.hass.states.async_set(entity_id, "not_home", state.attributes)

            self.known = current

        except Exception as e:
            _LOGGER.error("Klaipėdos transporto klaida: %s", e)

    def _fetch(self):
        req = urllib.request.Request(
            f"{URL}?t={int(time.time())}",
            headers={"User-Agent": "Mozilla/5.0"},
        )

        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read().decode("utf-8")
