from typing import List, Optional

PLAYING_FIELD = "playing"
SOUND_FIELD = "sound"
SOUNDS_FIELD = "sounds"


class BuzzerStatus:
    """Represents the current buzzer status."""

    def __init__(self, playing: bool, sound: Optional[str]) -> None:
        """Create a Buzzer Status object."""
        self.playing = playing
        self.sound = sound

    @classmethod
    def from_dict(cls, data: dict):
        """Create a Buzzer Status object from a dictionary."""
        return cls(
            playing=data.get(PLAYING_FIELD),
            sound=data.get(SOUND_FIELD),
        )


class BuzzerSounds:
    """Represents the list of supported buzzer sounds."""

    def __init__(self, sounds: Optional[List[str]]) -> None:
        """Create a Buzzer Sounds object."""
        self.sounds = sounds

    @classmethod
    def from_dict(cls, data: dict):
        """Create a Buzzer Sounds object from a dictionary."""
        return cls(sounds=data.get(SOUNDS_FIELD))
