"""
Component to integrate with blueprint.

For more details about this component, please refer to
https://github.com/custom-components/blueprint
"""
import os
from datetime import timedelta
import logging
import requests
from homeassistant.helpers import discovery
from homeassistant.util import Throttle
from .const import (
    DOMAIN_DATA, DOMAIN, ISSUE_URL, PLATFORMS, REQUIRED_FILES, STARTUP, URL,
    VERSION)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

_LOGGER = logging.getLogger(__name__)

# pylint: disable=unused-argument


async def async_setup(hass, config):
    """Set up this component."""

    # Print startup message
    startup = STARTUP.format(name=DOMAIN, version=VERSION, issueurl=ISSUE_URL)
    _LOGGER.info(startup)

    # Check that all required files are present
    file_check = await check_files(hass)
    if not file_check:
        return False

    # Create DATA dict
    hass.data[DOMAIN_DATA] = {}

    # Load platforms
    for platform in PLATFORMS:
        hass.async_create_task(
            discovery.async_load_platform(hass, platform, DOMAIN, {}, config)
        )
    return True

@Throttle(MIN_TIME_BETWEEN_UPDATES)
async def update_data(hass):
    """Update data."""
    # This is where the main logic to update platform data goes.
    try:
        request = requests.get(URL)
        jsondata = request.json()
        hass.data[DOMAIN_DATA] = jsondata
    except Exception as error:  # pylint: disable=broad-except
        _LOGGER.error("Could not update data - %s", error)


async def check_files(hass):
    """Retrun bool that idicate that all files are present."""
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
