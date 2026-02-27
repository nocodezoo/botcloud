#!/usr/bin/env python3
"""
BotCloud Worker with Real Capabilities
Can execute actual file ops, shell commands, and more
"""

import sys
import os
import subprocess
import shutil
import json

API_URL = os.environ.get("BOTCLOUD_API", "http://localhost:8000")
AGENT_ID = os.environ.get("BOTCLOUD_AGENT_ID", "")
API_KEY = os.environ.get("BOTCLOUD_API_KEY", "")
POLL_INTERVAL = int(os.environ.get("BOTCLOUD_POLL_INTERVAL", "2"))
WORKSPACE = os.environ.get("BOTCLOUD_WORKSPACE", "/home/openryanclaw/botcloud/workspace")

os.makedirs(WORKSPACE, exist_ok=True)

print(f"Worker {AGENT_ID} starting...")
print(f"Workspace: {WORKSPACE}")


def execute_command(cmd: str) -> str:
    """Execute a shell command"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return result.stdout if result.stdout else "OK"
        else:
            return f"Error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"


def read_file(filepath: str) -> str:
    """Read a file"""
    try:
        full_path = os.path.join(WORKSPACE, filepath)
        if not os.path.exists(full_path):
            # Try as absolute path
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return f.read()
            return f"File not found: {filepath}"
        with open(full_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading: {str(e)}"


def write_file(filepath: str, content: str) -> str:
    """Write a file"""
    try:
        full_path = os.path.join(WORKSPACE, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
        return f"Wrote to {filepath} ({len(content)} bytes)"
    except Exception as e:
        return f"Error writing: {str(e)}"


def list_files(dirpath: str = "") -> str:
    """List files in workspace"""
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
    """Delete a file or directory"""
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
    """Create a directory"""
    try:
        full_path = os.path.join(WORKSPACE, dirpath)
        os.makedirs(full_path, exist_ok=True)
        return f"Created: {dirpath}/"
    except Exception as e:
        return f"Error: {str(e)}"


def web_search(query: str) -> str:
    """Search the web - delegates to OpenClaw for best results"""
    if not query:
        return "Usage: search <query>"
    
    # Try DuckDuckGo instant
    try:
        import requests
        resp = requests.get(
            "https://duckduckgo.com/",
            params={"q": query, "ia": "answer"},
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        if resp.status_code == 200:
            # Check for instant answer
            import re
            # Look for related searches or quick answer
            results = re.findall(r'"query":"[^"]*","label":"([^"]+)"', resp.text)
            if results:
                return "Suggestions: " + ", ".join(results[:5])
    except:
        pass
    
    # Fallback: delegate to OpenClaw which has better search
    return delegate_to_openclaw(f"search: {query}")


def fetch_url(url: str) -> str:
    """Fetch a web page"""
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
        return f"Fetch error: {str(e)}"


def calculate(expr: str) -> str:
    """Evaluate a math expression"""
    if not expr:
        return "Usage: math <expression>"
    
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expr):
        return "Error: Only basic math allowed (+ - * /)"
    
    try:
        result = eval(expr, {"__builtins__": {}}, {})
        return f"{expr} = {result}"
    except Exception as e:
        return f"Math error: {str(e)}"


def make_http_request(request_def: str) -> str:
    """Make an HTTP request"""
    parts = request_def.split(None, 2)
    if len(parts) < 2:
        return "Usage: http <METHOD> <URL>"
    
    method = parts[0].upper()
    url = parts[1]
    body = parts[2] if len(parts) > 2 else None
    
    try:
        import requests
        kwargs = {"url": url, "timeout": 15}
        
        if method == "GET":
            pass
        elif method == "POST":
            kwargs["json"] = {"body": body} if body else {}
        elif method == "PUT":
            kwargs["json"] = {"body": body} if body else {}
        elif method == "DELETE":
            pass
        else:
            return f"Unsupported: {method}"
        
        resp = requests.request(method, **kwargs)
        return f"HTTP {resp.status_code}\n\n{resp.text[:1000]}"
    except Exception as e:
        return f"HTTP error: {str(e)}"


def delegate_to_openclaw(task: str) -> str:
    """Delegate a task to OpenClaw for processing"""
    # Import the connector
    import sys
    import os
    
    # Add workspace to path to import connector
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    
    try:
        from botcloud.openclaw_connector import OpenClawConnector
        
        openclaw_url = os.environ.get("OPENCLAW_URL", "http://localhost:8080")
        connector = OpenClawConnector(openclaw_url=openclaw_url)
        
        # Check if OpenClaw is reachable
        health = connector.health_check()
        if health["status"] != "healthy":
            return f"OpenClaw unreachable: {health.get('error', 'unknown')}"
        
        # Delegate the task
        result = connector.delegate_task(task, timeout=120)
        
        if result["status"] == "completed":
            # Extract result
            res = result.get("result", {})
            if isinstance(res, dict):
                return f"OpenClaw result: {res.get('content', res)}"
            return f"OpenClaw result: {res}"
        else:
            return f"OpenClaw error: {result.get('error', result.get('status'))}"
            
    except ImportError:
        return "OpenClaw connector not available"
    except Exception as e:
        return f"Delegate error: {str(e)}"


def process_task(task_input: str) -> str:
    """Process a task with actual capabilities"""
    task = task_input.strip()
    parts = task.split(None, 1)
    cmd = parts[0].lower() if parts else ""
    arg = parts[1] if len(parts) > 1 else ""
    
    # File operations
    if cmd == "read":
        return read_file(arg)
    
    elif cmd == "write":
        # Format: write <filename> <content>
        if " " in arg:
            space_idx = arg.index(" ")
            filepath = arg[:space_idx]
            content = arg[space_idx + 1:]
            return write_file(filepath, content)
        return "Usage: write <filename> <content>"
    
    elif cmd == "ls" or cmd == "list":
        return list_files(arg)
    
    elif cmd == "mkdir":
        return make_directory(arg)
    
    elif cmd == "rm" or cmd == "delete":
        return delete_file(arg)
    
    # Shell command execution
    elif cmd == "exec" or cmd == "run":
        return execute_command(arg)
    
    # Web search
    elif cmd == "search":
        return web_search(arg)
    
    # Fetch web page
    elif cmd == "fetch" or cmd == "curl":
        return fetch_url(arg)
    
    # Math calculation
    elif cmd == "math" or cmd == "calc":
        return calculate(arg)
    
    # Make HTTP request
    elif cmd == "http" or cmd == "request":
        return make_http_request(arg)
    
    # Delegate to OpenClaw (call back to OpenClaw API)
    elif cmd == "delegate":
        return delegate_to_openclaw(arg)
    
    # Get info
    elif cmd == "info":
        return f"Worker: {AGENT_ID}\nWorkspace: {WORKSPACE}\nAPI: {API_URL}"
    
    # Help
    elif cmd == "help":
        return """BotCloud Worker Commands:
