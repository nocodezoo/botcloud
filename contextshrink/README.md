# ContextShrink - AI Context Compression API

Version: 0.1.0

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Run
python main.py

# Test
curl -X POST http://localhost:8000/compress \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"},{"role":"assistant","content":"Hi!"},{"role":"user","content":"I want to build a SaaS."},{"role":"assistant","content":"Great! What kind?"},{"role":"user","content":"An AI agent infrastructure company called ContextShrink."},{"role":"assistant","content":"That sounds amazing! Let me help you."}],"mode":"medium"}'
```

## API Endpoints

- `POST /compress` - Compress messages
- `POST /estimate` - Estimate compressed size (free)
- `GET /health` - Health check

## Modes

- `light`: 80% token retention
- `medium`: 50% token retention  
- `aggressive`: 30% token retention

## Environment Variables

- `OPENAI_API_KEY`: For embeddings (optional - uses free alternatives if not set)
- `PORT`: Server port (default 8000)

---

*ContextShrink - Save 70% on LLM costs*
