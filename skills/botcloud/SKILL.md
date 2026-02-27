# BotCloud Skill

Use this skill when the user wants to manage BotCloud workers or distribute tasks across multiple agents.

## Triggers

- "botcloud" / "bot cloud" / "BotCloud"
- "start workers" / "spawn workers"
- "worker pool"
- "distributed agents"
- "parallel tasks"

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

### Submit Task to Specific Worker
```
botcloud task <worker> <task>
botcloud worker-0 "read file.txt"
```
Example: `botcloud task worker-0 "do something"`

### Submit Task to Any Worker (Parallel)
```
botcloud any "<task>"
```
Distributes task to next available worker (round-robin).

### Get Stats
```
botcloud stats
```
Returns detailed BotCloud network statistics.

## Worker Commands

Workers understand these commands:

- `read <filename>` - Read file from workspace
- `write <filename> <content>` - Write file to workspace
- `ls [dir]` - List files in workspace
- `mkdir <dir>` - Create directory
- `rm <file>` - Delete file
- `exec <command>` - Run shell command
- `info` - Worker info

## Implementation

The BotCloud manager is at: `botcloud/manager.py`

```python
import sys
sys.path.insert(0, '/home/openryanclaw/.openclaw/workspace')
from botcloud.manager import BotCloudManager, get_manager

# Get or create manager (singleton)
manager = get_manager()

# Start API (if not running)
manager.start_api()

# Spawn workers
workers = manager.spawn_workers(5)

# Submit to specific worker
result = manager.submit_task("worker-0", "read myfile.txt")

# Submit to any available worker (parallel)
result = manager.submit_task_any("echo hello")

# Batch submit
for i in range(10):
    manager.submit_task_any(f"process item {i}")

# Get status
stats = manager.get_stats()
print(f"Running: {stats['running_workers']}/{stats['total_workers']}")

# Cleanup
manager.stop_all()
```

## Notes

- Workers have real capabilities (file ops, shell exec)
- Round-robin distribution for `submit_task_any()`
- Each worker gets unique ID: "worker-0", "worker-1", etc.
- Workspace: `/home/openryanclaw/botcloud/workspace`
- Default port: 8000