FILE OPS:
- read <filename> - Read file
- write <filename> <content> - Write file
- ls [dir] - List files
- mkdir <dir> - Create directory
- rm <file> - Delete file

NETWORK:
- search <query> - Web search
- fetch <url> - Fetch web page
- http <METHOD> <URL> - Make HTTP request

COMPUTE:
- math <expression> - Calculate math
- exec <command> - Run shell command

AI:
- delegate <task> - Delegate to OpenClaw
- info - Worker info"""
    
    # Default: try as shell command
    return execute_command(task)


def main():
    """Main worker loop"""
    import requests
    import time
    
    print(f"Worker {AGENT_ID} polling for tasks...")
    
    while True:
        try:
            # Poll for tasks
            resp = requests.get(f"{API_URL}/agents/{AGENT_ID}/tasks", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                tasks = data.get("tasks", [])
                
                for task in tasks:
                    if task.get("status") == "pending":
                        task_id = task["id"]
                        task_input = task.get("input", "")
                        print(f"→ Task {task_id}: {task_input[:50]}...")
                        
                        # Process the task
                        result = process_task(task_input)
                        
                        # Mark complete
                        requests.post(
                            f"{API_URL}/tasks/{task_id}/complete",
                            headers={"X-API-Key": API_KEY},
                            json={"output": result}
                        )
                        print(f"✓ Task {task_id} completed")
                        
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
