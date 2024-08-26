from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import EntityCategory

from .devices.feeders.feeder import Feeder
from . import PetLibroHubConfigEntry


class ManualFeedingButton(ButtonEntity):
    """PETLIBRO Manual Feeding button entity."""

    def __init__(self, device: Feeder):
        self._device = device
        self._attr_name = "Manual Feeding"
        self._attr_unique_id = f"{device.serial}_manual_feeding"
        self._attr_entity_category = EntityCategory.CONFIG

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._device.manual_feed()


async def async_setup_entry(
    _: HomeAssistant,
    entry: PetLibroHubConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PETLIBRO button using config entry."""
    hub = entry.runtime_data
    entities = [
        ManualFeedingButton(device)
        for device in hub.devices
        if isinstance(device, Feeder)
    ]
    async_add_entities(entities)