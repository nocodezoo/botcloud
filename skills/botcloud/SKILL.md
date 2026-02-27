# BotCloud Skill

Use this skill when the user wants to run commands via BotCloud workers.

## Trigger

- "botcloud" / "send to botcloud" / "botcloud do"

## How It Works

BotCloud runs distributed workers that can execute real commands on your machine.

## Usage

```python
from botcloud.handler import send_command, send_command_any, status

# Check status
print(status())  # BotCloud: healthy | Workers: 1/1

# Send command to a worker (specific)
result = send_command("exec ls -la")
result = send_command("math 100 + 200")
result = send_command("hardware status")

# Send to any available worker (parallel)
result = send_command_any("exec echo parallel")

# Stop BotCloud
from botcloud.handler import stop
stop()
```

## Commands Available to Workers

| Category | Commands |
|----------|----------|
| **Shell** | `exec <cmd>`, `run <cmd>` |
| **File** | `read <file>`, `write <file> <content>`, `ls`, `mkdir <dir>`, `rm <file>` |
| **Memory** | `memory set <key> <val>`, `memory get <key>`, `memory list`, `memory del <key>` |
| **Cron** | `cron add every 30s "task"`, `cron list`, `cron remove <job_id>` |
| **Git** | `git status`, `git log`, `git commit -m "msg"`, etc. |
| **HTTP** | `http GET <url>`, `http POST <url>`, etc. |
| **Math** | `math 2+2*3` |
| **Hardware** | `hardware status`, `hardware processes` |
| **Browser** | `open <url>`, `screenshot` |
| **Pushover** | `push <message>` (requires env vars) |
| **Delegate** | `delegate <task>` → forwards to OpenClaw |

## Starting BotCloud

BotCloud will auto-start when you use it. Or start manually:

```bash
cd botcloud
python3 api/main.py
# API runs on port 8000
```

## How to Tell Me

Just say:
- "send to botcloud exec ls"
- "botcloud do math 50*10"
- "botcloud hardware status"
- "botcloud write test.txt hello world"

I'll run it and return the result.
