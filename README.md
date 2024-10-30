
# Watergate Local API Client

A robust Python client for interacting with the **Sonic Device Local API**. This client provides easy access to manage device settings, monitor telemetry data, and handle event webhooks from the device.

## Overview

The Watergate Local API Client simplifies interaction with the Sonic Device's local API, enabling developers to:
- Retrieve and update device state
- Access telemetry and networking data
- Configure auto shut-off settings and view reports
- Manage webhook configuration and receive real-time device events

## Features

- **Device State Management**: Access comprehensive device state details, including valve state, power supply, firmware version, and uptime.
- **Telemetry Access**: Retrieve telemetry data such as flow rate, pressure, and temperature.
- **Networking and Power Management**: Configure networking settings and monitor power supply status.
- **Event Webhook Support**: Handle and parse webhook events including auto-shut-off, telemetry, valve state changes, power supply changes, and WiFi updates.

## Installation

To install the Watergate Local API Client, clone the repository and install the package using `pip`:

```bash
git clone https://github.com/watergate-ai/watergate-local-api-python.git
cd watergate-local-api-python
pip install .
```

## Usage

### Basic Usage Example

This example demonstrates how to retrieve the device state and access telemetry data using the client.

```python
from watergate_local_api import WatergateLocalApiClient

async def main():
    async with WatergateLocalApiClient(base_url="http://testserver") as client:
        # Get device state
        device_state = await client.async_get_device_state()
        print("Valve State:", device_state.valve_state)

        # Access telemetry data
        telemetry_data = await client.async_get_telemetry_data()
        print("Flow Rate:", telemetry_data.flow)
```

### Webhook Event Parsing

You can parse incoming webhook events to handle device notifications, such as telemetry updates or auto-shut-off reports.

```python
from watergate_local_api.models import WebhookEvent

webhook_payload = {
    "type": "telemetry",
    "data": {
        "flow": 6800,
        "pressure": 2320,
        "temperature": 23.5,
        "event": {"volume": 16000, "duration": 90},
        "errors": ["flow"]
    }
}

# Parse webhook event
event = WebhookEvent.parse_webhook_event(webhook_payload)
print("Parsed Event:", event)
```

## Development

To contribute to this project, follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Make your changes and add tests where appropriate.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature/YourFeature`).
6. Open a Pull Request.

We welcome all contributions that can improve the project! If you have any ideas or suggestions, feel free to open an issue or submit a pull request.

### Running Tests

To run tests, use `pytest`:

```bash
pip install -r requirements-dev.txt
pytest
```

Make sure to add tests for any new features or functionality you contribute.

## Contributing

We welcome contributions from the community to help improve the Watergate Local API Client. If you’re interested in contributing, please feel free to reach out by opening an issue or submitting a pull request.

### Reporting Issues

If you find a bug or have a feature request, please create an issue using the template provided in the [Issues section](https://github.com/hero-laboratories/watergate-local-api-python/issues). This helps us track and address your feedback effectively.

## License

This project is licensed under a GPL 3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Special thanks to all contributors and the community for supporting and improving this project!
