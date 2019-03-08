"""Conststants for blueprint."""
# Base component constants
DOMAIN = "blueprint"
DOMAIN_DATA = "{}_data".format(DOMAIN)
VERSION = "0.0.1"
PLATFORMS = ["binary_sensor", "sensor"]
REQUIRED_FILES = ["binary_sensor.py", "sensor.py", "const.py"]
ISSUE_URL = "https://github.com/custom-components/blueprint/issues"

STARTUP = """
-------------------------------------------------------------------
{name}
Version: {version}
This is a custom component
If you have any issues with this you need to open an issue here:
{issueurl}
-------------------------------------------------------------------
"""

# Operational
URL = 'https://jsonplaceholder.typicode.com/todos/1'

# Icons
SENSOR_ICON = "mdi:format-quote-close"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = 'connectivity'
