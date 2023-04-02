"""Constants for integration_blueprint."""
from logging import Logger, getLogger

################################
# Do not change! Will be set by release workflow
INTEGRATION_VERSION = "main"  # git tag will be used
MIN_REQUIRED_HA_VERSION = "0.0.0"  # set min required version in hacs.json
################################

LOGGER: Logger = getLogger(__package__)

NAME = "Integration blueprint"
DOMAIN = "integration_blueprint"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
