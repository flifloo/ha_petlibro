"""Support for PETLIBRO switches."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Generic

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PetLibroHubConfigEntry
from .entity import PetLibroEntity, _DeviceT, PetLibroEntityDescription
from .devices.device import Device
from .devices.feeders.feeder import Feeder

import logging

_LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True)
class RequiredKeysMixin(Generic[_DeviceT]):
    """A class that describes devices switch entity required keys."""

    set_fn: Callable[[_DeviceT, bool], Coroutine[Any, Any, None]]


@dataclass(frozen=True)
class PetLibroSwitchEntityDescription(SwitchEntityDescription, PetLibroEntityDescription[_DeviceT], RequiredKeysMixin[_DeviceT]):
    """A class that describes device switch entities."""

    entity_category: EntityCategory = EntityCategory.CONFIG


DEVICE_SWITCH_MAP: dict[type[Device], list[PetLibroSwitchEntityDescription]] = {
    Feeder: [
        PetLibroSwitchEntityDescription[Feeder](
            key="feeding_plan",
            translation_key="feeding_plan",
            set_fn=lambda device, value: device.set_feeding_plan(value)
        ),
        PetLibroSwitchEntityDescription[Feeder](
            key="feeding_plan_today_all",
            translation_key="feeding_plan_today_all",
            set_fn=lambda device, value: device.set_feeding_plan_today_all(value)
        ),
        PetLibroSwitchEntityDescription[Feeder](
            key="manual_feed",
            translation_key="manual_feed",
            set_fn=lambda device, value: device.set_manual_feed(value)
        )
    ]
}

class PetLibroSwitchEntity(PetLibroEntity[_DeviceT], SwitchEntity):
    """PETLIBRO switch entity."""

    entity_description: PetLibroSwitchEntityDescription[_DeviceT]  # type: ignore [reportIncompatibleVariableOverride]

    @cached_property
    def is_on(self) -> bool | None:
        """Return true if switch is on."""
        return bool(getattr(self.device, self.entity_description.key))

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.entity_description.set_fn(self.device, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.entity_description.set_fn(self.device, False)

def generate_feeding_plan_switches(device: Feeder) -> List[PetLibroSwitchEntityDescription[Feeder]]:
    """Generate switch descriptions for each feeding plan."""
    switches = []

    feeding_plans = device.feeding_plan_today_new.get("plans", [])
    for plan in feeding_plans:
        plan_id = plan["planId"]
        time = plan["time"]

        switch_description = PetLibroSwitchEntityDescription[Feeder](
            key=f"daily_feeding_plan_{plan_id}",
            name=f"Feeding Plan {time}",
            translation_key=f"daily_feeding_plan_{plan_id}",  # Assuming dynamic translation if needed
            set_fn=lambda dev, value, plan_id=plan_id: dev.set_feeding_plan_state(plan_id, value)
        )
        switches.append(switch_description)

    return switches

async def async_setup_entry(
    _: HomeAssistant,
    entry: PetLibroHubConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PETLIBRO switches using config entry."""

    _LOGGER.error("Starting setup of PETLIBRO switches")

    hub = entry.runtime_data
    entities = []

    _LOGGER.error("Devices found: %s", hub.devices)

    for device in hub.devices:
        _LOGGER.error("Processing device: %s", device)
        # Add statically defined switches
        for device_type, entity_descriptions in DEVICE_SWITCH_MAP.items():
            _LOGGER.error("Device matches type %s. Adding static switches.", device_type)
            if isinstance(device, device_type):
                for description in entity_descriptions:
                    _LOGGER.error("Creating switch entity: %s", description)
                    entity = PetLibroSwitchEntity(device, hub, description)
                    entities.append(entity)
            else:
                _LOGGER.error("Device does not match type %s.", device_type)

        # Add dynamically generated feeding plan switches for Feeder devices
        if isinstance(device, Feeder):
            _LOGGER.error("Device is a Feeder. Generating feeding plan switches.")
            feeding_plan_switches = generate_feeding_plan_switches(device)
            _LOGGER.error("Generated feeding plan switches: %s", feeding_plan_switches)
            for description in feeding_plan_switches:
                _LOGGER.error("Creating switch entity: %s", description)
                entity = PetLibroSwitchEntity(device, hub, description)
                entities.append(entity)

    _LOGGER.error("Adding entities to Home Assistant: %d entities", len(entities))
    async_add_entities(entities)