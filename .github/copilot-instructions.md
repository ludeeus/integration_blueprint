# Copilot instructions

## What this repository is

This repository contains a Home Assistant custom integration. It is based on the
[`ludeeus/integration_blueprint`](https://github.com/ludeeus/integration_blueprint)
template, where `integration_blueprint` / `Integration Blueprint` is the placeholder
integration domain and name.

How to treat the placeholder depends on which repository you are working in:

- **In the blueprint template itself** (the domain is `integration_blueprint` on
  purpose): keep the placeholder names, keep the code generic and minimal, and avoid
  anything specific to one product or API — this code is copied by other developers
  as a starting point. The API client intentionally targets
  `jsonplaceholder.typicode.com` as a stand-in; keep it a simple example.
- **In a repository bootstrapped from the template**: the placeholder should be
  renamed consistently everywhere — the `custom_components/<domain>/` directory name,
  `domain` in `manifest.json`, `DOMAIN` in `const.py`, class-name prefixes, and
  `translations/`. If you find leftover `integration_blueprint` references, that is
  an incomplete rename, not a convention to follow. The sample API client is expected
  to be replaced with a real one.

## Layout

All integration code lives in a single package under `custom_components/<domain>/`:

| File | Role |
| -- | -- |
| `__init__.py` | Config entry setup/unload/reload; defines the `PLATFORMS` list |
| `api.py` | Async API client and its exception hierarchy (base error, communication error, authentication error) |
| `coordinator.py` | `DataUpdateCoordinator` subclass that polls the API client |
| `data.py` | Runtime-data dataclass and the typed `ConfigEntry` alias |
| `entity.py` | Base `CoordinatorEntity` with shared device info and attribution |
| `config_flow.py` | UI config flow (credential validation against the API client) |
| `sensor.py`, `binary_sensor.py`, `switch.py` | Entity platforms |
| `const.py` | `DOMAIN`, `LOGGER`, and other constants |
| `manifest.json` | Integration manifest |
| `translations/en.json` | UI strings for the config flow |

## Architecture and conventions

- Data flows one way: the API client (`api.py`) is polled by the single coordinator
  (`coordinator.py`), and all entities read from `coordinator.data`.
- The integration is set up exclusively via config flow (UI). Do not add YAML
  configuration support.
- Everything an entry needs at runtime (client, coordinator, integration) is stored
  on `entry.runtime_data` using the dataclass in `data.py`, typed through the
  `type ...ConfigEntry = ConfigEntry[...]` alias defined there. Use that alias in
  signatures instead of a bare `ConfigEntry`.
- In the coordinator, map API authentication errors to `ConfigEntryAuthFailed` and
  other API errors to `UpdateFailed`. Raise only the exception types defined in
  `api.py` from the client.
- Entities inherit from the base class in `entity.py` and are declared through
  `EntityDescription` tuples in each platform module. A new platform means a new
  module plus an entry in `PLATFORMS` in `__init__.py`.
- Every module starts with `from __future__ import annotations`; imports used only
  for typing go inside an `if TYPE_CHECKING:` block. All modules, classes, and
  functions have docstrings — ruff enforces this.
- Follow the patterns documented at https://developers.home-assistant.io/ for
  anything not covered here.

## Developer workflow

- `scripts/setup` — install the development requirements from `requirements.txt`
  (also run automatically in the devcontainer).
- `scripts/develop` — start a local Home Assistant instance with
  `custom_components/` on `PYTHONPATH` and its configuration in `config/`.
- `scripts/lint` — run `ruff format` and `ruff check --fix`.
- The Python and Home Assistant versions are pinned in `requirements.txt` and
  `.devcontainer.json`; do not assume others.

## Validation

- Run `scripts/lint` before committing. Linting is strict: ruff runs with
  `select = ["ALL"]` (see `.ruff.toml`); prefer fixing findings over adding
  `noqa` comments.
- CI (`.github/workflows/`) must stay green: `lint.yml` runs `ruff check` and
  `ruff format --check`; `validate.yml` runs hassfest and HACS validation, so
  `manifest.json` and `hacs.json` must remain valid.
- Keep `translations/en.json` in sync when config-flow steps, fields, or errors
  change.
- There is no unit test suite; verify changes by running the integration with
  `scripts/develop`. Repositories bootstrapped from the template are encouraged to
  add tests with `pytest-homeassistant-custom-component`.
