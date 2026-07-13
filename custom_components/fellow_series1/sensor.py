"""Sensors for Fellow Espresso Series 1."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import FellowSeries1Coordinator
from .entity import FellowSeries1Entity
from .models import CoordinatorData


@dataclass(frozen=True, kw_only=True)
class FellowSensorDescription(SensorEntityDescription):
    """Describe a Series 1 sensor."""

    value_fn: Callable[[CoordinatorData], Any]


SENSOR_DESCRIPTIONS = (
    FellowSensorDescription(
        key="firmware_version",
        translation_key="firmware_version",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.device.firmware_version,
    ),
    FellowSensorDescription(
        key="active_profile",
        translation_key="active_profile",
        value_fn=lambda data: (
            data.active_profile.title if data.active_profile is not None else None
        ),
    ),
    FellowSensorDescription(
        key="profile_count",
        translation_key="profile_count",
        value_fn=lambda data: len(data.profiles),
    ),
    FellowSensorDescription(
        key="elevation",
        translation_key="elevation",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfLength.METERS,
        value_fn=lambda data: data.device.elevation,
    ),
    FellowSensorDescription(
        key="settings_version",
        translation_key="settings_version",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.device.settings_version,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Series 1 sensors."""
    coordinator: FellowSeries1Coordinator = entry.runtime_data
    async_add_entities(
        FellowSeries1Sensor(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    )


class FellowSeries1Sensor(FellowSeries1Entity, SensorEntity):
    """A Series 1 sensor."""

    entity_description: FellowSensorDescription

    def __init__(
        self,
        coordinator: FellowSeries1Coordinator,
        description: FellowSensorDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        if self.entity_description.key != "active_profile":
            return None
        active_profile = self.coordinator.data.active_profile
        return active_profile.recipe_attributes if active_profile is not None else None
