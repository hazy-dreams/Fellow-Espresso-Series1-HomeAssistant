"""Typed models for the supported subset of the Fellow Solo API."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


def _optional_float(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _optional_int(value: Any) -> int | None:
    number = _optional_float(value)
    return int(number) if number is not None else None


def _optional_bool(value: Any) -> bool | None:
    return value if isinstance(value, bool) else None


def _optional_str(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


@dataclass(frozen=True, slots=True)
class Device:
    """A privacy-minimized Fellow Series 1 device."""

    id: str
    display_name: str
    device_type: str
    connected: bool | None
    firmware_version: str | None
    firmware_upgrade_required: bool | None
    active_profile_id: str | None
    elevation: float | None
    settings_version: int | None

    @classmethod
    def from_api(cls, data: Mapping[str, Any]) -> Device:
        """Parse the supported device fields from an API mapping."""
        device_id = _optional_str(data.get("id"))
        if device_id is None:
            raise ValueError("Device response is missing an id")
        display_name = _optional_str(data.get("displayName")) or "Fellow Series 1"
        return cls(
            id=device_id,
            display_name=display_name,
            device_type=_optional_str(data.get("deviceType")) or "",
            connected=_optional_bool(data.get("isConnected")),
            firmware_version=_optional_str(data.get("firmwareVersion")),
            firmware_upgrade_required=_optional_bool(
                data.get("firmwareUpgradeRequired")
            ),
            active_profile_id=_optional_str(data.get("activeProfileId")),
            elevation=_optional_float(data.get("elevation")),
            settings_version=_optional_int(data.get("settingsVersion")),
        )


@dataclass(frozen=True, slots=True)
class InfusionStage:
    """A supported infusion recipe stage."""

    duration: float | None
    pressure: float | None

    @classmethod
    def from_api(cls, data: Mapping[str, Any]) -> InfusionStage:
        return cls(
            duration=_optional_float(data.get("duration")),
            pressure=_optional_float(data.get("pressure")),
        )

    @property
    def attributes(self) -> dict[str, float | None]:
        return {"duration": self.duration, "pressure": self.pressure}


@dataclass(frozen=True, slots=True)
class Profile:
    """A profile containing only its identity, title, and recipe fields."""

    id: str
    title: str
    dose: float | None
    ratio: float | None
    temperature: float | None
    grind_size: float | None
    adaptive: bool | None
    pre_infusion_enabled: bool | None
    pre_infusion_duration: float | None
    pre_infusion_fill_flow_rate: float | None
    pre_infusion_hold_pressure: float | None
    infusion: tuple[InfusionStage, ...]
    ramp_down_enabled: bool | None
    ramp_down_duration: float | None
    ramp_down_end_pressure: float | None

    @classmethod
    def from_api(cls, data: Mapping[str, Any]) -> Profile:
        profile_id = _optional_str(data.get("id"))
        if profile_id is None:
            raise ValueError("Profile response is missing an id")
        raw_infusion = data.get("infusion")
        infusion = (
            tuple(
                InfusionStage.from_api(item)
                for item in raw_infusion
                if isinstance(item, Mapping)
            )
            if isinstance(raw_infusion, list)
            else ()
        )
        return cls(
            id=profile_id,
            title=_optional_str(data.get("title")) or "Profile",
            dose=_optional_float(data.get("dose")),
            ratio=_optional_float(data.get("ratio")),
            temperature=_optional_float(data.get("temperature")),
            grind_size=_optional_float(data.get("grindSize")),
            adaptive=_optional_bool(data.get("adaptive")),
            pre_infusion_enabled=_optional_bool(data.get("preInfusionEnabled")),
            pre_infusion_duration=_optional_float(data.get("preInfusionDuration")),
            pre_infusion_fill_flow_rate=_optional_float(
                data.get("preInfusionFillFlowRate")
            ),
            pre_infusion_hold_pressure=_optional_float(
                data.get("preInfusionHoldPressure")
            ),
            infusion=infusion,
            ramp_down_enabled=_optional_bool(data.get("rampDownEnabled")),
            ramp_down_duration=_optional_float(data.get("rampDownDuration")),
            ramp_down_end_pressure=_optional_float(data.get("rampDownEndPressure")),
        )

    @property
    def target_yield(self) -> float | None:
        """Return the planned beverage yield derived from dose and ratio."""
        return (
            round(self.dose * self.ratio, 3)
            if self.dose is not None and self.ratio is not None
            else None
        )

    @property
    def planned_duration(self) -> float | None:
        """Return the planned duration of enabled recipe phases in seconds."""
        durations: list[float] = []
        if self.pre_infusion_enabled is None or self.ramp_down_enabled is None:
            return None
        if not self.infusion:
            return None
        if self.pre_infusion_enabled:
            if self.pre_infusion_duration is None:
                return None
            durations.append(self.pre_infusion_duration)
        for stage in self.infusion:
            if stage.duration is None:
                return None
            durations.append(stage.duration)
        if self.ramp_down_enabled:
            if self.ramp_down_duration is None:
                return None
            durations.append(self.ramp_down_duration)
        return round(sum(durations), 3) if durations else None

    @property
    def recipe_attributes(self) -> dict[str, Any]:
        """Return the explicitly permitted structured recipe attributes."""
        return {
            "dose": self.dose,
            "ratio": self.ratio,
            "target_yield": self.target_yield,
            "planned_duration": self.planned_duration,
            "temperature": self.temperature,
            "grind_size": self.grind_size,
            "adaptive": self.adaptive,
            "pre_infusion": {
                "enabled": self.pre_infusion_enabled,
                "duration": self.pre_infusion_duration,
                "fill_flow_rate": self.pre_infusion_fill_flow_rate,
                "hold_pressure": self.pre_infusion_hold_pressure,
            },
            "infusion": [stage.attributes for stage in self.infusion],
            "ramp_down": {
                "enabled": self.ramp_down_enabled,
                "duration": self.ramp_down_duration,
                "end_pressure": self.ramp_down_end_pressure,
            },
        }


@dataclass(frozen=True, slots=True)
class CoordinatorData:
    """One atomic coordinator refresh."""

    device: Device
    profiles: tuple[Profile, ...]

    @property
    def active_profile(self) -> Profile | None:
        return next(
            (
                profile
                for profile in self.profiles
                if profile.id == self.device.active_profile_id
            ),
            None,
        )
