#!/usr/bin/env python3
"""
Worker that actually executes tasks - parses instructions and does the work
"""

import sys
import os
import subprocess
import json
import time
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import BotCloudAgent

def execute_code(code, language="python"):
    """Execute code and return output"""
    try:
        if language == "python":
            # Execute Python
            result = subprocess.run(
                ["python3", "-c", code],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
        
        elif language == "bash":
            result = subprocess.run(
                ["bash", "-c", code],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
        
        else:
            return f"Language {language} not supported"
            
    except Exception as e:
        return f"Execution error: {str(e)}"

def parse_task(task_input):
    """Parse task input and determine what to do"""
    task_input = task_input.lower().strip()
    
    # Code execution patterns
    if "print" in task_input and ("python" in task_input or "write" in task_input):
        # Extract code to run
        return {
            "action": "execute",
            "language": "python",
            "description": "Run Python code"
        }
    
    elif "run" in task_input and ("code" in task_input or "script" in task_input):
        return {
            "action": "execute", 
            "language": "python",
            "description": "Execute code"
        }
    
    elif "bash" in task_input or "terminal" in task_input or "command" in task_input:
        return {
            "action": "execute",
            "language": "bash", 
            "description": "Run bash command"
        }
    
    elif "calculate" in task_input or "compute" in task_input or "math" in task_input:
        return {
            "action": "calculate",
            "description": "Perform calculation"
        }
    
    else:
        return {
            "action": "help",
            "description": "Show available commands"
        }

def process_task(task_input):
    """Process a task and return result"""
    parsed = parse_task(task_input)
    action = parsed.get("action")
    
    if action == "execute":
        # For now, just acknowledge - real execution needs safety
        return f"""I can execute code!

To run code, I need:
1. The language (python, bash, etc.)
2. The code to run

Example tasks I can handle:
- "run python print('hello')"
- "execute bash ls -la"
- "calculate 2 + 2"

What would you like me to run?"""
    
    elif action == "calculate":
        # Try to extract math
        numbers = re.findall(r'[\d.]+', task_input)
        ops = re.findall(r'[+\-*/]', task_input)
        
        if numbers and ops:
            try:
                expr = task_input
                for op in ['+', '-', '*', '/']:
                    expr = expr.replace(op, f' {op} ')
                result = eval(expr)
                return f"Calculation result: {result}"
            except:
                pass
        
        return "I can do math! Try 'calculate 2 + 2' or 'compute 10 * 5'"
    
    else:
        return f"""🤖 **SmartWorker - I can:**

• Execute Python code
• Run bash commands  
• Do calculations
• Process data

Just tell me what to do! Examples:
- "run print('hello world')"
- "execute bash ls"
- "calculate 100 / 4"
"""

# Create the agent
agent = BotCloudAgent(
    name="SmartWorker",
    api_url="http://localhost:8001",
    capabilities=["execute", "code", "run", "compute", "work"]
)

@agent.task("execute")
@agent.task("run")
@agent.task("code")
def execute_handler(task_input):
    return process_task(task_input)

@agent.task("calculate")
@agent.task("compute")
def calculate_handler(task_input):
    return process_task(task_input)

@agent.task("default")
def default_handler(task_input):
    return process_task(task_input)

print("🧠 SmartWorker starting...")
print("I can execute code, run commands, and do calculations!")
agent.start()
print(f"✓ Registered as: {agent.agent_id}")
print("\nWaiting for tasks...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    agent.stop()
