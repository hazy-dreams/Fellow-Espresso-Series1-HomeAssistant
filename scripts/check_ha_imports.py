"""Import every integration module against an installed Home Assistant version."""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MODULES = (
    "custom_components.fellow_series1",
    "custom_components.fellow_series1.api",
    "custom_components.fellow_series1.binary_sensor",
    "custom_components.fellow_series1.config_flow",
    "custom_components.fellow_series1.const",
    "custom_components.fellow_series1.coordinator",
    "custom_components.fellow_series1.diagnostics",
    "custom_components.fellow_series1.entity",
    "custom_components.fellow_series1.models",
    "custom_components.fellow_series1.sensor",
)

for module_name in MODULES:
    import_module(module_name)

print(f"Imported {len(MODULES)} integration modules successfully")
