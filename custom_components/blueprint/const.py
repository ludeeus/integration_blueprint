"""Constants for blueprint."""
# Base component constants
DOMAIN = "blueprint"
DOMAIN_DATA = "{}_data".format(DOMAIN)
VERSION = "0.0.1"
PLATFORMS = ["binary_sensor", "sensor", "switch"]
REQUIRED_FILES = [
    "binary_sensor.py",
    "const.py",
    "manifest.json",
    "sensor.py",
    "switch.py",
]
ISSUE_URL = "https://github.com/custom-components/blueprint/issues"
ATTRIBUTION = "Data from this is provided by blueprint."
STARTUP = """
-------------------------------------------------------------------
{name}
Version: {version}
This is a custom component
If you have any issues with this you need to open an issue here:
{issueurl}
-------------------------------------------------------------------
"""

# Icons
ICON = "mdi:format-quote-close"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Configuration
CONF_BINARY_SENSOR = "binary_sensor"
CONF_SENSOR = "sensor"
CONF_SWITCH = "switch"
CONF_ENABLED = "enabled"
CONF_NAME = "name"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# Defaults
DEFAULT_NAME = DOMAIN
