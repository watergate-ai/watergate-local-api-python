class Event:
    """Represents the water event."""

    def __init__(self, volume: int, duration: int) -> None:
        """Create an water event object."""

        self.volume = volume
        self.duration = duration