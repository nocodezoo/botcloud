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
    
    # Get info
    elif cmd == "info":
        return f"Worker: {AGENT_ID}\nWorkspace: {WORKSPACE}\nAPI: {API_URL}"
    
    # Help
    elif cmd == "help":
        return """BotCloud Worker Commands:
- read <filename> - Read file
- write <filename> <content> - Write file
- ls [dir] - List files
- mkdir <dir> - Create directory
- rm <file> - Delete file
- exec <command> - Run shell command
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
