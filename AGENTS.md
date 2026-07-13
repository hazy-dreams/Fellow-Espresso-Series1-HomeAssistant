# Fellow Series 1 for Home Assistant — agent instructions

This repository is intended for public release under the GNU GPL v3.0 license.

## Scope

Build a standalone Home Assistant custom integration with domain `fellow_series1`.

The integration is cloud-polling and read-only. It supports Fellow Espresso Series 1 (`deviceType: Solo`) only.

## Non-negotiable constraints

- Never read credentials, private data, or secrets from outside this repository.
- Never use or invent real account, device, profile, serial, MAC, or token values.
- Fixtures must use obviously fake identifiers and neutral profile names.
- Never persist the Fellow password. Exchange it during config flow, then store only the email, selected device identifier, and token pair required by Fellow's refresh contract.
- Redact tokens, serial numbers, device IDs, emails, profile notes, image URLs, and user-authored text from diagnostics and logs.
- No remote brew, schedules, profile writes, firmware writes, or device-setting writes.
- Keep dependencies minimal. Runtime dependencies should normally be none beyond Home Assistant/aiohttp.
- Use typed, readable Python and modern Home Assistant ConfigEntry `runtime_data` patterns.
- Automated contributors may commit locally after tests pass. They must not create external repositories, push, publish, or access external credentials unless explicitly authorized.

## Acceptance criteria

- Config flow accepts email/password, authenticates, discovers one or more Solo devices, and stores no password.
- Reauthentication updates the refresh token without changing the account identity.
- Coordinator polls device and profiles through the v2 Solo API.
- Entities: connected, firmware update required, firmware version, active profile, target yield, planned duration, profile count, elevation, and settings version.
- Active-profile attributes expose only structured recipe fields and safe derivations, never identifiers/private notes/URLs.
- Diagnostics are aggressively redacted.
- Config flow, API client, models/helpers, coordinator behavior, entities, and diagnostics have tests with sanitized fixtures.
- README documents cloud dependence, supported features, unsupported telemetry/control, installation, security/privacy, and reverse-engineered/unofficial status.
- Include GPL-3.0 LICENSE, HACS metadata, translations, GitHub CI, Ruff configuration, pytest configuration, and synchronized project/manifest versions.
- `pytest`, Ruff, syntax compilation, JSON parsing, and manifest/HACS structure checks pass.
