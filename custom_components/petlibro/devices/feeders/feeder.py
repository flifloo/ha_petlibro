"""Generic PETLIBRO feeder"""
from typing import Optional
from . import Device


UNITS = {
    1: "cup",
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
