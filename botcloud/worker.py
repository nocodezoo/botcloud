#!/usr/bin/env python3
"""
BotCloud Worker with Full Capabilities
Tools: shell, file, memory, cron, git, pushover, browser, http, screenshot, composio, delegate, hardware
"""

import sys
import os
import subprocess
import shutil
import json
import re
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    _HAS_APSCHEDULER = True
except ImportError:
    _HAS_APSCHEDULER = False
    BackgroundScheduler = None

API_URL = os.environ.get("BOTCLOUD_API", "http://localhost:8000")
AGENT_ID = os.environ.get("BOTCLOUD_AGENT_ID", "")
API_KEY = os.environ.get("BOTCLOUD_API_KEY", "")
POLL_INTERVAL = int(os.environ.get("BOTCLOUD_POLL_INTERVAL", "2"))
WORKSPACE = os.environ.get("BOTCLOUD_WORKSPACE", "/home/openryanclaw/botcloud/workspace")
COMPOSIO_API_KEY = os.environ.get("COMPOSIO_API_KEY", "")

os.makedirs(WORKSPACE, exist_ok=True)

# In-memory scheduler for cron tasks
_scheduler = BackgroundScheduler() if _HAS_APSCHEDULER else None
if _scheduler:
    _scheduler.start()


# ============ SHELL ============

