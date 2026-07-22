import aiohttp
import pytest
from aioresponses import aioresponses
import pytest_asyncio
from watergate_local_api import WatergateLocalApiClient, WatergateApiException

@pytest_asyncio.fixture
async def client():
    # Create and initialize the client within an async context
    client = WatergateLocalApiClient(base_url="http://testserver")
    yield client
    # Ensure proper cleanup after each test
    await client.async_close()

@pytest.mark.asyncio
async def test_get_device_state(client):
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/", payload={
            "valveState": "closed",
            "waterFlowing": False,
            "mqttConnected": True,
            "wifiConnected": True,
            "powerSupply": "external",
            "firmwareVersion": "2024.1.0",
            "waterMeter": {"volume": 567820, "duration": 3908},
            "uptime": 1024560,
            "serialNumber": "123123"
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

@pytest.mark.asyncio
async def test_get_networking(client):
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

@pytest.mark.asyncio
async def test_get_telemetry_data(client):
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

@pytest.mark.asyncio
async def test_patch_auto_shut_off(client):
    with aioresponses() as mock:
        mock.patch("http://testserver/api/sonic/auto-shut-off", status=204)

        result = await client.async_patch_auto_shut_off(enabled=True, duration=10, volume=5)
        assert result is True

@pytest.mark.asyncio
async def test_get_auto_shut_off(client):
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/auto-shut-off", payload={
            "volumeThreshold": 300,
            "durationThreshold": 60,
        })

        report = await client.async_get_auto_shut_off()
        assert report.volume_threshold == 300
        assert report.duration_threshold == 60

@pytest.mark.asyncio
async def test_get_auto_shut_off_report(client):
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

@pytest.mark.asyncio
async def test_set_webhook_url(client):
    with aioresponses() as mock:
        mock.put("http://testserver/api/sonic/webhook", status=204)

        result = await client.async_set_webhook_url("http://webhook.url")
        assert result is True

@pytest.mark.asyncio
async def test_set_valve(client):
    with aioresponses() as mock:
        mock.put("http://testserver/api/sonic/valve", status=204)

        result = await client.async_set_valve_state("open")
        assert result is True

@pytest.mark.asyncio
async def test_retry_logic(client):
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic", status=500)

        with pytest.raises(WatergateApiException):
            await client.async_get_device_state()

@pytest.mark.asyncio
async def test_custom_exception(client):
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic", exception=aiohttp.ClientError)

        with pytest.raises(WatergateApiException):
            await client.async_get_device_state()

@pytest.mark.asyncio
async def test_api_rate_limit_handling(client):
    # Simulate API rate limit response (HTTP 429)
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic", status=429)

        with pytest.raises(WatergateApiException):
            await client.async_get_device_state()

@pytest.mark.asyncio
async def test_get_networking_with_unexpected_status_code(client):
    # Simulate an unexpected status code (HTTP 403)
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/networking", status=403)

        with pytest.raises(WatergateApiException):
            await client.async_get_networking()

@pytest.mark.asyncio
async def test_set_webhook_url_invalid_response(client):
    # Simulate an invalid response when setting webhook (e.g., status 400)
    with aioresponses() as mock:
        mock.patch("http://testserver/api/sonic/webhook", status=400)

        with pytest.raises(WatergateApiException):
            await client.async_set_webhook_url("http://invalid-webhook.url")

@pytest.mark.asyncio
async def test_auto_shut_off_report_with_missing_fields(client):
    # Response with some fields missing
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/auto-shut-off/report", payload={"type": "VOLUME_THRESHOLD"})

        report = await client.async_get_auto_shut_off_report()
        assert report.type == "VOLUME_THRESHOLD"
        assert report.volume is None  # Missing fields should default to None


@pytest.mark.asyncio
async def test_get_auto_shut_off_report_no_content_returns_none(client):
    # 204 No Content -> None (must stay true after consolidating onto _get).
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/auto-shut-off/report", status=204)

        report = await client.async_get_auto_shut_off_report()
        assert report is None

