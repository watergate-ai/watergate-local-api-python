from typing import Any, Mapping
from ._util import field
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
    def from_dict(cls, data: Mapping[str, Any]) -> "AutoShutOffState":
        """Create an Auto Shut Off object from a dictionary."""
        return cls(
            enabled=field(data, ENABLED_FIELD),
            volume_threshold=field(data, VOLUME_THRESHOLD_FIELD),
            duration_threshold=field(data, DURATION_THRESHOLD_FIELD),
        )