def exec_shell(cmd: str) -> str:
    """Execute a shell command"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            return result.stdout if result.stdout else "OK"
        return f"Error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"


# ============ FILE ============

def read_file(filepath: str) -> str:
    try:
        full_path = os.path.join(WORKSPACE, filepath)
        if not os.path.exists(full_path):
            if os.path.exists(filepath):
                with open(filepath) as f:
                    return f.read()
            return f"File not found: {filepath}"
        with open(full_path) as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"


def write_file(filepath: str, content: str) -> str:
    try:
        full_path = os.path.join(WORKSPACE, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
        return f"Wrote to {filepath} ({len(content)} bytes)"
    except Exception as e:
        return f"Error: {str(e)}"


def list_files(dirpath: str = "") -> str:
    try:
        full_path = os.path.join(WORKSPACE, dirpath) if dirpath else WORKSPACE
        if not os.path.exists(full_path):
            return f"Directory not found: {dirpath}"
        items = []
        for item in os.listdir(full_path):
            full_item = os.path.join(full_path, item)
            items.append(item + "/" if os.path.isdir(full_item) else item)
        return "\n".join(items) if items else "Empty"
    except Exception as e:
        return f"Error: {str(e)}"


def delete_file(filepath: str) -> str:
    try:
        full_path = os.path.join(WORKSPACE, filepath)
        if not os.path.exists(full_path):
            return f"Not found: {filepath}"
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        return f"Deleted: {filepath}"
    except Exception as e:
        return f"Error: {str(e)}"


def make_directory(dirpath: str) -> str:
    try:
        full_path = os.path.join(WORKSPACE, dirpath)
        os.makedirs(full_path, exist_ok=True)
        return f"Created: {dirpath}/"
    except Exception as e:
        return f"Error: {str(e)}"


# ============ MEMORY ============

_memory_store = {}


def memory_set(key: str, value: str) -> str:
    """Store a memory"""
    _memory_store[key] = {"value": value, "timestamp": datetime.now().isoformat()}
    return f"Memory set: {key}"


def memory_get(key: str) -> str:
    """Get a memory"""
    if key in _memory_store:
        mem = _memory_store[key]
        return f"{key}: {mem['value']} (at {mem['timestamp']})"
    return f"No memory: {key}"


def memory_list() -> str:
    """List all memories"""
    if not _memory_store:
        return "No memories stored"
    return "\n".join(f"- {k}: {v['value'][:50]}" for k, v in _memory_store.items())


def memory_delete(key: str) -> str:
    """Delete a memory"""
    if key in _memory_store:
        del _memory_store[key]
        return f"Deleted: {key}"
    return f"Not found: {key}"


# ============ CRON/SCHEDULE ============

_scheduled_tasks = {}


def schedule_task(cron_expr: str, task: str) -> str:
    """Schedule a task (simple interval: every N seconds/minutes/hours)"""
    # Simple format: "every 30s", "every 5m", "every 1h"
    match = re.match(r"every\s+(\d+)\s*([smh])", cron_expr.lower())
    if not match:
        return "Usage: every <number><s|m|h> (e.g., every 30s, every 5m)"
    
    value, unit = int(match.group(1)), match.group(2)
    
    if unit == "s":
        interval = value
    elif unit == "m":
        interval = value * 60
    else:
        interval = value * 3600
    
    job_id = f"job_{len(_scheduled_tasks)}"
    
    def run_task():
        # Execute and optionally report back
        result = process_single_task(task)
        print(f"[Scheduled] {task} -> {result[:50]}")
    
    _scheduler.add_job(run_task, 'interval', seconds=interval, id=job_id)
    _scheduled_tasks[job_id] = {"task": task, "interval": interval}
    
    return f"Scheduled: {task} every {value}{unit} (job_id: {job_id})"


def list_scheduled() -> str:
    """List scheduled tasks"""
    if not _scheduled_tasks:
        return "No scheduled tasks"
    lines = []
    for job_id, info in _scheduled_tasks.items():
        interval = info["interval"]
        if interval < 60:
            unit = "s"
        elif interval < 3600:
            unit = "m"
            interval //= 60
        else:
            unit = "h"
            interval //= 3600
        lines.append(f"- {job_id}: {info['task']} every {interval}{unit}")
    return "\n".join(lines)


def unschedule_task(job_id: str) -> str:
    """Remove a scheduled task"""
    if job_id in _scheduled_tasks:
        _scheduler.remove_job(job_id)
        del _scheduled_tasks[job_id]
        return f"Removed: {job_id}"
    return f"Not found: {job_id}"


# ============ GIT ============

def git_command(args: str) -> str:
    """Run git commands"""
    # Security: only allow safe git commands
    allowed = {"status", "log", "diff", "branch", "checkout", "add", "commit", "push", "pull", "clone", "init"}
    
    parts = args.split()
    if not parts:
        return "Usage: git <command> [args]"
    
    cmd = parts[0]
    if cmd not in allowed:
        return f"Git command not allowed: {cmd}. Allowed: {allowed}"
    
    try:
        result = subprocess.run(
            ["git"] + parts,
            capture_output=True, text=True, timeout=30, cwd=WORKSPACE
        )
        if result.returncode == 0:
            return result.stdout[:2000] if result.stdout else "OK"
        return f"Error: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"


# ============ PUSHOVER ============

def send_pushover(message: str, title: str = "BotCloud") -> str:
    """Send Pushover notification"""
    token = os.environ.get("PUSHOVER_TOKEN", "")
    user = os.environ.get("PUSHOVER_USER", "")
    
    if not token or not user:
        return "Pushover not configured. Set PUSHOVER_TOKEN and PUSHOVER_USER"
    
    try:
        import requests
        resp = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={"token": token, "user": user, "message": message, "title": title},
            timeout=10
        )
        if resp.status_code == 200:
            return f"Notification sent: {message[:50]}"
        return f"Failed: {resp.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


# ============ BROWSER ============

def browser_open(url: str) -> str:
    """Open a URL in browser"""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    try:
        import webbrowser
        webbrowser.open(url)
        return f"Opened: {url}"
    except Exception as e:
        return f"Error: {str(e)}"


def browser_screenshot(name: str = "screenshot.png") -> str:
    """Take a screenshot"""
    try:
        # Try different methods
        try:
            import pyscreenshot
            img = pyscreenshot.grab()
            path = os.path.join(WORKSPACE, name)
            img.save(path)
            return f"Screenshot saved: {name}"
        except:
            pass
        
        # Try gnome-screenshot
        result = subprocess.run(["gnome-screenshot", "-f", name], capture_output=True, text=True)
        if result.returncode == 0:
            return f"Screenshot: {name}"
        
        return "Screenshot tool not available"
    except Exception as e:
        return f"Error: {str(e)}"


# ============ HTTP REQUEST ============

def http_request(request_def: str) -> str:
    """Make HTTP request"""
    parts = request_def.split(None, 2)
    if len(parts) < 2:
        return "Usage: http <METHOD> <URL> [body]"
    
    method, url = parts[0].upper(), parts[1]
    body = parts[2] if len(parts) > 2 else None
    
    try:
        import requests
        kwargs = {"url": url, "timeout": 15, "headers": {"User-Agent": "BotCloud/1.0"}}
        
        if method == "GET":
            pass
        elif method in ("POST", "PUT"):
            kwargs["json"] = {"body": body} if body else {}
        elif method == "DELETE":
            pass
        else:
            return f"Unsupported: {method}"
        
        resp = requests.request(method, **kwargs)
        return f"HTTP {resp.status_code}\n\n{resp.text[:1500]}"
    except Exception as e:
        return f"HTTP error: {str(e)}"


# ============ SCREENSHOT (standalone) ============

def take_screenshot(name: str = None) -> str:
    """Take screenshot - alias for browser_screenshot"""
    if not name:
        name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    return browser_screenshot(name)


# ============ COMPOSIO (opt-in) ============

def composio_action(action: str, params: str = "") -> str:
    """Execute Composio action (opt-in)"""
    if not COMPOSIO_API_KEY:
        return "Composio not enabled. Set COMPOSIO_API_KEY to enable."
    
    try:
        import requests
        
        # Parse action and params
        # Format: "action_name param1=value1 param2=value2"
        parts = params.split() if params else []
        param_dict = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                param_dict[k] = v
        
        resp = requests.post(
            "https://api.composio.dev/v1/actions/execute",
            headers={"x-api-key": COMPOSIO_API_KEY, "Content-Type": "application/json"},
            json={"action": action, "params": param_dict},
            timeout=30
        )
        
        if resp.status_code == 200:
            return f"Action executed: {action}\n{resp.json()}"
        return f"Failed: {resp.status_code} - {resp.text}"
    except Exception as e:
        return f"Error: {str(e)}"


# ============ DELEGATE ============

def delegate_to_openclaw(task: str) -> str:
    """Delegate task to OpenClaw"""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    
    try:
        from botcloud.openclaw_connector import OpenClawConnector
        
        openclaw_url = os.environ.get("OPENCLAW_URL", "http://localhost:8080")
        connector = OpenClawConnector(openclaw_url=openclaw_url)
        
        health = connector.health_check()
        if health["status"] != "healthy":
            return f"OpenClaw unreachable: {health.get('error', 'unknown')}"
        
        result = connector.delegate_task(task, timeout=120)
        
        if result["status"] == "completed":
            res = result.get("result", {})
            if isinstance(res, dict):
                return f"OpenClaw: {res.get('content', res)}"
            return f"OpenClaw: {res}"
        return f"OpenClaw error: {result.get('error', result.get('status'))}"
    except ImportError:
        return "OpenClaw connector not available"
    except Exception as e:
        return f"Delegate error: {str(e)}"


# ============ HARDWARE ============

def hardware_status() -> str:
    """Get hardware status"""
    try:
        import psutil
        
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return f"""Hardware Status:
CPU: {cpu}%
Memory: {mem.percent}% ({mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB)
Disk: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)"""
    except ImportError:
        return "psutil not installed. Install: pip install psutil"
    except Exception as e:
        return f"Error: {str(e)}"


def hardware_reboot() -> str:
    """Reboot system (requires root)"""
    return "Reboot disabled for safety. Use exec sudo reboot manually."


def hardware_shutdown() -> str:
    """Shutdown system (requires root)"""
    return "Shutdown disabled for safety. Use exec sudo shutdown manually."


def hardware_processes() -> str:
    """List top processes"""
    try:
        import psutil
        procs = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']), 
                      key=lambda x: x.info['cpu_percent'] or 0, reverse=True)[:10]
        
        lines = ["Top Processes:"]
        for p in procs:
            lines.append(f"  {p.info['pid']}: {p.info['name']} ({p.info['cpu_percent']}%)")
        return "\n".join(lines)
    except:
        return "Could not get processes"


# ============ NETWORK ============

def web_search(query: str) -> str:
    """Web search - delegates to OpenClaw"""
    if not query:
        return "Usage: search <query>"
    return delegate_to_openclaw(f"search: {query}")


def fetch_url(url: str) -> str:
    """Fetch web page"""
    if not url:
        return "Usage: fetch <url>"
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    try:
        import requests
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            return f"=== {url} ===\n\n{resp.text[:2000]}"
        return f"Fetch failed: HTTP {resp.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


# ============ MATH ============

def calculate(expr: str) -> str:
    """Math calculation"""
    if not expr:
        return "Usage: math <expression>"
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expr):
        return "Error: Only basic math allowed"
    try:
        result = eval(expr, {"__builtins__": {}}, {})
        return f"{expr} = {result}"
    except Exception as e:
        return f"Math error: {str(e)}"


# ============ MAIN PROCESSOR ============

def process_single_task(task_input: str) -> str:
    """Process a single task"""
    task = task_input.strip()
    parts = task.split(None, 1)
    cmd = parts[0].lower() if parts else ""
    arg = parts[1] if len(parts) > 1 else ""
    
    # Shell
    if cmd in ("exec", "run", "sh"):
        return exec_shell(arg)
    
    # File ops
    if cmd == "read":
        return read_file(arg)
    if cmd == "write":
        if " " in arg:
            idx = arg.index(" ")
            return write_file(arg[:idx], arg[idx+1:])
        return "Usage: write <filename> <content>"
    if cmd in ("ls", "list"):
        return list_files(arg)
    if cmd in ("rm", "delete"):
        return delete_file(arg)
    if cmd == "mkdir":
        return make_directory(arg)
    
    # Memory
    if cmd == "memory" or cmd == "mem":
        sub = arg.split(None, 1)
        if not sub:
            return memory_list()
        if sub[0] == "set" and len(sub) > 1:
            parts2 = sub[1].split(None, 1)
            if len(parts2) == 2:
                return memory_set(parts2[0], parts2[1])
        if sub[0] == "get":
            return memory_get(sub[1] if len(sub) > 1 else "")
        if sub[0] == "del":
            return memory_delete(sub[1] if len(sub) > 1 else "")
        return "Usage: memory [set <key> <val>|get <key>|del <key>|list]"
    
    # Cron
    if cmd == "cron" or cmd == "schedule":
        sub = arg.split(None, 1)
        if sub[0] == "add":
            parts2 = sub[1].split(None, 1)
            if len(parts2) == 2:
                return schedule_task(parts2[0], parts2[1])
        if sub[0] == "list":
            return list_scheduled()
        if sub[0] == "remove":
            return unschedule_task(sub[1] if len(sub) > 1 else "")
        return "Usage: cron [add <interval> <task>|list|remove <job_id>]"
    
    # Git
    if cmd == "git":
        return git_command(arg)
    
    # Pushover
    if cmd == "push":
        sub = arg.split(None, 1)
        if len(sub) == 2:
            return send_pushover(sub[1], sub[0] if sub[0] else "BotCloud")
        return send_pushover(arg)
    
    # Browser
    if cmd == "open" or cmd == "browse":
        return browser_open(arg)
    if cmd == "screenshot" or cmd == "screen":
        return take_screenshot(arg if arg else None)
    
    # HTTP
    if cmd == "http":
        return http_request(arg)
    if cmd in ("curl", "fetch", "wget"):
        return fetch_url(arg)
    
    # Composio
    if cmd == "composio" or cmd == "action":
        sub = arg.split(None, 1)
        return composio_action(sub[0], sub[1] if len(sub) > 1 else "")
    
    # Delegate
    if cmd == "delegate":
        return delegate_to_openclaw(arg)
    
    # Hardware
    if cmd == "hardware" or cmd == "sys":
        sub = arg.split(None, 1) if arg else []
        if not sub or sub[0] == "status":
            return hardware_status()
        if sub[0] == "processes":
            return hardware_processes()
        return "Usage: hardware [status|processes]"
    
    # Network
    if cmd == "search":
        return web_search(arg)
    if cmd == "math" or cmd == "calc":
        return calculate(arg)
    
    # Info
    if cmd == "info":
        return f"Worker: {AGENT_ID}\nWorkspace: {WORKSPACE}\nAPI: {API_URL}"
    
    if cmd == "help":
        return """BotCloud Worker Commands:

