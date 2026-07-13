# Sanitized protocol notes

These notes describe observed Fellow cloud behavior without account/device secrets. The API is undocumented and unofficial.

## Gateways

```text
Legacy/shared: https://l8qtmnc692.execute-api.us-west-2.amazonaws.com/v1
Current:       https://l8qtmnc692.execute-api.us-west-2.amazonaws.com/v2
```

Prefer v2 for authentication and Series 1 operations. A compatibility fallback to v1 login may be implemented only if it does not cause password persistence.

## Authentication

Current app behavior:

```http
POST /v2/auth/login
Content-Type: application/json

{"email": "…", "password": "…"}
```

Successful login may return HTTP 200 or 201 and JSON containing `accessToken` and `refreshToken`. Access tokens are short-lived. Never retain the password after this exchange.

Current app bytecode implements:

```http
POST /v2/auth/refresh-token
Content-Type: application/json

{"refreshToken": "…"}
```

The client must accept a rotated `refreshToken` when returned. Treat a rejected refresh request (HTTP 401/403) or an unusable successful token response as an authentication failure so Home Assistant starts reauthentication. Preserve transport and non-authentication server failures as retryable update errors; do not discard the stored token pair or retain/retry a password.

Authenticated requests use:

```http
Authorization: Bearer <accessToken>
Accept: application/json
```

## Device discovery

Shared discovery has historically used:

```http
GET /v1/devices?dataType=real
```

The current app may use v2. A client may try v2 first and use v1 only for read-only discovery when v2 returns a clear unsupported response. Select only devices whose `deviceType` is case-insensitively `Solo`. Multiple devices must not be silently collapsed.

Relevant observed device fields:

```text
id, displayName, deviceType, isConnected, firmwareVersion,
firmwareUpgradeRequired, activeProfileId, elevation, settingsVersion,
tempUnit, deviceTimezone, sku, missingWater, awsStatus
```

Identifiers, serial numbers, addresses, and user-provided display names are private diagnostics data.

## Series 1 reads

```http
GET /v2/solo/devices/{url_encoded_device_id}?dataType=real
GET /v2/solo/devices/{url_encoded_device_id}/profiles
```

Both returned HTTP 200 in read-only discovery.

Profile fields observed:

```text
id, title, folder, status, dose, ratio, temperature, grindSize,
adaptive, decliningTemp, preInfusionEnabled, preInfusionDuration,
preInfusionFillFlowRate, preInfusionHoldPressure, infusion,
rampDownEnabled, rampDownDuration, rampDownEndPressure,
transition, updatedAt, scheduledAt, deletedAt,
roasterName, notes, imageUrl, blurHash
```

Each `infusion` item observed has `duration` and `pressure`.

Do not expose profile IDs, notes, roaster names, image URLs, hashes, or timestamps as diagnostics. The active profile entity may expose structured recipe fields: dose, ratio, derived target yield, derived planned duration, temperature, grind size, adaptive, pre-infusion configuration, infusion stages, and ramp-down configuration.

## Unsupported or unverified

- `/v2/solo/devices/{id}/schedules` returned HTTP 403.
- No shot history, total shot counter, water usage, live pressure/flow, heater state, ready state, or shot timestamps were observed.
- `missingWater` and `awsStatus` were null while idle; do not create entities until behavior is proven.
- App code contains write/control routes, but this integration must not call them.
- Do not expose remote brew.
