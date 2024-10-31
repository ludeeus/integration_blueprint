#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

# Create config dir if not present
if [[ ! -d "${PWD}/config" ]]; then
    mkdir -p "${PWD}/config"
    hass --config "${PWD}/config" --script ensure_config
fi

# Start Home Assistant
hass --config "${PWD}/config" --debug
