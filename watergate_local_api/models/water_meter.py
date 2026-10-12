from typing import Any, Mapping
from ._util import field
from typing import Optional

VOLUME_FIELD = "volume"
DURATION_FIELD = "duration"

class WaterMeter:
    """Represents the water meter."""

    def __init__(self, volume: Optional[int], duration: Optional[int]) -> None:
        """Create an Water Meter object."""

        self.volume = volume
        self.duration = duration
        
    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "WaterMeter":
        """Create a WaterMeter object from a dictionary."""
        return cls(
            volume=field(data, VOLUME_FIELD),
            duration=field(data, DURATION_FIELD)
        )