from typing import cast

from .feeder import Feeder
import time
import requests


import logging

# Configure the logger
logging.basicConfig(level=logging.ERROR)  # Adjust the level as needed
logger = logging.getLogger(__name__)

class OneRFIDPetFeeder(Feeder):
    async def refresh(self):
        await super().refresh()
        
        # Fetch data from API
        grain_status = await self.api.device_grain_status(self.serial)
        real_info = await self.api.device_real_info(self.serial)
        
        # Debug logging
        logger.debug(f"Fetched grain_status: {grain_status}")
        logger.debug(f"Fetched real_info: {real_info}")

        # Update internal data
        self.update_data({
            "grainStatus": grain_status,
            "realInfo": real_info
        })

    @property
    def remaining_desiccant(self) -> str:
        return cast(str, self._data.get("remainingDesiccantDays"))

    @property
    def today_feeding_quantity(self) -> int:
        quantity = self._data.get("grainStatus", {}).get("todayFeedingQuantity")
        if not quantity:
            return 0

        return self.convert_unit(quantity)

    @property
    def today_feeding_times(self) -> int:
        return cast(int, self._data.get("grainStatus", {}).get("todayFeedingTimes"))

    @property
    def today_eating_time(self) -> int:
        eating_time_str = self._data.get("grainStatus", {}).get("eatingTime", "0'0''")
        if not eating_time_str:
            return 0

        try:
            minutes, seconds = map(int, eating_time_str.replace("''", "").split("'"))
            total_seconds = minutes * 60 + seconds
        except ValueError as e:
            return 0

        return total_seconds
    
    @property
    def today_eating_times(self) -> int:
        return cast(int, self._data.get("grainStatus", {}).get("todayEatingTimes"))

    @property
    def battery_state(self) -> str:
        return cast(str, self._data.get("realInfo", {}).get("batteryState"))
    
    @property
    def door_state(self) -> bool:
        state = self._data.get("realInfo", {}).get("barnDoorState")
        if not state:
            return 0
        elif state == "false":
            return 0
        elif state == "true":
            return 1
        else:
            return 0
    
    @property
    def food_dispenser_state(self) -> bool:
        state = self._data.get("realInfo", {}).get("grainOutletState")
        if not state:
            return 1
        elif state == "false":
            return 1
        elif state == "true":
            return 0
        else:
            return 1
    
    @property
    def door_blocked(self) -> bool:
        state = self._data.get("realInfo", {}).get("barnDoorError")
        if not state:
            return 1
        elif state == "false":
            return 1
        elif state == "true":
            return 0
        else:
            return 1

    @property   
    def food_low(self) -> bool:
        state = self._data.get("realInfo", {}).get("surplusGrain")
        if not state:
            return 0
        elif state == "true":
            return 0
        else:
            return 1
