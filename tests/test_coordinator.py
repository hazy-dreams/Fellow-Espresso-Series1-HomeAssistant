from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace

import pytest
from custom_components.fellow_series1 import coordinator as coordinator_module
from custom_components.fellow_series1.const import (
    DEFAULT_SCAN_INTERVAL,
    PROFILE_SCAN_INTERVAL,
)
from custom_components.fellow_series1.coordinator import FellowSeries1Coordinator
from custom_components.fellow_series1.models import Device, Profile


class FakeApi:
    def __init__(self, device: Device, profiles: tuple[Profile, ...]) -> None:
        self.device = device
        self.profiles = profiles
        self.calls: list[str] = []

    async def async_get_device(self, device_id: str) -> Device:
        self.calls.append("device")
        return self.device

    async def async_get_profiles(self, device_id: str) -> tuple[Profile, ...]:
        self.calls.append("profiles")
        return self.profiles


def make_coordinator(api: FakeApi) -> FellowSeries1Coordinator:
    return FellowSeries1Coordinator(SimpleNamespace(), api, "FAKE-SOLO-DEVICE-0001")


def test_polling_intervals() -> None:
    assert DEFAULT_SCAN_INTERVAL.total_seconds() == 5 * 60
    assert PROFILE_SCAN_INTERVAL.total_seconds() == 30 * 60


@pytest.mark.asyncio
async def test_regular_update_reuses_cached_profiles(
    device_payload, profiles_payload, monkeypatch
):
    now = 0.0
    monkeypatch.setattr(coordinator_module, "monotonic", lambda: now, raising=False)
    api = FakeApi(
        Device.from_api(device_payload),
        tuple(Profile.from_api(item) for item in profiles_payload["profiles"]),
    )
    coordinator = make_coordinator(api)

    first = await coordinator._async_update_data()
    now = 5 * 60
    second = await coordinator._async_update_data()

    assert api.calls == ["device", "profiles", "device"]
    assert first.profiles is second.profiles
    assert second.active_profile.title == "Test Profile"


@pytest.mark.asyncio
async def test_profiles_refresh_after_thirty_minutes(
    device_payload, profiles_payload, monkeypatch
):
    now = 0.0
    monkeypatch.setattr(coordinator_module, "monotonic", lambda: now, raising=False)
    api = FakeApi(
        Device.from_api(device_payload),
        tuple(Profile.from_api(item) for item in profiles_payload["profiles"]),
    )
    coordinator = make_coordinator(api)

    await coordinator._async_update_data()
    now = 30 * 60
    await coordinator._async_update_data()

    assert api.calls == ["device", "profiles", "device", "profiles"]


@pytest.mark.asyncio
@pytest.mark.parametrize("changed_field", ["active_profile_id", "settings_version"])
async def test_device_revision_change_refreshes_profiles_early(
    device_payload, profiles_payload, monkeypatch, changed_field
):
    now = 0.0
    monkeypatch.setattr(coordinator_module, "monotonic", lambda: now, raising=False)
    api = FakeApi(
        Device.from_api(device_payload),
        tuple(Profile.from_api(item) for item in profiles_payload["profiles"]),
    )
    coordinator = make_coordinator(api)

    await coordinator._async_update_data()
    now = 5 * 60
    replacement = (
        "FAKE-PROFILE-CHANGED"
        if changed_field == "active_profile_id"
        else (api.device.settings_version or 0) + 1
    )
    api.device = replace(api.device, **{changed_field: replacement})
    await coordinator._async_update_data()

    assert api.calls == ["device", "profiles", "device", "profiles"]


@pytest.mark.asyncio
async def test_manual_refresh_forces_profiles(
    device_payload, profiles_payload, monkeypatch
):
    now = 0.0
    monkeypatch.setattr(coordinator_module, "monotonic", lambda: now, raising=False)
    api = FakeApi(
        Device.from_api(device_payload),
        tuple(Profile.from_api(item) for item in profiles_payload["profiles"]),
    )
    coordinator = make_coordinator(api)

    coordinator.data = await coordinator._async_update_data()
    now = 5 * 60
    await coordinator.async_request_refresh()

    assert api.calls == ["device", "profiles", "device", "profiles"]
