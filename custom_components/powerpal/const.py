"""Constants for powerpal."""
# Base component constants
NAME = "Powerpal"
DOMAIN = "powerpal"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.1.0"
ATTRIBUTION = "Data provided by https://readings.powerpal.net"
ISSUE_URL = "https://github.com/mindmelting/hass-powerpal/issues"

# Icons
ICON = "mdi:transmission-tower"

# Device classes

# Platforms
SENSOR = "sensor"
PLATFORMS = [SENSOR]


# Configuration and options
CONF_ENABLED = "enabled"
CONF_AUTH_KEY = "auth_key"
CONF_DEVICE_ID = "device_id"

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