@pytest.mark.asyncio
async def test_get_device_state_v2(client):
    """Test fetching device state V2 with positive and negative water meters."""
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/", payload={
            "valveState": "open",
            "waterFlowing": True,
            "mqttConnected": True,
            "wifiConnected": True,
            "powerSupply": "external+battery",
            "firmwareVersion": "2024.2.1",
            "uptime": 5000,
            "serialNumber": "abc123",
            "waterMeter": {
                "positive": {"volume": 100000, "duration": 500},
                "negative": {"volume": 1000, "duration": 10}
            }
        })

        device_state = await client.async_get_device_state_v2()
        assert device_state.valve_state == "open"
        assert device_state.water_flow_indicator is True
        assert device_state.mqtt_status is True
        assert device_state.wifi_status is True
        assert device_state.power_supply == "external+battery"
        assert device_state.firmware_version == "2024.2.1"
        assert device_state.uptime == 5000
        assert device_state.serial_number == "abc123"
        assert device_state.water_meter_positive.volume == 100000
        assert device_state.water_meter_positive.duration == 500
        assert device_state.water_meter_negative.volume == 1000
        assert device_state.water_meter_negative.duration == 10

@pytest.mark.asyncio
async def test_get_device_state_v2_without_water_meter(client):
    """Test device state V2 with missing water meter data."""
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/", payload={
            "valveState": "closed",
            "waterFlowing": False,
            "mqttConnected": False,
            "wifiConnected": True,
            "powerSupply": "battery",
            "firmwareVersion": "2024.1.0",
            "uptime": 1234,
            "serialNumber": "xyz789"
        })

        device_state = await client.async_get_device_state_v2()
        assert device_state.valve_state == "closed"
        assert device_state.water_meter_positive is None
        assert device_state.water_meter_negative is None

@pytest.mark.asyncio
async def test_get_device_state_v2_network_error(client):
    """Test device state V2 network error handling."""
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/", status=500)

        with pytest.raises(WatergateApiException):
            await client.async_get_device_state_v2()

@pytest.mark.asyncio
async def test_injected_session():
    """Test that an injected aiohttp session is used and not closed by the client."""
    # Create a session to inject
    injected_session = aiohttp.ClientSession()
    
    try:
        # Create client with injected session
        client = WatergateLocalApiClient(base_url="http://testserver", session=injected_session)
        
        with aioresponses() as mock:
            mock.get("http://testserver/api/sonic/", payload={
                "valveState": "open",
                "waterFlowing": True,
                "mqttConnected": True,
                "wifiConnected": True,
                "powerSupply": "external",
                "firmwareVersion": "2024.1.0",
                "waterMeter": {"volume": 100, "duration": 10},
                "uptime": 1000,
                "serialNumber": "test123"
            })
            
            device_state = await client.async_get_device_state()
            assert device_state.valve_state == "open"
        
        # Close the client - should NOT close the injected session
        await client.async_close()
        
        # Verify the injected session is still open
        assert not injected_session.closed
    finally:
        # Clean up the injected session
        await injected_session.close()

@pytest.mark.asyncio
async def test_owned_session_is_closed():
    """Test that a client-owned session is properly closed."""
    client = WatergateLocalApiClient(base_url="http://testserver")
    
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/", payload={
            "valveState": "closed",
            "waterFlowing": False,
            "mqttConnected": True,
            "wifiConnected": True,
            "powerSupply": "battery",
            "firmwareVersion": "2024.1.0",
            "waterMeter": {"volume": 200, "duration": 20},
            "uptime": 2000,
            "serialNumber": "test456"
        })
        
        device_state = await client.async_get_device_state()
        assert device_state.valve_state == "closed"
    
    # Get reference to the session before closing
    session = client._session
    assert session is not None
    assert not session.closed
    
    # Close the client - should close the owned session
    await client.async_close()
    
    # Verify the owned session is closed
    assert session.closed

