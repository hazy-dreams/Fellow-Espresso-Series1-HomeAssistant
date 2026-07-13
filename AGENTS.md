# Fellow Series 1 for Home Assistant — agent instructions

This repository is intended for public release under the GNU GPL v3.0 license.

## Scope

Build a standalone Home Assistant custom integration with domain `fellow_series1`. It must coexist with the unrelated `fellow` / Fellow Aiden integration.

Version 0.1.0 is cloud-polling and read-only. It supports Fellow Espresso Series 1 (`deviceType: Solo`) only.

## Non-negotiable constraints

- Never read files outside this repository, especially `~/.hermes/secrets`.
- Never use or invent real account, device, profile, serial, MAC, or token values.
- Fixtures must use obviously fake identifiers and neutral profile names.
- Never persist the Fellow password. Exchange it during config flow, then store only the email, selected device identifier, and token pair required by Fellow's refresh contract.
- Redact tokens, serial numbers, device IDs, emails, profile notes, image URLs, and user-authored text from diagnostics and logs.
- No remote brew, schedules, profile writes, firmware writes, or device-setting writes in v0.1.0.
- Do not copy implementation code from FellowAiden-HomeAssistant. This is a clean implementation based on the protocol facts in `PROTOCOL.md`.
- Keep dependencies minimal. Runtime dependencies should normally be none beyond Home Assistant/aiohttp.
- Use typed, readable Python and modern Home Assistant ConfigEntry `runtime_data` patterns.
- Codex may commit locally after tests pass. It must not create a GitHub repository, push, publish, or access external credentials.

## Acceptance criteria

- Config flow accepts email/password, authenticates, discovers one or more Solo devices, and stores no password.
- Reauthentication updates the refresh token without changing the account identity.
- Coordinator polls device and profiles through the v2 Solo API.
- Entities: connected, firmware update required, firmware version, active profile, profile count, elevation, and settings version.
- Active-profile attributes expose only structured recipe fields and never identifiers/private notes/URLs.
- Diagnostics are aggressively redacted.
- Config flow, API client, models/helpers, coordinator behavior, entities, and diagnostics have tests with sanitized fixtures.
- README documents cloud dependence, supported features, unsupported telemetry/control, installation, security/privacy, and reverse-engineered/unofficial status.
- Include GPL-3.0 LICENSE, HACS metadata, translations, GitHub CI, Ruff configuration, pytest configuration, and a manifest with version `0.1.0`.
- `pytest`, Ruff, syntax compilation, JSON parsing, and manifest/HACS structure checks pass.
