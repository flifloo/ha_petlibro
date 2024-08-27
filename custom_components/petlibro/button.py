"""Support for PETLIBRO buttons."""

from __future__ import annotations
from logging import getLogger

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Generic

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PetLibroHubConfigEntry
from .entity import PetLibroEntity, _DeviceT, PetLibroEntityDescription
from .devices.device import Device
from .devices.feeders.feeder import Feeder

_LOGGER = getLogger(__name__)

@dataclass(frozen=True)
class RequiredKeysMixin(Generic[_DeviceT]):
    """A class that describes devices button entity required keys."""

    set_fn: Callable[[_DeviceT, bool], Coroutine[Any, Any, None]]


@dataclass(frozen=True)
class PetLibroButtonEntityDescription(ButtonEntityDescription, PetLibroEntityDescription[_DeviceT], RequiredKeysMixin[_DeviceT]):
    """A class that describes device button entities."""

    entity_category: EntityCategory = EntityCategory.CONFIG


DEVICE_BUTTON_MAP: dict[type[Device], list[PetLibroButtonEntityDescription]] = {
    Feeder: [
        PetLibroButtonEntityDescription[Feeder](
            key="manual_feed",
            translation_key="manual_feed",
            set_fn=lambda device, value: device.manual_feed(value)
        )
    ]
}


class PetLibroButtonEntity(PetLibroEntity[_DeviceT], ButtonEntity):
    """PETLIBRO button entity."""

    entity_description: PetLibroButtonEntityDescription[_DeviceT]  # type: ignore [reportIncompatibleVariableOverride]

    async def async_press(self) -> None:
        await self.entity_description.set_fn(self._device, True)
        """Handle the button press."""

async def async_setup_entry(
    _: HomeAssistant,
    entry: PetLibroHubConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PETLIBRO buttons using config entry."""
    hub = entry.runtime_data
    entities = [
        PetLibroButtonEntity(device, hub, description)
        for device in hub.devices
        for device_type, entity_descriptions in DEVICE_BUTTON_MAP.items()
        if _LOGGER.error(f"Checking device type: {type(device)} against {device_type}") or isinstance(device, device_type)
        for description in entity_descriptions
    ]

    _LOGGER.error(f"Button entities to add: {entities}")

    async_add_entities(entities)
