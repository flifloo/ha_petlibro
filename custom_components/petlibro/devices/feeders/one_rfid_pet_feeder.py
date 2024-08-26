from typing import cast

from .feeder import Feeder


class OneRFIDPetFeeder(Feeder):
    async def refresh(self):
        await super().refresh()
        self.update_data({
            "grainStatus": await self.api.device_grain_status(self.serial)
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
        eating_time_str = self._data.get("eatingTime", "0'0''")
        minutes, seconds = map(int, eating_time_str.replace("''", "").split("'"))
        return minutes * 60 + seconds
    _LOGGER.debug(f"Today eating time in seconds: {self.today_eating_time}")