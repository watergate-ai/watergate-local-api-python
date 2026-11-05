from typing import Any, Mapping
from ._util import field
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
    
    def __init__(self, event_type: str, volume: int, duration: int, timestamp: int) -> None:
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
    def from_dict(cls, data: Mapping[str, Any]) -> "AutoShutOffReportData":
        """Create an AutoShutOffReportData object from a dictionary."""
        return cls(
            event_type=field(data, TYPE_FIELD),
            volume=field(data, VOLUME_FIELD),
            duration=field(data, DURATION_FIELD),
            timestamp=field(data, TIMESTAMP_FIELD)
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
    ) -> None:
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
    def from_dict(cls, data: Mapping[str, Any]) -> "TelemetryEventData":
        """Create a TelemetryEventData object from a dictionary."""
        return cls(
            flow=field(data, FLOW_FIELD),
            pressure=field(data, PRESSURE_FIELD),
            temperature=field(data, TEMPERATURE_FIELD),
            event=field(data, EVENT_FIELD),
            errors=field(data, ERRORS_FIELD)
        )


class ValveEventData:
    """Represents data for the valve state change webhook event."""
    
    def __init__(self, state: str) -> None:
        """
        Initialize the ValveEventData object.
        
        :param state: State of the valve ("open", "closed", "opening", or "closing").
        """
        self.state = state

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ValveEventData":
        """Create a ValveEventData object from a dictionary."""
        return cls(
            state=field(data, VALVE_STATE_FIELD)
        )


class PowerSupplyChangedEventData:
    """Represents data for the power supply change webhook event."""
    
    def __init__(self, supply: str) -> None:
        """
        Initialize the PowerSupplyChangedEventData object.
        
        :param supply: Type of power supply ("battery", "external", or "external+battery").
        """
        self.supply = supply

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PowerSupplyChangedEventData":
        """Create a PowerSupplyChangedEventData object from a dictionary."""
        return cls(
            supply=field(data, SUPPLY_FIELD)
        )


class WifiChangedEventData:
    """Represents data for the WiFi configuration change webhook event."""
    
    def __init__(self, ip: str, gateway: str, subnet: str, ssid: str, rssi: int) -> None:
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
    def from_dict(cls, data: Mapping[str, Any]) -> "WifiChangedEventData":
        """Create a WifiChangedEventData object from a dictionary."""
        return cls(
            ip=field(data, IP_FIELD),
            gateway=field(data, GATEWAY_FIELD),
            subnet=field(data, SUBNET_FIELD),
            ssid=field(data, SSID_FIELD),
            rssi=field(data, RSSI_FIELD)
        )


class OnlineEvent:
    """Represents an online status webhook event with no specific data."""
    
    def __init__(self) -> None:
        """
        Initialize the OnlineEvent object.
        
        This event indicates that the device has come online.
        """
        self.type = "online"
    
    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "OnlineEvent":
        """Create an OnlineEvent object from a dictionary."""
        return cls()


class WebhookEvent:
    """Base class for all webhook events."""
    
    def __init__(self, event_type: str, data: dict[str, Any]) -> None:
        """
        Initialize the WebhookEvent object.
        
        :param event_type: Type of the webhook event.
        :param data: Data payload associated with the event.
        """
        self.type = event_type
        self.data = data

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "WebhookEvent":
        """Create a base WebhookEvent object from a dictionary."""
        return cls(
            event_type=field(data, "type"),
            data=data.get("data", {})
        )
    
    @classmethod
    def parse_webhook_event(cls, data: Mapping[str, Any]) -> Union[
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
