"""Constants for ims_envista."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "ims_envista"
ATTRIBUTION = "Data provided by IMS Envista"

CONF_STATION = "station"
CONF_STATION_ID = "station_id"
CONF_STATION_CONDITIONS = "station_conditions"
STATION_NAME_CHANNEL = "station_name"
LAST_UPDATED_CHANNEL = "last_updated"
STATIC_DATA_CHANNELS = [STATION_NAME_CHANNEL]
LATEST_KEY = "latest"
DAILY_KEY = "daily"
RAIN_CHANNEL = "Rain"
WSMAX_CHANNEL = "WSmax"
WDMAX_CHANNEL = "WDmax"
WS_CHANNEL = "WS"
WD_CHANNEL = "WD"
STDWD_CHANNEL = "STDwd"
TD_CHANNEL = "TD"
TDMAX_CHANNEL = "TDmax"
TDMIN_CHANNEL = "TDmin"
RH_CHANNEL = "RH"
TG_CHANNEL = "TG"
RAD_AGRO_CHANNEL = "RadAgro"
WS_1MM_CHANNEL = "WS1mm"
WS_10MM_CHANNEL = "Ws10mm"
TIME_CHANNEL = "Time"
TW_CHANNEL = "TW"
