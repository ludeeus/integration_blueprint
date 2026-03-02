"""Constants for the ENGIE Belgium integration."""

from __future__ import annotations

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "engie_be"
ATTRIBUTION = "Data provided by ENGIE Belgium"

# OAuth / Auth0 endpoints
AUTH_BASE_URL = "https://account.engie.be"
API_BASE_URL = "https://www.engie.be/api/engie/be/ms/billing/customer/v1"
PREMISES_BASE_URL = "https://www.engie.be/api/engie/be/ms/premises/customer/v1"

# OAuth configuration (public mobile-app client, no secret needed)
DEFAULT_CLIENT_ID = "R0PQyUdjO5B2tBaRnltgitVnnUmjGyld"
REDIRECT_URI = "be.engie.smart://login-callback/nl"
OAUTH_SCOPES = "openid profile roles offline_access"
OAUTH_AUDIENCE = "customer"

# Config entry keys (beyond homeassistant.const CONF_USERNAME / CONF_PASSWORD)
CONF_CUSTOMER_NUMBER = "customer_number"
CONF_MFA_METHOD = "mfa_method"
CONF_CLIENT_ID = "client_id"
CONF_ACCESS_TOKEN = "access_token"  # noqa: S105
CONF_REFRESH_TOKEN = "refresh_token"  # noqa: S105

# MFA method options
MFA_METHOD_SMS = "sms"
MFA_METHOD_EMAIL = "email"

# User-Agent strings matching the ENGIE mobile app
USER_AGENT_BROWSER = (
    "Mozilla/5.0 (Linux; Android 10; K) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/142.0.0.0 Mobile Safari/537.36"
)
USER_AGENT_NATIVE = "Dalvik/2.1.0 (Linux; U; Android 16; Pixel 6 Build/BP4A.251205.006)"

# Token refresh interval in seconds (access token valid ~2 min, refresh every 1 min)
TOKEN_REFRESH_INTERVAL_SECONDS = 60

# Price update interval (configurable via options flow)
CONF_UPDATE_INTERVAL = "update_interval"
DEFAULT_UPDATE_INTERVAL_HOURS = 1
MIN_UPDATE_INTERVAL_HOURS = 1
MAX_UPDATE_INTERVAL_HOURS = 24
