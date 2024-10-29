from typing import Optional, List, Dict, Union

# Constants for field names
VALVE_STATE_FIELD = "state"
SUPPLY_FIELD = "supply"
IP_FIELD = "ip"
GATEWAY_FIELD = "gateway"
SUBNET_FIELD = "subnet"
SSID_FIELD = "ssid"
RSSI_FIELD = "rssi"
TYPE_FIELD = "type"
VOLUME_FIELD = "volume"
DURATION_FIELD = "duration"
TIMESTAMP_FIELD = "timestamp"
FLOW_FIELD = "flow"
PRESSURE_FIELD = "pressure"
TEMPERATURE_FIELD = "temperature"
EVENT_FIELD = "event"
ERRORS_FIELD = "errors"


class AutoShutOffReportData:
    """Represents data for the auto-shut-off report webhook event."""
    
    def __init__(self, event_type: str, volume: int, duration: int, timestamp: int):
        """
        Initialize the AutoShutOffReportData object.
        
        :param event_type: Type of the auto-shut-off event ("VOLUME_THRESHOLD" or "DURATION_THRESHOLD").
        :param volume: Volume of water in liters when the event occurred.
        :param duration: Duration in minutes when the event occurred.
        :param timestamp: Timestamp in milliseconds of the event occurrence.
        """
        self.type = event_type
        self.volume = volume
        self.duration = duration
        self.timestamp = timestamp

    @classmethod
    def from_dict(cls, data: dict):
        """Create an AutoShutOffReportData object from a dictionary."""
        return cls(
            event_type=data.get(TYPE_FIELD),
            volume=data.get(VOLUME_FIELD),
            duration=data.get(DURATION_FIELD),
            timestamp=data.get(TIMESTAMP_FIELD)
        )


class TelemetryEventData:
    """Represents data for the telemetry webhook event."""
    
    def __init__(
        self,
        flow: Optional[int] = None,
        pressure: Optional[int] = None,
        temperature: Optional[float] = None,
        event: Optional[Dict[str, int]] = None,
        errors: Optional[List[str]] = None,
    ):
        """
        Initialize the TelemetryEventData object.
        
        :param flow: Flow rate in ml/min.
        :param pressure: Pressure in mbar.
        :param temperature: Temperature in °C.
        :param event: Event-specific data containing volume and duration.
        :param errors: List of errors, if any (e.g., "flow", "pressure", "temperature").
        """
        self.flow = flow
        self.pressure = pressure
        self.temperature = temperature
        self.event = event
        self.errors = errors

    @classmethod
    def from_dict(cls, data: dict):
        """Create a TelemetryEventData object from a dictionary."""
        return cls(
            flow=data.get(FLOW_FIELD),
            pressure=data.get(PRESSURE_FIELD),
            temperature=data.get(TEMPERATURE_FIELD),
            event=data.get(EVENT_FIELD),
            errors=data.get(ERRORS_FIELD)
        )


class ValveEventData:
    """Represents data for the valve state change webhook event."""
    
    def __init__(self, state: str):
        """
        Initialize the ValveEventData object.
        
        :param state: State of the valve ("open", "closed", "opening", or "closing").
        """
        self.state = state

    @classmethod
    def from_dict(cls, data: dict):
        """Create a ValveEventData object from a dictionary."""
        return cls(
            state=data.get(VALVE_STATE_FIELD)
        )


class PowerSupplyChangedEventData:
    """Represents data for the power supply change webhook event."""
    
    def __init__(self, supply: str):
        """
        Initialize the PowerSupplyChangedEventData object.
        
        :param supply: Type of power supply ("battery", "external", or "external+battery").
        """
        self.supply = supply

    @classmethod
    def from_dict(cls, data: dict):
        """Create a PowerSupplyChangedEventData object from a dictionary."""
        return cls(
            supply=data.get(SUPPLY_FIELD)
        )


class WifiChangedEventData:
    """Represents data for the WiFi configuration change webhook event."""
    
    def __init__(self, ip: str, gateway: str, subnet: str, ssid: str, rssi: int):
        """
        Initialize the WifiChangedEventData object.
        
        :param ip: IP address of the device.
        :param gateway: Gateway IP address.
        :param subnet: Subnet mask.
        :param ssid: SSID of the connected WiFi network.
        :param rssi: Received Signal Strength Indicator (RSSI) in dBm.
        """
        self.ip = ip
        self.gateway = gateway
        self.subnet = subnet
        self.ssid = ssid
        self.rssi = rssi

    @classmethod
    def from_dict(cls, data: dict):
        """Create a WifiChangedEventData object from a dictionary."""
        return cls(
            ip=data.get(IP_FIELD),
            gateway=data.get(GATEWAY_FIELD),
            subnet=data.get(SUBNET_FIELD),
            ssid=data.get(SSID_FIELD),
            rssi=data.get(RSSI_FIELD)
        )


class OnlineEvent:
    """Represents an online status webhook event with no specific data."""
    
    def __init__(self):
        """
        Initialize the OnlineEvent object.
        
        This event indicates that the device has come online.
        """
        self.type = "online"
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create an OnlineEvent object from a dictionary."""
        return cls()


class WebhookEvent:
    """Base class for all webhook events."""
    
    def __init__(self, event_type: str, data: dict):
        """
        Initialize the WebhookEvent object.
        
        :param event_type: Type of the webhook event.
        :param data: Data payload associated with the event.
        """
        self.type = event_type
        self.data = data

    @classmethod
    def from_dict(cls, data: dict):
        """Create a base WebhookEvent object from a dictionary."""
        return cls(
            event_type=data.get("type"),
            data=data.get("data", {})
        )
    
    @classmethod
    def parse_webhook_event(cls, data: dict) -> Union[
        AutoShutOffReportData, TelemetryEventData, ValveEventData, 
        PowerSupplyChangedEventData, WifiChangedEventData, OnlineEvent
    ]:
        """
        Parse a raw webhook event dictionary and return the appropriate event object.

        :param data: Dictionary containing the raw webhook event data.
        :return: An instance of the appropriate event class.
        :raises ValueError: If the event type is unknown.
        """
        event_type = data.get("type")
        event_data = data.get("data", {})
        
        if event_type == "auto-shut-off-report":
            return AutoShutOffReportData.from_dict(event_data)
        elif event_type == "telemetry":
            return TelemetryEventData.from_dict(event_data)
        elif event_type == "valve":
            return ValveEventData.from_dict(event_data)
        elif event_type == "power-supply-changed":
            return PowerSupplyChangedEventData.from_dict(event_data)
        elif event_type == "wifi-changed":
            return WifiChangedEventData.from_dict(event_data)
        elif event_type == "online":
            return OnlineEvent.from_dict({})
        else:
            raise ValueError(f"Unknown event type: {event_type}")
