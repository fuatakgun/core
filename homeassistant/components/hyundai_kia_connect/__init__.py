"""The Hyundai / Kia Connect integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import HyundaiKiaConnectDataUpdateCoordinator

PLATFORMS: list[str] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    """Set up Hyundai / Kia Connect from a config entry."""
    coordinator = HyundaiKiaConnectDataUpdateCoordinator(hass, config_entry)
    await coordinator.async_refresh()
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][config_entry.entry_id] = coordinator
    hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = coordinator
    hass.config_entries.async_setup_platforms(config_entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )
    if unload_ok:
        hass.data[DOMAIN] = None

    return unload_ok
