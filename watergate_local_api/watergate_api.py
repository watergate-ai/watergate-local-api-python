import logging
import json
from typing import Optional

import aiohttp
import asyncio

from .models import (
    DeviceState,
    DeviceStateV2,
    DeviceStateV3,
    NetworkingData,
    TelemetryData,
    AutoShutOffState,
    AutoShutOffReport,
    ValveState,
    PowerSupply,
    BuzzerStatus,
    BuzzerSounds,
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
POWER_URL = "/power"
COMMAND_URL = "/command"
BUZZER_URL = "/buzzer"
BUZZER_SOUNDS_URL = "/buzzer/sounds"

RETRY_ATTEMPTS = range(3)

class WatergateApiException(Exception):
    """Custom exception for critical errors in WatergateLocalApiClient."""
    pass

class WatergateLocalApiClient:
    """API Client for interacting with the external service."""

    def __init__(self, base_url: str, timeout: int = 10, session: Optional[aiohttp.ClientSession] = None) -> None:
        """Initialize the API client. Optionally inject aiohttp session for Home Assistant compatibility."""
        self._base_url = base_url + "/api/sonic"
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._session = session
        self._session_owner = session is None

    async def _ensure_session(self):
        """Ensure the session is open, creating it if necessary (only if owned)."""
        if self._session_owner and (self._session is None or self._session.closed):
            self._session = aiohttp.ClientSession(timeout=self._timeout, json_serialize=lambda data: json.dumps(data, separators=(',', ':')))
            _LOGGER.debug("Created a new aiohttp session.")

    async def __aenter__(self):
        """Enter the context and create the session if owned."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Exit the context and close the session if owned."""
        await self.async_close()

    async def _get(self, url: str, headers: dict) -> Optional[dict]:
        """Helper method to perform GET requests."""
        await self._ensure_session()

        for attempt in RETRY_ATTEMPTS:  # Retry logic
            try:
                response = await self._session.get(url, headers=headers)
                if response.status == 200:
                    return await response.json()
                _LOGGER.error("Failed to fetch data from %s: %s", url, response.status)
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                _LOGGER.error("Network error occurred: %s", e)
            await asyncio.sleep(1)
        raise WatergateApiException(f"Failed to fetch data from {url} after 3 attempts")

    async def _put(self, url: str, headers: dict, data: dict, redact_fields: Optional[set] = None) -> bool:
        # Never log secret fields (e.g. Wi-Fi password); the real data is still sent on the wire.
        log_data = (
            {k: ("***" if k in redact_fields else v) for k, v in data.items()}
            if redact_fields
            else data
        )
        _LOGGER.debug("PUT %s with data: %s and headers: %s", url, log_data, headers)
        await self._ensure_session()
        for attempt in RETRY_ATTEMPTS:  # Retry logic
            try:
                async with self._session.put(url, json=data, headers=headers) as response:
                    if response.status == 204 or response.status == 200:
                        return True
                _LOGGER.error("Failed to put data %s, %s, %s: %s", url, log_data, headers, response.status)
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                _LOGGER.error("Network error occurred: %s", e)
            await asyncio.sleep(1)
        raise WatergateApiException(f"Failed to put data to {url} after 3 attempts")

    async def _delete(self, url: str, headers: dict) -> bool:
        """Helper method to perform DELETE requests."""
        await self._ensure_session()
        for attempt in RETRY_ATTEMPTS:  # Retry logic
            try:
                async with self._session.delete(url, headers=headers) as response:
                    if response.status == 204 or response.status == 200:
                        return True
                _LOGGER.error("Failed to delete %s: %s", url, response.status)
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                _LOGGER.error("Network error occurred: %s", e)
            await asyncio.sleep(1)
        raise WatergateApiException(f"Failed to delete {url} after 3 attempts")

    async def async_close(self):
        """Explicitly close the session if owned."""
        if self._session_owner and self._session and not self._session.closed:
            await self._session.close()
            _LOGGER.debug("Closed the aiohttp session.")

    async def async_get_device_state(self) -> Optional[DeviceState]:
        """GET /api/sonic/ - Get device state."""
        headers = {ACCEPT_HEADER: "application/vnd.wtg.local.device-state.v1+json"}
        data = await self._get(self._base_url + "/", headers)
        return DeviceState.from_dict(data) if data else None

    async def async_get_device_state_v2(self) -> Optional[DeviceStateV2]:
        """GET /api/sonic/ - Get device state (API v2 with positive/negative water meter)."""
        headers = {ACCEPT_HEADER: "application/vnd.wtg.local.device-state.v2+json"}
        data = await self._get(self._base_url + "/", headers)
        return DeviceStateV2.from_dict(data) if data else None

    async def async_get_device_state_v3(self) -> Optional[DeviceStateV3]:
        """GET /api/sonic/ - Get device state (API v3, adds buzzerPlaying)."""
        headers = {ACCEPT_HEADER: "application/vnd.wtg.local.device-state.v3+json"}
        data = await self._get(self._base_url + "/", headers)
        return DeviceStateV3.from_dict(data) if data else None

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
        
        await self._ensure_session()

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

    async def async_update_auto_shut_off(
        self,
        enabled: Optional[bool] = None,
        duration: Optional[int] = None,
        volume: Optional[int] = None,
    ) -> bool:
        """PUT /api/sonic/auto-shut-off - Update auto shut-off settings (firmware 2026.1.0+).

        Documented replacement for the legacy PATCH (async_patch_auto_shut_off). At least one
        of enabled/duration/volume must be provided.
        """
        url = self._base_url + AUTO_SHUT_OFF_URL
        headers = {CONTENT_TYPE_HEADER: "application/vnd.wtg.local.auto-shut-off-change.v1+json"}

        data = {}
        if enabled is not None:
            data["enabled"] = enabled
        if duration is not None:
            data["durationThreshold"] = duration
        if volume is not None:
            data["volumeThreshold"] = volume

        return await self._put(url, headers, data)

    async def async_get_auto_shut_off_report(self) -> Optional[AutoShutOffReport]:
        """GET /api/sonic/auto-shut-off/report - Get auto shut-off report."""
        url = self._base_url + AUTO_SHUT_OFF_REPORT_URL
        headers = {ACCEPT_HEADER: "application/vnd.wtg.local.auto-shut-off.report.v1+json"}

        await self._ensure_session()

        for attempt in RETRY_ATTEMPTS:  # Retry logic
            try:
                response = await self._session.get(url, headers=headers)
                if response.status == 200:
                    data = await response.json()
                    return AutoShutOffReport.from_dict(data) if data else None
                if response.status == 204:
                    return None
                _LOGGER.error("Failed to fetch data from %s: %s", url, response.status)
            except aiohttp.ClientError as e:
                _LOGGER.error("Network error occurred: %s", e)
            await asyncio.sleep(1)  # Wait before retrying
        raise WatergateApiException(f"Failed to fetch data from {url} after 3 attempts")

    async def async_set_webhook_url(self, webhook: str) -> bool:
        """PUT /api/sonic/webhook - Set webhook URL."""
        url = self._base_url + WEBHOOK_URL
        headers = {CONTENT_TYPE_HEADER: "application/vnd.wtg.local.webhook.v1+json"}
        data = {"url": webhook}
        return await self._put(url, headers, data)

    async def async_get_webhook_url(self) -> Optional[str]:
        """GET /api/sonic/webhook - Get the configured webhook URL (None if unset)."""
        url = self._base_url + WEBHOOK_URL
        headers = {ACCEPT_HEADER: "application/vnd.wtg.local.webhook.v1+json"}

        await self._ensure_session()

        for attempt in RETRY_ATTEMPTS:  # Retry logic
            try:
                response = await self._session.get(url, headers=headers)
                if response.status == 200:
                    data = await response.json()
                    return data.get("url") if data else None
                if response.status == 204:
                    return None
                _LOGGER.error("Failed to fetch data from %s: %s", url, response.status)
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                _LOGGER.error("Network error occurred: %s", e)
            await asyncio.sleep(1)
        raise WatergateApiException(f"Failed to fetch data from {url} after 3 attempts")

    async def async_delete_webhook_url(self) -> bool:
        """DELETE /api/sonic/webhook - Clear the configured webhook URL."""
        url = self._base_url + WEBHOOK_URL
        headers = {ACCEPT_HEADER: "application/vnd.wtg.local.webhook.v1+json"}
        return await self._delete(url, headers)

    async def async_send_command(self, command_type: str) -> bool:
        """PUT /api/sonic/command - Execute a device command (e.g. "reboot")."""
        url = self._base_url + COMMAND_URL
        headers = {CONTENT_TYPE_HEADER: "application/vnd.wtg.local.command.v1+json"}
        data = {"type": command_type}
        return await self._put(url, headers, data)

    async def async_reboot(self) -> bool:
        """PUT /api/sonic/command - Convenience wrapper to reboot the device."""
        return await self.async_send_command("reboot")

    async def async_change_network(self, ssid: str, password: str) -> bool:
        """PUT /api/sonic/networking - Update the Wi-Fi configuration."""
        url = self._base_url + NETWORKING_URL
        headers = {CONTENT_TYPE_HEADER: "application/vnd.wtg.local.network-change.v1+json"}
        data = {"ssid": ssid, "password": password}
        return await self._put(url, headers, data, redact_fields={"password"})

    async def async_get_buzzer_status(self) -> Optional[BuzzerStatus]:
        """GET /api/sonic/buzzer - Get the current buzzer status."""
        url = self._base_url + BUZZER_URL
        headers = {ACCEPT_HEADER: "application/vnd.wtg.local.buzzer.v1+json"}
        data = await self._get(url, headers)
        return BuzzerStatus.from_dict(data) if data else None

    async def async_get_buzzer_sounds(self) -> Optional[BuzzerSounds]:
        """GET /api/sonic/buzzer/sounds - Get the list of supported buzzer sounds."""
        url = self._base_url + BUZZER_SOUNDS_URL
        headers = {ACCEPT_HEADER: "application/vnd.wtg.local.buzzer-sounds.v1+json"}
        data = await self._get(url, headers)
        return BuzzerSounds.from_dict(data) if data else None

    async def async_control_buzzer(
        self,
        action: str,
        name: Optional[str] = None,
        interval: Optional[int] = None,
        times: Optional[int] = None,
    ) -> bool:
        """PUT /api/sonic/buzzer - Control the buzzer (action "start" or "stop")."""
        url = self._base_url + BUZZER_URL
        headers = {CONTENT_TYPE_HEADER: "application/vnd.wtg.local.buzzer-control.v1+json"}

        data = {"action": action}
        if name is not None:
            data["name"] = name
        if interval is not None:
            data["interval"] = interval
        if times is not None:
            data["times"] = times

        return await self._put(url, headers, data)

    async def async_set_valve_state(self, state: str) -> bool:
        """PUT /api/sonic/valve - Set valve state."""
        url = self._base_url + VALVE_URL
        headers = {CONTENT_TYPE_HEADER: "application/vnd.wtg.local.valve-change.v1+json"}
        data = {"state": state}
        return await self._put(url, headers, data)

    async def async_get_valve_state(self) -> Optional[ValveState]:
        """GET /api/sonic/valve - Get valve state."""
        url = self._base_url + VALVE_URL
        headers = {ACCEPT_HEADER: "application/vnd.wtg.local.valve.v1+json"}
        data = await self._get(url, headers)
        return ValveState.from_dict(data) if data else None

    async def async_get_power_supply_data(self) -> Optional[PowerSupply]:
        """GET /api/sonic/power - Get power supply status."""
        url = self._base_url + POWER_URL
        headers = {ACCEPT_HEADER: "application/vnd.wtg.local.power.v1+json"}
        data = await self._get(url, headers)
        return PowerSupply.from_dict(data) if data else None