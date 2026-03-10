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
- Detects gas and electricity contracts via the ENGIE service-points endpoint
- Creates price sensors per energy type, direction (offtake / injection), and
  tariff rate (single-rate, dual-rate, or tri-rate contracts)
- Configurable update interval via the integration options

## Sensors

The integration auto-detects your energy contracts and creates sensors
accordingly. Electricity price sensors are in **EUR/kWh** and gas price sensors
are in **EUR/m³**, both with 6 decimal precision.
Each sensor exposes the following attributes: `ean`, `from`, `to`,
`vat_tariff`, and `time_of_use_slot_code`.

Which sensors are created depends on your contract type. The integration reads
the `timeOfUseSlotCode` from the API response to determine whether you have a
single-rate, dual-rate (peak / off-peak), or tri-rate
(peak / off-peak / super off-peak) contract.

### Gas

Gas contracts are always single-rate.

| Sensor | Entity ID | Description |
|---|---|---|
| Gas offtake price | `sensor.engie_belgium_gas_offtake_price` | Current gas offtake price incl. VAT |
| Gas offtake price (excl. VAT) | `sensor.engie_belgium_gas_offtake_price_excl_vat` | Current gas offtake price excl. VAT |

### Electricity: single-rate

Created when the API returns `TOTAL_HOURS` as the time-of-use slot code.

| Sensor | Entity ID | Description |
|---|---|---|
| Electricity offtake price | `sensor.engie_belgium_electricity_offtake_price` | Current electricity offtake price incl. VAT |
| Electricity offtake price (excl. VAT) | `sensor.engie_belgium_electricity_offtake_price_excl_vat` | Current electricity offtake price excl. VAT |
| Electricity injection price | `sensor.engie_belgium_electricity_injection_price` | Current electricity injection price incl. VAT |
| Electricity injection price (excl. VAT) | `sensor.engie_belgium_electricity_injection_price_excl_vat` | Current electricity injection price excl. VAT |

### Electricity: dual-rate (peak / off-peak)

Created when the API returns `PEAK` and `OFFPEAK` as time-of-use slot codes
(e.g. two-period meter contracts). These sensors replace the single-rate
offtake/injection sensors for that EAN.

| Sensor | Entity ID | Description |
|---|---|---|
| Electricity peak offtake price | `sensor.engie_belgium_electricity_peak_offtake_price` | Current electricity peak offtake price incl. VAT |
| Electricity peak offtake price (excl. VAT) | `sensor.engie_belgium_electricity_peak_offtake_price_excl_vat` | Current electricity peak offtake price excl. VAT |
| Electricity off-peak offtake price | `sensor.engie_belgium_electricity_off_peak_offtake_price` | Current electricity off-peak offtake price incl. VAT |
| Electricity off-peak offtake price (excl. VAT) | `sensor.engie_belgium_electricity_off_peak_offtake_price_excl_vat` | Current electricity off-peak offtake price excl. VAT |
| Electricity peak injection price | `sensor.engie_belgium_electricity_peak_injection_price` | Current electricity peak injection price incl. VAT |
| Electricity peak injection price (excl. VAT) | `sensor.engie_belgium_electricity_peak_injection_price_excl_vat` | Current electricity peak injection price excl. VAT |
| Electricity off-peak injection price | `sensor.engie_belgium_electricity_off_peak_injection_price` | Current electricity off-peak injection price incl. VAT |
| Electricity off-peak injection price (excl. VAT) | `sensor.engie_belgium_electricity_off_peak_injection_price_excl_vat` | Current electricity off-peak injection price excl. VAT |

### Electricity: tri-rate (peak / off-peak / super off-peak)

Created when the API returns `PEAK`, `OFFPEAK`, and `SUPEROFFPEAK` as
time-of-use slot codes.

| Sensor | Entity ID | Description |
|---|---|---|
| Electricity peak offtake price | `sensor.engie_belgium_electricity_peak_offtake_price` | Current electricity peak offtake price incl. VAT |
| Electricity peak offtake price (excl. VAT) | `sensor.engie_belgium_electricity_peak_offtake_price_excl_vat` | Current electricity peak offtake price excl. VAT |
| Electricity off-peak offtake price | `sensor.engie_belgium_electricity_off_peak_offtake_price` | Current electricity off-peak offtake price incl. VAT |
| Electricity off-peak offtake price (excl. VAT) | `sensor.engie_belgium_electricity_off_peak_offtake_price_excl_vat` | Current electricity off-peak offtake price excl. VAT |
| Electricity super off-peak offtake price | `sensor.engie_belgium_electricity_super_off_peak_offtake_price` | Current electricity super off-peak offtake price incl. VAT |
| Electricity super off-peak offtake price (excl. VAT) | `sensor.engie_belgium_electricity_super_off_peak_offtake_price_excl_vat` | Current electricity super off-peak offtake price excl. VAT |
| Electricity peak injection price | `sensor.engie_belgium_electricity_peak_injection_price` | Current electricity peak injection price incl. VAT |
| Electricity peak injection price (excl. VAT) | `sensor.engie_belgium_electricity_peak_injection_price_excl_vat` | Current electricity peak injection price excl. VAT |
| Electricity off-peak injection price | `sensor.engie_belgium_electricity_off_peak_injection_price` | Current electricity off-peak injection price incl. VAT |
| Electricity off-peak injection price (excl. VAT) | `sensor.engie_belgium_electricity_off_peak_injection_price_excl_vat` | Current electricity off-peak injection price excl. VAT |
| Electricity super off-peak injection price | `sensor.engie_belgium_electricity_super_off_peak_injection_price` | Current electricity super off-peak injection price incl. VAT |
| Electricity super off-peak injection price (excl. VAT) | `sensor.engie_belgium_electricity_super_off_peak_injection_price_excl_vat` | Current electricity super off-peak injection price excl. VAT |

> Injection sensors are only created when injection data is present in the API
> response.

### Authentication

A binary connectivity sensor (`binary_sensor.engie_belgium_authentication`) is
always created, showing whether the integration is currently authenticated with
the ENGIE API.

## Prerequisites

- An active [ENGIE Belgium](https://www.engie.be/) account
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
- **Energy type detection**: At startup the integration calls the ENGIE
  service-points endpoint for each EAN to determine whether the contract is gas
  or electricity. If the lookup fails, a generic "Energy" label is used as
  fallback.

## License

[MIT](LICENSE) - Daan Vervacke ([@DaanVervacke](https://github.com/DaanVervacke))

---

*Data provided by ENGIE Belgium*

[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg
[release]: https://github.com/DaanVervacke/hass-engie-be/releases
[releasebadge]: https://img.shields.io/github/v/release/DaanVervacke/hass-engie-be
[licensebadge]: https://img.shields.io/github/license/DaanVervacke/hass-engie-be
