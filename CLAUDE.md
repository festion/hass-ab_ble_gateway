# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- Format: `black custom_components/`
- Lint: `flake8 custom_components/`
- Import sorting: `isort custom_components/`
- Test: `pytest tests/`
- Run single test: `pytest tests/test_file.py::test_function -v`

## Style Guidelines
- Follow Home Assistant custom component conventions
- Line length: 88 characters (black default)
- Imports: Use isort with sections (stdlib, third-party, first-party)
- Type hints: Required for function parameters and return values
- Error handling: Use try/except blocks with specific exceptions, log errors
- Naming: snake_case for variables/functions, PascalCase for classes
- String formatting: Use f-strings

## Development Notes
- This is a Home Assistant custom component for April Brother BLE Gateway V4
- Uses Home Assistant's ConfigFlow, Bluetooth, and MQTT components
- Follow changes to HomeAssistant core APIs as they evolve
- Documentation in docstrings and README.md