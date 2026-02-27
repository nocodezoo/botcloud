# BotCloud v0.4.1 - With Start Scripts

## Quick Start

```bash
# Start everything
~/botcloud/scripts/start.sh

# Start a worker
~/botcloud/scripts/start_worker.sh fullstack

# Stop everything
~/botcloud/scripts/stop.sh
```

## Scripts

| Script | Description |
|--------|-------------|
| scripts/start.sh | Start API + Dashboard |
| scripts/start_worker.sh | Start a worker |
| scripts/stop.sh | Stop all services |

## Worker Types
- `fullstack` - FullStackDev (default)
- `smart` - SmartWorker  
- `worker` - Basic WorkerBot

## Access
- Dashboard: http://localhost:9090/dashboard.html
- API: http://localhost:8001

## Files
- api/main.py - API server
- agent/ - Worker agents
- dashboard.html - Dashboard
