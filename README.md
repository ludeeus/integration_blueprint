# ENGIE Belgium HACS integration

[![HACS Custom][hacsbadge]][hacs]
[![GitHub Release][releasebadge]][release]
[![License][licensebadge]](LICENSE)

Custom [Home Assistant](https://www.home-assistant.io/) integration for
[ENGIE Belgium](https://www.engie.be/). Retrieves your personal energy price
data from the ENGIE Belgium API and exposes it as sensors.

## Features

- Authenticates via ENGIE Belgium's OAuth2/PKCE flow with two-factor
  authentication (SMS or email)
- Automatically refreshes access tokens in the background
- Detects gas and electricity contracts from your EAN numbers
- Creates price sensors per energy type, direction (offtake / injection), and
  tariff rate (single-rate or peak / off-peak for dual-rate contracts)
- Configurable update interval via the integration options

## Sensors

The integration auto-detects your energy contracts and creates sensors
accordingly. All price sensors are in **EUR/kWh** with 6 decimal precision.

| Sensor | Description | Energy type |
|---|---|---|
| Gas offtake price | Current gas offtake price incl. VAT | Gas |
| Gas offtake price (excl. VAT) | Current gas offtake price excl. VAT | Gas |
| Electricity offtake price | Current electricity offtake price incl. VAT | Electricity |
| Electricity offtake price (excl. VAT) | Current electricity offtake price excl. VAT | Electricity |
| Electricity peak offtake price | Current electricity peak offtake price incl. VAT | Electricity |
| Electricity peak offtake price (excl. VAT) | Current electricity peak offtake price excl. VAT | Electricity |
| Electricity off-peak offtake price | Current electricity off-peak offtake price incl. VAT | Electricity |
| Electricity off-peak offtake price (excl. VAT) | Current electricity off-peak offtake price excl. VAT | Electricity |
| Electricity injection price | Current electricity injection price incl. VAT | Electricity |
| Electricity injection price (excl. VAT) | Current electricity injection price excl. VAT | Electricity |
| Authentication | Binary sensor showing authentication status | N/A |

> Injection sensors are only created when injection data is present in the API
> response. Gas contracts never have injection data. Peak and off-peak sensors
> are only created for dual-rate (day/night) contracts. Single-rate contracts
> get the standard offtake/injection sensors.

Each sensor also exposes the following attributes: `ean`, `from`, `to`,
`vat_tariff`, and `time_of_use_slot_code`.

## Prerequisites

- An active [ENGIE Belgium](https://www.engie.be/) account with online access
- Your ENGIE customer number (business agreement number)
- Access to SMS or email for two-factor authentication during setup

## Installation

### HACS (recommended)

1. Open HACS in your Home Assistant instance
2. Click the three dots in the top right corner and select **Custom repositories**
3. Add `https://github.com/DaanVervacke/hass-engie-be` with category **Integration**
4. Search for **ENGIE Belgium** in HACS and install it
5. Restart Home Assistant

## Configuration

Configuration is done entirely through the Home Assistant UI.

1. Go to **Settings** > **Devices & Services** > **Add Integration**
2. Search for **ENGIE Belgium**
3. Enter your credentials:
   - **Email address** - your ENGIE Belgium login email
   - **Password** - your ENGIE Belgium password
   - **Customer number** - your ENGIE customer/business agreement number
   - **Client ID** - leave at the default unless you know what you're doing
   - **Two-factor authentication method** - choose SMS or Email
4. Click **Submit** - you will receive a verification code via your chosen method
5. Enter the 6-digit verification code and click **Submit**

The integration will authenticate, fetch your energy prices, and create the
appropriate sensors.

### Options

After setup, you can configure the price update interval:

1. Go to **Settings** > **Devices & Services**
2. Find the **ENGIE Belgium** integration and click **Configure**
3. Set the **Update interval** (1--24 hours, default: 1 hour)

## How it works

- **Authentication**: Uses OAuth2 with PKCE (public client, no secret) through
  ENGIE's Auth0 login. Two-factor authentication is required only during
  initial setup. The refresh token is persisted across restarts.
- **Token refresh**: Access tokens expire in ~2 minutes. The integration
  refreshes tokens every 60 seconds automatically. Refresh tokens are rotated
  and persisted to the config entry.
- **Data polling**: Energy prices are fetched at the configured interval
  (default: every hour). The coordinator makes a single API call per update.
- **Energy type detection**: The EAN prefix determines whether a contract is
  gas (`5414488600*`) or electricity (`5414488200*`).

## License

[MIT](LICENSE) - Daan Vervacke ([@DaanVervacke](https://github.com/DaanVervacke))

---

*Data provided by ENGIE Belgium*

[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg
[release]: https://github.com/DaanVervacke/hass-engie-be/releases
[releasebadge]: https://img.shields.io/github/v/release/DaanVervacke/hass-engie-be
[licensebadge]: https://img.shields.io/github/license/DaanVervacke/hass-engie-be
