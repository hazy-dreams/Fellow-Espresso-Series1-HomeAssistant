<div align="center">

# Fellow Espresso Series 1 for Home Assistant

**Bring the Fellow Espresso Series 1 into Home Assistant.**

[![GitHub Release](https://img.shields.io/github/v/release/hazy-dreams/Fellow-Espresso-Series1-HomeAssistant)](https://github.com/hazy-dreams/Fellow-Espresso-Series1-HomeAssistant/releases)
[![CI](https://img.shields.io/github/actions/workflow/status/hazy-dreams/Fellow-Espresso-Series1-HomeAssistant/ci.yml?branch=main&label=validation)](https://github.com/hazy-dreams/Fellow-Espresso-Series1-HomeAssistant/actions/workflows/ci.yml)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://www.hacs.xyz/docs/faq/custom_repositories/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.11%2B-18BCF2.svg)](https://www.home-assistant.io/)
[![License](https://img.shields.io/github/license/hazy-dreams/Fellow-Espresso-Series1-HomeAssistant)](LICENSE)

[Installation](#installation) · [Entities](#entities) · [Privacy](#security-and-privacy) · [Limitations](#currently-unsupported)

</div>

> [!IMPORTANT]
> This is an unofficial integration based on observed Fellow app and cloud API behavior. It is not documented, supported, or endorsed by Fellow. Cloud API changes may break it without notice.

## What it does

Fellow Espresso Series 1 uses Fellow's cloud API. This integration connects it to Home Assistant under the dedicated domain `fellow_series1`.

The integration is intentionally read-only. It checks machine state every five minutes and refreshes cached profiles every 30 minutes, or sooner when the active profile or settings revision changes. It exposes machine connectivity, firmware, and the currently selected espresso profile—including the structured recipe behind that profile.

### Highlights

- **Machine status** — cloud connectivity and firmware-update status.
- **Firmware details** — installed firmware version and settings revision.
- **Espresso profiles** — active profile, profile count, and structured recipe attributes.
- **Recipe data** — dose, ratio, planned target yield and duration, temperature, pre-infusion, infusion stages, and ramp-down data.
- **Multiple machines** — select a Series 1 during setup and repeat setup for additional machines.
- **Privacy-conscious auth** — the Fellow password is exchanged during setup and never stored.
- **Safe by default** — no remote brew, steam, hot-water, firmware, profile, or settings writes.
- **Respectful polling** — device state every five minutes, profiles every 30 minutes, and full refreshes on demand.

## Entities

Entity IDs depend on the machine name in Home Assistant. The examples below assume the machine is named `Espresso Series 1`.

| Entity | Type | Description |
| --- | --- | --- |
| `binary_sensor.espresso_series_1_connected` | Connectivity | Whether Fellow cloud reports the machine connected |
| `binary_sensor.espresso_series_1_firmware_update_required` | Update | Whether Fellow reports that firmware must be upgraded |
| `sensor.espresso_series_1_firmware_version` | Diagnostic | Installed firmware version |
| `sensor.espresso_series_1_active_profile` | Sensor | Title of the currently active espresso profile |
| `sensor.espresso_series_1_target_yield` | Weight | Planned beverage yield derived from active-profile dose × ratio |
| `sensor.espresso_series_1_planned_duration` | Duration | Planned active-profile duration from enabled pre-infusion, infusion, and ramp-down phases |
| `sensor.espresso_series_1_profile_count` | Sensor | Number of profiles returned by Fellow |
| `sensor.espresso_series_1_elevation` | Diagnostic | Machine elevation in meters |
| `sensor.espresso_series_1_settings_version` | Diagnostic | Fellow's device-settings revision |

Target yield is unavailable when the active profile does not include both dose and ratio. Planned duration is unavailable unless phase enablement and every included phase duration are present.

### Active-profile attributes

The active-profile sensor exposes only structured recipe values:

```yaml
dose: 18.0
ratio: 2.0
target_yield: 36.0
planned_duration: 35.0
temperature: 93.0
grind_size: 5.0
adaptive: true
pre_infusion:
  enabled: true
  duration: 5.0
  fill_flow_rate: 4.5
  hold_pressure: 3.0
infusion:
  - duration: 25.0
    pressure: 9.0
ramp_down:
  enabled: true
  duration: 5.0
  end_pressure: 5.0
```

Recipe values use Fellow's API units: dose and target yield are grams; planned and phase durations are seconds; temperature is degrees Celsius; pressure is bar; and pre-infusion flow rate is milliliters per second. Ratio and grind size are unitless. Nested attributes are plain numbers and do not carry Home Assistant unit metadata.

Profile identifiers, notes, roaster names, image URLs, and other authored text are not exposed as attributes.

## Installation

Home Assistant `2024.11.0` or newer is required.

### HACS

[![Open your Home Assistant instance and add this repository to HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=hazy-dreams&repository=Fellow-Espresso-Series1-HomeAssistant&category=integration)

Or add it manually:

1. Open **HACS → Integrations**.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add:
   ```text
   https://github.com/hazy-dreams/Fellow-Espresso-Series1-HomeAssistant
   ```
4. Select **Integration** as the category.
5. Install **Fellow Espresso Series 1**.
6. Restart Home Assistant.

### Manual

1. Download the latest release.
2. Copy `custom_components/fellow_series1` into your Home Assistant `custom_components` directory.
3. Restart Home Assistant.

## Configuration

1. Open **Settings → Devices & services**.
2. Select **Add integration**.
3. Search for **Fellow Espresso Series 1**.
4. Enter your Fellow account email and password.
5. If multiple Series 1 machines are found, choose one.
6. Repeat setup for each additional machine.

The machine must already be associated with the Fellow account in the official app.

## Security and privacy

- The account password is used only for login and is never stored.
- Home Assistant stores the account email, selected device identifier, access token, and refresh token in Home Assistant-managed config-entry storage.
- Fellow's refresh endpoint requires both tokens; rotated token pairs replace the stored credentials atomically.
- API responses and private profile data are never written to logs.
- Diagnostics redact email, tokens, device/profile identifiers, names, profile titles, notes, URLs, hashes, timestamps, and other authored text.
- All included tests and fixtures use conspicuously fake identifiers and reserved test addresses such as `.invalid` and `.example`.

This is a **cloud-polling** integration. Home Assistant needs internet access, Fellow's service must be available, and the machine must remain linked to the Fellow account.

## Currently unsupported

The current Series 1 cloud response does not expose shot telemetry or historical usage counters.

The integration therefore does **not** provide:

- remote brew, steam, or hot-water control;
- profile, schedule, firmware, or machine-setting writes;
- live pressure, flow, heater, or ready state;
- shot history, shot count, or shot timestamps;
- water usage or brew analytics;
- schedules;
- Wi-Fi or Bluetooth addresses.

These features are omitted rather than guessed. If Fellow exposes safe, verifiable telemetry later, support can be added with sanitized fixtures and tests.

## Troubleshooting

### Authentication expired

Home Assistant will open a reauthentication flow. Re-enter the Fellow password; it is exchanged for a new token pair and discarded again.

### No Series 1 devices found

Confirm that:

- the machine appears in the official Fellow app;
- the account credentials are correct;
- the device is an Espresso Series 1 (`deviceType: Solo`).

### Entities are unavailable

Check Fellow cloud availability and the machine's Wi-Fi connection. Home Assistant marks the entities unavailable when a coordinator update cannot complete.

## Development

```bash
uv sync --group dev
uv run pytest
uv run ruff check .
uv run ruff format --check .
python scripts/validate.py
```

The project also validates module imports against Home Assistant `2024.11.0` on Python `3.12`.

See [`PROTOCOL.md`](PROTOCOL.md) for the sanitized API basis and [`AGENTS.md`](AGENTS.md) for project safety boundaries.

## Contributing

Issues and pull requests are welcome. Contributions should:

- remain read-only unless a write operation has a documented safety case;
- include tests with sanitized fixtures;
- avoid real Fellow account, device, profile, serial, or token data; and
- preserve diagnostic redaction and password-free storage.

## Acknowledgements

- The Home Assistant and HACS communities for their integration tooling and documentation.

Fellow brand assets are sourced from the official [Home Assistant brands repository](https://github.com/home-assistant/brands/tree/master/custom_integrations/fellow). Fellow and its logos are trademarks of their respective owner and are not licensed under this project's GPL-3.0 software license.

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE). Distributed modifications must remain available under the same license.
