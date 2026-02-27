"""
BotCloud - OpenClaw Agent Integration
Connects OpenClaw agents to BotCloud
"""

import requests
import json
import os

BOTCLOUD_URL = os.getenv("BOTCLOUD_URL", "http://localhost:8000")

class BotCloudAgent:
    """OpenClaw agent wrapper for BotCloud"""
    
    def __init__(self, name: str, capabilities: list, api_key: str = None):
        self.name = name
        self.capabilities = capabilities
        self.api_key = api_key
        self.agent_id = None
        self.register()
    
    def register(self):
        """Register this agent with BotCloud"""
        resp = requests.post(f"{BOTCLOUD_URL}/agents", json={
            "name": self.name,
            "capabilities": self.capabilities
        })
        if resp.status_code == 200:
            data = resp.json()
            self.agent_id = data["id"]
            self.api_key = data.get("api_key", self.api_key)
            print(f"Registered: {self.name} ({self.agent_id})")
        return self
    
    def start(self):
        """Start the agent"""
        resp = requests.post(
            f"{BOTCLOUD_URL}/agents/{self.agent_id}/start",
            headers=self._auth()
        )
        return resp.json() if resp.status_code == 200 else None
    
    def stop(self):
        """Stop the agent"""
        resp = requests.post(
            f"{BOTCLOUD_URL}/agents/{self.agent_id}/stop",
            headers=self._auth()
        )
        return resp.json() if resp.status_code == 200 else None
    
    def send_task(self, task: str):
        """Send a task to this agent"""
        resp = requests.post(
            f"{BOTCLOUD_URL}/agents/{self.agent_id}/tasks",
            data=json.dumps(task),
            headers={**self._auth(), "Content-Type": "application/json"}
        )
        return resp.json() if resp.status_code == 200 else None
    
    def delegate_to(self, to_agent_id: str, task: str):
        """Delegate a task to another agent"""
        resp = requests.post(
            f"{BOTCLOUD_URL}/agents/{self.agent_id}/delegate",
            json={"to_agent": to_agent_id, "task": task},
            headers=self._auth()
        )
        return resp.json() if resp.status_code == 200 else None
    
    def send_message(self, to_agent_id: str, message: str):
        """Send a message to another agent"""
        resp = requests.post(
            f"{BOTCLOUD_URL}/agents/{self.agent_id}/message",
            json={"to_agent": to_agent_id, "content": message},
            headers=self._auth()
        )
        return resp.json() if resp.status_code == 200 else None
    
    def store_memory(self, key: str, value: str):
        """Store memory"""
        resp = requests.post(
            f"{BOTCLOUD_URL}/memory/{self.agent_id}",
            json={"key": key, "value": value},
            headers=self._auth()
        )
        return resp.json() if resp.status_code == 200 else None
    
    def get_memories(self):
        """Get all memories"""
        resp = requests.get(
            f"{BOTCLOUD_URL}/memory/{self.agent_id}",
            headers=self._auth()
        )
        return resp.json() if resp.status_code == 200 else None
    
    def get_messages(self):
        """Get messages for this agent"""
        resp = requests.get(
            f"{BOTCLOUD_URL}/agents/{self.agent_id}/messages",
            headers=self._auth()
        )
        return resp.json() if resp.status_code == 200 else None
    
    def get_metrics(self):
        """Get agent metrics"""
        resp = requests.get(f"{BOTCLOUD_URL}/metrics/{self.agent_id}")
        return resp.json() if resp.status_code == 200 else None
    
    def _auth(self):
        return {"X-API-Key": self.api_key}


# Example usage
if __name__ == "__main__":
    # Create an agent
    agent = BotCloudAgent(
        name="ResearcherBot",
        capabilities=["web_search", "browse", "read"]
    )
    
    # Start it
    agent.start()
    
    # Store some memory
    agent.store_memory("personality", "Helpful research assistant")
    agent.store_memory("expertise", "AI, LLMs, automation")
    
    # Get memories
    print(agent.get_memories())
    
    # Get metrics
    print(agent.get_metrics())
