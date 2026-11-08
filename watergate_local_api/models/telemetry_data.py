from typing import Any, Mapping, Optional
from ._util import field
from .water_event import Event

FLOW_FIELD = "flow"
PRESSURE_FIELD = "pressure"
TEMPERATURE_FIELD = "temperature"
EVENT_FIELD = "event"
ERRORS_FIELD = "errors"

class TelemetryData:
    """Represents telemetry data."""

    def __init__(
        self,
        flow: Optional[float],
        pressure: Optional[float],
        water_temperature: Optional[float],
        ongoing_event: Event | None,
        errors: list[str],
    ) -> None:
        """Create an Telemetry Data object."""
        self.flow = flow
        self.pressure = pressure
        self.water_temperature = water_temperature
        self.ongoing_event = ongoing_event
        self.errors = errors

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "TelemetryData":
        """Create an Telemetry Data object from a dictionary."""
        return cls(
            flow=field(data, FLOW_FIELD),
            pressure=field(data, PRESSURE_FIELD),
            water_temperature=field(data, TEMPERATURE_FIELD),
            ongoing_event=Event(**field(data, EVENT_FIELD)) if field(data, EVENT_FIELD) else None,
            errors=field(data, ERRORS_FIELD)
        )