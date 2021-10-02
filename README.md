# Powerpal custom component for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]

[![hacs][hacsbadge]][hacs]

_Component to integrate with [powerpal][powerpal]._

**This component will set up the following platforms.**

Platform | Description
-- | --
`sensor` | Show info from powerpal API.

![example][exampleimg]

## Manual Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `powerpal`.
4. Download _all_ the files from the `custom_components/powerpal/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Powerpal"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/powerpal/translations/en.json
custom_components/powerpal/__init__.py
custom_components/powerpal/config_flow.py
custom_components/powerpal/const.py
custom_components/powerpal/manifest.json
custom_components/powerpal/sensor.py
```

## Configuration is done in the UI

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[powerpal]: https://github.com/mindmelting/powerpal
[commits-shield]: https://img.shields.io/github/commit-activity/y/mindmelting/hass-powerpal.svg?style=for-the-badge
[commits]: https://github.com/mindmelting/hass-powerpal/commits/master
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/mindmelting/hass-powerpal.svg?style=for-the-badge
[releases]: https://github.com/mindmelting/hass-powerpal/releases
[exampleimg]: example.png
