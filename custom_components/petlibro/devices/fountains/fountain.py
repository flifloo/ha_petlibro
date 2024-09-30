from typing import Optional, cast
from . import Device

UNITS = {
    1: "cup",
    2: "oz",
    3: "g",
    4: "mL"
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
         return value