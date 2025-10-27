"""Constants for HDFury integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "hdfury"
ATTRIBUTION = "Data provided by HDFury Device"

# Configuration
CONF_HOST = "host"

# Default values
DEFAULT_SCAN_INTERVAL = 5  # seconds
DEFAULT_PORT = 80
MAX_INPUT_PORT = 3  # Maximum input port number (0-3)

# Input names (can be customized by user)
INPUT_NAMES = ["Input 0", "Input 1", "Input 2", "Input 3"]
