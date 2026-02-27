#!/usr/bin/env python3
"""
OpenClaw Connector - Connect BotCloud to OpenClaw sessions
Allows BotCloud workers to delegate tasks to OpenClaw and get results
"""

import os
import sys
import requests
import uuid
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

# OpenClaw API defaults
DEFAULT_OPENCLAW_URL = os.environ.get("OPENCLAW_URL", "http://localhost:8080")
DEFAULT_OPENCLAW_API_KEY = os.environ.get("OPENCLAW_API_KEY", "")


@dataclass
class OpenClawTask:
    """Represents a task sent to OpenClaw"""
    task_id: str
    prompt: str
    status: str = "pending"
    result: Optional[str] = None


class OpenClawConnector:
    """
    Connector to OpenClaw API.
    Allows BotCloud workers to delegate tasks to OpenClaw.
    """
    
    def __init__(
        self,
        openclaw_url: str = DEFAULT_OPENCLAW_URL,
        api_key: str = DEFAULT_OPENCLAW_API_KEY
    ):
        self.openclaw_url = openclaw_url.rstrip('/')
        self.api_key = api_key
        self.session_id = None
        
    def health_check(self) -> Dict[str, Any]:
        """Check if OpenClaw is reachable"""
        try:
            resp = requests.get(f"{self.openclaw_url}/health", timeout=5)
            return {"status": "healthy", "url": self.openclaw_url}
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}
    
    def check_status(self) -> Dict[str, Any]:
        """Get OpenClaw status"""
        try:
            resp = requests.get(f"{self.openclaw_url}/status", timeout=5)
            return resp.json()
        except:
            return {"status": "unknown"}
    
    def create_session(self, agent_id: str = "botcloud-worker") -> str:
        """Create a new OpenClaw session for this worker"""
        try:
            # Try to create a session via the sessions API
            resp = requests.post(
                f"{self.openclaw_url}/sessions",
                json={"agent_id": agent_id},
                timeout=10
            )
            if resp.status_code in (200, 201):
                data = resp.json()
                self.session_id = data.get("session_id") or data.get("id")
                return self.session_id
        except Exception as e:
            print(f"Session creation note: {e}")
        
        # If no sessions API, generate a session key
        self.session_id = f"bc-{agent_id}-{uuid.uuid4().hex[:8]}"
        return self.session_id
    
    def send_message(self, message: str, wait_for_response: bool = True, timeout: int = 60) -> Dict[str, Any]:
        """
        Send a message to OpenClaw and optionally wait for response.
        
        This is the main integration point - BotCloud workers call this
        to delegate complex tasks to OpenClaw.
        """
        if not self.session_id:
            self.create_session()
        
        task_id = f"bc-task-{uuid.uuid4().hex[:8]}"
        
        try:
            # Try the sessions/message endpoint
            resp = requests.post(
                f"{self.openclaw_url}/sessions/{self.session_id}/message",
                json={"message": message},
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                timeout=timeout if wait_for_response else 5
            )
            
            if resp.status_code == 200:
                if wait_for_response:
                    return {
                        "task_id": task_id,
                        "status": "completed",
                        "result": resp.json()
                    }
                else:
                    return {
                        "task_id": task_id,
                        "status": "sent",
                        "response": resp.json()
                    }
            else:
                return {
                    "task_id": task_id,
                    "status": "error",
                    "error": f"HTTP {resp.status_code}: {resp.text}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "task_id": task_id,
                "status": "timeout",
                "error": "Request timed out"
            }
        except Exception as e:
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(e)
            }
    
    def delegate_task(self, task: str, timeout: int = 60) -> Dict[str, Any]:
        """
        Delegate a task to OpenClaw - alias for send_message.
        """
        return self.send_message(task, wait_for_response=True, timeout=timeout)
    
    def run_agent(self, prompt: str, agent_type: str = None) -> Dict[str, Any]:
        """
        Run an agent with a prompt.
        Optionally specify agent type.
        """
        if agent_type:
            full_prompt = f"[Agent: {agent_type}] {prompt}"
        else:
            full_prompt = prompt
        
        return self.delegate_task(full_prompt)


# Convenience function for quick testing
def test_connector():
    """Test OpenClaw connection"""
    print("=== OpenClaw Connector Test ===")
    
    connector = OpenClawConnector()
    
    # Health check
    health = connector.health_check()
    print(f"Health: {health}")
    
    # Status
    status = connector.check_status()
    print(f"Status: {status}")
    
    # Create session
    session_id = connector.create_session()
    print(f"Session: {session_id}")
    
    # Send test message (if OpenClaw is running)
    if health["status"] == "healthy":
        result = connector.send_message("Hello from BotCloud test!")
        print(f"Result: {result}")
    else:
        print("OpenClaw not reachable - skipping message test")


if __name__ == "__main__":
    test_connector()
