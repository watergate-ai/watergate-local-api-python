MQTT_CONNECTED_FIELD = "mqttConnected"
WIFI_CONNECTED_FIELD = "wifiConnected"
IP_FIELD = "ip"
GATEWAY_FIELD = "gateway"
SUBNET_FIELD = "subnet"
SSID_FIELD = "ssid"
RSSI_FIELD = "rssi"
WIFI_UPTIME_FIELD = "wifiUpTime"
MQTT_UPTIME_FIELD = "mqttUpTime"

class NetworkingData:
    """Represents networking data."""

    def __init__(
        self,
        mqtt_connected: bool,
        wifi_connected: bool,
        ip: str,
        gateway: str,
        subnet: str,
        ssid: str,
        rssi: str,
        wifi_uptime: str,
        mqtt_uptime: str,
    ) -> None:
        """Create an Networking object."""
        self.mqtt_connected = mqtt_connected
        self.wifi_connected = wifi_connected
        self.ip = ip
        self.gateway = gateway
        self.subnet = subnet
        self.ssid = ssid
        self.rssi = rssi
        self.wifi_uptime = wifi_uptime
        self.mqtt_uptime = mqtt_uptime

    @classmethod
    def from_dict(cls, data: dict):
        """Create an Networking from a dictionary."""
        return cls(
            mqtt_connected=data.get(MQTT_CONNECTED_FIELD),
            wifi_connected=data.get(WIFI_CONNECTED_FIELD),
            ip=data.get(IP_FIELD),
            gateway=data.get(GATEWAY_FIELD),
            subnet=data.get(SUBNET_FIELD),
            ssid=data.get(SSID_FIELD),
            rssi=data.get(RSSI_FIELD),
            wifi_uptime=data.get(WIFI_UPTIME_FIELD),
            mqtt_uptime=data.get(MQTT_UPTIME_FIELD),
        )