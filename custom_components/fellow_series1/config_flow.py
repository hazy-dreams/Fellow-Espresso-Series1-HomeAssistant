"""Config flow for Fellow Espresso Series 1."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import ApiAuthenticationError, FellowApiClient, FellowApiError, TokenSet
from .const import (
    CONF_ACCESS_TOKEN,
    CONF_DEVICE_ID,
    CONF_EMAIL,
    CONF_REFRESH_TOKEN,
    DOMAIN,
)
from .models import Device

CONF_PASSWORD = "password"

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): TextSelector(
            TextSelectorConfig(type=TextSelectorType.EMAIL, autocomplete="email")
        ),
        vol.Required(CONF_PASSWORD): TextSelector(
            TextSelectorConfig(
                type=TextSelectorType.PASSWORD,
                autocomplete="current-password",
            )
        ),
    }
)
REAUTH_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PASSWORD): TextSelector(
            TextSelectorConfig(
                type=TextSelectorType.PASSWORD,
                autocomplete="current-password",
            )
        )
    }
)


class FellowSeries1ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Fellow Series 1 config flow."""

    VERSION = 1

    def __init__(self) -> None:
        super().__init__()
        self._email: str | None = None
        self._tokens: TokenSet | None = None
        self._devices: dict[str, Device] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Authenticate and discover supported devices."""
        errors: dict[str, str] = {}
        if user_input is not None:
            email = user_input[CONF_EMAIL]
            password = user_input[CONF_PASSWORD]
            client = FellowApiClient(
                async_get_clientsession(self.hass),
                on_tokens=self._capture_tokens,
            )
            try:
                await client.async_login(email, password)
                devices = await client.async_discover_devices()
            except ApiAuthenticationError:
                errors["base"] = "invalid_auth"
            except FellowApiError:
                errors["base"] = "cannot_connect"
            else:
                if not devices:
                    errors["base"] = "no_devices"
                else:
                    self._email = email
                    self._devices = {device.id: device for device in devices}
                    if len(devices) == 1:
                        return await self._async_create_device_entry(devices[0])
                    return await self.async_step_device()
            finally:
                password = ""

        return self.async_show_form(
            step_id="user",
            data_schema=USER_SCHEMA,
            errors=errors,
        )

    async def async_step_device(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select one device when discovery returns several."""
        if not self._devices:
            return self.async_abort(reason="no_devices")
        if user_input is not None:
            device = self._devices.get(user_input[CONF_DEVICE_ID])
            if device is None:
                return self.async_abort(reason="no_devices")
            return await self._async_create_device_entry(device)
        choices = {device.id: device.display_name for device in self._devices.values()}
        return self.async_show_form(
            step_id="device",
            data_schema=vol.Schema({vol.Required(CONF_DEVICE_ID): vol.In(choices)}),
        )

    async def _async_create_device_entry(self, device: Device) -> ConfigFlowResult:
        if self._email is None or self._tokens is None:
            return self.async_abort(reason="unknown")
        await self.async_set_unique_id(device.id)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=device.display_name,
            data={
                CONF_EMAIL: self._email,
                CONF_ACCESS_TOKEN: self._tokens.access_token,
                CONF_REFRESH_TOKEN: self._tokens.refresh_token,
                CONF_DEVICE_ID: device.id,
            },
        )

    def _capture_tokens(self, tokens: TokenSet) -> None:
        """Keep the latest rotated token pair during setup discovery."""
        self._tokens = tokens

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        """Start reauthentication for an existing account."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Exchange a password and update only the refresh token."""
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        if entry is None:
            return self.async_abort(reason="unknown")
        errors: dict[str, str] = {}
        if user_input is not None:
            password = user_input[CONF_PASSWORD]
            client = FellowApiClient(async_get_clientsession(self.hass))
            try:
                tokens = await client.async_login(entry.data[CONF_EMAIL], password)
            except ApiAuthenticationError:
                errors["base"] = "invalid_auth"
            except FellowApiError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={
                        CONF_ACCESS_TOKEN: tokens.access_token,
                        CONF_REFRESH_TOKEN: tokens.refresh_token,
                    },
                )
            finally:
                password = ""
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=REAUTH_SCHEMA,
            errors=errors,
        )
