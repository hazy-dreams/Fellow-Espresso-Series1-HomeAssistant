"""Polling coordinator for Fellow Espresso Series 1."""

from __future__ import annotations

import logging
from time import monotonic

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ApiAuthenticationError, FellowApiClient, FellowApiError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, PROFILE_SCAN_INTERVAL
from .models import CoordinatorData, Profile

_LOGGER = logging.getLogger(__name__)


class FellowSeries1Coordinator(DataUpdateCoordinator):
    """Fetch the supported device and profile state as one update."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: FellowApiClient,
        device_id: str,
        *,
        config_entry: ConfigEntry | None = None,
    ) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
            config_entry=config_entry,
        )
        self.api = api
        self.device_id = device_id
        self._profiles: tuple[Profile, ...] | None = None
        self._profiles_updated_at: float | None = None
        self._last_active_profile_id: str | None = None
        self._last_settings_version: int | None = None
        self._force_profile_refresh = False

    async def async_request_refresh(self) -> None:
        """Request a full device and profile refresh from an explicit update."""
        self._force_profile_refresh = True
        await super().async_request_refresh()

    async def _async_update_data(self) -> CoordinatorData:
        try:
            device = await self.api.async_get_device(self.device_id)
            now = monotonic()
            profiles_due = (
                self._force_profile_refresh
                or self._profiles is None
                or self._profiles_updated_at is None
                or now - self._profiles_updated_at
                >= PROFILE_SCAN_INTERVAL.total_seconds()
                or device.active_profile_id != self._last_active_profile_id
                or device.settings_version != self._last_settings_version
            )
            if profiles_due:
                profiles = await self.api.async_get_profiles(self.device_id)
            else:
                assert self._profiles is not None
                profiles = self._profiles
        except ApiAuthenticationError as err:
            raise ConfigEntryAuthFailed("Fellow authentication expired") from err
        except FellowApiError as err:
            raise UpdateFailed("Unable to update Fellow Series 1 data") from err

        if profiles_due:
            self._profiles = profiles
            self._profiles_updated_at = now
            self._force_profile_refresh = False
        self._last_active_profile_id = device.active_profile_id
        self._last_settings_version = device.settings_version
        return CoordinatorData(device=device, profiles=profiles)
