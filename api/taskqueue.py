"""
BotCloud Task Queue
Async task processing for agents
"""

import uuid
import asyncio
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Callable
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="BotCloud Task Queue")

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Task(BaseModel):
    id: str
    agent_id: str
    payload: dict
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[dict] = None
    error: Optional[str] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class TaskQueue:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.queue: List[str] = []  # Task IDs in queue
        self.handlers: Dict[str, Callable] = {}
    
    def register_handler(self, task_type: str, handler: Callable):
        """Register a handler function for a task type"""
        self.handlers[task_type] = handler
    
    def submit(self, agent_id: str, task_type: str, payload: dict) -> str:
        """Submit a new task"""
        task_id = f"task_{uuid.uuid4().hex[:10]}"
        
        task = Task(
            id=task_id,
            agent_id=agent_id,
            payload={"type": task_type, **payload},
            created_at=datetime.utcnow()
        )
        
        self.tasks[task_id] = task
        self.queue.append(task_id)
        
        return task_id
    
    async def process(self, task_id: str) -> Task:
        """Process a task"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task.status = TaskStatus.PROCESSING
        task.started_at = datetime.utcnow()
        
        task_type = task.payload.get("type", "default")
        
        try:
            if task_type in self.handlers:
                result = await self.handlers[task_type](task.payload)
                task.result = result
                task.status = TaskStatus.COMPLETED
            else:
                # Default processing
                await asyncio.sleep(0.1)  # Simulate work
                task.result = {"processed": True, "task_type": task_type}
                task.status = TaskStatus.COMPLETED
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
        
        task.completed_at = datetime.utcnow()
        return task
    
    def get_task(self, task_id: str) -> Task:
        """Get a task by ID"""
        if task_id not in self.tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        return self.tasks[task_id]
    
    def get_queue_status(self) -> dict:
        """Get queue status"""
        return {
            "total": len(self.tasks),
            "pending": len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
            "processing": len([t for t in self.tasks.values() if t.status == TaskStatus.PROCESSING]),
            "completed": len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]),
            "failed": len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])
        }

queue = TaskQueue()

# ============= API Endpoints =============

@app.get("/")
def root():
    return {"service": "BotCloud Task Queue", "version": "1.0.0"}

@app.get("/health")
def health():
    return queue.get_queue_status()

@app.post("/submit")
def submit_task(agent_id: str, task_type: str, payload: dict):
    """Submit a new task"""
    task_id = queue.submit(agent_id, task_type, payload)
    return {"task_id": task_id, "status": "pending"}

@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    """Get task status and result"""
    task = queue.get_task(task_id)
    return {
        "id": task.id,
        "agent_id": task.agent_id,
        "payload": task.payload,
        "status": task.status,
        "result": task.result,
        "error": task.error,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None
    }

@app.get("/status")
def get_status():
    """Get queue status"""
    return queue.get_queue_status()

@app.post("/tasks/{task_id}/process")
async def process_task(task_id: str):
    """Manually trigger task processing"""
    task = await queue.process(task_id)
    return {"status": task.status, "result": task.result}

# Example handler
async def search_handler(payload: dict):
    """Example: Search task handler"""
    query = payload.get("query")
    # In real implementation, this would do actual search
    return {"query": query, "results": ["result1", "result2"], "count": 2}

queue.register_handler("search", search_handler)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
