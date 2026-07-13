"""Privacy-minimized diagnostics for Fellow Espresso Series 1."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import FellowSeries1Coordinator

REDACTED = "**REDACTED**"


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics without credentials, identifiers, or authored text."""
    coordinator: FellowSeries1Coordinator = entry.runtime_data
    data = coordinator.data
    active_profile = data.active_profile
    return {
        "config_entry": {
            "email": REDACTED,
            "access_token": REDACTED,
            "refresh_token": REDACTED,
            "device_id": REDACTED,
        },
        "device": {
            "id": REDACTED,
            "display_name": REDACTED,
            "device_type": data.device.device_type,
            "connected": data.device.connected,
            "firmware_version": data.device.firmware_version,
            "firmware_upgrade_required": data.device.firmware_upgrade_required,
            "active_profile_id": REDACTED,
            "elevation": data.device.elevation,
            "settings_version": data.device.settings_version,
        },
        "profiles": {
            "count": len(data.profiles),
            "active": (
                {
                    "id": REDACTED,
                    "title": REDACTED,
                    "recipe": active_profile.recipe_attributes,
                }
                if active_profile is not None
                else None
            ),
        },
    }
