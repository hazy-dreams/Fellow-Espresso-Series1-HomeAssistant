"""Constants for the Fellow Espresso Series 1 integration."""

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "fellow_series1"
PLATFORMS = (Platform.BINARY_SENSOR, Platform.SENSOR)
DEFAULT_SCAN_INTERVAL = timedelta(minutes=5)
PROFILE_SCAN_INTERVAL = timedelta(minutes=30)

CONF_EMAIL = "email"
CONF_ACCESS_TOKEN = "access_token"
CONF_REFRESH_TOKEN = "refresh_token"
CONF_DEVICE_ID = "device_id"