@pytest.mark.asyncio
async def test_context_manager_with_injected_session():
    """Test context manager doesn't close injected session."""
    injected_session = aiohttp.ClientSession()
    
    try:
        async with WatergateLocalApiClient(base_url="http://testserver", session=injected_session) as client:
            with aioresponses() as mock:
                mock.get("http://testserver/api/sonic/", payload={
                    "valveState": "opening",
                    "waterFlowing": False,
                    "mqttConnected": True,
                    "wifiConnected": True,
                    "powerSupply": "external",
                    "firmwareVersion": "2024.1.0",
                    "waterMeter": {"volume": 300, "duration": 30},
                    "uptime": 3000,
                    "serialNumber": "test789"
                })
                
                device_state = await client.async_get_device_state()
                assert device_state.valve_state == "opening"
        
        # After exiting context, injected session should still be open
        assert not injected_session.closed
    finally:
        await injected_session.close()

@pytest.mark.asyncio
async def test_context_manager_with_owned_session():
    """Test context manager closes owned session."""
    session_ref = None
    
    async with WatergateLocalApiClient(base_url="http://testserver") as client:
        with aioresponses() as mock:
            mock.get("http://testserver/api/sonic/", payload={
                "valveState": "closing",
                "waterFlowing": True,
                "mqttConnected": True,
                "wifiConnected": True,
                "powerSupply": "battery",
                "firmwareVersion": "2024.1.0",
                "waterMeter": {"volume": 400, "duration": 40},
                "uptime": 4000,
                "serialNumber": "test000"
            })
            
            device_state = await client.async_get_device_state()
            assert device_state.valve_state == "closing"
            session_ref = client._session
    
    # After exiting context, owned session should be closed
    assert session_ref is not None
    assert session_ref.closed


# --- New endpoints: full 2025.2.0 firmware coverage ---

@pytest.mark.asyncio
async def test_get_valve_state(client):
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/valve", payload={"state": "open"})

        valve = await client.async_get_valve_state()
        assert valve.state == "open"


@pytest.mark.asyncio
async def test_get_valve_state_unexpected_status(client):
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/valve", status=500)

        with pytest.raises(WatergateApiException):
            await client.async_get_valve_state()


@pytest.mark.asyncio
async def test_get_power_supply(client):
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/power", payload={
            "battery": True,
            "external": False,
            "batteriesVoltage": 6800,
        })

        power = await client.async_get_power_supply_data()
        assert power.battery is True
        assert power.external is False
        assert power.batteries_voltage == 6800


@pytest.mark.asyncio
async def test_get_webhook_url(client):
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/webhook", payload={"url": "http://hook.url"})

        url = await client.async_get_webhook_url()
        assert url == "http://hook.url"


@pytest.mark.asyncio
async def test_get_webhook_url_not_set_returns_none(client):
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/webhook", status=204)

        url = await client.async_get_webhook_url()
        assert url is None


@pytest.mark.asyncio
async def test_delete_webhook_url(client):
    with aioresponses() as mock:
        mock.delete("http://testserver/api/sonic/webhook", status=204)

        result = await client.async_delete_webhook_url()
        assert result is True


@pytest.mark.asyncio
async def test_delete_webhook_url_invalid_response(client):
    with aioresponses() as mock:
        mock.delete("http://testserver/api/sonic/webhook", status=400)

        with pytest.raises(WatergateApiException):
            await client.async_delete_webhook_url()


@pytest.mark.asyncio
async def test_send_command_reboot(client):
    with aioresponses() as mock:
        mock.put("http://testserver/api/sonic/command", status=204)

        result = await client.async_send_command("reboot")
        assert result is True


@pytest.mark.asyncio
async def test_reboot(client):
    with aioresponses() as mock:
        mock.put("http://testserver/api/sonic/command", status=204)

        result = await client.async_reboot()
        assert result is True


@pytest.mark.asyncio
async def test_change_network(client):
    with aioresponses() as mock:
        mock.put("http://testserver/api/sonic/networking", status=204)

        result = await client.async_change_network("MyWiFi", "secret")
        assert result is True


