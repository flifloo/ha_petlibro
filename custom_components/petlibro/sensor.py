"""Support for PETLIBRO sensors."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from functools import cached_property
from typing import Any, cast

from homeassistant.components.sensor.const import SensorStateClass, SensorDeviceClass

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .devices import Device
from .devices.feeders.granary_feeder import GranaryFeeder
from . import PetLibroHubConfigEntry
from .entity import PetLibroEntity, PetLibroEntityDescription, _DeviceT


def icon_for_gauge_level(gauge_level: int | None = None, offset: int = 0) -> str:
    """Return a gauge icon valid identifier."""
    if gauge_level is None or gauge_level <= 0 + offset:
        return "mdi:gauge-empty"
    if gauge_level > 70 + offset:
        return "mdi:gauge-full"
    if gauge_level > 30 + offset:
        return "mdi:gauge"
    return "mdi:gauge-low"


class PetLibroSensorEntityDescription(PetLibroEntityDescription[_DeviceT], SensorEntityDescription):
    """A class that describes device sensor entities."""

    icon_fn: Callable[[Any], str | None] = lambda _: None
    should_report: Callable[[_DeviceT], bool] = lambda _: True


class PetLibroSensorEntity(PetLibroEntity[_DeviceT], SensorEntity):
    """PETLIBRO sensor entity."""

    @cached_property
    def native_value(self) -> float | datetime | str | None:
        """Return the state."""
        if not isinstance(self.entity_description, PetLibroSensorEntityDescription) \
            or self.entity_description.should_report(self.device):
            if isinstance(val := getattr(self.device, self.entity_description.key), str):
                return val.lower()
            return cast(float | datetime | None, val)
        return None

    @cached_property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, if any."""
        if isinstance(self.entity_description, PetLibroSensorEntityDescription) \
            and (icon := self.entity_description.icon_fn(self.state)) is not None:
            return icon
        return super().icon


DEVICE_SENSOR_MAP: dict[type[Device], list[PetLibroSensorEntityDescription]] = {
    GranaryFeeder: [
        PetLibroSensorEntityDescription[GranaryFeeder](
            key="remaining_desiccant",
            translation_key="remaining_desiccant",
            icon="mdi:package",
            native_unit_of_measurement=UnitOfTime.DAYS,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT
        )
    ]
}


async def async_setup_entry(
    _: HomeAssistant,
    entry: PetLibroHubConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PETLIBRO sensors using config entry."""
    hub = entry.runtime_data
    entities = [
        PetLibroSensorEntity(device, hub, description)
        for device in hub.devices
        for device_type, entity_descriptions in DEVICE_SENSOR_MAP.items()
        if isinstance(device, device_type)
        for description in entity_descriptions
    ]
    async_add_entities(entities)
