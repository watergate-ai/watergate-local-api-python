from typing import Any, Mapping
from ._util import field
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
    def from_dict(cls, data: Mapping[str, Any]) -> "BuzzerStatus":
        """Create a Buzzer Status object from a dictionary."""
        return cls(
            playing=field(data, PLAYING_FIELD),
            sound=field(data, SOUND_FIELD),
        )


class BuzzerSounds:
    """Represents the list of supported buzzer sounds."""

    def __init__(self, sounds: Optional[List[str]]) -> None:
        """Create a Buzzer Sounds object."""
        self.sounds = sounds

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "BuzzerSounds":
        """Create a Buzzer Sounds object from a dictionary."""
        return cls(sounds=field(data, SOUNDS_FIELD))
