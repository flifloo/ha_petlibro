"""Support for PETLIBRO buttons."""

from __future__ import annotations

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

@dataclass(frozen=True)
class RequiredKeysMixin(Generic[_DeviceT]):
    """A class that describes devices button entity required keys."""

    set_fn: Callable[[_DeviceT], Coroutine[Any, Any, None]]

@dataclass(frozen=True)
class PetLibroButtonEntityDescription(ButtonEntityDescription, PetLibroEntityDescription[_DeviceT], RequiredKeysMixin[_DeviceT]):
    """A class that describes device button entities."""

    entity_category: EntityCategory = EntityCategory.CONFIG


DEVICE_BUTTON_MAP: dict[type[Device], list[PetLibroButtonEntityDescription]] = {
    Feeder: [
        PetLibroButtonEntityDescription[Feeder](
            key="manual_feed",
            translation_key="manual_feed",
            set_fn=lambda device: device.set_manual_feed()
        )
    ]
}

class PetLibroButtonEntity(PetLibroEntity[_DeviceT], ButtonEntity):
    """PETLIBRO button entity."""

    entity_description: PetLibroButtonEntityDescription[_DeviceT]

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.entity_description.set_fn(self.device)

import logging
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    _: HomeAssistant,
    entry: PetLibroHubConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PETLIBRO buttons using config entry."""

    hub = entry.runtime_data
    _LOGGER.error(f"Found {len(hub.devices)} devices in the hub")
    entities = [
        PetLibroButtonEntity(device, hub, description)
        for device in hub.devices
        for device_type, entity_descriptions in DEVICE_BUTTON_MAP.items()
        if isinstance(device, device_type)
        for description in entity_descriptions
    ]
    _LOGGER.error(f"Adding {len(entities)} button entities")
    if entities:
        _LOGGER.error(f"Entities: {[entity.entity_description.key for entity in entities]}")
    async_add_entities(entities)