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
    def from_dict(cls, data: dict):
        """Create a WaterMeter object from a dictionary."""
        return cls(
            volume=data.get(VOLUME_FIELD),
            duration=data.get(DURATION_FIELD)
        )