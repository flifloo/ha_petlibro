from typing import Optional, cast
from . import Device

UNITS = {
    1: "ml",
    2: "oz"
}

UNITS_RATIO = {
    1: 1,
    2: 0.35
}

class Fountain(Device):
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

    def convert_unit(self, value: int) -> int:
        """
        Convert a value to the device unit

        :param unit: Value to convert
        :return: Converted value or unchanged if no unit
        """
        if self.unit_id:
            return value * UNITS_RATIO.get(self.unit_id, 1)
        return value