def _put_call_count(mock):
    return sum(len(v) for k, v in mock.requests.items() if k[0] == "PUT")


def _connect_error():
    # A demonstrably pre-dispatch failure: the request was never sent.
    from aiohttp.client_reqrep import ConnectionKey
    key = ConnectionKey("testserver", 80, False, None, None, None, None)
    return aiohttp.ClientConnectorError(key, OSError(61, "Connection refused"))


@pytest.mark.asyncio
async def test_reboot_lost_response_is_indeterminate_and_not_retried(client):
    from watergate_local_api import WatergateIndeterminateError
    with aioresponses() as mock:
        # Response lost after dispatch (timeout): the device may have rebooted -> ambiguous.
        mock.put("http://testserver/api/sonic/command", exception=TimeoutError(), repeat=True)

        with pytest.raises(WatergateIndeterminateError):
            await client.async_reboot()

        assert _put_call_count(mock) <= 1  # non-idempotent: must not be resent


@pytest.mark.asyncio
async def test_change_network_lost_response_is_indeterminate_and_not_retried(client):
    from watergate_local_api import WatergateIndeterminateError
    with aioresponses() as mock:
        mock.put("http://testserver/api/sonic/networking", exception=TimeoutError(), repeat=True)

        with pytest.raises(WatergateIndeterminateError):
            await client.async_change_network("MyWiFi", "secret")

        assert _put_call_count(mock) <= 1


@pytest.mark.asyncio
async def test_reboot_rejected_4xx_is_definite_failure_not_retried(client):
    from watergate_local_api import WatergateApiException, WatergateIndeterminateError
    with aioresponses() as mock:
        # 4xx = the device rejected the request; it was not applied -> definite failure.
        mock.put("http://testserver/api/sonic/command", status=400, repeat=True)

        with pytest.raises(WatergateApiException) as exc:
            await client.async_reboot()

        assert not isinstance(exc.value, WatergateIndeterminateError)
        assert _put_call_count(mock) <= 1


@pytest.mark.asyncio
async def test_reboot_5xx_is_indeterminate_not_retried(client):
    from watergate_local_api import WatergateIndeterminateError
    with aioresponses() as mock:
        # 5xx may occur after the device applied the change -> ambiguous, not a definite failure.
        mock.put("http://testserver/api/sonic/command", status=500, repeat=True)

        with pytest.raises(WatergateIndeterminateError):
            await client.async_reboot()

        assert _put_call_count(mock) <= 1


@pytest.mark.asyncio
async def test_reboot_pre_dispatch_connect_error_is_retried(client):
    from watergate_local_api import WatergateApiException, WatergateIndeterminateError
    with aioresponses() as mock:
        # Could not connect: the request was never sent -> safe to retry, and a definite failure.
        mock.put("http://testserver/api/sonic/command", exception=_connect_error(), repeat=True)

        with pytest.raises(WatergateApiException) as exc:
            await client.async_reboot()

        assert not isinstance(exc.value, WatergateIndeterminateError)  # never sent -> not indeterminate


@pytest.mark.asyncio
async def test_reboot_connect_timeout_is_retried(client):
    from watergate_local_api import WatergateApiException, WatergateIndeterminateError
    with aioresponses() as mock:
        # Connection establishment timed out: the request was never sent -> safe to retry.
        mock.put("http://testserver/api/sonic/command",
                 exception=aiohttp.ConnectionTimeoutError("connect timed out"), repeat=True)

        with pytest.raises(WatergateApiException) as exc:
            await client.async_reboot()

        assert not isinstance(exc.value, WatergateIndeterminateError)  # never established -> not indeterminate


@pytest.mark.asyncio
async def test_get_buzzer_status(client):
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/buzzer", payload={"playing": True, "sound": "beep"})

        status = await client.async_get_buzzer_status()
        assert status.playing is True
        assert status.sound == "beep"


