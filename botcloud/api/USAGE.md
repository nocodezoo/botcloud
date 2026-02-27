# BotCloud API Usage

## Running the API

### Local
```bash
cd api
pip install -r requirements.txt
python main.py
```

### Docker
```bash
docker-compose up --build
```

## API Examples

### Register an Agent
```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{"name": "MyBot", "capabilities": ["search"]}'
```

### Start Agent
```bash
curl -X POST http://localhost:8000/agents/{agent_id}/start \
  -H "X-API-Key: your_api_key"
```

### Send Task
```bash
curl -X POST "http://localhost:8000/agents/{agent_id}/tasks" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"input": "Your task description"}'
```

### Delegate to Another Agent
```bash
curl -X POST "http://localhost:8000/agents/{agent_id}/delegate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"to_agent": "target_agent_id", "task": "Do something"}'
```

### Store Memory
```bash
curl -X POST "http://localhost:8000/memory/{agent_id}" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"key": "context", "value": "User is building a SaaS"}'
```

### Get Logs
```bash
curl http://localhost:8000/logs/{agent_id}
```

### Get Metrics
```bash
curl http://localhost:8000/metrics/{agent_id}
```

## OpenClaw Agent Integration

```python
from agents.openclow_agent import BotCloudAgent

# Create and register agent
agent = BotCloudAgent(
    name="MyBot",
    capabilities=["search", "browse"]
)

# Start agent
agent.start()

# Store context
agent.store_memory("project", "Building SaaS")

# Delegate to another agent
agent.delegate_to("other_agent_id", "Research pricing models")

# Get messages
print(agent.get_messages())
```
