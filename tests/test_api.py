from __future__ import annotations

from dataclasses import dataclass

import pytest
from custom_components.fellow_series1.api import (
    ApiAuthenticationError,
    FellowApiClient,
    TokenSet,
)


@dataclass
class FakeResponse:
    status: int
    payload: object

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def json(self, **kwargs):
        return self.payload

    async def text(self):
        return "sanitized error"


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return self.responses.pop(0)


@pytest.mark.asyncio
async def test_login_and_solo_discovery_filter(device_payload):
    non_solo = {**device_payload, "id": "FAKE-OTHER-0001", "deviceType": "Other"}
    session = FakeSession(
        [
            FakeResponse(
                201, {"accessToken": "FAKE-ACCESS", "refreshToken": "FAKE-REFRESH"}
            ),
            FakeResponse(200, {"devices": [device_payload, non_solo]}),
        ]
    )
    client = FellowApiClient(session, api_origin="")

    tokens = await client.async_login("user@example.invalid", "FAKE-PASSWORD")
    devices = await client.async_discover_devices()

    assert tokens.refresh_token == "FAKE-REFRESH"
    assert [device.id for device in devices] == ["FAKE-SOLO-DEVICE-0001"]
    assert session.calls[0][0:2] == ("POST", "/v2/auth/login")
    assert session.calls[1][0:2] == ("GET", "/v2/devices?dataType=real")
    assert session.calls[0][2]["timeout"] == 20


@pytest.mark.asyncio
async def test_discovery_falls_back_only_when_v2_unsupported(device_payload):
    session = FakeSession(
        [
            FakeResponse(404, {}),
            FakeResponse(200, [device_payload]),
        ]
    )
    client = FellowApiClient(session, access_token="FAKE-ACCESS", api_origin="")

    assert len(await client.async_discover_devices()) == 1
    assert session.calls[1][1] == "/v1/devices?dataType=real"


@pytest.mark.asyncio
async def test_refresh_rotation_and_auth_failure():
    rotated = []
    session = FakeSession(
        [
            FakeResponse(
                200, {"accessToken": "FAKE-ACCESS-2", "refreshToken": "FAKE-REFRESH-2"}
            ),
            FakeResponse(401, {}),
            FakeResponse(401, {}),
        ]
    )
    client = FellowApiClient(
        session,
        access_token="FAKE-ACCESS-1",
        refresh_token="FAKE-REFRESH-1",
        on_tokens=rotated.append,
        api_origin="",
    )

    await client.async_refresh_access_token()
    assert rotated == [TokenSet("FAKE-ACCESS-2", "FAKE-REFRESH-2")]
    assert session.calls[0][2]["headers"]["Authorization"] == "Bearer FAKE-ACCESS-1"
    with pytest.raises(ApiAuthenticationError):
        await client.async_get_device("FAKE-SOLO-DEVICE-0001")


@pytest.mark.asyncio
async def test_expired_access_token_refreshes_and_retries(device_payload):
    session = FakeSession(
        [
            FakeResponse(401, {}),
            FakeResponse(
                200, {"accessToken": "FAKE-ACCESS-2", "refreshToken": "FAKE-REFRESH-2"}
            ),
            FakeResponse(200, device_payload),
        ]
    )
    client = FellowApiClient(
        session,
        access_token="FAKE-ACCESS-1",
        refresh_token="FAKE-REFRESH-1",
        api_origin="",
    )

    device = await client.async_get_device("FAKE-SOLO-DEVICE-0001")

    assert device.connected is True
    assert [call[1] for call in session.calls] == [
        "/v2/solo/devices/FAKE-SOLO-DEVICE-0001?dataType=real",
        "/v2/auth/refresh-token",
        "/v2/solo/devices/FAKE-SOLO-DEVICE-0001?dataType=real",
    ]


@pytest.mark.asyncio
async def test_solo_reads_url_encode_device_id(device_payload, profiles_payload):
    session = FakeSession(
        [
            FakeResponse(200, device_payload),
            FakeResponse(200, profiles_payload),
        ]
    )
    client = FellowApiClient(session, access_token="FAKE-ACCESS", api_origin="")

    await client.async_get_device("FAKE DEVICE/0001")
    await client.async_get_profiles("FAKE DEVICE/0001")

    assert session.calls[0][1] == "/v2/solo/devices/FAKE%20DEVICE%2F0001?dataType=real"
    assert session.calls[1][1] == "/v2/solo/devices/FAKE%20DEVICE%2F0001/profiles"
