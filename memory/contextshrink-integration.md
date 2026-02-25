# ContextShrink Memory Integration

This skill compresses session memory using ContextShrink API before memory flush is triggered.

## Usage

**Trigger:** When session tokens exceed ~4000 (before 6000 threshold)

**Command:** "compress memory" or "shrink context"

## How It Works

1. Gets current session messages
2. Sends to ContextShrink API (localhost:8000)
3. Returns compressed context that preserves conversation meaning

## Integration with OpenClaw

The memoryFlush is already configured at 6000 tokens. To integrate ContextShrink:

Option 1: Use as skill before memory flush
```
You: compress my memory
Claw: *calls ContextShrink API* → returns compressed context
```

Option 2: Add to cron job for periodic compression
```json
{
  "schedule": "*/15 * * * *",
  "action": "compress-memory"
}
```

## API Endpoints

- `POST /compress` - Compress messages
- `POST /estimate` - Free estimation
- `GET /health` - Health check

## Example

```bash
# Compress session messages
curl -X POST http://localhost:8000/compress \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [...],
    "mode": "medium",
    "preserve_last": 5
  }'
```

---

*🦞 ContextShrink - Save 70% on LLM context costs*
