# GitHub Copilot Instructions for Watergate Local API Python Client

## Project Overview
This is a Python client library for the **Watergate/Sonic Device Local API**. It provides async HTTP communication with water monitoring and control devices.

## Core Technologies
- **Language**: Python 3.x
- **Async Framework**: `aiohttp` for all HTTP operations
- **Testing**: `pytest` with `pytest-asyncio` and `aioresponses`
- **Package Management**: setuptools
- **Virtual Environment**: `.venv/` - ALWAYS use the project's venv for all operations

## 🚨 CRITICAL: Virtual Environment Usage

**ALWAYS activate and use the project's virtual environment (`.venv/`) for ALL operations:**

- ✅ **CORRECT**: Activate venv before running any Python commands
  ```bash
  source .venv/bin/activate  # On macOS/Linux
  .venv\Scripts\activate     # On Windows
  ```

- ❌ **WRONG**: Running Python commands without activating venv
  ```bash
  python -m pytest  # DON'T do this without venv activated
  pip install aiohttp  # DON'T do this in global environment
  ```

### Virtual Environment Rules
1. **Always activate venv first** before any pip install, pytest, or python commands
2. **Never install packages globally** - all dependencies go in `.venv/`
3. **Check venv is activated** - prompt should show `(.venv)` prefix
4. **Create venv if missing**: `python3 -m venv .venv`
5. **When running tests**: Activate venv, then run `pytest`
6. **When installing dependencies**: Activate venv, then run `pip install -r requirements.txt`

## Critical Design Patterns

### 1. Async-First Architecture
- ALL API methods MUST be async (`async def`)
- Use `aiohttp.ClientSession` for HTTP operations
- Session management via context manager (`async with`)
- Never use synchronous HTTP libraries (requests, urllib, etc.)

### 2. Session Management Pattern
```python
# Session is lazily initialized and reused
async def _ensure_session(self):
    if self._session is None or self._session.closed:
        self._session = aiohttp.ClientSession(...)
```
- Session is created on first use or when closed
- Must be properly closed in `__aexit__` or `async_close()`
- Supports context manager usage

### 3. Retry Logic Pattern
- ALL network operations retry 3 times (using `RETRY_ATTEMPTS = range(3)`)
- 1-second sleep between retries
- Raises `WatergateApiException` after exhausting retries
- Pattern:
```python
for attempt in RETRY_ATTEMPTS:
    try:
        # operation
        if success:
            return result
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        _LOGGER.error("Network error: %s", e)
    await asyncio.sleep(1)
raise WatergateApiException("Failed after 3 attempts")
```

### 4. Content Type Versioning
- Uses versioned media types (e.g., `application/vnd.wtg.local.device-state.v1+json`)
- Accept header for GET requests
- Content-Type header for PUT/PATCH requests
- MUST match API specifications exactly

## Data Model Conventions

### Model Structure
- All models use `from_dict(cls, data: dict)` class method for deserialization
- Field names defined as module-level constants (e.g., `VALVE_STATE_FIELD = "valveState"`)
- Use `data.get(FIELD_NAME)` for safe field access (returns None if missing)
- No serialization to dict (one-way deserialization only)

### Field Mapping Pattern
```python
FIELD_NAME_CONSTANT = "apiFieldName"

class Model:
    def __init__(self, field_name: type):
        self.field_name = field_name
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(field_name=data.get(FIELD_NAME_CONSTANT))
```

### Nested Objects
- Use conditional instantiation for optional nested objects:
```python
Event(**data.get(EVENT_FIELD)) if data.get(EVENT_FIELD) else None
```

## API Endpoints Pattern

### Endpoint URLs
- Base URL: `{base_url}/api/sonic`
- Endpoint constants defined at module level
- Examples: `VALVE_URL = "/valve"`, `TELEMETRY_URL = "/telemetry"`

### HTTP Method Patterns
- **GET**: Use `_get(url, headers)` helper → returns Optional[dict]
- **PUT**: Use `_put(url, headers, data)` helper → returns bool
- **PATCH**: Implement inline with retry logic → returns bool

### Response Status Codes
- **200**: Success with JSON body
- **204**: Success with no content
- **Others**: Log error and retry or raise exception

## Webhook Event System

### Event Types
1. `auto-shut-off-report` → `AutoShutOffReportData`
2. `telemetry` → `TelemetryEventData`
3. `valve` → `ValveEventData`
4. `power-supply-changed` → `PowerSupplyChangedEventData`
5. `wifi-changed` → `WifiChangedEventData`
6. `online` → `OnlineEvent`

### Event Parsing
- Use `WebhookEvent.parse_webhook_event(data)` to parse raw webhook payload
- Returns appropriate typed event object
- Raises `ValueError` for unknown event types

## Testing Requirements

### Test Structure
- Use `pytest` with `pytest-asyncio` for async tests
- Mock HTTP with `aioresponses`
- All tests marked with `@pytest.mark.asyncio`
- Fixture pattern:
```python
@pytest_asyncio.fixture
async def client():
    return WatergateLocalApiClient(base_url="http://testserver")
```