FILE: read, write, ls, mkdir, rm
SHELL: exec <cmd>, run <cmd>
MEMORY: memory [set|get|del|list]
CRON: cron [add|list|remove]
GIT: git <command>
PUSHOVER: push <message>
BROWSER: open <url>, screenshot [name]
HTTP: http <METHOD> <URL>
SEARCH: search <query>
MATH: math <expr>
COMPOSIO: composio <action> [params]
DELEGATE: delegate <task>
HARDWARE: hardware [status|processes]
INFO: info"""
    
    # Default: shell
    return exec_shell(task)


def main():
    """Main worker loop"""
    import requests
    
    print(f"Worker {AGENT_ID} starting...")
    print(f"Workspace: {WORKSPACE}")
    
    while True:
        try:
            resp = requests.get(f"{API_URL}/agents/{AGENT_ID}/tasks", timeout=5)
            if resp.status_code == 200:
                tasks = resp.json().get("tasks", [])
                
                for task in tasks:
                    if task.get("status") == "pending":
                        task_id = task["id"]
                        task_input = task.get("input", "")
                        print(f"→ Task {task_id}: {task_input[:50]}...")
                        
                        result = process_single_task(task_input)
                        
                        requests.post(
                            f"{API_URL}/tasks/{task_id}/complete",
                            headers={"X-API-Key": API_KEY},
                            json={"output": result}
                        )
                        print(f"✓ Task {task_id} completed")
        
        except Exception as e:
            print(f"Error: {e}")
        
        import time
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
