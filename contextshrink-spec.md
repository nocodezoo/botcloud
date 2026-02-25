# ContextShrink - AI Context Compression API

## The Problem
- Long conversations = expensive API calls
- 50 messages = ~15K tokens = $0.015 per call
- Multiply by 1000s of conversations = massive cost bleed

## Our Solution
**ContextShrink API** - Compress conversation history to 30% of original size while retaining 95%+ of semantic meaning.

## How It Works

```
Input: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...] (15,000 tokens)

↓ ContextShrink Engine

Output: [{"role": "system", "content": "SUMMARY: User is building a SaaS..."}, {"role": "user", "content": "latest message"}] (3,500 tokens)
```

## Technical Approach

### 1. Recency Bias
- Keep last N messages (configurable) at full fidelity
- Compress everything before that

### 2. Semantic Deduplication
- Embed all messages
- Find clusters of semantically similar messages
- Replace cluster with single summary

### 3. Key Entity Extraction
- Extract: names, dates, numbers, decisions, preferences
- Store in structured "memory block"
- Inject as system context

### 4. Progressive Compression
- Light (80% retained): Just deduplicate
- Medium (50% retained): + summarize old messages  
- Aggressive (30% retained): Full compression

## API Endpoints

### POST /compress
```json
{
  "messages": [...],
  "mode": "medium", // light, medium, aggressive
  "preserve_last": 5, // number of recent messages to keep intact
  "extract_entities": true
}
```

### POST /estimate
- Returns estimated token count after compression
- Free to call

### GET /usage
- Track compression savings

## Pricing

| Tier | Monthly Cost | Compressed Tokens | Savings |
|------|-------------|-------------------|---------|
| Free | $0 | 10,000 | ~$3/mo value |
| Indie | $19 | 100,000 | ~$30/mo value |
| Pro | $49 | 500,000 | ~$150/mo value |
| Scale | $199 | 2,000,000 | ~$600/mo value |

## Competitive Advantage

1. **Faster than competitors** - <500ms compression
2. **Preserves context** - Not just summarize, maintain relationships
3. **Framework agnostic** - Works with OpenAI, Anthropic, Ollama, local LLMs
4. **Self-hosted option** - Docker image for enterprises

## Technical Stack

- FastAPI (Python)
- Sentence Transformers (embeddings)
- LangChain (summarization)
- Redis (caching)
- PostgreSQL (user data)

## Build Cost
- $500 (APIs + hosting for MVP)
- Most expensive: embedding API calls

## Differentiation

| Competitor | They Do | We Do |
|-----------|---------|-------|
| LangChain | Summarization chains | Optimized compression |
| Memo | Free summarization | Token optimization |
| None | API-first compression | Full context preservation |

## Quick Win
Build as OpenAI-compatible API middleware. Any app using OpenAI API can point to us first.

---

*Build it. Ship it. Profit.*
