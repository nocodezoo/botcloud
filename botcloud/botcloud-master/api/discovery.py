"""
BotCloud - Agent Discovery Service
Find agents by capabilities
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI(title="BotCloud Discovery")

# Agent registry
agents_db = {}

class AgentRegistration(BaseModel):
    name: str
    capabilities: List[str]
    endpoint: Optional[str] = None
    description: Optional[str] = None

@app.get("/")
def root():
    return {"service": "BotCloud Discovery", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy", "agents": len(agents_db)}

@app.post("/register", response_model=dict)
def register_agent(agent: AgentRegistration):
    """Register an agent with the discovery service"""
    agent_id = f"agent_{uuid.uuid4().hex[:8]}"
    agents_db[agent_id] = {
        "id": agent_id,
        "name": agent.name,
        "capabilities": agent.capabilities,
        "endpoint": agent.endpoint,
        "description": agent.description
    }
    return {"agent_id": agent_id, "status": "registered"}

@app.get("/agents", response_model=dict)
def list_agents():
    """List all registered agents"""
    return {"agents": list(agents_db.values())}

@app.get("/agents/{agent_id}", response_model=dict)
def get_agent(agent_id: str):
    """Get a specific agent"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents_db[agent_id]

@app.get("/find", response_model=dict)
def find_agents(capabilities: str):
    """Find agents by capabilities (comma-separated)"""
    required = [c.strip().lower() for c in capabilities.split(",")]
    matching = []
    
    for agent in agents_db.values():
        agent_caps = [c.lower() for c in agent.get("capabilities", [])]
        if any(req in agent_caps for req in required):
            matching.append(agent)
    
    return {"agents": matching, "count": len(matching)}

@app.get("/capabilities", response_model=dict)
def list_capabilities():
    """List all available capabilities"""
    all_caps = set()
    for agent in agents_db.values():
        all_caps.update(agent.get("capabilities", []))
    return {"capabilities": sorted(list(all_caps))}

@app.delete("/agents/{agent_id}")
def unregister_agent(agent_id: str):
    """Unregister an agent"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    del agents_db[agent_id]
    return {"status": "unregistered"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
