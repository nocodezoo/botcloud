# BotCloud Skill

Use this skill when the user wants to manage BotCloud workers or distribute tasks across multiple agents.

## Triggers

- "botcloud" / "bot cloud" / "BotCloud"
- "start workers" / "spawn workers"
- "worker pool"
- "distributed agents"

## What BotCloud Does

BotCloud is a distributed task execution network that lets OpenClaw spawn multiple parallel worker agents. Each worker polls a queue and executes tasks independently.

**Use cases:**
- Parallel file processing (read/write many files)
- Concurrent API calls
- Batch operations
- Scaling agent capacity beyond single-threaded limits

## Commands

### Check Status
```
botcloud status
```
Returns: Number of workers, API health, worker details.

### Start Workers
```
botcloud start <count>
botcloud workers <count>
```
Example: `botcloud start 5` - Spawns 5 workers.

### Stop All
```
botcloud stop
```
Stops all workers and the API server.

### Submit Task
```
botcloud task <worker> <task>
```
Example: `botcloud task worker-0 "do something"`

### Get Stats
```
botcloud stats
```
Returns detailed BotCloud network statistics.

## Implementation

The BotCloud manager is at: `botcloud/manager.py`

```python
import sys
sys.path.insert(0, '/home/openryanclaw/.openclaw/workspace')
from botcloud.manager import BotCloudManager

# Initialize
manager = BotCloudManager()

# Start API
manager.start_api()

# Spawn workers
workers = manager.spawn_workers(5)

# Submit task
result = manager.submit_task("worker-0", "your task here")

# Get status
stats = manager.get_stats()

# Cleanup
manager.stop_all()
```

## Notes

- Workers auto-complete tasks immediately (the API simulates this)
- For real async work, workers need to actually process tasks
- The manager defaults to port 8000
- Each worker gets a unique ID like "worker-0", "worker-1", etc.
