"""
BotCloud WebSocket Server
Real-time communication between agents
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}  # agent_id -> websocket
        self.agents: Dict[str, dict] = {}  # agent_id -> agent info
    
    async def connect(self, websocket: WebSocket, agent_id: str):
        await websocket.accept()
        self.active_connections[agent_id] = websocket
        print(f"Agent {agent_id} connected via WebSocket")
    
    def disconnect(self, agent_id: str):
        if agent_id in self.active_connections:
            del self.active_connections[agent_id]
        print(f"Agent {agent_id} disconnected")
    
    async def send_message(self, agent_id: str, message: dict):
        if agent_id in self.active_connections:
            await self.active_connections[agent_id].send_json(message)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)
    
    def get_connected_agents(self) -> list:
        return list(self.active_connections.keys())


manager = ConnectionManager()

# In-memory agent registry (would be database in production)
AGENTS_DB = {}

@app.get("/ws/health")
async def ws_health():
    return {
        "status": "healthy",
        "connected_agents": len(manager.active_connections)
    }

@app.websocket("/ws/connect/{agent_id}")
async def websocket_connect(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for agent connection"""
    await manager.connect(websocket, agent_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await handle_message(agent_id, message)
    except WebSocketDisconnect:
        manager.disconnect(agent_id)

async def handle_message(agent_id: str, message: dict):
    """Handle incoming WebSocket messages"""
    msg_type = message.get("type")
    
    if msg_type == "register":
        # Agent registering its capabilities
        AGENTS_DB[agent_id] = {
            "id": agent_id,
            "name": message.get("name"),
            "capabilities": message.get("capabilities", []),
            "status": "online",
            "last_seen": datetime.utcnow().isoformat()
        }
        await manager.send_message(agent_id, {
            "type": "registered",
            "agent_id": agent_id
        })
    
    elif msg_type == "delegate":
        # Delegate task to another agent
        target_id = message.get("to_agent")
        task = message.get("task")
        
        if target_id in manager.active_connections:
            await manager.send_message(target_id, {
                "type": "task_delegated",
                "from_agent": agent_id,
                "task": task,
                "timestamp": datetime.utcnow().isoformat()
            })
            await manager.send_message(agent_id, {
                "type": "delegation_sent",
                "to_agent": target_id,
                "status": "delivered"
            })
        else:
            await manager.send_message(agent_id, {
                "type": "error",
                "message": f"Agent {target_id} not connected"
            })
    
    elif msg_type == "broadcast":
        # Broadcast to all connected agents
        await manager.broadcast({
            "type": "broadcast",
            "from_agent": agent_id,
            "message": message.get("message"),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    elif msg_type == "find_agents":
        # Find agents with specific capabilities
        required_caps = message.get("capabilities", [])
        matching = [
            {"id": a_id, "name": a.get("name"), "capabilities": a.get("capabilities", [])}
            for a_id, a in AGENTS_DB.items()
            if any(cap in a.get("capabilities", []) for cap in required_caps)
        ]
        await manager.send_message(agent_id, {
            "type": "agents_found",
            "agents": matching
        })
    
    elif msg_type == "ping":
        await manager.send_message(agent_id, {"type": "pong"})

@app.get("/ws/agents")
async def list_ws_agents():
    """List all WebSocket-connected agents"""
    return {
        "connected": list(manager.active_connections.keys()),
        "registry": AGENTS_DB
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
