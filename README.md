# HDFury Home Assistant Integration

A custom Home Assistant integration for HDFury devices, allowing you to control and monitor your HDFury Vertex² and other compatible devices.

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/pkern90/hdfury-homeassistant.svg)](https://github.com/pkern90/hdfury-homeassistant/releases)
[![License](https://img.shields.io/github/license/pkern90/hdfury-homeassistant.svg)](LICENSE)

## Features

- **Input Selection**: Switch between HDMI inputs (0-3) via a select entity
- **Status Monitoring**: Track device status including:
  - Current active input
  - RX0/RX1 input status
  - TX0/TX1 output status
  - Audio output status
- **Signal Detection**: Binary sensor to detect if HDMI signal is present
- **Local Control**: All communication happens locally via HTTP API (no cloud required)

## Supported Devices

- HDFury Vertex²
- Other HDFury devices with HTTP API support (may require adjustments)

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the three dots in the top right corner and select "Custom repositories"
4. Add the repository URL: `https://github.com/pkern90/hdfury-homeassistant`
5. Select category: "Integration"
6. Click "Add"
7. Find "HDFury" in the integration list and click "Download"
8. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/pkern90/hdfury-homeassistant/releases)
2. Extract the `hdfury` folder from the archive
3. Copy the `hdfury` folder to your `custom_components` directory in your Home Assistant configuration directory
4. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "HDFury"
4. Enter the IP address or hostname of your HDFury device
5. Click **Submit**

The integration will automatically create the following entities:

### Entities Created

| Entity | Type | Description |
|--------|------|-------------|
| `select.hdfury_input_selection` | Select | Change the active HDMI input (0-3) |
| `sensor.hdfury_current_input` | Sensor | Display the currently active input |
| `sensor.hdfury_rx0_status` | Sensor | RX0 input status |
| `sensor.hdfury_rx1_status` | Sensor | RX1 input status |
| `sensor.hdfury_tx0_status` | Sensor | TX0 output status |
| `sensor.hdfury_tx1_status` | Sensor | TX1 output status |
| `sensor.hdfury_audio_output` | Sensor | Audio output status |
| `binary_sensor.hdfury_signal_detected` | Binary Sensor | Signal detection status |

## Usage Examples

### Automations

#### Switch Input When TV Turns On

```yaml
automation:
  - alias: "Switch HDFury to FireTV when TV turns on"
    trigger:
      - platform: state
        entity_id: media_player.tv
        to: "on"
    action:
      - service: select.select_option
        target:
          entity_id: select.hdfury_input_selection
        data:
          option: "Input 0"  # FireTV
```

#### Notify When Signal Lost

```yaml
automation:
  - alias: "Notify when HDMI signal lost"
    trigger:
      - platform: state
        entity_id: binary_sensor.hdfury_signal_detected
        to: "off"
        for:
          seconds: 5
    action:
      - service: notify.mobile_app
        data:
          message: "HDFury lost HDMI signal"
```

### Lovelace Card Example

```yaml
type: entities
title: HDFury Control
entities:
  - entity: select.hdfury_input_selection
    name: Select Input
  - entity: sensor.hdfury_current_input
    name: Current Input
  - entity: binary_sensor.hdfury_signal_detected
    name: Signal Detected
  - entity: sensor.hdfury_tx0_status
    name: Output Status
```

## Configuration Options

### Custom Input Names

By default, inputs are named "Input 0", "Input 1", etc. To customize these names, you need to modify the `INPUT_NAMES` constant in `custom_components/hdfury/const.py`:

```python
INPUT_NAMES = ["FireTV", "Xbox", "Nintendo", "HiFiBerry"]
```

After changing this, restart Home Assistant.

### Scan Interval

The default polling interval is 5 seconds. To change this, modify the `DEFAULT_SCAN_INTERVAL` constant in `custom_components/hdfury/const.py`:

```python
DEFAULT_SCAN_INTERVAL = 10  # seconds
```

## API Documentation

This integration uses the HDFury HTTP API. The main endpoints used are:

- `GET http://<device_ip>/ssi/infopage.ssi` - Get device status
- `GET http://<device_ip>/cmd?insel=<input>%20<output>` - Set input

For more details on the HDFury API, refer to the official HDFury Vertex² manual.

## Troubleshooting

### Connection Issues

1. Verify your HDFury device is accessible on the network
2. Try accessing `http://<device_ip>/ssi/infopage.ssi` in a web browser
3. Check that your device IP address hasn't changed (consider setting a static IP)
4. Ensure no firewall is blocking access between Home Assistant and the HDFury device

### Entity Not Updating

1. Check the Home Assistant logs for errors
2. Verify the device is responding to API calls
3. Try reloading the integration from Settings → Devices & Services

### Debug Logging

To enable debug logging, add the following to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.hdfury: debug
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [Report a bug](https://github.com/pkern90/hdfury-homeassistant/issues)
- [Request a feature](https://github.com/pkern90/hdfury-homeassistant/issues)
- [Home Assistant Community Forum](https://community.home-assistant.io/)

## Acknowledgments

- Based on the [Integration Blueprint](https://github.com/ludeeus/integration_blueprint)
- HDFury for their excellent devices and API documentation
