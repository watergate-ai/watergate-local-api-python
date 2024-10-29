import aiohttp
import pytest
from aioresponses import aioresponses
from watergate_local_api import WatergateLocalApiClient, WatergateApiException
from watergate_local_api.models import DeviceState, NetworkingData, TelemetryData, AutoShutOffReport

@pytest.fixture
def client():
    # Return an uninitialized instance of the client
    return WatergateLocalApiClient(base_url="http://testserver")

@pytest.mark.asyncio
async def test_get_device_state(client):
    await client.__aenter__()

    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic", payload={
            "valveState": "closed",
            "waterFlowing": False,
            "mqttConnected": True,
            "wifiConnected": True,
            "powerSupply": "external",
            "firmwareVersion": "2024.1.0",
            "waterMeter": {"volume": 567820, "duration": 3908},
            "uptime": 1024560
        })

        device_state = await client.async_get_device_state()
        assert device_state.valve_state == "closed"
        assert device_state.water_flow_indicator is False
        assert device_state.mqtt_status is True
        assert device_state.wifi_status is True
        assert device_state.power_supply == "external"
        assert device_state.firmware_version == "2024.1.0"
        assert device_state.uptime == 1024560
        assert device_state.water_meter.volume == 567820

    await client.__aexit__(None, None, None)

@pytest.mark.asyncio
async def test_get_networking(client):
    await client.__aenter__()

    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/networking", payload={
            "mqttConnected": True,
            "wifiConnected": True,
            "ip": "192.168.21.37",
            "gateway": "192.168.1.0",
            "subnet": "192.168.1.0/24",
            "ssid": "MyWiFi",
            "rssi": -45,
            "wifiUpTime": 1024560,
            "mqttUpTime": 1023450
        })

        networking_data = await client.async_get_networking()
        assert networking_data.ip == "192.168.21.37"
        assert networking_data.gateway == "192.168.1.0"
        assert networking_data.subnet == "192.168.1.0/24"
        assert networking_data.ssid == "MyWiFi"
        assert networking_data.rssi == -45

    await client.__aexit__(None, None, None)

@pytest.mark.asyncio
async def test_get_telemetry_data(client):
    await client.__aenter__()

    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/telemetry", payload={
            "flow": 6800,
            "pressure": 2320,
            "temperature": 23.5,
            "event": {"volume": 16000, "duration": 90},
            "errors": ["flow"]
        })

        telemetry_data = await client.async_get_telemetry_data()
        assert telemetry_data.flow == 6800
        assert telemetry_data.pressure == 2320
        assert telemetry_data.water_temperature == 23.5
        assert telemetry_data.ongoing_event.volume == 16000
        assert telemetry_data.ongoing_event.duration == 90
        assert "flow" in telemetry_data.errors

    await client.__aexit__(None, None, None)

@pytest.mark.asyncio
async def test_patch_auto_shut_off(client):
    await client.__aenter__()

    with aioresponses() as mock:
        mock.patch("http://testserver/api/sonic/auto-shut-off", status=204)

        result = await client.async_patch_auto_shut_off(enabled=True, duration=10, volume=5)
        assert result is True

    await client.__aexit__(None, None, None)

@pytest.mark.asyncio
async def test_get_auto_shut_off_report(client):
    await client.__aenter__()

    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/auto-shut-off/report", payload={
            "type": "VOLUME_THRESHOLD",
            "volume": 300,
            "duration": 60,
            "timestamp": 1623456789
        })

        report = await client.async_get_auto_shut_off_report()
        assert report.type == "VOLUME_THRESHOLD"
        assert report.volume == 300
        assert report.duration == 60
        assert report.timestamp == 1623456789

    await client.__aexit__(None, None, None)

@pytest.mark.asyncio
async def test_set_webhook_url(client):
    await client.__aenter__()

    with aioresponses() as mock:
        mock.patch("http://testserver/api/sonic/webhook", status=204)

        result = await client.async_set_webhook_url("http://webhook.url")
        assert result is True

    await client.__aexit__(None, None, None)

@pytest.mark.asyncio
async def test_retry_logic(client):
    await client.__aenter__()

    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic", status=500)

        with pytest.raises(WatergateApiException):
            await client.async_get_device_state()

    await client.__aexit__(None, None, None)

@pytest.mark.asyncio
async def test_custom_exception(client):
    await client.__aenter__()

    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic", exception=aiohttp.ClientError)

        with pytest.raises(WatergateApiException):
            await client.async_get_device_state()

    await client.__aexit__(None, None, None)

@pytest.mark.asyncio
async def test_api_rate_limit_handling(client):
    await client.__aenter__()

    # Simulate API rate limit response (HTTP 429)
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic", status=429)

        with pytest.raises(WatergateApiException):
            await client.async_get_device_state()

    await client.__aexit__(None, None, None)

@pytest.mark.asyncio
async def test_get_networking_with_unexpected_status_code(client):
    await client.__aenter__()

    # Simulate an unexpected status code (HTTP 403)
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/networking", status=403)

        with pytest.raises(WatergateApiException):
            await client.async_get_networking()

    await client.__aexit__(None, None, None)

@pytest.mark.asyncio
async def test_set_webhook_url_invalid_response(client):
    await client.__aenter__()

    # Simulate an invalid response when setting webhook (e.g., status 400)
    with aioresponses() as mock:
        mock.patch("http://testserver/api/sonic/webhook", status=400)

        with pytest.raises(WatergateApiException):
            await client.async_set_webhook_url("http://invalid-webhook.url")

    await client.__aexit__(None, None, None)

@pytest.mark.asyncio
async def test_auto_shut_off_report_with_missing_fields(client):
    await client.__aenter__()

    # Response with some fields missing
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/auto-shut-off/report", payload={"type": "VOLUME_THRESHOLD"})

        report = await client.async_get_auto_shut_off_report()
        assert report.type == "VOLUME_THRESHOLD"
        assert report.volume is None  # Missing fields should default to None

    await client.__aexit__(None, None, None)