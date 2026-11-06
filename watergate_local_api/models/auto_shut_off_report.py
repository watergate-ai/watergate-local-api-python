from typing import Any, Mapping
from ._util import field
TIMESTAMP_FIELD = "timestamp"
TYPE_FIELD = "type"
DURATION_FIELD = "duration"
VOLUME_FIELD = "volume"

class AutoShutOffReport:
    """Represents auto shut off report."""

    def __init__(
        self,
        timestamp: int,
        type: str,
        duration: int,
        volume: int,
    ) -> None:
        """Create an Auto Shut Off Report object."""
        self.timestamp = timestamp
        self.type = type
        self.duration = duration
        self.volume = volume

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "AutoShutOffReport":
        """Create an Auto Shut Off Report object from dictionary."""
        return cls(
            timestamp=field(data, TIMESTAMP_FIELD),
            type=field(data, TYPE_FIELD),
            duration=field(data, DURATION_FIELD),
            volume=field(data, VOLUME_FIELD)
        )