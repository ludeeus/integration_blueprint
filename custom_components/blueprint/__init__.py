"""
Component to integrate with blueprint.

For more details about this component, please refer to
https://github.com/custom-components/blueprint
"""
import os
from datetime import timedelta
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import discovery
from homeassistant.util import Throttle
from .const import (
    CONF_BINARY_SENSOR,
    CONF_ENABLED,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_SENSOR,
    CONF_SWITCH,
    CONF_USERNAME,
    DEFAULT_NAME,
    DOMAIN_DATA,
    DOMAIN,
    ISSUE_URL,
    PLATFORMS,
    REQUIRED_FILES,
    STARTUP,
    VERSION,
)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

_LOGGER = logging.getLogger(__name__)

BINARY_SENSOR_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_ENABLED, default=True): cv.boolean,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

SENSOR_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_ENABLED, default=True): cv.boolean,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

SWITCH_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_ENABLED, default=True): cv.boolean,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_USERNAME): cv.string,
                vol.Optional(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_BINARY_SENSOR): vol.All(
                    cv.ensure_list, [BINARY_SENSOR_SCHEMA]
                ),
                vol.Optional(CONF_SENSOR): vol.All(cv.ensure_list, [SENSOR_SCHEMA]),
                vol.Optional(CONF_SWITCH): vol.All(cv.ensure_list, [SWITCH_SCHEMA]),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Set up this component."""
    # Import client from a external python package hosted on PyPi
    from sampleclient.client import Client

    # Print startup message
    startup = STARTUP.format(name=DOMAIN, version=VERSION, issueurl=ISSUE_URL)
    _LOGGER.info(startup)

    # Check that all required files are present
    file_check = await check_files(hass)
    if not file_check:
        return False

    # Create DATA dict
    hass.data[DOMAIN_DATA] = {}

    # Get "global" configuration.
    username = config[DOMAIN].get(CONF_USERNAME)
    password = config[DOMAIN].get(CONF_PASSWORD)

    # Configure the client.
    client = Client(username, password)
    hass.data[DOMAIN_DATA]["client"] = BlueprintData(hass, client)

    # Load platforms
    for platform in PLATFORMS:
        # Get platform specific configuration
        platform_config = config[DOMAIN].get(platform, {})

        # If platform is not enabled, skip.
        if not platform_config:
            continue

        for entry in platform_config:
            entry_config = entry

            # If entry is not enabled, skip.
            if not entry_config[CONF_ENABLED]:
                continue

            hass.async_create_task(
                discovery.async_load_platform(
                    hass, platform, DOMAIN, entry_config, config
                )
            )
    return True


class BlueprintData:
    """This class handle communication and stores the data."""

    def __init__(self, hass, client):
        """Initialize the class."""
        self.hass = hass
        self.client = client

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def update_data(self):
        """Update data."""
        # This is where the main logic to update platform data goes.
        try:
            data = self.client.get_data()
            self.hass.data[DOMAIN_DATA]["data"] = data
        except Exception as error:  # pylint: disable=broad-except
            _LOGGER.error("Could not update data - %s", error)


async def check_files(hass):
    """Return bool that indicates if all files are present."""
    # Verify that the user downloaded all files.
    base = "{}/custom_components/{}/".format(hass.config.path(), DOMAIN)
    missing = []
    for file in REQUIRED_FILES:
        fullpath = "{}{}".format(base, file)
        if not os.path.exists(fullpath):
            missing.append(file)

    if missing:
        _LOGGER.critical("The following files are missing: %s", str(missing))
        returnvalue = False
    else:
        returnvalue = True

    return returnvalue
