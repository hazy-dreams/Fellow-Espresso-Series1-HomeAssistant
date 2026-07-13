from types import SimpleNamespace

import pytest
from custom_components.fellow_series1.diagnostics import (
    async_get_config_entry_diagnostics,
)
from custom_components.fellow_series1.models import CoordinatorData, Device, Profile


@pytest.mark.asyncio
async def test_diagnostics_redact_all_private_values(device_payload, profiles_payload):
    data = CoordinatorData(
        Device.from_api(device_payload),
        tuple(Profile.from_api(item) for item in profiles_payload["profiles"]),
    )
    entry = SimpleNamespace(
        entry_id="FAKE-ENTRY-0001",
        data={
            "email": "user@example.invalid",
            "access_token": "FAKE-ACCESS-SECRET",
            "refresh_token": "FAKE-REFRESH-SECRET",
            "device_id": "FAKE-SOLO-DEVICE-0001",
        },
        runtime_data=SimpleNamespace(data=data),
    )

    result = await async_get_config_entry_diagnostics(SimpleNamespace(), entry)
    serialized = repr(result)
    for private in (
        "user@example.invalid",
        "FAKE-ACCESS-SECRET",
        "FAKE-REFRESH-SECRET",
        "FAKE-SOLO-DEVICE-0001",
        "FAKE-PROFILE-0001",
        "Test Profile",
        "PRIVATE",
        "invalid.example",
    ):
        assert private not in serialized
