from typing import Optional
from . import Device


UNITS = {
    1: "cup",
    2: "oz",
    3: "g",
    4: "mL"
}

class Feeder(Device):
    @property
    def unit_type(self) -> str | None:
        unit : Optional[str] = None

        if unit_id := self._data.get("unitType"):
            unit = UNITS.get(unit_id)

        return unit
