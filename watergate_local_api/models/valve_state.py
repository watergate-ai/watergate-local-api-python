from typing import Any, Mapping
from ._util import field
STATE_FIELD = "state"


class ValveState:
    """Represents the valve state."""

    def __init__(self, state: str) -> None:
        """Create a Valve State object."""
        self.state = state

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ValveState":
        """Create a Valve State object from a dictionary."""
        return cls(state=field(data, STATE_FIELD))
