# Anova Nano Home Asssistant Integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Project Maintenance][maintenance-shield]

_Integration to integrate with [pyanova_nano]._

**This integration will set up the following platforms.**

| Platform        | Description                         |
| --------------- | ----------------------------------- |
| `binary_sensor` | Show something `True` or `False`.   |
| `sensor`        | Show info from blueprint API.       |
| `switch`        | Switch something `True` or `False`. |

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `anova_nano`.
1. Download _all_ the files from the `custom_components/anova_nano/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Anova Nano"

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

---

[pyanova_nano]: https://github.com/filmkorn/pyanova-nano
[commits-shield]: https://img.shields.io/github/commit-activity/y/mcolyer/hacs-anova-nano.svg?style=for-the-badge
[commits]: https://github.com/mcolyer/hacs-anova-nano/commits/main
[license-shield]: https://img.shields.io/github/license/mcolyer/hacs-anova-nano.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Matt%20Colyer%20%40mcolyer-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/mcolyer/hacs-anova-nano.svg?style=for-the-badge
[releases]: https://github.com/mcolyer/hacs-anova-nano/releases
