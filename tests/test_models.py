from dataclasses import replace

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
    assert attributes["planned_duration"] == 34.0
    assert attributes["infusion"] == [{"duration": 25.0, "pressure": 9.0}]
    serialized = repr(attributes)
    for private in ("FAKE-PROFILE", "PRIVATE", "invalid.example", "updatedAt"):
        assert private not in serialized


def test_profile_derivations_respect_enabled_phases(profiles_payload):
    profile = Profile.from_api(profiles_payload["profiles"][0])

    assert profile.target_yield == 36.0
    assert profile.planned_duration == 34.0
    assert (
        replace(
            profile,
            pre_infusion_enabled=False,
            ramp_down_enabled=False,
        ).planned_duration
        == 25.0
    )


def test_planned_duration_is_unknown_if_phase_enablement_is_unknown(
    profiles_payload,
):
    profile = Profile.from_api(profiles_payload["profiles"][0])

    assert replace(profile, pre_infusion_enabled=None).planned_duration is None
    assert replace(profile, ramp_down_enabled=None).planned_duration is None


def test_planned_duration_is_unknown_if_any_included_phase_is_unknown(
    profiles_payload,
):
    profile = Profile.from_api(profiles_payload["profiles"][0])
    stage = profile.infusion[0]

    assert replace(profile, pre_infusion_duration=None).planned_duration is None
    assert replace(profile, infusion=()).planned_duration is None
    assert (
        replace(
            profile,
            infusion=(replace(stage, duration=None),),
        ).planned_duration
        is None
    )
    assert replace(profile, ramp_down_duration=None).planned_duration is None


def test_profile_derivations_are_unknown_without_inputs(profiles_payload):
    profile = replace(
        Profile.from_api(profiles_payload["profiles"][0]),
        dose=None,
        ratio=None,
        pre_infusion_enabled=False,
        infusion=(),
        ramp_down_enabled=False,
    )

    assert profile.target_yield is None
    assert profile.planned_duration is None
