from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntry

from .devices import Device
from .devices.feeders.granary_feeder import GranaryFeeder
from .const import DOMAIN
from .hub import PetLibroHub

type PetLibroHubConfigEntry = ConfigEntry[PetLibroHub]

PLATFORMS_BY_TYPE = {
    Device: (
        Platform.SENSOR,
    ),
    GranaryFeeder: set()
}


def get_platforms_for_devices(devices: list[Device]) -> set[Platform]:
    """Get platforms for devices."""
    return {
        platform
        for device in devices
        for device_type, platforms in PLATFORMS_BY_TYPE.items()
        if isinstance(device, device_type)
        for platform in platforms
    }


async def async_setup_entry(hass: HomeAssistant, entry: PetLibroHubConfigEntry) -> bool:
    """Set up platform from a ConfigEntry."""
    hub = PetLibroHub(hass, entry.data)
    await hub.login()
    await hub.load_devices()
    entry.runtime_data = hub

    if platforms := get_platforms_for_devices(hub.devices):
        await hass.config_entries.async_forward_entry_setups(entry, platforms)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: PetLibroHubConfigEntry) -> bool:
    """Unload a config entry."""
    await entry.runtime_data.logout()

    platforms = get_platforms_for_devices(entry.runtime_data.devices)
    return await hass.config_entries.async_unload_platforms(entry, platforms)


async def async_remove_config_entry_device(_: HomeAssistant, entry: PetLibroHubConfigEntry,
                                           device_entry: DeviceEntry) -> bool:
    """Remove a config entry from a device."""
    return not any(
        identifier
        for identifier in device_entry.identifiers
        if identifier[0] == DOMAIN
        for device in entry.runtime_data.devices
        if device.serial == identifier[1]
    )
