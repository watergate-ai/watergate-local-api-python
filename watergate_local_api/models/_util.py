from typing import Any, Mapping


def field(data: Mapping[str, Any], key: str) -> Any:
    """Return ``data.get(key)`` typed as ``Any``.

    The model constructors annotate the values the Sonic API documents; the payload is untrusted
    JSON, so a missing key yields ``None`` at runtime exactly as ``dict.get`` always did.
    """
    return data.get(key)
