# Israel Meteorological Service (IMS) Envista Custom Component

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]


_Integration to integrate with [IMS Envista API][ims-envista-api]._

**This integration could set up the following conditions.**

![Example Image][exampleimg]


Condition | Description
-- | --
`station_name` | The Station Name
`last_updated` | Date/Time of the Last Data Update
`rain` | Amount of rain in mm
`rh` | Relative Humidity
`wd` | Wind Direction
`wd_max` | Top Gust Wind Direction
`std_wd` | Wind Direction Deviation
`td` | Dry Temperature
`td_max` | Maximal Temperature
`td_min` | Minimal Temperature
`tg` | (Next to the) Ground Temperature
`ws` | Wind Speed
`ws_max` | Top Gust Wind Speed
`ws_1mm` | Maximal 1min Wind Speed
`ws_10mm` | Maximal 10min Wind Speed
`bp` | Barometric Pressure
`diff` | Diffused Radiation
`grad` | Global Radiation
`nip` | Direct Radiation

## Installation

Automatic (HACS):
1. Add this path to HACS: `https://github.com/GuyKh/ims-envista-custom-component`
2. Install through HACS

Manual:
1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `ims_envista`.
1. Download _all_ the files from the `custom_components/ims_envista/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "IMS Envista"

## Configuration is done in the UI

## Logs
To view logs in debug add this to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    ...
    custom_components.ims_envista: debug
    ims_envista: debug
```

<!---->

## Frequently Asked Questions

#### How can I get an API key?
Contact [ims@ims.gov.il](mailto:ims@ims.gov.il).

#### Can I use the integration without an API key?
**No.**

#### How often is the data fetched?
The component currently fetches data from IMS **every hour**, but it really depends on how often the weather station updates its data.

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[ims-envista-api]: https://ims.gov.il/sites/default/files/2021-09/API%20explanation.pdf
[buymecoffee]: https://www.buymeacoffee.com/guykh
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/guykh/ims-envista-custom-component.svg?style=for-the-badge
[commits]: https://github.com/guykh/ims-envista-custom-component/commits/main
[exampleimg]: example.png
[license-shield]: https://img.shields.io/github/license/guykh/ims-envista-custom-component.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Guy%20Khmelnitsky%20%40GuyKh-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/guykh/ims-envista-custom-component.svg?style=for-the-badge
[releases]: https://github.com/guykh/ims-envista-custom-component/releases
