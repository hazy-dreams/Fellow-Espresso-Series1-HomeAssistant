"""Binary sensors for Fellow Espresso Series 1."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import FellowSeries1Coordinator
from .entity import FellowSeries1Entity
from .models import CoordinatorData


@dataclass(frozen=True, kw_only=True)
class FellowBinarySensorDescription(BinarySensorEntityDescription):
    """Describe a Series 1 binary sensor."""

    value_fn: Callable[[CoordinatorData], bool | None]


BINARY_SENSOR_DESCRIPTIONS = (
    FellowBinarySensorDescription(
        key="connected",
        translation_key="connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda data: data.device.connected,
    ),
    FellowBinarySensorDescription(
        key="firmware_update_required",
        translation_key="firmware_update_required",
        device_class=BinarySensorDeviceClass.UPDATE,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.device.firmware_upgrade_required,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Series 1 binary sensors."""
    coordinator: FellowSeries1Coordinator = entry.runtime_data
    async_add_entities(
        FellowSeries1BinarySensor(coordinator, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class FellowSeries1BinarySensor(FellowSeries1Entity, BinarySensorEntity):
    """A Series 1 binary sensor."""

    entity_description: FellowBinarySensorDescription

    def __init__(
        self,
        coordinator: FellowSeries1Coordinator,
        description: FellowBinarySensorDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.value_fn(self.coordinator.data)
