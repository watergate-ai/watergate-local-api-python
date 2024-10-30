import logging
from typing import Optional

import aiohttp
import asyncio

from .models import (
    DeviceState,
    NetworkingData,
    TelemetryData,
    AutoShutOffState,
    AutoShutOffReport
)

_LOGGER = logging.getLogger(__name__)

ACCEPT_HEADER = "Accept"
CONTENT_TYPE_HEADER = "Content-Type"

NETWORKING_URL = "/networking"
VALVE_URL = "/valve"
TELEMETRY_URL = "/telemetry"
AUTO_SHUT_OFF_URL = "/auto-shut-off"
AUTO_SHUT_OFF_REPORT_URL = "/auto-shut-off/report"
WEBHOOK_URL = "/webhook"

RETRY_ATTEMPTS = range(3)

class WatergateApiException(Exception):
    """Custom exception for critical errors in WatergateLocalApiClient."""
    pass

class WatergateLocalApiClient:
    """API Client for interacting with the external service."""

    def __init__(self, base_url: str, timeout: int = 10) -> None:
        """Initialize the API client."""
        self._base_url = base_url + "/api/sonic"
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._session = aiohttp.ClientSession(timeout=self._timeout)

    async def _get(self, url: str, headers: dict) -> Optional[dict]:
        """Helper method to perform GET requests."""
        if not self._session:
            raise RuntimeError("Session not initialized")

        for attempt in RETRY_ATTEMPTS:  # Retry logic
            try:
                response = await self._session.get(url, headers=headers)
                if response.status == 200:
                    return await response.json()
                _LOGGER.error("Failed to fetch data from %s: %s", url, response.status)
            except aiohttp.ClientError as e:
                _LOGGER.error("Network error occurred: %s", e)
            await asyncio.sleep(1)  # Wait before retrying
        raise WatergateApiException(f"Failed to fetch data from {url} after 3 attempts")

    async def _put(self, url: str, headers: dict, data: dict) -> bool:
        for attempt in RETRY_ATTEMPTS:  # Retry logic
            try:
                async with self._session.put(url, json=data, headers=headers) as response:
                    if response.status == 204:
                        return True
                _LOGGER.error("Failed to put data %s: %s", url, response.status)
            except aiohttp.ClientError as e:
                _LOGGER.error("Network error occurred: %s", e)
            await asyncio.sleep(1)  # Wait before retrying
        raise WatergateApiException(f"Failed to put data to {url} after 3 attempts")

    async def async_get_device_state(self) -> Optional[DeviceState]:
        """GET /api/sonic/ - Get device state."""
        headers = {ACCEPT_HEADER: "application/vnd.wtg.local.device-state.v1+json"}
        data = await self._get(self._base_url + "/", headers)
        return DeviceState.from_dict(data) if data else None

    async def async_get_networking(self) -> Optional[NetworkingData]:
        """GET /api/sonic/networking - Get networking."""
        url = self._base_url + NETWORKING_URL
        headers = {ACCEPT_HEADER: "application/vnd.wtg.local.networking.v1+json"}
        data = await self._get(url, headers)
        return NetworkingData.from_dict(data) if data else None

    async def async_get_telemetry_data(self) -> Optional[TelemetryData]:
        """GET /api/sonic/telemetry - Get telemetry data."""
        url = self._base_url + TELEMETRY_URL
        headers = {ACCEPT_HEADER: "application/vnd.wtg.local.telemetry.v1+json"}
        data = await self._get(url, headers)
        return TelemetryData.from_dict(data) if data else None

    async def async_get_auto_shut_off(self) -> Optional[AutoShutOffState]:
        """GET /api/sonic/auto-shut-off - Get Auto shut off state."""
        url = self._base_url + AUTO_SHUT_OFF_URL
        headers = {ACCEPT_HEADER: "application/vnd.wtg.local.auto-shut-off.v1+json"}
        data = await self._get(url, headers)
        return AutoShutOffState.from_dict(data) if data else None

    async def async_patch_auto_shut_off(
        self, enabled: Optional[bool] = None, duration: Optional[int] = None, volume: Optional[int] = None
    ) -> bool:
        """PATCH /api/sonic/auto-shut-off - Patch auto shut off."""
        url = self._base_url + AUTO_SHUT_OFF_URL
        headers = {CONTENT_TYPE_HEADER: "application/vnd.wtg.local.auto-shut-off.v1+json"}

        data = {}

        if enabled is not None:
            data["enabled"] = enabled
        if duration is not None:
            data["durationThreshold"] = duration
        if volume is not None:
            data["volumeThreshold"] = volume

        for attempt in RETRY_ATTEMPTS:  # Retry logic
            try:
                async with self._session.patch(url, json=data, headers=headers) as response:
                    if response.status == 204:
                        return True
                    _LOGGER.error("Failed to set auto shut off parameter: %s", response.status)
            except aiohttp.ClientError as e:
                _LOGGER.error("Network error occurred: %s", e)
            await asyncio.sleep(1)  # Wait before retrying
        raise WatergateApiException(f"Failed to patch auto shut off after 3 attempts")

    async def async_get_auto_shut_off_report(self) -> Optional[AutoShutOffReport]:
        """GET /api/sonic/auto-shut-off/report - Get auto shut-off report."""
        url = self._base_url + AUTO_SHUT_OFF_REPORT_URL
        headers = {ACCEPT_HEADER: "application/vnd.wtg.local.auto-shut-off.report.v1+json"}

        data = await self._get(url, headers)
        return AutoShutOffReport.from_dict(data) if data else None

    async def async_set_webhook_url(self, webhook: str) -> bool:
        """PATCH /api/sonic/webhook - Set webhook URL."""
        url = self._base_url + WEBHOOK_URL
        headers = {CONTENT_TYPE_HEADER: "application/vnd.wtg.local.webhook.v1+json"}
        data = {"webhookUrl": webhook}
        return await self._put(url, headers, data)

    async def async_set_valve_state(self, state: str) -> bool:
        """PUT /api/sonic/webhook - Set webhook URL."""
        url = self._base_url + VALVE_URL
        headers = {CONTENT_TYPE_HEADER: "application/vnd.wtg.local.valve-change.v1+json"}
        data = {"state": state}
        return await self._put(url, headers, data)