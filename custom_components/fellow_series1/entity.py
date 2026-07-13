"""Shared entity support for Fellow Espresso Series 1."""

from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FellowSeries1Coordinator


class FellowSeries1Entity(CoordinatorEntity):
    """Base for coordinator-backed Series 1 entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: FellowSeries1Coordinator, key: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        device = self.coordinator.data.device
        return DeviceInfo(
            identifiers={(DOMAIN, device.id)},
            name=device.display_name,
            manufacturer="Fellow",
            model="Espresso Series 1",
            sw_version=device.firmware_version,
        )
