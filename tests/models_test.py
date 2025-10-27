import pytest
from watergate_local_api.models import TelemetryData, DeviceState, DeviceStateV2
from watergate_local_api.models.water_meter import WaterMeter


def test_telemetry_data_should_be_able_build_without_ongoing_even():
    telemetry_data = TelemetryData.from_dict({"flow" : 12, "pressure" : 34, "temperature" : 56})
    assert telemetry_data.flow == 12
    assert telemetry_data.pressure == 34
    assert telemetry_data.water_temperature == 56
    assert telemetry_data.ongoing_event is None
    assert telemetry_data.errors is None
    
def test_device_state_should_be_able_to_build_when_there_is_no_water_meter():
    device_state = DeviceState.from_dict({"waterFlowing" : False, "mqttConnected" : False, "wifiConnected" : False, 
                                            "powerSupply" : "battery", "firmwareVersion" : "1.0.0", "uptime": 1234, "serialNumber": "123123"})
    assert device_state.water_flow_indicator == False
    assert device_state.mqtt_status == False
    assert device_state.wifi_status == False
    assert device_state.power_supply == "battery"
    assert device_state.firmware_version == "1.0.0"
    assert device_state.uptime == 1234
    assert device_state.water_meter is None
    assert device_state.serial_number == "123123"

def test_water_meter_from_dict():
    """Test WaterMeter.from_dict deserialization."""
    water_meter = WaterMeter.from_dict({"volume": 567820, "duration": 3908})
    assert water_meter.volume == 567820
    assert water_meter.duration == 3908

def test_water_meter_from_dict_missing_fields():
    """Test WaterMeter.from_dict with missing fields."""
    water_meter = WaterMeter.from_dict({})
    assert water_meter.volume is None
    assert water_meter.duration is None

def test_device_state_v2_with_complete_data():
    """Test DeviceStateV2 with complete positive and negative water meter data."""
    device_state = DeviceStateV2.from_dict({
        "valveState": "open",
        "waterFlowing": True,
        "mqttConnected": True,
        "wifiConnected": True,
        "powerSupply": "external",
        "firmwareVersion": "2024.2.1",
        "uptime": 5000,
        "serialNumber": "abc123",
        "waterMeter": {
            "positive": {"volume": 100000, "duration": 500},
            "negative": {"volume": 1000, "duration": 10}
        }
    })
    assert device_state.valve_state == "open"
    assert device_state.water_flow_indicator == True
    assert device_state.mqtt_status == True
    assert device_state.wifi_status == True
    assert device_state.power_supply == "external"
    assert device_state.firmware_version == "2024.2.1"
    assert device_state.uptime == 5000
    assert device_state.serial_number == "abc123"
    assert device_state.water_meter_positive.volume == 100000
    assert device_state.water_meter_positive.duration == 500
    assert device_state.water_meter_negative.volume == 1000
    assert device_state.water_meter_negative.duration == 10

def test_device_state_v2_without_water_meter():
    """Test DeviceStateV2 when water meter data is missing."""
    device_state = DeviceStateV2.from_dict({
        "valveState": "closed",
        "waterFlowing": False,
        "mqttConnected": False,
        "wifiConnected": True,
        "powerSupply": "battery",
        "firmwareVersion": "2024.1.0",
        "uptime": 1234,
        "serialNumber": "xyz789"
    })
    assert device_state.valve_state == "closed"
    assert device_state.water_meter_positive is None
    assert device_state.water_meter_negative is None

def test_device_state_v2_with_partial_water_meter():
    """Test DeviceStateV2 with only positive water meter."""
    device_state = DeviceStateV2.from_dict({
        "valveState": "opening",
        "waterFlowing": True,
        "mqttConnected": True,
        "wifiConnected": True,
        "powerSupply": "external+battery",
        "firmwareVersion": "2024.2.0",
        "uptime": 2500,
        "serialNumber": "def456",
        "waterMeter": {
            "positive": {"volume": 50000, "duration": 250}
        }
    })
    assert device_state.valve_state == "opening"
    assert device_state.water_meter_positive.volume == 50000
    assert device_state.water_meter_positive.duration == 250
    assert device_state.water_meter_negative is None
    