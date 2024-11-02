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
        flow: float,
        pressure: float,
        water_temperature: float,
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
    def from_dict(cls, data: dict):
        """Create an Telemetry Data object from a dictionary."""
        return cls(
            flow=data.get(FLOW_FIELD),
            pressure=data.get(PRESSURE_FIELD),
            water_temperature=data.get(TEMPERATURE_FIELD),
            ongoing_event=Event(**data.get(EVENT_FIELD)) if data.get(EVENT_FIELD) else None,
            errors=data.get(ERRORS_FIELD)
        )