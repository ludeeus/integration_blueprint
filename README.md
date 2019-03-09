# Notice

The component and platforms in this repository are not meant to be used by a
user, but as a "blueprint" that custom component developers can build
upon, to make more awesome stuff.

## Why?

This is simple, buy having custom_components look (README + structure) look the same
it is easier for developers to help each other and for users to start using it.

If you are a developer and you want to add things to this "blueprint" that you think more 
developers will have use for, please open a PR to add it :)

***
README content if this was a published component:
***

# blueprint

[![BuyMeCoffee][buymecoffeebedge]][buymecoffee]
[![custom_updater][customupdaterbadge]][customupdater]

_Component to integrate with [blueprint][blueprint]._

**This component will set up the following platforms.**

Platform | Description
-- | --
`binary_sensor` | Show something `True` or `False`
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
custom_components/blueprint/binary_sensor.py
custom_components/blueprint/const.py
custom_components/blueprint/sensor.py
```

## Example configuration.yaml

```yaml
blueprint:
  binary_sensor:
    - enabled: true
      name: My custom name
  sensor:
    - enabled: true
      name: My custom name
```

## Configuration options

Key | Type | Required | Description
-- | -- | -- | --
`binary_sensor` | `list` | `False` | Configuration for the `binary_sensor` platform.
`sensor` | `list` | `False` | Configuration for the `sensor` platform.

### Configuration options for `binary_sensor` list

Key | Type | Required | Default | Description
-- | -- | -- | -- | --
`enabled` | `boolean` | `False` | `False` | Boolean to enable/disable the platform.
`name` | `string` | `False` | `blueprint` | Custom name for the entity.

### Configuration options for `sensor` list

Key | Type | Required | Default | Description
-- | -- | -- | -- | --
`enabled` | `boolean` | `False` | `False` | Boolean to enable/disable the platform.
`name` | `string` | `False` | `blueprint` | Custom name for the entity.


## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[exampleimg]: example.png
[buymecoffee]: https://www.buymeacoffee.com/ludeeus
[buymecoffeebedge]: https://camo.githubusercontent.com/cd005dca0ef55d7725912ec03a936d3a7c8de5b5/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6275792532306d6525323061253230636f666665652d646f6e6174652d79656c6c6f772e737667
[blueprint]: https://github.com/custom-components/blueprint
[customupdater]: https://github.com/custom-components/custom_updater
[customupdaterbadge]: https://img.shields.io/badge/custom__updater-true-success.svg