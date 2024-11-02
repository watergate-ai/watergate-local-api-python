from .water_meter import WaterMeter

VALVE_STATE_FIELD = "valveState"
WATER_FLOW_INDICATOR_FIELD = "waterFlowing"
MQTT_STATUS_FIELD = "mqttConnected"
WIFI_STATUS_FIELD = "wifiConnected"
POWER_SUPPLY_FIELD = "powerSupply"
FIRMWARE_VERSION_FIELD = "firmwareVersion"
UPTIME_FIELD = "uptime"
WATER_METER_FIELD = "waterMeter"

class DeviceState:
    """Represents the device state."""

    def __init__(
        self,
        valve_state: str,
        water_flow_indicator: bool,
        mqtt_status: bool,
        wifi_status: bool,
        power_supply: str,
        firmware_version: str,
        uptime: int,
        water_meter: WaterMeter,
    ) -> None:
        """Create an Device State object."""

        self.valve_state = valve_state
        self.water_flow_indicator = water_flow_indicator
        self.mqtt_status = mqtt_status
        self.wifi_status = wifi_status
        self.power_supply = power_supply
        self.firmware_version = firmware_version
        self.uptime = uptime
        self.water_meter = water_meter

    @classmethod
    def from_dict(cls, data: dict):
        """Create an Device State object from a dictionary."""
        return cls(
            valve_state=data.get(VALVE_STATE_FIELD),
            water_flow_indicator=data.get(WATER_FLOW_INDICATOR_FIELD),
            mqtt_status=data.get(MQTT_STATUS_FIELD),
            wifi_status=data.get(WIFI_STATUS_FIELD),
            power_supply=data.get(POWER_SUPPLY_FIELD),
            firmware_version=data.get(FIRMWARE_VERSION_FIELD),
            uptime=data.get(UPTIME_FIELD),
            water_meter=WaterMeter(**data.get(WATER_METER_FIELD)) if data.get(WATER_METER_FIELD) else None
        )