### Test Coverage Areas
1. **Happy paths**: Successful API calls with valid responses
2. **Error handling**: Network errors, timeouts, invalid status codes
3. **Retry logic**: Ensure 3 attempts before exception
4. **Edge cases**: Missing fields, None values, empty responses
5. **Status codes**: 200, 204, 400, 403, 429, 500

### Mock Response Pattern
```python
with aioresponses() as mock:
    mock.get("http://testserver/api/sonic/endpoint", payload={...})
    # or
    mock.get("http://testserver/api/sonic/endpoint", status=500)
    # or
    mock.get("http://testserver/api/sonic/endpoint", exception=aiohttp.ClientError)
    
    result = await client.async_method()
    assert result.field == expected_value
```

## Logging Standards
- Use Python's `logging` module
- Logger name: `__name__` (module-specific)
- Log levels:
  - `DEBUG`: Session creation/closure, detailed flow
  - `ERROR`: Network errors, API failures, retry attempts
- Log format: `"Message: %s", variable` (not f-strings for performance)

## Error Handling

### Exception Hierarchy
- `WatergateApiException`: Base exception for all API errors
- Inherit from `Exception`
- Raised when retries exhausted or critical errors occur

### Error Sources
1. Network errors: `aiohttp.ClientError`
2. Timeouts: `asyncio.TimeoutError`
3. Invalid responses: Log and retry
4. Unknown webhook types: `ValueError`

## Naming Conventions

### Methods
- API methods: `async_<action>_<resource>` (e.g., `async_get_device_state`)
- Private helpers: `_<name>` (e.g., `_get`, `_ensure_session`)

### Classes
- PascalCase for all classes
- Descriptive names ending in purpose: `Data`, `State`, `Report`, `Event`

### Constants
- SCREAMING_SNAKE_CASE for all constants
- Suffix: `_URL` for endpoints, `_FIELD` for JSON fields, `_HEADER` for HTTP headers

### Variables
- snake_case for all variables
- Descriptive names (e.g., `device_state`, not `ds`)

## File Organization

### Directory Structure
```
watergate_local_api/
├── __init__.py          # Package exports
├── watergate_api.py     # Main client class
└── models/
    ├── __init__.py      # Model exports
    ├── device_state.py
    ├── telemetry_data.py
    ├── networking.py
    ├── auto_shut_off_state.py
    ├── auto_shut_off_report.py
    ├── webhook_model.py
    ├── water_event.py
    └── water_meter.py
```

### Import Conventions
- Models imported in `models/__init__.py`
- Client and exception imported in package `__init__.py`
- Absolute imports from package root

## Version Management
- Version stored in `version.txt` file
- Format: `YYYY.MAJOR.MINOR` (e.g., `2024.4.1`)
- Read by `setup.py` during package build

## Package Configuration
- License: GPL-3.0
- Repository: `hero-laboratories/watergate-local-api-python`
- Dependencies defined in `requirements.txt`
- Package name: `watergate_local_api`

## Common Pitfalls to Avoid

1. **Don't create synchronous methods** - Everything must be async
2. **Don't forget retry logic** - All network operations need retries
3. **Don't hardcode URLs** - Use base_url + constants
4. **Don't forget session cleanup** - Always close sessions
5. **Don't use requests library** - Only aiohttp
6. **Don't ignore optional fields** - Use `.get()` for safe access
7. **Don't forget content-type versioning** - Match API specs exactly
8. **Don't skip error logging** - Log all network errors
9. **Don't forget async context managers** - Support `async with`
10. **Don't create models without from_dict** - All models need deserialization

## Development Workflow

### Environment Setup (REQUIRED FIRST)
**Before ANY development work:**
```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify installation
pytest --version
```

### Adding New API Endpoint
1. **ACTIVATE VENV FIRST**: `source .venv/bin/activate`
2. Define endpoint URL constant
3. Define versioned Accept/Content-Type headers
4. Create async method in `WatergateLocalApiClient`
5. Implement retry logic
6. Create/update model class if needed
7. Add comprehensive tests (run with `pytest` in activated venv)
8. Update this documentation

### Adding New Model
1. **ACTIVATE VENV FIRST**: `source .venv/bin/activate`
2. Create file in `models/` directory
3. Define field constants at module level
4. Create class with `__init__` and `from_dict`
5. Export in `models/__init__.py`
6. Add tests in `tests/models_test.py` (run with `pytest` in activated venv)
7. Update this documentation

### Adding New Webhook Event
1. **ACTIVATE VENV FIRST**: `source .venv/bin/activate`
2. Add event data class in `webhook_model.py`
3. Update `WebhookEvent.parse_webhook_event()` method
4. Add event type to documentation
5. Create tests for event parsing (run with `pytest` in activated venv)
6. Update this documentation

---

## 🚨 IMPORTANT: Keep This File Updated!

**After any significant change to the codebase, this file MUST be updated to reflect:**
- New API endpoints or methods
- New models or data structures
- Changed patterns or conventions
- New dependencies or requirements
- Updated error handling approaches
- Modified testing strategies

**This ensures all AI agents have accurate, up-to-date information about the codebase architecture and patterns.**