@pytest.mark.asyncio
async def test_get_buzzer_sounds(client):
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/buzzer/sounds", payload={
            "sounds": ["beep", "christmas_1", "christmas_2"]
        })

        result = await client.async_get_buzzer_sounds()
        assert result.sounds == ["beep", "christmas_1", "christmas_2"]


@pytest.mark.asyncio
async def test_control_buzzer_start(client):
    with aioresponses() as mock:
        mock.put("http://testserver/api/sonic/buzzer", status=204)

        result = await client.async_control_buzzer("start", name="beep", interval=1000, times=3)
        assert result is True


@pytest.mark.asyncio
async def test_control_buzzer_stop(client):
    with aioresponses() as mock:
        mock.put("http://testserver/api/sonic/buzzer", status=204)

        result = await client.async_control_buzzer("stop")
        assert result is True


@pytest.mark.asyncio
async def test_get_device_state_v3(client):
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/", payload={
            "valveState": "closed",
            "waterFlowing": False,
            "mqttConnected": True,
            "wifiConnected": True,
            "powerSupply": "external",
            "firmwareVersion": "2025.2.0",
            "uptime": 1000,
            "serialNumber": "xyz",
            "waterMeter": {
                "positive": {"volume": 10, "duration": 1},
                "negative": {"volume": 0, "duration": 0},
            },
            "buzzerPlaying": False,
        })

        device_state = await client.async_get_device_state_v3()
        assert device_state.buzzer_playing is False
        assert device_state.water_meter_positive.volume == 10
        assert device_state.serial_number == "xyz"


@pytest.mark.asyncio
async def test_update_auto_shut_off(client):
    with aioresponses() as mock:
        mock.put("http://testserver/api/sonic/auto-shut-off", status=204)

        result = await client.async_update_auto_shut_off(enabled=True, duration=10, volume=5)
        assert result is True


@pytest.mark.asyncio
async def test_update_auto_shut_off_partial(client):
    with aioresponses() as mock:
        mock.put("http://testserver/api/sonic/auto-shut-off", status=204)

        result = await client.async_update_auto_shut_off(volume=100)
        assert result is True


@pytest.mark.asyncio
async def test_update_auto_shut_off_invalid_response(client):
    with aioresponses() as mock:
        mock.put("http://testserver/api/sonic/auto-shut-off", status=400)

        with pytest.raises(WatergateApiException):
            await client.async_update_auto_shut_off(enabled=False)


@pytest.mark.asyncio
async def test_update_auto_shut_off_requires_at_least_one_field(client):
    # Per the AutoShutOffChange schema (minProperties: 1) an empty update is invalid;
    # fail fast instead of PUTting an empty body.
    with pytest.raises(ValueError):
        await client.async_update_auto_shut_off()


@pytest.mark.asyncio
async def test_put_does_not_log_request_body(client, caplog):
    import logging
    # The request body is never logged - it may carry secrets (e.g. Wi-Fi password).
    with aioresponses() as mock:
        mock.put("http://testserver/api/sonic/networking", status=204)
        with caplog.at_level(logging.DEBUG, logger="watergate_local_api.watergate_api"):
            await client.async_change_network("MyWiFi", "sup3r-secret-pw")

    assert "sup3r-secret-pw" not in caplog.text   # password never logged
    assert "MyWiFi" not in caplog.text            # body (even non-secret fields) never logged
    assert "/api/sonic/networking" in caplog.text  # url metadata still logged


@pytest.mark.asyncio
async def test_put_does_not_log_request_body_on_failure(client, caplog):
    import logging
    with aioresponses() as mock:
        mock.put("http://testserver/api/sonic/networking", status=400)
        with caplog.at_level(logging.DEBUG, logger="watergate_local_api.watergate_api"):
            with pytest.raises(WatergateApiException):
                await client.async_change_network("MyWiFi", "sup3r-secret-pw")

    assert "sup3r-secret-pw" not in caplog.text   # not leaked via the error log either
    assert "MyWiFi" not in caplog.text