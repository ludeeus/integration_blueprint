# Notice

The component and platforms in this repository are not meant to be used by a
user, but as a "blueprint" that custom component developers can build
upon, to make more awesome stuff.

HAVE FUN! 😎

## Why?

This is simple, by having custom_components look (README + structure) the same
it is easier for developers to help each other and for users to start using them.

If you are a developer and you want to add things to this "blueprint" that you think more
developers will have use for, please open a PR to add it :)

## What?

This repository contains multiple files, here is a overview:

File | Purpose
-- | --
`.devcontainer.json` | Used for development/testing with Visual Studio Code.
`.github/ISSUE_TEMPLATE/feature_request.md` | Template for Feature Requests
`.github/ISSUE_TEMPLATE/issue.md` | Template for issues
`.vscode/tasks.json` | Tasks for the devcontainer.
`custom_components/integration_blueprint/translations/*` | [Translation files.](https://developers.home-assistant.io/docs/internationalization/custom_integration)
`custom_components/integration_blueprint/__init__.py` | The component file for the integration.
`custom_components/integration_blueprint/api.py` | This is a sample API client.
`custom_components/integration_blueprint/binary_sensor.py` | Binary sensor platform for the integration.
`custom_components/integration_blueprint/config_flow.py` | Config flow file, this adds the UI configuration possibilities.
`custom_components/integration_blueprint/const.py` | A file to hold shared variables/constants for the entire integration.
`custom_components/integration_blueprint/manifest.json` | A [manifest file](https://developers.home-assistant.io/docs/en/creating_integration_manifest.html) for Home Assistant.
`custom_components/integration_blueprint/sensor.py` | Sensor platform for the integration.
`custom_components/integration_blueprint/switch.py` | Switch sensor platform for the integration.
`CONTRIBUTING.md` | Guidelines on how to contribute.
`LICENSE` | The license file for the project.
`README.md` | The file you are reading now, should contain info about the integration, installation and configuration instructions.
`requirements.txt` | Python packages used for development/lint/testing this integration.

## How?

If you want to use all the potential and features of this blueprint template you
should use Visual Studio Code to develop in a container. In this container you
will have all the tools to ease your python development and a dedicated Home
Assistant core instance to run your integration.

