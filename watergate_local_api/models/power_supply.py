from typing import Optional

BATTERY_FIELD = "battery"
EXTERNAL_FIELD = "external"
BATTERIES_VOLTAGE_FIELD = "batteriesVoltage"


class PowerSupply:
    """Represents the power supply status."""

    def __init__(
        self,
        battery: bool,
        external: bool,
        batteries_voltage: Optional[int],
    ) -> None:
        """Create a Power Supply object."""
        self.battery = battery
        self.external = external
        self.batteries_voltage = batteries_voltage

    @classmethod
    def from_dict(cls, data: dict):
        """Create a Power Supply object from a dictionary."""
        return cls(
            battery=data.get(BATTERY_FIELD),
            external=data.get(EXTERNAL_FIELD),
            batteries_voltage=data.get(BATTERIES_VOLTAGE_FIELD),
        )
