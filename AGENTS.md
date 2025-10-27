# AI Agent Guide for Watergate Local API Python Client

> **⚠️ CRITICAL**: This file MUST be updated after every significant change to the codebase. It serves as the single source of truth for AI agents working on this project.

## Table of Contents
1. [Project Identity](#project-identity)
2. [Architecture Overview](#architecture-overview)
3. [Core Concepts](#core-concepts)
4. [Repeatable Patterns](#repeatable-patterns)
5. [API Specifications](#api-specifications)
6. [Model Specifications](#model-specifications)
7. [Testing Guidelines](#testing-guidelines)
8. [Quality Standards](#quality-standards)
9. [Change Management](#change-management)

---

## Project Identity

### What This Project Is
A **Python async HTTP client library** for communicating with Watergate/Sonic water monitoring devices via their Local API. The library abstracts complex HTTP interactions into simple async Python methods.

### What This Project Is NOT
- Not a REST API server (it's a client)
- Not a synchronous library (async-only)
- Not a Home Assistant integration (though it can be used by one)
- Not a general-purpose HTTP client (device-specific)

### Primary Use Cases
1. Retrieving device state (valve position, connectivity, power)
2. Monitoring telemetry (flow rate, pressure, temperature)
3. Configuring auto shut-off thresholds
4. Receiving and parsing webhook events
5. Controlling valve state remotely

---

## Architecture Overview

### High-Level Architecture
```
┌─────────────────────────────────────────────┐
│         User Application Code               │
│  (Home Assistant, custom scripts, etc.)     │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│     WatergateLocalApiClient                 │
│  - Session management                       │
│  - Retry logic                              │
│  - HTTP operations                          │
│  - Error handling                           │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│          Data Models                        │
│  - DeviceState, TelemetryData, etc.        │
│  - WebhookEvent parsing                     │
│  - Type safety & validation                 │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│      Sonic Device Local API                 │
│   (Physical/Virtual Device)                 │
└─────────────────────────────────────────────┘
```

### Technology Stack
| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Language | Python | 3.x | Core programming language |
| Virtual Environment | venv | Built-in | **REQUIRED**: `.venv/` for all operations |
| HTTP Client | aiohttp | 3.13.1 | Async HTTP operations |
| Testing | pytest | 8.4.2 | Test framework |
| Async Testing | pytest-asyncio | 1.2.0 | Async test support |
| HTTP Mocking | aioresponses | 0.7.8 | HTTP response mocking |
| Package Build | setuptools | Latest | Distribution packaging |

### 🚨 CRITICAL: Virtual Environment Requirements

**ALL Python operations MUST be run within the project's virtual environment (`.venv/`):**

#### Setup Virtual Environment
```bash
# Create venv if it doesn't exist
python3 -m venv .venv

# Activate venv (REQUIRED before every operation)
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

#### Virtual Environment Rules
1. ✅ **ALWAYS activate venv first**: `source .venv/bin/activate`
2. ✅ **Verify activation**: Terminal prompt shows `(.venv)` prefix
3. ✅ **All pip installs go in venv**: Never install globally
4. ✅ **All pytest runs in venv**: `pytest` after activation
5. ✅ **All python commands in venv**: Including builds, installs, tests
6. ❌ **NEVER run without venv**: This causes dependency conflicts
7. ❌ **NEVER install packages globally**: Always in `.venv/`

### Key Dependencies
```python
aiohttp==3.13.1      # MUST use aiohttp, not requests
pytest==8.4.2        # Testing framework
pytest-asyncio==1.2.0  # Async test support
aioresponses==0.7.8  # HTTP mocking for tests
```

---

## Core Concepts

### 1. Async-First Design
**Every operation is asynchronous**. This is not optional.

```python
# ✅ CORRECT
async def async_get_device_state(self) -> Optional[DeviceState]:
    data = await self._get(url, headers)
    return DeviceState.from_dict(data)

# ❌ WRONG - Never create sync methods
def get_device_state(self) -> Optional[DeviceState]:
    response = requests.get(url)  # NEVER use requests
    return DeviceState.from_dict(response.json())
```

**Why**: The device API may be slow or unreliable. Async allows non-blocking operations and better resource utilization.

### 2. Session Lifecycle Management
**One session per client instance, created lazily, reused throughout lifetime**.

```python
# Session creation is lazy
async def _ensure_session(self):
    if self._session is None or self._session.closed:
        self._session = aiohttp.ClientSession(
            timeout=self._timeout,
            json_serialize=lambda data: json.dumps(data, separators=(',', ':'))
        )
```

**Critical Rules**:
- Session created on first API call, not in `__init__`
- Session reused for all subsequent calls
- Session MUST be closed in `async_close()` and `__aexit__()`
- Supports both manual management and context manager usage

```python
# Context manager (recommended)
async with WatergateLocalApiClient(base_url="http://device") as client:
    state = await client.async_get_device_state()

# Manual management
client = WatergateLocalApiClient(base_url="http://device")
try:
    state = await client.async_get_device_state()
finally:
    await client.async_close()
```

### 3. Resilient Retry Logic
**All network operations retry up to 3 times with exponential backoff**.

```python
RETRY_ATTEMPTS = range(3)  # Module-level constant

for attempt in RETRY_ATTEMPTS:
    try:
        response = await self._session.get(url, headers=headers)
        if response.status == 200:
            return await response.json()
        _LOGGER.error("Failed to fetch: %s", response.status)
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        _LOGGER.error("Network error: %s", e)
    await asyncio.sleep(1)  # 1 second between retries

raise WatergateApiException(f"Failed after 3 attempts")
```

**Why**: Devices may be on unreliable networks (WiFi), experience temporary issues, or be under load.

### 4. Content-Type Versioning
**API uses versioned media types for forward/backward compatibility**.

```python
# Different versions for different resources
DEVICE_STATE_MEDIA_TYPE = "application/vnd.wtg.local.device-state.v1+json"
TELEMETRY_MEDIA_TYPE = "application/vnd.wtg.local.telemetry.v1+json"
WEBHOOK_MEDIA_TYPE = "application/vnd.wtg.local.webhook.v1+json"

# GET requests - Accept header
headers = {ACCEPT_HEADER: "application/vnd.wtg.local.device-state.v1+json"}

# PUT/PATCH requests - Content-Type header
headers = {CONTENT_TYPE_HEADER: "application/vnd.wtg.local.valve-change.v1+json"}
```

**Critical**: Media types MUST match API specifications exactly. Changing them can break compatibility.

### 5. Data Model Pattern
**All models follow immutable, dict-to-object deserialization pattern**.

```python
# Field names as constants (matches API response keys)
VALVE_STATE_FIELD = "valveState"
UPTIME_FIELD = "uptime"

class DeviceState:
    def __init__(self, valve_state: str, uptime: int):
        self.valve_state = valve_state
        self.uptime = uptime
    
    @classmethod
    def from_dict(cls, data: dict):
        """Safe deserialization with None defaults"""
        return cls(
            valve_state=data.get(VALVE_STATE_FIELD),
            uptime=data.get(UPTIME_FIELD)
        )
```

**Key Points**:
- Field constants prevent typos and enable IDE autocomplete
- `.get()` method returns None for missing fields (graceful degradation)
- No `to_dict()` method - deserialization only (data flows one way)
- Nested objects conditionally instantiated

### 6. Webhook Event System
**Type-safe parsing of polymorphic webhook events**.

```python
event_data = {
    "type": "telemetry",
    "data": {"flow": 6800, "pressure": 2320, "temperature": 23.5}
}

# Parse into appropriate typed object
event = WebhookEvent.parse_webhook_event(event_data)
# Returns: TelemetryEventData instance

# Type-specific handling
if isinstance(event, TelemetryEventData):
    print(f"Flow: {event.flow} ml/min")
```

**Event Type Mapping**:
- `auto-shut-off-report` → `AutoShutOffReportData`
- `telemetry` → `TelemetryEventData`
- `valve` → `ValveEventData`
- `power-supply-changed` → `PowerSupplyChangedEventData`
- `wifi-changed` → `WifiChangedEventData`
- `online` → `OnlineEvent`

---

## Repeatable Patterns

### Pattern 1: Adding a New GET Endpoint

**Prerequisites**: 
1. ✅ **ACTIVATE VENV**: `source .venv/bin/activate`
2. ✅ **VERIFY ACTIVATION**: Check for `(.venv)` in prompt

**Template**:
```python
# 1. Define endpoint constant
NEW_RESOURCE_URL = "/new-resource"

# 2. In WatergateLocalApiClient class
async def async_get_new_resource(self) -> Optional[NewResourceData]:
    """GET /api/sonic/new-resource - Get new resource data."""
    url = self._base_url + NEW_RESOURCE_URL
    headers = {ACCEPT_HEADER: "application/vnd.wtg.local.new-resource.v1+json"}
    data = await self._get(url, headers)
    return NewResourceData.from_dict(data) if data else None
```

**Checklist**:
- [ ] Define URL constant at module level
- [ ] Use correct versioned media type
- [ ] Use `_get()` helper method
- [ ] Return `Optional[ModelClass]`
- [ ] Handle None response
- [ ] Add retry logic (built into `_get`)
- [ ] Add docstring with endpoint path
- [ ] Create corresponding model class
- [ ] Write tests

### Pattern 2: Adding a New PUT/PATCH Endpoint

**Prerequisites**: 
1. ✅ **ACTIVATE VENV**: `source .venv/bin/activate`
2. ✅ **VERIFY ACTIVATION**: Check for `(.venv)` in prompt

**Template**:
```python
async def async_update_resource(self, param: str) -> bool:
    """PUT /api/sonic/resource - Update resource."""
    url = self._base_url + RESOURCE_URL
    headers = {CONTENT_TYPE_HEADER: "application/vnd.wtg.local.resource.v1+json"}
    data = {"parameter": param}
    return await self._put(url, headers, data)
```

**Checklist**:
- [ ] Use `_put()` helper for PUT
- [ ] Implement inline retry for PATCH
- [ ] Return `bool` (success/failure)
- [ ] Set Content-Type header
- [ ] Construct request body dict
- [ ] Accept 200 or 204 as success
- [ ] Write tests for success and failure

### Pattern 3: Adding a New Model

**Prerequisites**: 
1. ✅ **ACTIVATE VENV**: `source .venv/bin/activate`
2. ✅ **VERIFY ACTIVATION**: Check for `(.venv)` in prompt

**Template**:
```python
# In models/new_model.py

# 1. Define field constants
FIELD_ONE = "fieldOne"
FIELD_TWO = "fieldTwo"
NESTED_FIELD = "nestedObject"

class NewModel:
    """Represents new model data."""
    
    def __init__(
        self,
        field_one: str,
        field_two: int,
        nested_object: Optional[NestedModel] = None
    ):
        """Create a NewModel object."""
        self.field_one = field_one
        self.field_two = field_two
        self.nested_object = nested_object
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create a NewModel from dictionary."""
        return cls(
            field_one=data.get(FIELD_ONE),
            field_two=data.get(FIELD_TWO),
            nested_object=NestedModel(**data.get(NESTED_FIELD)) if data.get(NESTED_FIELD) else None
        )
```

**Checklist**:
- [ ] Create file in `models/` directory
- [ ] Define all field constants at module level
- [ ] Use descriptive class name with suffix (`Data`, `State`, `Report`)
- [ ] Type hint all parameters
- [ ] Implement `from_dict` classmethod
- [ ] Handle nested objects conditionally
- [ ] Use `.get()` for safe access
- [ ] Export in `models/__init__.py`
- [ ] Add tests for deserialization
- [ ] Test with missing fields

### Pattern 4: Adding a New Webhook Event Type

**Template**:
```python
# In models/webhook_model.py

# 1. Create event data class
class NewEventData:
    """Represents new event webhook data."""
    
    def __init__(self, field: str):
        self.field = field
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(field=data.get(FIELD_CONSTANT))

# 2. Update parse_webhook_event method
@classmethod
def parse_webhook_event(cls, data: dict) -> Union[...]:
    event_type = data.get("type")
    event_data = data.get("data", {})
    
    # Add new case
    if event_type == "new-event-type":
        return NewEventData.from_dict(event_data)
    # ... existing cases ...
    else:
        raise ValueError(f"Unknown event type: {event_type}")
```

**Checklist**:
- [ ] Create event data class in `webhook_model.py`
- [ ] Implement `from_dict` classmethod
- [ ] Add case to `parse_webhook_event`
- [ ] Update type hints in method signature
- [ ] Write parsing tests
- [ ] Test with sample webhook payload
- [ ] Document event structure

### Pattern 5: Writing Comprehensive Tests

**Prerequisites**: 
1. ✅ **ACTIVATE VENV**: `source .venv/bin/activate`
2. ✅ **VERIFY ACTIVATION**: Check for `(.venv)` in prompt
3. ✅ **INSTALL TEST DEPS**: `pip install -r requirements.txt`

**Template**:
```python
@pytest.mark.asyncio
async def test_operation_success(client):
    """Test successful operation."""
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/endpoint", payload={
            "field": "value"
        })
        
        result = await client.async_method()
        assert result.field == "value"

@pytest.mark.asyncio
async def test_operation_network_error(client):
    """Test network error handling with retries."""
    with aioresponses() as mock:
        # Fail all 3 attempts
        mock.get("http://testserver/api/sonic/endpoint", status=500)
        
        with pytest.raises(WatergateApiException):
            await client.async_method()

@pytest.mark.asyncio
async def test_operation_missing_fields(client):
    """Test graceful handling of missing fields."""
    with aioresponses() as mock:
        mock.get("http://testserver/api/sonic/endpoint", payload={})
        
        result = await client.async_method()
        assert result.field is None  # Should not crash
```

**Test Categories**:
1. **Happy path**: Valid responses, correct parsing
2. **Error conditions**: 4xx, 5xx status codes
3. **Network failures**: Timeouts, connection errors
4. **Edge cases**: Missing fields, None values, empty responses
5. **Retry logic**: Verify 3 attempts before exception

---

## API Specifications

### Base Configuration
- **Base URL Pattern**: `{device_ip}/api/sonic`
- **Default Timeout**: 10 seconds
- **Retry Count**: 3 attempts
- **Retry Delay**: 1 second

### Endpoint Inventory

| Method | Endpoint | Purpose | Response Status | Model |
|--------|----------|---------|----------------|-------|
| GET | `/` | Get device state | 200 | `DeviceState` |
| GET | `/networking` | Get network info | 200 | `NetworkingData` |
| GET | `/telemetry` | Get telemetry data | 200 | `TelemetryData` |
| GET | `/auto-shut-off` | Get auto shut-off state | 200 | `AutoShutOffState` |
| PATCH | `/auto-shut-off` | Update auto shut-off | 204 | N/A |
| GET | `/auto-shut-off/report` | Get last report | 200/204 | `AutoShutOffReport` or None |
| PUT | `/webhook` | Set webhook URL | 200/204 | N/A |
| PUT | `/valve` | Set valve state | 200/204 | N/A |

### Media Type Matrix

| Endpoint | Accept (GET) | Content-Type (PUT/PATCH) |
|----------|-------------|-------------------------|
| `/` | `application/vnd.wtg.local.device-state.v1+json` | N/A |
| `/networking` | `application/vnd.wtg.local.networking.v1+json` | N/A |
| `/telemetry` | `application/vnd.wtg.local.telemetry.v1+json` | N/A |
| `/auto-shut-off` | `application/vnd.wtg.local.auto-shut-off.v1+json` | `application/vnd.wtg.local.auto-shut-off.v1+json` |
| `/auto-shut-off/report` | `application/vnd.wtg.local.auto-shut-off.report.v1+json` | N/A |
| `/webhook` | N/A | `application/vnd.wtg.local.webhook.v1+json` |
| `/valve` | N/A | `application/vnd.wtg.local.valve-change.v1+json` |

---

## Model Specifications

### DeviceState
**Purpose**: Complete device status snapshot

**Fields**:
- `valve_state: str` - Valve position: "open", "closed", "opening", "closing"
- `water_flow_indicator: bool` - Is water currently flowing
- `mqtt_status: bool` - MQTT connection status
- `wifi_status: bool` - WiFi connection status
- `power_supply: str` - Power source: "battery", "external", "external+battery"
- `firmware_version: str` - Firmware version (e.g., "2024.1.0")
- `uptime: int` - Device uptime in seconds
- `water_meter: WaterMeter` - Total water usage stats
- `serial_number: str` - Device serial number

### TelemetryData
**Purpose**: Real-time sensor readings

**Fields**:
- `flow: float` - Flow rate in ml/min
- `pressure: float` - Water pressure in mbar
- `water_temperature: float` - Temperature in °C
- `ongoing_event: Event | None` - Current water usage event
- `errors: list[str]` - List of sensor errors ("flow", "pressure", "temperature")

### NetworkingData
**Purpose**: Network configuration and status

**Fields**:
- `mqtt_connected: bool` - MQTT connection status
- `wifi_connected: bool` - WiFi connection status
- `ip: str` - Device IP address
- `gateway: str` - Gateway IP
- `subnet: str` - Subnet mask
- `ssid: str` - Connected WiFi SSID
- `rssi: str` - WiFi signal strength in dBm
- `wifi_uptime: str` - WiFi connection duration
- `mqtt_uptime: str` - MQTT connection duration

### AutoShutOffState
**Purpose**: Auto shut-off configuration

**Fields**:
- `enabled: bool` - Is auto shut-off enabled
- `volume_threshold: int` - Volume limit in liters
- `duration_threshold: int` - Time limit in minutes

### AutoShutOffReport
**Purpose**: Last auto shut-off event details

**Fields**:
- `timestamp: int` - Event timestamp in milliseconds
- `type: str` - Trigger type: "VOLUME_THRESHOLD" or "DURATION_THRESHOLD"
- `duration: int` - Event duration in minutes
- `volume: int` - Water volume in liters

### WaterMeter
**Purpose**: Cumulative water usage

**Fields**:
- `volume: int` - Total volume in liters
- `duration: int` - Total usage duration in minutes

### Event (Water Event)
**Purpose**: Ongoing water usage event

**Fields**:
- `volume: int` - Current event volume in liters
- `duration: int` - Current event duration in minutes

---

## Testing Guidelines

### Test File Organization
```
tests/
├── __init__.py
├── local_api_test.py      # Client API tests
└── models_test.py         # Model deserialization tests
```

### Test Fixture Pattern
```python
import pytest
import pytest_asyncio
from watergate_local_api import WatergateLocalApiClient

@pytest_asyncio.fixture
async def client():
    """Provide a test client instance."""
    return WatergateLocalApiClient(base_url="http://testserver")
```

### Mock Response Scenarios

**Success Response**:
```python
with aioresponses() as mock:
    mock.get("http://testserver/api/sonic/endpoint", payload={"field": "value"})
    result = await client.async_method()
```

**Error Status Code**:
```python
with aioresponses() as mock:
    mock.get("http://testserver/api/sonic/endpoint", status=500)
    with pytest.raises(WatergateApiException):
        await client.async_method()
```

**Network Exception**:
```python
with aioresponses() as mock:
    mock.get("http://testserver/api/sonic/endpoint", exception=aiohttp.ClientError)
    with pytest.raises(WatergateApiException):
        await client.async_method()
```

### Critical Test Cases

Every API method must test:
1. ✅ Successful response with valid data
2. ✅ 500 Internal Server Error (triggers retry and exception)
3. ✅ Network errors (ClientError, TimeoutError)
4. ✅ Missing optional fields (shouldn't crash)
5. ✅ Rate limiting (429 status)
6. ✅ Authentication errors (403 status)

Every model must test:
1. ✅ Complete valid data deserialization
2. ✅ Missing optional fields (None defaults)
3. ✅ Nested object handling
4. ✅ Empty dict handling

---

## Quality Standards

### Code Quality Metrics
- **Test Coverage**: Minimum 80% line coverage
- **Type Hints**: All public methods must have type hints
- **Docstrings**: All public classes and methods need docstrings
- **Logging**: All network errors must be logged

### Documentation Requirements
- **Docstring Format**: Google style
- **API Method Format**: `"{HTTP_METHOD} {endpoint} - {description}"`
- **Examples**: All public APIs should have usage examples

### Performance Expectations
- **Timeout**: Default 10s, configurable
- **Retry Delay**: 1s between attempts
- **Session Reuse**: Single session per client instance
- **Memory**: Minimal - no caching, streaming responses

### Security Considerations
- **No credentials storage**: Client doesn't handle authentication
- **HTTPS support**: Works with https:// URLs
- **Input validation**: Done by device API, not client
- **Webhook security**: Consumer's responsibility to validate

---

## Change Management

### When to Update This Document

**MANDATORY updates required for**:
- ✅ New API endpoints
- ✅ New models or data structures
- ✅ Changed retry logic or error handling
- ✅ New dependencies
- ✅ Breaking changes to public API
- ✅ New webhook event types
- ✅ Changed media types or versioning

**RECOMMENDED updates for**:
- New test patterns
- Performance optimizations
- Bug fix patterns
- Documentation improvements
- Example code updates

### Update Process
1. Make code changes
2. Update relevant sections in this document
3. Update `.github/copilot-instructions.md` if patterns changed
4. Verify documentation accuracy
5. Commit documentation with code changes

### Version History
- **2024.4.1**: Initial comprehensive documentation
- *(Add entries for each significant update)*

---

## Quick Reference Card

### Virtual Environment Commands (ALWAYS RUN FIRST)
```bash
# Activate venv (REQUIRED before any other command)
source .venv/bin/activate

# Verify activation
which python  # Should show: .../watergate-local-api-python/.venv/bin/python

# Deactivate when done
deactivate
```

### Common Commands (Run AFTER activating venv)
```bash
# FIRST: Activate venv
source .venv/bin/activate

# Install package
pip install .

# Install dev dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run specific test file
pytest tests/local_api_test.py

# Run with coverage
pytest --cov=watergate_local_api

# Build package
python setup.py sdist bdist_wheel
```

### Common Import Patterns
```python
# Client usage
from watergate_local_api import WatergateLocalApiClient, WatergateApiException

# Models
from watergate_local_api.models import (
    DeviceState,
    TelemetryData,
    NetworkingData,
    AutoShutOffState,
    AutoShutOffReport,
    WebhookEvent
)
```

### Quick Debug Checklist
- [ ] **Is venv activated?** (Check for `.venv` in prompt)
- [ ] Is method async?
- [ ] Using aiohttp (not requests)?
- [ ] Session being closed?
- [ ] Retry logic implemented?
- [ ] Correct media type headers?
- [ ] Logging errors?
- [ ] Returning Optional[Model]?
- [ ] Tests written?
- [ ] **Tests run in venv?** (`pytest` after `source .venv/bin/activate`)

---

**Document Version**: 1.0  
**Last Updated**: 2024-10-27  
**Maintainers**: All contributors must keep this updated  
**Review Frequency**: After every PR that touches architecture or patterns
