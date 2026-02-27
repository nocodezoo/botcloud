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

## CLI Commands

```bash
# Check status
python3 botcloud/cli.py status

# Start workers
python3 botcloud/cli.py start 5

# Submit task to specific worker
python3 botcloud/cli.py task "exec echo hi" --worker worker-0

# Submit to any worker (parallel)
python3 botcloud/cli.py any "exec echo hi"

# Stop all
python3 botcloud/cli.py stop

# Detailed stats
python3 botcloud/cli.py stats
```

## Python API

```python
from botcloud.manager import BotCloudManager

manager = BotCloudManager()
manager.start_api()
workers = manager.spawn_workers(5)

# Specific worker
result = manager.submit_task("worker-0", "read file.txt")

# Any worker (parallel)
result = manager.submit_task_any("exec echo hi")

# With OpenClaw delegation
workers = manager.spawn_workers(5, openclaw_url="http://localhost:8080")

manager.stop_all()
```

## Worker Commands

- `read <filename>` - Read file
- `write <filename> <content>` - Write file
- `ls [dir]` - List files
- `mkdir <dir>` - Create directory
- `rm <file>` - Delete file
- `exec <command>` - Run shell command
- `delegate <task>` - Delegate to OpenClaw
- `info` - Worker info
