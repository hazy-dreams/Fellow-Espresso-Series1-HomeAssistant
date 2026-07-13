from custom_components.fellow_series1.models import Device, Profile


def test_device_parses_only_supported_fields(device_payload):
    device = Device.from_api(device_payload)

    assert device.id == "FAKE-SOLO-DEVICE-0001"
    assert device.connected is True
    assert device.settings_version == 7
    assert not hasattr(device, "serial_number")


def test_profile_recipe_attributes_are_structured_and_private_free(profiles_payload):
    profile = Profile.from_api(profiles_payload["profiles"][0])

    attributes = profile.recipe_attributes
    assert attributes["target_yield"] == 36.0
    assert attributes["infusion"] == [{"duration": 25.0, "pressure": 9.0}]
    serialized = repr(attributes)
    for private in ("FAKE-PROFILE", "PRIVATE", "invalid.example", "updatedAt"):
        assert private not in serialized
