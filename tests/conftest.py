from unittest.mock import Mock

import aioresponses.core
import pytest
from aiohttp import ClientResponse


class _ClientResponse(ClientResponse):
    """aioresponses 0.7.9 predates aiohttp 3.14, whose ClientResponse requires
    ``stream_writer``. Drop this shim once aioresponses supports it."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("stream_writer", Mock(output_size=0))
        super().__init__(*args, **kwargs)


@pytest.fixture(autouse=True)
def _aioresponses_aiohttp_314(monkeypatch):
    monkeypatch.setattr(aioresponses.core, "ClientResponse", _ClientResponse)
