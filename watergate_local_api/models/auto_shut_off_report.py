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
    def from_dict(cls, data: dict):
        """Create an Auto Shut Off Report object from dictionary."""
        return cls(
            timestamp=data.get(TIMESTAMP_FIELD),
            type=data.get(TYPE_FIELD),
            duration=data.get(DURATION_FIELD),
            volume=data.get(VOLUME_FIELD)
        )