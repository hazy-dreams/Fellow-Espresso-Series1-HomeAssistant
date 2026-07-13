"""Small read-only client for the supported Fellow cloud API surface."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from aiohttp import ClientError, ClientSession

from .models import Device, Profile

API_ORIGIN = "https://l8qtmnc692.execute-api.us-west-2.amazonaws.com"
_UNSUPPORTED_STATUSES = {404, 405, 501}


class FellowApiError(Exception):
    """Base exception for safe-to-report Fellow API failures."""


class ApiAuthenticationError(FellowApiError):
    """Authentication or token refresh failed."""


@dataclass(frozen=True, slots=True)
class TokenSet:
    access_token: str
    refresh_token: str


class FellowApiClient:
    """Client exposing only authentication and documented read operations."""

    def __init__(
        self,
        session: ClientSession,
        *,
        access_token: str | None = None,
        refresh_token: str | None = None,
        on_tokens: Callable[[TokenSet], Any] | None = None,
        api_origin: str = API_ORIGIN,
    ) -> None:
        self._session = session
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._on_tokens = on_tokens
        self._api_origin = api_origin.rstrip("/")

    async def async_login(self, email: str, password: str) -> TokenSet:
        payload = await self._request_json(
            "POST",
            "/v2/auth/login",
            authenticated=False,
            json={"email": email, "password": password},
            expected_statuses={200, 201},
        )
        tokens = self._parse_tokens(payload)
        self._apply_tokens(tokens)
        return tokens

    async def async_refresh_access_token(self) -> TokenSet:
        if self._refresh_token is None or self._access_token is None:
            raise ApiAuthenticationError("Authentication required")
        try:
            payload = await self._request_json(
                "POST",
                "/v2/auth/refresh-token",
                authenticated=False,
                authorization_token=self._access_token,
                json={"refreshToken": self._refresh_token},
                expected_statuses={200, 201},
            )
            tokens = self._parse_tokens(payload, fallback_refresh=self._refresh_token)
        except FellowApiError as err:
            raise ApiAuthenticationError("Token refresh failed") from err

        self._apply_tokens(tokens)
        return tokens

    def _apply_tokens(self, tokens: TokenSet) -> None:
        """Apply and persist the current credential pair through the callback."""
        self._access_token = tokens.access_token
        self._refresh_token = tokens.refresh_token
        if self._on_tokens is not None:
            self._on_tokens(tokens)

    async def async_discover_devices(self) -> list[Device]:
        try:
            payload = await self._request_json("GET", "/v2/devices?dataType=real")
        except _UnsupportedEndpointError:
            payload = await self._request_json("GET", "/v1/devices?dataType=real")
        raw_devices = self._extract_list(payload, "devices")
        devices: list[Device] = []
        for item in raw_devices:
            if str(item.get("deviceType", "")).casefold() != "solo":
                continue
            try:
                devices.append(Device.from_api(item))
            except ValueError as err:
                raise FellowApiError("Device response was invalid") from err
        return devices

    async def async_get_device(self, device_id: str) -> Device:
        encoded_id = quote(device_id, safe="")
        payload = await self._request_json(
            "GET", f"/v2/solo/devices/{encoded_id}?dataType=real"
        )
        mapping = self._extract_mapping(payload, "device")
        try:
            return Device.from_api(mapping)
        except ValueError as err:
            raise FellowApiError("Device response was invalid") from err

    async def async_get_profiles(self, device_id: str) -> tuple[Profile, ...]:
        encoded_id = quote(device_id, safe="")
        payload = await self._request_json(
            "GET", f"/v2/solo/devices/{encoded_id}/profiles"
        )
        profiles: list[Profile] = []
        for item in self._extract_list(payload, "profiles"):
            try:
                profiles.append(Profile.from_api(item))
            except ValueError as err:
                raise FellowApiError("Profile response was invalid") from err
        return tuple(profiles)

    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        authenticated: bool = True,
        authorization_token: str | None = None,
        expected_statuses: set[int] | None = None,
        _retry_auth: bool = True,
        **kwargs: Any,
    ) -> Any:
        if authenticated and self._access_token is None:
            await self.async_refresh_access_token()
        headers = {"Accept": "application/json"}
        if authenticated:
            headers["Authorization"] = f"Bearer {self._access_token}"
        elif authorization_token is not None:
            headers["Authorization"] = f"Bearer {authorization_token}"
        should_retry_auth = False
        kwargs.setdefault("timeout", 20)
        try:
            async with self._session.request(
                method,
                f"{self._api_origin}{path}" if self._api_origin else path,
                headers=headers,
                **kwargs,
            ) as response:
                valid_statuses = expected_statuses or {200}
                if response.status in valid_statuses:
                    try:
                        return await response.json(content_type=None)
                    except (TypeError, ValueError) as err:
                        raise FellowApiError("Fellow API response was invalid") from err
                if response.status in _UNSUPPORTED_STATUSES:
                    raise _UnsupportedEndpointError("API endpoint is unsupported")
                if response.status == 401 and authenticated and _retry_auth:
                    should_retry_auth = True
                elif response.status in {401, 403}:
                    raise ApiAuthenticationError("Authentication failed")
                else:
                    raise FellowApiError(
                        f"Fellow API request failed ({response.status})"
                    )
        except (ClientError, TimeoutError) as err:
            raise FellowApiError("Unable to communicate with Fellow cloud") from err
        if should_retry_auth:
            await self.async_refresh_access_token()
            return await self._request_json(
                method,
                path,
                authenticated=True,
                expected_statuses=expected_statuses,
                _retry_auth=False,
                **kwargs,
            )
        raise FellowApiError("Fellow API request failed")

    @staticmethod
    def _parse_tokens(payload: Any, *, fallback_refresh: str | None = None) -> TokenSet:
        if not isinstance(payload, Mapping):
            raise ApiAuthenticationError("Authentication response was invalid")
        access_token = payload.get("accessToken")
        refresh_token = payload.get("refreshToken", fallback_refresh)
        if not isinstance(access_token, str) or not isinstance(refresh_token, str):
            raise ApiAuthenticationError("Authentication response was invalid")
        return TokenSet(access_token, refresh_token)

    @staticmethod
    def _extract_mapping(payload: Any, key: str) -> Mapping[str, Any]:
        if not isinstance(payload, Mapping):
            raise FellowApiError("Fellow API response was invalid")
        nested = payload.get(key)
        if isinstance(nested, Mapping):
            return nested
        return payload

    @staticmethod
    def _extract_list(payload: Any, key: str) -> list[Mapping[str, Any]]:
        raw_items = payload.get(key) if isinstance(payload, Mapping) else payload
        if not isinstance(raw_items, list) or not all(
            isinstance(item, Mapping) for item in raw_items
        ):
            raise FellowApiError("Fellow API response was invalid")
        return raw_items


class _UnsupportedEndpointError(FellowApiError):
    """Internal signal permitting the documented discovery fallback."""
