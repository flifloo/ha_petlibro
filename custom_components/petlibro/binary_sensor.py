"""Support for PETLIBRO binary sensors."""

from __future__ import annotations

from dataclasses import dataclass
from logging import getLogger
from collections.abc import Callable
from datetime import datetime
from functools import cached_property
from typing import Any, cast
from typing import Optional

from homeassistant.components.binary_sensor.const import BinarySensorStateClass, BinarySensorDeviceClass

from homeassistant.components.binary_sensor import binarySensorEntity, BinarySensorEntityDescription
from homeassistant.const import UnitOfMass, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .devices import Device
from .devices.feeders.feeder import Feeder
from .devices.feeders.granary_feeder import GranaryFeeder
from .devices.feeders.one_rfid_pet_feeder import OneRFIDPetFeeder
from . import PetLibroHubConfigEntry
from .entity import PetLibroEntity, _DeviceT, PetLibroEntityDescription


_LOGGER = getLogger(__name__)


@dataclass(frozen=True)
class PetLibroBinarySensorEntityDescription(BinarySensorEntityDescription, PetLibroEntityDescription[_DeviceT]):
    """A class that describes device binary sensor entities."""

    device_class_fn: Callable[[_DeviceT], BinarySensorDeviceClass | None] = lambda _: None
    should_report: Callable[[_DeviceT], bool] = lambda _: True
    device_class: Optional[BinarySensorDeviceClass] = None


class PetLibroBinarySensorEntity(PetLibroEntity[_DeviceT], BinarySensorEntity):  # type: ignore [reportIncompatibleVariableOverride]
    """PETLIBRO sensor entity."""

    entity_description: PetLibroBinarySensorEntityDescription[_DeviceT]  # type: ignore [reportIncompatibleVariableOverride]

    @cached_property
    def device_class(self) -> BinarySensorDeviceClass | None:
        """Return the device class to use in the frontend, if any."""
        return self.entity_description.device_class

DEVICE_BINARY_SENSOR_MAP: dict[type[Device], list[PetLibroBinarySensorEntityDescription]] = {
    GranaryFeeder: [
    ],
    OneRFIDPetFeeder: [
        PetLibroBinarySensorEntityDescription[OneRFIDPetFeeder](
            key="door_state",
            translation_key="door_state",
            icon="mdi:door",
            device_class=BinarySensorDeviceClass.DOOR
        ),
        PetLibroBinarySensorEntityDescription[OneRFIDPetFeeder](
            key="food_dispensor_state"
            translation_key="food_dispensor_state",
            icon="mdi:bowl-outline"
            device_class=BinarySensorDeviceClass.PROBLEM
        ),
        PetLibroBinarySensorEntityDescription[OneRFIDPetFeeder](
            key="door_blocked"
            translation_key="door_blocked",
            icon="mdi:door"
            device_class=BinarySensorDeviceClass.PROBLEM
        ),
        PetLibroBinarySensorEntityDescription[OneRFIDPetFeeder](
            key="food_low"
            translation_key="food_low",
            icon="mdi:bowl-mix-outline"
            device_class=BinarySensorDeviceClass.PROBLEM
        )
    ]
}

async def async_setup_entry(
    _: HomeAssistant,
    entry: PetLibroHubConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PETLIBRO binary sensors using config entry."""
    hub = entry.runtime_data
    entities = [
        PetLibroBinarySensorEntity(device, hub, description)
        for device in hub.devices
        for device_type, entity_descriptions in DEVICE_BINARY_SENSOR_MAP.items()
        if isinstance(device, device_type)
        for description in entity_descriptions
    ]
    async_add_entities(entities)
