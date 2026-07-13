"""Polling coordinator for Fellow Espresso Series 1."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ApiAuthenticationError, FellowApiClient, FellowApiError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .models import CoordinatorData

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

    async def _async_update_data(self) -> CoordinatorData:
        try:
            device = await self.api.async_get_device(self.device_id)
            profiles = await self.api.async_get_profiles(self.device_id)
        except ApiAuthenticationError as err:
            raise ConfigEntryAuthFailed("Fellow authentication expired") from err
        except FellowApiError as err:
            raise UpdateFailed("Unable to update Fellow Series 1 data") from err
        return CoordinatorData(device=device, profiles=profiles)
