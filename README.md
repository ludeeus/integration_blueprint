# blueprint

[![BuyMeCoffee][buymecoffeebedge]][buymecoffee]
[![custom_updater][customupdaterbadge]][customupdater]

_Component to integrate with [blueprint][blueprint]._

**This component will set up the following platforms.**

Platform | Description
-- | --
`sensor` | Show info from blueprint API.

![example][exampleimg]

## Installation

1. Using you tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `blueprint`.
4. Download _all_ the files from the `custom_components/blueprint/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Add `blueprint:` to your HA configuration.

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/blueprint/__init__.py
custom_components/blueprint/const.py
custom_components/blueprint/sensor.py
```

## Example configuration.yaml

```yaml
blueprint:
```


***

[exampleimg]: example.png
[buymecoffee]: https://www.buymeacoffee.com/ludeeus
[buymecoffeebedge]: https://camo.githubusercontent.com/cd005dca0ef55d7725912ec03a936d3a7c8de5b5/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6275792532306d6525323061253230636f666665652d646f6e6174652d79656c6c6f772e737667
[blueprint]: https://github.com/custom-components/blueprint
[customupdater]: https://github.com/custom-components/custom_updater
[customupdaterbadge]: https://img.shields.io/badge/custom__updater-true-success.svg