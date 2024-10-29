ENABLED_FIELD = "enabled"
VOLUME_THRESHOLD_FIELD = "volumeThreshold"
DURATION_THRESHOLD_FIELD = "durationThreshold"

class AutoShutOffState:
    """Represents Auto Shut Off state."""

    def __init__(
        self,
        enabled: bool,
        volume_threshold: int,
        duration_threshold: int,
    ) -> None:
        """Create an Auto Shut Off object."""
        self.enabled = enabled
        self.volume_threshold = volume_threshold
        self.duration_threshold = duration_threshold

    @classmethod
    def from_dict(cls, data: dict):
        """Create an Auto Shut Off object from a dictionary."""
        return cls(
            enabled=data.get(ENABLED_FIELD),
            volume_threshold=data.get(VOLUME_THRESHOLD_FIELD),
            duration_threshold=data.get(DURATION_THRESHOLD_FIELD),
        )