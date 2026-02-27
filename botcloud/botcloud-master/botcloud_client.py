"""
BotCloud Client for OpenClaw
Use this to connect OpenClaw to BotCloud workers
"""

import requests
import time
import json
from typing import List, Dict, Optional, Any

class BotCloudClient:
    """Client for OpenClaw to interact with BotCloud"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
        
    def health_check(self) -> Dict:
        """Check if BotCloud is running"""
        try:
            r = self.session.get(f"{self.api_url}/health")
            return r.json()
        except Exception as e:
            return {"error": str(e), "status": "unhealthy"}
    
    def list_agents(self) -> List[Dict]:
        """List all registered agents"""
        r = self.session.get(f"{self.api_url}/agents")
        return r.json().get("agents", [])
    
    def find_agents(self, capabilities: List[str] = None, status: str = None) -> List[Dict]:
        """Find agents by capabilities or status"""
        agents = self.list_agents()
        
        if capabilities:
            agents = [a for a in agents if any(c in a.get("capabilities", []) for c in capabilities)]
        
        if status:
            agents = [a for a in agents if a.get("status") == status]
            
        return agents
    
    def get_agent(self, agent_id: str) -> Dict:
        """Get agent details"""
        r = self.session.get(f"{self.api_url}/agents/{agent_id}")
        return r.json()
    
    def assign_task(
        self, 
        agent_id: str = None,
        agent_name: str = None,
        capabilities: List[str] = None,
        task_input: str = "",
        task_type: str = "default"
    ) -> Dict:
        """
        Assign a task to an agent.
        
        Priority: agent_id > agent_name > capabilities
        """
        # Find agent
        if not agent_id:
            if agent_name:
                agents = self.list_agents()
                for a in agents:
                    if a.get("name") == agent_name:
                        agent_id = a["id"]
                        break
            elif capabilities:
                found = self.find_agents(capabilities=capabilities, status="running")
                if found:
                    agent_id = found[0]["id"]
        
        if not agent_id:
            return {"error": "No suitable agent found"}
        
        # Get agent details including API key
        agent_info = self.get_agent(agent_id)
        api_key = agent_info.get("api_key", "")
        
        # Assign task
        r = self.session.post(
            f"{self.api_url}/agents/{agent_id}/tasks",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key
            },
            json={"input": task_input}
        )
        
        if r.status_code == 200:
            return r.json()
        else:
            return {"error": r.text}
    
    def get_task(self, task_id: str) -> Dict:
        """Get task status and result"""
        r = self.session.get(f"{self.api_url}/tasks/{task_id}")
        return r.json()
    
    def wait_for_task(self, task_id: str, timeout: int = 60, poll_interval: int = 2) -> Dict:
        """Wait for task to complete"""
        start = time.time()
        
        while time.time() - start < timeout:
            task = self.get_task(task_id)
            
            if task.get("status") == "completed":
                return {
                    "status": "completed",
                    "output": task.get("output"),
                    "task_id": task_id
                }
            
            if task.get("status") == "failed":
                return {
                    "status": "failed",
                    "output": task.get("output"),
                    "task_id": task_id
                }
            
            time.sleep(poll_interval)
        
        return {"status": "timeout", "task_id": task_id}
    
    def run_task_and_wait(
        self,
        agent_name: str = None,
        capabilities: List[str] = None,
        task_input: str = "",
        timeout: int = 60
    ) -> Dict:
        """Assign task and wait for result"""
        # Assign task
        result = self.assign_task(
            agent_name=agent_name,
            capabilities=capabilities,
            task_input=task_input
        )
        
        if "error" in result:
            return result
        
        # Wait for result
        task_id = result.get("id")
        return self.wait_for_task(task_id, timeout=timeout)
    
    def get_worker_stats(self) -> Dict:
        """Get overall worker statistics"""
        health = self.health_check()
        agents = self.list_agents()
        
        running = [a for a in agents if a.get("status") == "running"]
        stopped = [a for a in agents if a.get("status") == "stopped"]
        
        return {
            "status": health.get("status"),
            "total_agents": len(agents),
            "running": len(running),
            "stopped": len(stopped),
            "workers": [
                {
                    "name": a.get("name"),
                    "status": a.get("status"),
                    "capabilities": a.get("capabilities", [])
                }
                for a in running
            ]
        }


# Convenience function for quick use
def quick_task(task: str, agent: str = "WorkerBot") -> str:
    """Quick task assignment - returns output"""
    client = BotCloudClient()
    result = client.run_task_and_wait(agent_name=agent, task_input=task)
    
    if result.get("status") == "completed":
        return result.get("output", "")
    else:
        return f"Error: {result.get('status')} - {result.get('output', 'Unknown error')}"


if __name__ == "__main__":
    # Demo
    client = BotCloudClient()
    
    print("🤖 BotCloud Client")
    print("=" * 40)
    
    # Health check
    health = client.health_check()
    print(f"Status: {health.get('status')}")
    
    # List agents
    agents = client.list_agents()
    print(f"Agents: {len(agents)}")
    for a in agents:
        print(f"  - {a.get('name')}: {a.get('status')}")
    
    # Get stats
    stats = client.get_worker_stats()
    print(f"\nWorkers: {stats.get('running')} running, {stats.get('stopped')} stopped")
