# Fellow Espresso Series 1 for Home Assistant

An unofficial, read-only Home Assistant custom integration for the **Fellow
Espresso Series 1** (`deviceType: Solo`). It uses Fellow's cloud API and can
coexist with integrations whose domain is `fellow`; this integration's domain
is `fellow_series1`.

Home Assistant 2024.11.0 or newer is required.

This project is reverse-engineered from observed app behavior. It is not
documented, supported, or endorsed by Fellow. Cloud API changes can break it
without notice.

## Features

Version 0.1.0 polls the Fellow cloud once per minute and provides:

- connected state;
- firmware-update-required state;
- firmware version;
- active profile and structured recipe attributes;
- profile count;
- elevation; and
- settings version.

The active profile's attributes are limited to dose, ratio, calculated target
yield, temperature, grind size, adaptive mode, pre-infusion settings, infusion
stages, and ramp-down settings.

## Explicitly unsupported

Version 0.1.0 does **not** brew remotely or write schedules, profiles, firmware,
or device settings. It does not provide shot history, shot count, water usage,
live pressure or flow, heater/ready state, shot timestamps, or unverified idle
fields. Those operations and measurements are absent rather than guessed.

## Cloud dependence

This is a cloud-polling integration, not a local-network integration. Home
Assistant needs internet access, Fellow's service must be available, and the
machine must be associated with the Fellow account. Normal polling sends the
stored refresh token and bearer access token to Fellow's API.

## Installation

### HACS custom repository

1. Add this repository to HACS as an **Integration** custom repository.
2. Install **Fellow Espresso Series 1**.
3. Restart Home Assistant.

### Manual

1. Copy `custom_components/fellow_series1` into the `custom_components`
   directory in the Home Assistant configuration directory.
2. Restart Home Assistant.

Then open **Settings → Devices & services → Add integration**, search for
**Fellow Espresso Series 1**, and enter the Fellow account email and password.
If several Series 1 machines are found, choose one; run setup again for each
additional machine.

## Security and privacy

The password is used only for the login exchange and is never saved. The config
entry stores the account email, access token, refresh token, and selected device
identifier. Fellow's refresh endpoint requires both tokens; rotated token pairs
atomically replace the stored credentials. Reauthentication uses the existing
account email, so it cannot silently change account identity.

Diagnostics redact account email, tokens, device and profile identifiers,
serial-like data, device names, profile titles, notes, roaster names, image
URLs, hashes, timestamps, and other authored text. Recipe values and operational
state remain visible. Avoid posting unreviewed Home Assistant logs or config
storage even though this integration does not log private API payloads.

## Development

The runtime has no third-party dependency beyond Home Assistant and its
`aiohttp` stack. Run the checks used by CI:

```bash
pytest
ruff check .
ruff format --check .
python -m compileall -q custom_components tests
python scripts/validate.py
```

All tests and fixtures use conspicuously fake identifiers and `.invalid`
addresses. See `PROTOCOL.md` for the sanitized protocol basis.

## License

MIT. See [LICENSE](LICENSE).
