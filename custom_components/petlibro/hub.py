from logging import getLogger
from asyncio import gather
from collections.abc import Mapping
from typing import List, Any, Optional
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_REGION, CONF_API_TOKEN
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from aiohttp import ClientResponseError, ClientConnectorError

from custom_components.petlibro.api import PetLibroAPI

from .const import DOMAIN
from .api import PetLibroAPIError
from .devices import Device, product_name_map

_LOGGER = getLogger(__name__)
UPDATE_INTERVAL_SECONDS = 60 * 5


class PetLibroHub:
    """A PetLibro hub wrapper class"""

    devices : List[Device] = []

    def __init__(self, hass: HomeAssistant, data: Mapping[str, Any]) -> None:
        """Init the hub"""
        self._data = data
        self.session = None
        self.api = PetLibroAPI(async_get_clientsession(hass), hass.config.time_zone, data[CONF_REGION], data[CONF_API_TOKEN])

        self.coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_method=self.refresh_devices,
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )

    async def get_device(self, serial: str) -> Optional[Device]:
        """If found, return the device with the specified serial number."""
        return next(
            (device for device in self.devices if device.serial == serial),
            None,
        )

    async def load_devices(self):
        """Get information about devices connected to the account."""
        for device_data in await self.api.list_devices():
            if device := await self.get_device(device_data["deviceSn"]):
                await device.refresh()
            else:
                if device_data["productName"] in product_name_map:
                    device = product_name_map[device_data["productName"]](device_data, self.api)
                    await device.refresh()  # Get all API data
                    self.devices.append(device)
                else:
                    _LOGGER.error("Unsupported device found: %s", device_data["productName"])

    async def refresh_devices(self) -> bool:
        """Update all known devices states from the PETLIBRO API."""
        try:
            await gather(*(device.refresh() for device in self.devices))
        except (PetLibroAPIError, ClientResponseError, ClientConnectorError) as ex:
            _LOGGER.error("Unable to refresh your devices: %s", ex)
        return True
