import pytest
from watergate_local_api.models import TelemetryData, DeviceState


def test_telemetry_data_should_be_able_build_without_ongoing_even():
    telemetry_data = TelemetryData.from_dict({"flow" : 12, "pressure" : 34, "temperature" : 56})
    assert telemetry_data.flow == 12
    assert telemetry_data.pressure == 34
    assert telemetry_data.water_temperature == 56
    assert telemetry_data.ongoing_event is None
    assert telemetry_data.errors is None
    
def test_device_state_should_be_able_to_build_when_there_is_no_water_meter():
    device_state = DeviceState.from_dict({"waterFlowing" : False, "mqttConnected" : False, "wifiConnected" : False, 
                                            "powerSupply" : "battery", "firmwareVersion" : "1.0.0", "uptime": 1234})
    assert device_state.water_flow_indicator == False
    assert device_state.mqtt_status == False
    assert device_state.wifi_status == False
    assert device_state.power_supply == "battery"
    assert device_state.firmware_version == "1.0.0"
    assert device_state.uptime == 1234
    assert device_state.water_meter is None
    