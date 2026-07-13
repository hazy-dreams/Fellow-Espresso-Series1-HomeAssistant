from __future__ import annotations

from types import SimpleNamespace
from typing import ClassVar

import pytest
from custom_components.fellow_series1 import config_flow
from custom_components.fellow_series1.api import TokenSet
from custom_components.fellow_series1.const import (
    CONF_ACCESS_TOKEN,
    CONF_DEVICE_ID,
    CONF_EMAIL,
    CONF_REFRESH_TOKEN,
)
from custom_components.fellow_series1.models import Device


class FakeApi:
    devices: ClassVar[list[Device]] = []

    def __init__(self, session, *, on_tokens=None):
        self.on_tokens = on_tokens

    async def async_login(self, email, password):
        tokens = TokenSet("FAKE-ACCESS-NEW", "FAKE-REFRESH-NEW")
        if self.on_tokens is not None:
            self.on_tokens(tokens)
        return tokens

    async def async_discover_devices(self):
        if self.on_tokens is not None:
            self.on_tokens(TokenSet("FAKE-ACCESS-ROTATED", "FAKE-REFRESH-ROTATED"))
        return self.devices


def test_password_selectors_are_masked():
    assert config_flow.USER_SCHEMA["password"].options["type"] == "password"
    assert config_flow.REAUTH_SCHEMA["password"].options["type"] == "password"


@pytest.mark.asyncio
async def test_user_flow_persists_latest_tokens_after_discovery(
    monkeypatch, device_payload
):
    second = {
        **device_payload,
        "id": "FAKE-SOLO-DEVICE-0002",
        "displayName": "Test Machine Two",
    }
    FakeApi.devices = [Device.from_api(device_payload), Device.from_api(second)]
    monkeypatch.setattr(config_flow, "FellowApiClient", FakeApi)
    flow = config_flow.FellowSeries1ConfigFlow()
    flow.hass = SimpleNamespace(session=object())

    result = await flow.async_step_user(
        {CONF_EMAIL: "user@example.invalid", "password": "FAKE-PASSWORD"}
    )
    assert result["step_id"] == "device"

    result = await flow.async_step_device({CONF_DEVICE_ID: "FAKE-SOLO-DEVICE-0002"})
    assert result["type"] == "create_entry"
    assert result["data"] == {
        CONF_EMAIL: "user@example.invalid",
        CONF_ACCESS_TOKEN: "FAKE-ACCESS-ROTATED",
        CONF_REFRESH_TOKEN: "FAKE-REFRESH-ROTATED",
        CONF_DEVICE_ID: "FAKE-SOLO-DEVICE-0002",
    }
    assert "password" not in result["data"]


@pytest.mark.asyncio
async def test_reauth_rotates_token_pair(monkeypatch):
    monkeypatch.setattr(config_flow, "FellowApiClient", FakeApi)
    entry = SimpleNamespace(
        data={
            CONF_EMAIL: "user@example.invalid",
            CONF_ACCESS_TOKEN: "FAKE-ACCESS-OLD",
            CONF_REFRESH_TOKEN: "FAKE-REFRESH-OLD",
            CONF_DEVICE_ID: "FAKE-SOLO-DEVICE-0001",
        }
    )
    flow = config_flow.FellowSeries1ConfigFlow()
    flow.hass = SimpleNamespace(
        session=object(),
        config_entries=SimpleNamespace(async_get_entry=lambda entry_id: entry),
    )
    flow.context = {"entry_id": "FAKE-ENTRY-0001"}

    result = await flow.async_step_reauth_confirm({"password": "FAKE-PASSWORD"})

    assert result["reason"] == "reauth_successful"
    assert entry.data == {
        CONF_EMAIL: "user@example.invalid",
        CONF_ACCESS_TOKEN: "FAKE-ACCESS-NEW",
        CONF_REFRESH_TOKEN: "FAKE-REFRESH-NEW",
        CONF_DEVICE_ID: "FAKE-SOLO-DEVICE-0001",
    }
