from custom_components.fellow_series1.binary_sensor import BINARY_SENSOR_DESCRIPTIONS
from custom_components.fellow_series1.models import CoordinatorData, Device, Profile
from custom_components.fellow_series1.sensor import (
    SENSOR_DESCRIPTIONS,
    FellowSeries1Sensor,
)


def test_required_entity_keys_are_present():
    keys = {item.key for item in BINARY_SENSOR_DESCRIPTIONS + SENSOR_DESCRIPTIONS}
    assert keys == {
        "connected",
        "firmware_update_required",
        "firmware_version",
        "active_profile",
        "target_yield",
        "planned_duration",
        "profile_count",
        "elevation",
        "settings_version",
    }


def test_active_profile_exposes_only_recipe_fields(device_payload, profiles_payload):
    data = CoordinatorData(
        Device.from_api(device_payload),
        tuple(Profile.from_api(item) for item in profiles_payload["profiles"]),
    )
    coordinator = type(
        "Coordinator",
        (),
        {"data": data, "device_id": "FAKE-SOLO-DEVICE-0001"},
    )()
    description = next(x for x in SENSOR_DESCRIPTIONS if x.key == "active_profile")
    entity = FellowSeries1Sensor(coordinator, description)

    assert entity.native_value == "Test Profile"
    serialized = repr(entity.extra_state_attributes)
    assert "PRIVATE" not in serialized
    assert "FAKE-PROFILE" not in serialized


def test_derived_profile_sensors(device_payload, profiles_payload):
    data = CoordinatorData(
        Device.from_api(device_payload),
        tuple(Profile.from_api(item) for item in profiles_payload["profiles"]),
    )
    coordinator = type(
        "Coordinator",
        (),
        {"data": data, "device_id": "FAKE-SOLO-DEVICE-0001"},
    )()

    target = FellowSeries1Sensor(
        coordinator,
        next(x for x in SENSOR_DESCRIPTIONS if x.key == "target_yield"),
    )
    duration = FellowSeries1Sensor(
        coordinator,
        next(x for x in SENSOR_DESCRIPTIONS if x.key == "planned_duration"),
    )

    assert target.native_value == 36.0
    assert duration.native_value == 34.0
