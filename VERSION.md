# BotCloud v1.2.0

## Version History
- v1.2.0 (Current) - Discovery + WebSocket + Task Queue
- v1.1.0 - OpenClaw integration + Docker
- v1.0.0 - Initial API

## What's New in v1.2.0

### WebSocket Server (port 8001)
Real-time agent communication:
- `/ws/connect/{agent_id}` - WebSocket endpoint
- Real-time messaging between agents
- Task delegation via WebSocket
- Agent discovery via WebSocket

### Discovery Service (port 8002)
Find agents by capabilities:
- `/register` - Register agent capabilities
- `/find?capabilities=search,browse` - Find agents by skills
- `/capabilities` - List all available capabilities

### Task Queue (port 8003)
Async task processing:
- `/submit` - Submit async task
- `/tasks/{id}` - Get task result
- `/status` - Queue status

## Services
| Port | Service | Description |
|------|---------|-------------|
| 8000 | Core API | Main REST API |
| 8001 | WebSocket | Real-time |
| 8002 | Discovery | Agent matching |
| 8003 | Task Queue | Async processing |

## Status
- Core API: ✅ Complete
- WebSocket: ✅ Complete  
- Discovery: ✅ Complete
- Task Queue: ✅ Complete
- Dashboard: 🔄 Next
