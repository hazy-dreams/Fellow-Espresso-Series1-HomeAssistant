"""Small Home Assistant interface stubs for dependency-light local tests."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest


class _FlowBase:
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__()

    def __init__(self) -> None:
        self.hass: Any = None
        self.context: dict[str, Any] = {}
        self._unique_id: str | None = None

    async def async_set_unique_id(self, unique_id: str) -> None:
        self._unique_id = unique_id

    def _abort_if_unique_id_configured(self) -> None:
        return None

    def async_show_form(self, **kwargs: Any) -> dict[str, Any]:
        return {"type": "form", **kwargs}

    def async_create_entry(self, **kwargs: Any) -> dict[str, Any]:
        return {"type": "create_entry", **kwargs}

    def async_abort(self, **kwargs: Any) -> dict[str, Any]:
        return {"type": "abort", **kwargs}

    def async_update_reload_and_abort(
        self, entry: Any, data_updates: dict[str, Any]
    ) -> dict[str, Any]:
        entry.data = {**entry.data, **data_updates}
        return {"type": "abort", "reason": "reauth_successful"}


class _Coordinator:
    def __init__(self, hass: Any, **kwargs: Any) -> None:
        self.hass = hass
        self.data: Any = None

    async def async_config_entry_first_refresh(self) -> None:
        self.data = await self._async_update_data()

    async def async_request_refresh(self) -> None:
        self.data = await self._async_update_data()


class _Entity:
    def __init__(self, coordinator: Any = None) -> None:
        self.coordinator = coordinator

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__()


@dataclass(frozen=True, kw_only=True)
class _Description:
    key: str
    translation_key: str | None = None
    entity_category: Any = None
    device_class: Any = None
    native_unit_of_measurement: str | None = None
    icon: str | None = None


def _module(name: str, **attrs: Any) -> ModuleType:
    module = ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    sys.modules[name] = module
    return module


ha = _module("homeassistant")
config_entries = _module(
    "homeassistant.config_entries",
    ConfigFlow=_FlowBase,
    ConfigEntry=object,
    ConfigFlowResult=dict,
)
ha.config_entries = config_entries
_module(
    "homeassistant.const",
    Platform=SimpleNamespace(BINARY_SENSOR="binary_sensor", SENSOR="sensor"),
    PERCENTAGE="%",
    UnitOfLength=SimpleNamespace(METERS="m"),
)
_module("homeassistant.core", HomeAssistant=object, callback=lambda fn: fn)
_module("homeassistant.data_entry_flow", FlowResult=dict)
_module(
    "homeassistant.exceptions",
    ConfigEntryAuthFailed=type("ConfigEntryAuthFailed", (Exception,), {}),
)
_module("homeassistant.helpers")
_module(
    "homeassistant.helpers.aiohttp_client",
    async_get_clientsession=lambda hass: hass.session,
)
_module(
    "homeassistant.helpers.update_coordinator",
    DataUpdateCoordinator=_Coordinator,
    CoordinatorEntity=_Entity,
    UpdateFailed=type("UpdateFailed", (Exception,), {}),
)
_module(
    "homeassistant.helpers.entity",
    DeviceInfo=dict,
    EntityCategory=SimpleNamespace(DIAGNOSTIC="diagnostic"),
)
_module("homeassistant.helpers.entity_platform", AddEntitiesCallback=object)


class _TextSelectorConfig:
    def __init__(self, **kwargs: Any) -> None:
        self.options = kwargs


_module(
    "homeassistant.helpers.selector",
    TextSelector=lambda config: config,
    TextSelectorConfig=_TextSelectorConfig,
    TextSelectorType=SimpleNamespace(EMAIL="email", PASSWORD="password"),
)
_module(
    "homeassistant.components.binary_sensor",
    BinarySensorEntity=_Entity,
    BinarySensorEntityDescription=_Description,
    BinarySensorDeviceClass=SimpleNamespace(
        CONNECTIVITY="connectivity", UPDATE="update"
    ),
)
_module(
    "homeassistant.components.sensor",
    SensorEntity=_Entity,
    SensorEntityDescription=_Description,
)

vol = _module("voluptuous")
vol.Schema = lambda value: value
vol.Required = lambda value, **kwargs: value
vol.In = lambda value: value


@pytest.fixture
def fixture_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def device_payload(fixture_dir: Path) -> dict[str, Any]:
    return json.loads((fixture_dir / "device.json").read_text())


@pytest.fixture
def profiles_payload(fixture_dir: Path) -> dict[str, Any]:
    return json.loads((fixture_dir / "profiles.json").read_text())
