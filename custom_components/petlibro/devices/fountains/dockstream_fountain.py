from typing import cast

from .fountain import Fountain


class DockstreamFountain(Fountain):
    async def refresh(self):
        await super().refresh()
        self.update_data({
            "grainStatus": await self.api.device_grain_status(self.serial)
        })

    @property
    def remaining_cleaning(self) -> str:
        return cast(str, self._data.get("remainingCleaningDays"))

    @property
    def remaining_replacement_days(self) -> str:
        return cast(str, self._data.get("remainingReplacementDays"))

    @property
    def today_totalMl(self) -> int:
        quantity = self._data.get("todayTotalMl")
        if not quantity:
            return 0

        return self.convert_unit(quantity)

    @property
    def weight_percent(self) -> int:
        return cast(int, self._data.get("weightPercent"))
