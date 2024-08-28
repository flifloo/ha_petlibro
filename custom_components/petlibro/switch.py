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
    hub = entry.runtime_data
    entities = []

    for device in hub.devices:
        # Add statically defined switches
        for device_type, entity_descriptions in DEVICE_SWITCH_MAP.items():
            if isinstance(device, device_type):
                for description in entity_descriptions:
                    entity = PetLibroSwitchEntity(device, hub, description)
                    entities.append(entity)

        # Add dynamically generated feeding plan switches for Feeder devices
        if isinstance(device, Feeder):
            feeding_plan_switches = generate_feeding_plan_switches(device)
            for description in feeding_plan_switches:
                entity = PetLibroSwitchEntity(device, hub, description)
                entities.append(entity)

    async_add_entities(entities)