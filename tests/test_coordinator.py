from types import SimpleNamespace
from typing import ClassVar

import pytest
from custom_components.fellow_series1.coordinator import FellowSeries1Coordinator
from custom_components.fellow_series1.models import Device, Profile


@pytest.mark.asyncio
async def test_coordinator_reads_device_and_profiles(device_payload, profiles_payload):
    device = Device.from_api(device_payload)
    profiles = tuple(Profile.from_api(item) for item in profiles_payload["profiles"])

    class Api:
        calls: ClassVar[list[tuple[str, str]]] = []

        async def async_get_device(self, device_id):
            self.calls.append(("device", device_id))
            return device

        async def async_get_profiles(self, device_id):
            self.calls.append(("profiles", device_id))
            return profiles

    api = Api()
    coordinator = FellowSeries1Coordinator(
        SimpleNamespace(), api, "FAKE-SOLO-DEVICE-0001"
    )
    data = await coordinator._async_update_data()

    assert api.calls == [
        ("device", "FAKE-SOLO-DEVICE-0001"),
        ("profiles", "FAKE-SOLO-DEVICE-0001"),
    ]
    assert data.active_profile.title == "Test Profile"
