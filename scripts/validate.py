"""Dependency-free repository structure and JSON validation."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components" / "fellow_series1"

required_files = (
    ROOT / "README.md",
    ROOT / "LICENSE",
    ROOT / "hacs.json",
    ROOT / "scripts" / "check_ha_imports.py",
    INTEGRATION / "manifest.json",
    INTEGRATION / "strings.json",
    INTEGRATION / "translations" / "en.json",
    INTEGRATION / "brand" / "icon.png",
    INTEGRATION / "brand" / "icon@2x.png",
    INTEGRATION / "brand" / "logo.png",
    INTEGRATION / "brand" / "logo@2x.png",
)
for path in required_files:
    if not path.is_file():
        raise SystemExit(f"Missing required file: {path.relative_to(ROOT)}")

for path in ROOT.rglob("*.json"):
    with path.open(encoding="utf-8") as file:
        json.load(file)

for path in (INTEGRATION / "brand").glob("*.png"):
    if not path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
        raise SystemExit(f"Invalid PNG brand asset: {path.relative_to(ROOT)}")

manifest = json.loads((INTEGRATION / "manifest.json").read_text(encoding="utf-8"))
expected = {
    "domain": "fellow_series1",
    "config_flow": True,
    "documentation": "https://github.com/hazy-dreams/Fellow-Espresso-Series1-HomeAssistant#readme",
    "iot_class": "cloud_polling",
    "requirements": [],
}
for key, value in expected.items():
    if manifest.get(key) != value:
        raise SystemExit(f"manifest.json has invalid {key!r}")

manifest_version = manifest.get("version")
if (
    not isinstance(manifest_version, str)
    or re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", manifest_version)
    is None
):
    raise SystemExit("manifest.json has invalid 'version'")
project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
if project.get("project", {}).get("version") != manifest_version:
    raise SystemExit("pyproject.toml and manifest.json versions must match")

hacs = json.loads((ROOT / "hacs.json").read_text(encoding="utf-8"))
if not isinstance(hacs.get("name"), str) or not hacs["name"]:
    raise SystemExit("hacs.json must contain a name")
if hacs.get("homeassistant") != "2024.11.0":
    raise SystemExit("hacs.json must declare the minimum Home Assistant version")

api_source = (INTEGRATION / "api.py").read_text(encoding="utf-8")
for forbidden in ('"PUT"', '"PATCH"', '"DELETE"', "/schedules", "/brew"):
    if forbidden in api_source:
        raise SystemExit(
            f"Read-only API client contains forbidden operation: {forbidden}"
        )

print("Repository structure and JSON are valid")
