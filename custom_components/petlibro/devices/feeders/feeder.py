"""Generic PETLIBRO feeder"""
from typing import Optional, cast
from . import Device


UNITS = {
    1: "cups",
    2: "oz",
    3: "g",
    4: "mL"
}

UNITS_RATIO = {
    1: 1/12,
    2: 0.35,
    3: 10,
    4: 20
}

class Feeder(Device):
    """Generic PETLIBRO feeder device"""

    async def refresh(self):
        await super().refresh()
        self.update_data({
            "feedingPlanTodayNew": await self.api.device_feeding_plan_today_new(self.serial)
        })

    @property
    def unit_id(self) -> int | None:
        """The device unit type identifier"""
        return self._data.get("unitType")

    @property
    def unit_type(self) -> str | None:
        """The device unit type"""
        unit : Optional[str] = None

        if unit_id := self.unit_id:
            unit = UNITS.get(unit_id)

        return unit

    @property
    def feeding_plan(self) -> bool:
        return self._data.get("enableFeedingPlan", False)

    async def set_feeding_plan(self, value: bool):
        await self.api.set_device_feeding_plan(self.serial, value)
        await self.refresh()

    @property
    def feeding_plan_today_all(self) -> bool:
        return not cast(bool, self._data.get("feedingPlanTodayNew", {}).get("allSkipped"))

    async def set_feeding_plan_today_all(self, value: bool):
        await self.api.set_device_feeding_plan_today_all(self.serial, value)
        await self.refresh()

    def convert_unit(self, value: int) -> int:
        """
        Convert a value to the device unit

        :param unit: Value to convert
        :return: Converted value or unchanged if no unit (truncated to 2 decimal points)
        """
        if self.unit_id:
            return float('%.2f'%(value)) * UNITS_RATIO.get(self.unit_id, 1)
        return float('%.2f'%(value))
