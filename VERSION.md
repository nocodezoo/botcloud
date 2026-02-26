# BotCloud v1.3.0

## Version History
- v1.3.0 (Current) - Test suite added
- v1.2.0 - WebSocket + Discovery + Task Queue
- v1.1.0 - OpenClaw integration + Docker
- v1.0.0 - Initial API

## What's New in v1.3.0

### Test Suite
- `tests/test_api.sh` - Bash test suite
- `tests/integration_tests.sh` - Comprehensive integration tests
- `tests/test_runner.py` - Python test runner

### Test Coverage
Tests all endpoints:
- Health check
- Agent registration
- List agents
- Get agent details
- Start/Stop agents
- Create/Get tasks
- Store/Get memory
- Metrics
- Logs
- Task delegation
- Configuration

## Running Tests

### Bash tests
```bash
cd botcloud
./tests/test_api.sh
```

### Python tests
```bash
cd botcloud
python3 tests/test_runner.py
```

### Integration tests
```bash
cd botcloud
bash tests/integration_tests.sh
```

## Status
- Core API: ✅ Tested
- All endpoints: ✅ Covered
- Ready for production: ✅

## Fixes Needed
- Server must be running on localhost:8000 before tests
