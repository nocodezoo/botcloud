"""
BotCloud API - Core Server
"""

import os
import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

from fastapi import FastAPI, HTTPException, Header, Body
from pydantic import BaseModel
import uvicorn

# ============= Data Models =============

class AgentStatus(str, Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    BUSY = "busy"
    ERROR = "error"

class Agent(BaseModel):
    id: str
    name: str
    capabilities: List[str] = []
    status: AgentStatus = AgentStatus.STOPPED
    config: Dict = {}
    created_at: datetime = None
    last_active: datetime = None

class Task(BaseModel):
    id: str
    agent_id: str
    input: str
    output: Optional[str] = None
    status: str = "pending"
    created_at: datetime = None
    completed_at: Optional[datetime] = None

class Message(BaseModel):
    id: str
    from_agent_id: str
    to_agent_id: str
    content: str
    created_at: datetime = None

class Memory(BaseModel):
    key: str
    value: str
    agent_id: str
    created_at: datetime = None

# ============= In-Memory Store =============

class BotStore:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.messages: Dict[str, Message] = {}
        self.memories: Dict[str, List[Memory]] = {}
        self.api_keys: Dict[str, str] = {}  # api_key -> agent_id
    
    def create_agent(self, name: str, capabilities: List[str], api_key: str = None) -> Agent:
        agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        if not api_key:
            api_key = f"bc_{uuid.uuid4().hex}"
        
        agent = Agent(
            id=agent_id,
            name=name,
            capabilities=capabilities,
            status=AgentStatus.STOPPED,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow()
        )
        
        self.agents[agent_id] = agent
        self.api_keys[api_key] = agent_id
        self.memories[agent_id] = []
        
        return agent
    
    def get_agent(self, agent_id: str) -> Agent:
        if agent_id not in self.agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        return self.agents[agent_id]
    
    def start_agent(self, agent_id: str) -> Agent:
        agent = self.get_agent(agent_id)
        agent.status = AgentStatus.RUNNING
        agent.last_active = datetime.utcnow()
        return agent
    
    def stop_agent(self, agent_id: str) -> Agent:
        agent = self.get_agent(agent_id)
        agent.status = AgentStatus.STOPPED
        return agent
    
    def create_task(self, agent_id: str, input_data: str) -> Task:
        # Verify agent exists
        self.get_agent(agent_id)
        
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task = Task(
            id=task_id,
            agent_id=agent_id,
            input=input_data,
            status="pending",
            created_at=datetime.utcnow()
        )
        self.tasks[task_id] = task
        return task
    
    def get_task(self, task_id: str) -> Task:
        if task_id not in self.tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        return self.tasks[task_id]
    
    def send_message(self, from_agent_id: str, to_agent_id: str, content: str) -> Message:
        # Verify both agents exist
        self.get_agent(from_agent_id)
        self.get_agent(to_agent_id)
        
        msg_id = f"msg_{uuid.uuid4().hex[:8]}"
        message = Message(
            id=msg_id,
            from_agent_id=from_agent_id,
            to_agent_id=to_agent_id,
            content=content,
            created_at=datetime.utcnow()
        )
        self.messages[msg_id] = message
        return message
    
    def get_messages(self, agent_id: str) -> List[Message]:
        return [m for m in self.messages.values() 
                if m.from_agent_id == agent_id or m.to_agent_id == agent_id]
    
    def store_memory(self, agent_id: str, key: str, value: str) -> Memory:
        self.get_agent(agent_id)
        
        memory = Memory(
            key=key,
            value=value,
            agent_id=agent_id,
            created_at=datetime.utcnow()
        )
        
        # Remove existing key if present
        self.memories[agent_id] = [m for m in self.memories[agent_id] if m.key != key]
        self.memories[agent_id].append(memory)
        
        return memory
    
    def get_memories(self, agent_id: str) -> List[Memory]:
        self.get_agent(agent_id)
        return self.memories.get(agent_id, [])

# ============= Initialize =============

store = BotStore()

# Create a demo agent
demo_agent = store.create_agent(
    name="DemoBot", 
    capabilities=["chat", "search", "compute"],
    api_key="demo_key_123"
)
demo_agent.status = AgentStatus.RUNNING
store.agents[demo_agent.id] = demo_agent

# ============= API =============

app = FastAPI(title="BotCloud API", version="1.0.0")

def verify_api_key(x_api_key: str = Header(None)) -> str:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    if x_api_key not in store.api_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return store.api_keys[x_api_key]

# Root
@app.get("/")
def root():
    return {
        "name": "BotCloud API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

# Health
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "agents": len(store.agents),
        "tasks": len(store.tasks),
        "messages": len(store.messages)
    }

# ============= Agent Management =============

@app.post("/agents")
def register_agent(
    name: str = Body(...),
    capabilities: List[str] = Body(default=[]),
    api_key: str = Body(default=None)
):
    """Register a new agent"""
    agent = store.create_agent(name, capabilities, api_key)
    return {
        "id": agent.id,
        "name": agent.name,
        "capabilities": agent.capabilities,
        "status": agent.status,
        "api_key": list(store.api_keys.keys())[list(store.api_keys.values()).index(agent.id)],
        "created_at": agent.created_at.isoformat()
    }

@app.get("/agents")
def list_agents():
    """List all registered agents"""
    return {
        "agents": [
            {
                "id": a.id,
                "name": a.name,
                "capabilities": a.capabilities,
                "status": a.status,
                "last_active": a.last_active.isoformat() if a.last_active else None
            }
            for a in store.agents.values()
        ]
    }

@app.get("/agents/{agent_id}")
def get_agent(agent_id: str):
    """Get agent info"""
    agent = store.get_agent(agent_id)
    return {
        "id": agent.id,
        "name": agent.name,
        "capabilities": agent.capabilities,
        "status": agent.status,
        "config": agent.config,
        "created_at": agent.created_at.isoformat(),
        "last_active": agent.last_active.isoformat() if agent.last_active else None
    }

@app.post("/agents/{agent_id}/start")
def start_agent(agent_id: str, api_key: str = Header(None)):
    """Start an agent"""
    verify_api_key(api_key)
    agent = store.start_agent(agent_id)
    return {"status": "success", "agent_id": agent_id, "state": agent.status}

@app.post("/agents/{agent_id}/stop")
def stop_agent(agent_id: str, api_key: str = Header(None)):
    """Stop an agent"""
    verify_api_key(api_key)
    agent = store.stop_agent(agent_id)
    return {"status": "success", "agent_id": agent_id, "state": agent.status}

@app.post("/agents/{agent_id}/configure")
def configure_agent(agent_id: str, config: Dict = Body(...), api_key: str = Header(None)):
    """Update agent configuration"""
    verify_api_key(api_key)
    agent = store.get_agent(agent_id)
    agent.config.update(config)
    return {"status": "success", "config": agent.config}

# ============= Tasks =============

@app.post("/agents/{agent_id}/tasks")
def create_task(agent_id: str, input_data: str = Body(...), api_key: str = Header(None)):
    """Send a task to an agent"""
    verify_api_key(api_key)
    task = store.create_task(agent_id, input_data)
    
    # Simulate task completion (in real version, this would be async)
    task.status = "completed"
    task.output = f"Processed: {input_data}"
    task.completed_at = datetime.utcnow()
    
    return {
        "id": task.id,
        "agent_id": task.agent_id,
        "input": task.input,
        "output": task.output,
        "status": task.status,
        "created_at": task.created_at.isoformat(),
        "completed_at": task.completed_at.isoformat() if task.completed_at else None
    }

@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    """Get task result"""
    task = store.get_task(task_id)
    return {
        "id": task.id,
        "agent_id": task.agent_id,
        "input": task.input,
        "output": task.output,
        "status": task.status,
        "created_at": task.created_at.isoformat(),
        "completed_at": task.completed_at.isoformat() if task.completed_at else None
    }

@app.get("/agents/{agent_id}/tasks")
def list_agent_tasks(agent_id: str):
    """List all tasks for an agent"""
    store.get_agent(agent_id)
    tasks = [t for t in store.tasks.values() if t.agent_id == agent_id]
    return {
        "tasks": [
            {
                "id": t.id,
                "input": t.input,
                "output": t.output,
                "status": t.status,
                "created_at": t.created_at.isoformat()
            }
            for t in tasks
        ]
    }

# ============= Collaboration =============

@app.post("/agents/{agent_id}/delegate")
def delegate_task(
    agent_id: str,
    to_agent: str = Body(..., alias="to_agent"),
    task: str = Body(...),
    api_key: str = Header(None)
):
    """Delegate a task to another agent"""
    verify_api_key(api_key)
    
    # Verify source agent exists
    store.get_agent(agent_id)
    
    # Create task for target agent
    new_task = store.create_task(to_agent, f"[Delegated from {agent_id}]: {task}")
    new_task.status = "completed"
    new_task.output = f"Delegated task processed by {to_agent}"
    new_task.completed_at = datetime.utcnow()
    
    return {
        "status": "delegated",
        "from_agent": agent_id,
        "to_agent": to_agent,
        "task_id": new_task.id,
        "result": new_task.output
    }

@app.post("/agents/{agent_id}/message")
def send_message(
    agent_id: str,
    to_agent: str = Body(..., alias="to_agent"),
    content: str = Body(...),
    api_key: str = Header(None)
):
    """Send a message to another agent"""
    verify_api_key(api_key)
    message = store.send_message(agent_id, to_agent, content)
    return {
        "id": message.id,
        "from": message.from_agent_id,
        "to": message.to_agent_id,
        "content": message.content,
        "created_at": message.created_at.isoformat()
    }

@app.get("/agents/{agent_id}/messages")
def get_messages(agent_id: str):
    """Get messages for an agent"""
    store.get_agent(agent_id)
    messages = store.get_messages(agent_id)
    return {
        "messages": [
            {
                "id": m.id,
                "from": m.from_agent_id,
                "to": m.to_agent_id,
                "content": m.content,
                "created_at": m.created_at.isoformat()
            }
            for m in messages
        ]
    }

# ============= Memory =============

@app.post("/memory/{agent_id}")
def store_memory(
    agent_id: str,
    key: str = Body(...),
    value: str = Body(...),
    api_key: str = Header(None)
):
    """Store a memory for an agent"""
    verify_api_key(api_key)
    memory = store.store_memory(agent_id, key, value)
    return {
        "key": memory.key,
        "value": memory.value,
        "created_at": memory.created_at.isoformat()
    }

@app.get("/memory/{agent_id}")
def get_memories(agent_id: str):
    """Get all memories for an agent"""
    store.get_agent(agent_id)
    memories = store.get_memories(agent_id)
    return {
        "memories": [
            {
                "key": m.key,
                "value": m.value,
                "created_at": m.created_at.isoformat()
            }
            for m in memories
        ]
    }

@app.delete("/memory/{agent_id}/{key}")
def delete_memory(agent_id: str, key: str, api_key: str = Header(None)):
    """Delete a memory"""
    verify_api_key(api_key)
    store.get_agent(agent_id)
    store.memories[agent_id] = [m for m in store.memories[agent_id] if m.key != key]
    return {"status": "deleted", "key": key}

# ============= Logs & Metrics =============

@app.get("/logs/{agent_id}")
def get_logs(agent_id: str, limit: int = 100):
    """Get logs for an agent"""
    store.get_agent(agent_id)
    # Return recent activity as logs
    logs = []
    for task in list(store.tasks.values())[-limit:]:
        if task.agent_id == agent_id:
            logs.append({
                "type": "task",
                "id": task.id,
                "input": task.input,
                "status": task.status,
                "timestamp": task.created_at.isoformat()
            })
    return {"logs": logs}

@app.get("/metrics/{agent_id}")
def get_metrics(agent_id: str):
    """Get metrics for an agent"""
    agent = store.get_agent(agent_id)
    tasks = [t for t in store.tasks.values() if t.agent_id == agent_id]
    completed = len([t for t in tasks if t.status == "completed"])
    
    return {
        "agent_id": agent_id,
        "status": agent.status,
        "total_tasks": len(tasks),
        "completed_tasks": completed,
        "uptime_seconds": (datetime.utcnow() - agent.created_at).total_seconds()
    }

# ============= Run =============

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
