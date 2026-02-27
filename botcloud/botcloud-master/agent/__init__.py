"""
BotCloud Agent SDK
Create workers that connect to BotCloud and process tasks
"""

import requests
import time
import threading
import uuid
from typing import Callable, Dict, Any, Optional, List

class BotCloudAgent:
    """
    Agent that connects to BotCloud, polls for tasks, and executes them.
    """
    
    def __init__(
        self, 
        name: str, 
        api_url: str = "http://localhost:8000",
        capabilities: Optional[List[str]] = None,
        api_key: Optional[str] = None,
        poll_interval: int = 5
    ):
        self.name = name
        self.api_url = api_url.rstrip('/')
        self.capabilities = capabilities or []
        self.api_key = api_key
        self.poll_interval = poll_interval
        self.agent_id = None
        self._running = False
        self._task_handlers: Dict[str, Callable] = {}
        self._thread = None
        
    def register(self) -> str:
        """Register this agent with BotCloud"""
        response = requests.post(
            f"{self.api_url}/agents",
            json={
                "name": self.name,
                "capabilities": self.capabilities
            }
        )
        response.raise_for_status()
        data = response.json()
        self.agent_id = data["id"]
        self.api_key = data["api_key"]
        print(f"✓ Registered as {self.agent_id}")
        return self.agent_id
    
    def start(self):
        """Start the agent - register and begin polling"""
        if not self.agent_id:
            self.register()
        
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        print(f"✓ Agent {self.name} started polling for tasks")
        
    def stop(self):
        """Stop the agent"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)
        print(f"✓ Agent {self.name} stopped")
        
    def task(self, task_type: str = "default"):
        """Decorator to register a task handler"""
        def decorator(func: Callable) -> Callable:
            self._task_handlers[task_type] = func
            return func
        return decorator
    
    def _poll_loop(self):
        """Poll for tasks continuously"""
        while self._running:
            try:
                self._check_for_tasks()
            except Exception as e:
                print(f"Poll error: {e}")
            time.sleep(self.poll_interval)
    
    def _check_for_tasks(self):
        """Check for pending tasks"""
        if not self.agent_id:
            return
            
        # Get tasks for this agent
        response = requests.get(f"{self.api_url}/agents/{self.agent_id}/tasks")
        if response.status_code != 200:
            return
            
        tasks = response.json().get("tasks", [])
        
        for task in tasks:
            if task.get("status") == "pending":
                self._execute_task(task)
    
    def _execute_task(self, task: Dict[str, Any]):
        """Execute a task using the appropriate handler"""
        task_id = task["id"]
        task_input = task.get("input", "")
        
        print(f"→ Processing task {task_id}: {task_input[:50]}...")
        
        try:
            # Find handler - use "default" or match by task content
            handler = self._task_handlers.get("default")
            
            # Try to find a specific handler based on input
            for key, h in self._task_handlers.items():
                if key != "default" and key.lower() in str(task_input).lower():
                    handler = h
                    break
            
            if handler:
                result = handler(task_input)
            else:
                result = f"Processed: {task_input}"
            
            # Mark task complete
            requests.post(
                f"{self.api_url}/tasks/{task_id}/complete",
                headers={"X-API-Key": self.api_key},
                json={"output": str(result)}
            )
            print(f"✓ Task {task_id} completed: {result}")
            
        except Exception as e:
            print(f"✗ Task {task_id} failed: {e}")
            requests.post(
                f"{self.api_url}/tasks/{task_id}/complete",
                headers={"X-API-Key": self.api_key},
                json={"output": f"Error: {str(e)}", "status": "failed"}
            )
    
    def send_message(self, to_agent: str, message: str):
        """Send a message to another agent"""
        response = requests.post(
            f"{self.api_url}/agents/{self.agent_id}/message",
            headers={"X-API-Key": self.api_key},
            json={"to_agent": to_agent, "message": message}
        )
        return response.json()
    
    def get_messages(self) -> List[Dict]:
        """Get messages for this agent"""
        response = requests.get(
            f"{self.api_url}/agents/{self.agent_id}/messages",
            headers={"X-API-Key": self.api_key}
        )
        return response.json().get("messages", [])
    
    def store_memory(self, key: str, value: Any):
        """Store memory for this agent"""
        response = requests.post(
            f"{self.api_url}/memory/{self.agent_id}",
            headers={"X-API-Key": self.api_key},
            json={key: value}
        )
        return response.json()
    
    def get_memory(self, key: str) -> Any:
        """Get memory for this agent"""
        response = requests.get(
            f"{self.api_url}/memory/{self.agent_id}/{key}",
            headers={"X-API-Key": self.api_key}
        )
        return response.json()
    
    def get_logs(self) -> List[Dict]:
        """Get logs for this agent"""
        response = requests.get(
            f"{self.api_url}/logs/{self.agent_id}",
            headers={"X-API-Key": self.api_key}
        )
        return response.json().get("logs", [])
    
    def get_metrics(self) -> Dict:
        """Get metrics for this agent"""
        response = requests.get(
            f"{self.api_url}/metrics/{self.agent_id}",
            headers={"X-API-Key": self.api_key}
        )
        return response.json()


# Convenience function to run an agent from CLI
def run_agent(name: str, capabilities: List[str], api_url: str = "http://localhost:8000"):
    """Run an agent from command line"""
    agent = BotCloudAgent(name, api_url, capabilities)
    agent.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        agent.stop()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run a BotCloud agent")
    parser.add_argument("name", help="Agent name")
    parser.add_argument("--capabilities", nargs="+", default=[], help="Agent capabilities")
    parser.add_argument("--api-url", default="http://localhost:8000", help="BotCloud API URL")
    
    args = parser.parse_args()
    run_agent(args.name, args.capabilities, args.api_url)
