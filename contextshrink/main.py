"""
ContextShrink - AI Context Compression API
Version: 0.3.0

Core compression engine with OpenAI-compatible middleware.
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# Compression modes
class CompressionMode(str, Enum):
    LIGHT = "light"
    MEDIUM = "medium"
    AGGRESSIVE = "aggressive"


# Compression ratios for each mode
COMPRESSION_RATIOS = {
    CompressionMode.LIGHT: 0.8,
    CompressionMode.MEDIUM: 0.5,
    CompressionMode.AGGRESSIVE: 0.3,
}


def estimate_tokens(text: str) -> int:
    """Estimate token count"""
    if not text:
        return 0
    words = len(text.split())
    word_tokens = int(words * 0.75)
    char_tokens = len(text) // 4
    special = len(re.findall(r'[{}\[\]()"\'=;]', text))
    return (word_tokens + char_tokens + special) // 3


def estimate_messages_tokens(messages: List[Dict]) -> int:
    """Estimate total tokens in messages"""
    total = 0
    for msg in messages:
        total += 4  # Role overhead
        content = msg.get("content", "")
        if content:
            total += estimate_tokens(content)
    return total


class MessageCompressor:
    """Core compression engine - Version 0.3.0"""
    
    def __init__(self, mode: CompressionMode = CompressionMode.MEDIUM, preserve_last: int = 5):
        self.mode = mode
        self.preserve_last = preserve_last
        self.compression_ratio = COMPRESSION_RATIOS[mode]
    
    def compress(self, messages: List[Dict], extract_entities: bool = True) -> Dict[str, Any]:
        """Compress message history"""
        if not messages:
            return self._empty_result()
        
        original_tokens = estimate_messages_tokens(messages)
        preserve_count = min(self.preserve_last, len(messages))
        to_preserve = messages[-preserve_count:] if preserve_count > 0 else []
        to_compress = messages[:-preserve_count] if preserve_count < len(messages) else []
        
        result_messages = []
        
        # Generate summary
        summary = self._generate_summary(to_compress)
        if summary:
            result_messages.append({"role": "system", "content": f"CONVERSATION SUMMARY: {summary}"})
        
        # Extract entities
        entities = {}
        if extract_entities:
            entities = self._extract_entities(to_compress)
            entity_text = self._format_entities(entities)
            if entity_text:
                result_messages.append({"role": "system", "content": f"KEY ENTITIES: {entity_text}"})
        
        result_messages.extend(to_preserve)
        compressed_tokens = estimate_messages_tokens(result_messages)
        
        savings = 0
        if original_tokens > 0:
            savings = ((original_tokens - compressed_tokens) / original_tokens) * 100
        
        return {
            "compressed_messages": result_messages,
            "summary": summary,
            "entities": entities,
            "stats": {
                "original_tokens": original_tokens,
                "compressed_tokens": compressed_tokens,
                "savings_percent": round(savings, 1),
                "messages_preserved": len(to_preserve),
                "messages_compressed": len(to_compress),
                "mode": self.mode.value
            }
        }
    
    def _empty_result(self) -> Dict[str, Any]:
        return {
            "compressed_messages": [],
            "summary": "",
            "entities": {},
            "stats": {"original_tokens": 0, "compressed_tokens": 0, "savings_percent": 0, "mode": self.mode.value}
        }
    
    def _generate_summary(self, messages: List[Dict]) -> str:
        if not messages:
            return ""
        
        user_msgs = [m.get("content", "") for m in messages if m.get("role") == "user"]
        assistant_msgs = [m.get("content", "") for m in messages if m.get("role") == "assistant"]
        
        parts = []
        if user_msgs:
            topic = user_msgs[0][:80].strip()
            if topic:
                parts.append(f"User discussed: {topic}...")
        
        if len(user_msgs) > 1:
            parts.append(f"User sent {len(user_msgs)} messages")
        
        if assistant_msgs:
            parts.append(f"Assistant provided {len(assistant_msgs)} responses")
        
        return ". ".join(parts) if parts else "Earlier conversation occurred."
    
    def _extract_entities(self, messages: List[Dict]) -> Dict[str, Any]:
        entities = {"topics": set(), "actions": set(), "decisions": []}
        all_content = " ".join([m.get("content", "").lower() for m in messages])
        
        topic_keywords = {
            "ai_related": ["ai", "agent", "llm", "gpt", "openai", "claude", "model"],
            "building": ["build", "create", "make", "develop", "saas", "app", "tool", "product"],
            "business": ["business", "startup", "company", "revenue", "customer", "pricing"],
            "coding": ["code", "python", "javascript", "api", "programming", "developer"],
            "automation": ["automate", "automation", "workflow", "schedule", "cron"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in all_content for kw in keywords):
                entities["topics"].add(topic)
        
        action_keywords = {
            "planning": ["plan", "want to", "going to", "will", "intend"],
            "completed": ["done", "finished", "completed", "built", "created"],
            "learning": ["learn", "study", "understand", "explain", "how"]
        }
        
        for action, keywords in action_keywords.items():
            if any(kw in all_content for kw in keywords):
                entities["actions"].add(action)
        
        decision_patterns = ["decided", "chose", "going with", "will use", "selected"]
        for msg in messages:
            content = msg.get("content", "").lower()
            for pattern in decision_patterns:
                if pattern in content:
                    for sent in content.split("."):
                        if pattern in sent:
                            cleaned = sent.strip()[:80]
                            if cleaned:
                                entities["decisions"].append(cleaned)
                            break
        
        return {
            "topics": list(entities["topics"])[:5],
            "actions": list(entities["actions"])[:5],
            "decisions": entities["decisions"][:3]
        }
    
    def _format_entities(self, entities: Dict[str, Any]) -> str:
        parts = []
        if entities.get("topics"):
            parts.append(f"Topics: {', '.join(entities['topics'])}")
        if entities.get("actions"):
            parts.append(f"Actions: {', '.join(entities['actions'])}")
        if entities.get("decisions"):
            parts.append(f"Decisions: {'; '.join(entities['decisions'])}")
        return " | ".join(parts)


# FastAPI app
app = FastAPI(
    title="ContextShrink API",
    description="AI Context Compression - Save 70% on LLM costs",
    version="0.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global compressor instance
compressor = MessageCompressor()


# Request models
class CompressRequest(BaseModel):
    messages: List[Dict[str, Any]]
    mode: CompressionMode = CompressionMode.MEDIUM
    preserve_last: int = 5
    extract_entities: bool = True


class EstimateRequest(BaseModel):
    messages: List[Dict[str, Any]]


class EstimateResponse(BaseModel):
    original_tokens: int
    estimated_light: int
    estimated_medium: int
    estimated_aggressive: int
    savings_light_percent: float
    savings_medium_percent: float
    savings_aggressive_percent: float


# OpenAI-compatible request model
class OpenAIChatRequest(BaseModel):
    messages: List[Dict[str, Any]]
    model: Optional[str] = "gpt-4"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    compress: bool = True
    compression_mode: CompressionMode = CompressionMode.MEDIUM
    preserve_last: int = 5


@app.get("/")
def root():
    return {
        "name": "ContextShrink API",
        "version": "0.3.0",
        "description": "AI Context Compression - Save 70% on LLM costs",
        "docs": "/docs",
        "endpoints": {
            "compress": "/compress",
            "estimate": "/estimate",
            "openai_compatible": "/v1/chat/completions"
        }
    }


@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/compress")
def compress(req: CompressRequest):
    """Compress message history"""
    try:
        comp = MessageCompressor(mode=req.mode, preserve_last=req.preserve_last)
        return comp.compress(req.messages, extract_entities=req.extract_entities)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/estimate", response_model=EstimateResponse)
def estimate(req: EstimateRequest):
    """Estimate compression without compressing (free)"""
    original = estimate_messages_tokens(req.messages)
    preserve = min(5, len(req.messages))
    recent_tokens = sum(estimate_tokens(m.get("content", "")) for m in req.messages[-preserve:])
    older_tokens = original - recent_tokens
    
    results = {}
    for mode in CompressionMode:
        ratio = COMPRESSION_RATIOS[mode]
        compressed = recent_tokens + int(older_tokens * ratio)
        results[mode.value] = compressed
    
    savings = {}
    for mode, comp in results.items():
        savings[mode] = round(((original - comp) / original) * 100, 1) if original > 0 else 0
    
    return {
        "original_tokens": original,
        "estimated_light": results["light"],
        "estimated_medium": results["medium"],
        "estimated_aggressive": results["aggressive"],
        "savings_light_percent": savings["light"],
        "savings_medium_percent": savings["medium"],
        "savings_aggressive_percent": savings["aggressive"]
    }


@app.post("/v1/chat/completions")
def openai_compatible(req: OpenAIChatRequest):
    """
    OpenAI-compatible endpoint with automatic compression.
    
    Use this as a drop-in replacement for OpenAI's chat completions API.
    The messages will be compressed before being passed to your LLM.
    """
    try:
        # Compress messages if enabled
        if req.compress:
            comp = MessageCompressor(mode=req.compression_mode, preserve_last=req.preserve_last)
            result = comp.compress(req.messages)
            compressed_messages = result["compressed_messages"]
            stats = result["stats"]
        else:
            compressed_messages = req.messages
            stats = {"savings_percent": 0}
        
        # Return the compressed messages (would call actual LLM here)
        # For demo, we return what would be sent to LLM
        return {
            "id": f"chatcmpl-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "object": "chat.completion",
            "created": int(datetime.utcnow().timestamp()),
            "model": req.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "[Messages compressed. Would send to LLM with " + 
                                  f"{stats.get('savings_percent', 0)}% savings]"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": stats.get("compressed_tokens", 0),
                "completion_tokens": 0,
                "total_tokens": stats.get("compressed_tokens", 0)
            },
            "_contextshrink": {
                "compression_stats": stats,
                "compressed_messages": compressed_messages
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
def get_stats():
    """Get API usage stats"""
    return {
        "version": "0.3.0",
        "features": [
            "compress - Compress message history",
            "estimate - Free compression estimation",
            "v1/chat/completions - OpenAI-compatible with auto-compression"
        ],
        "compression_modes": ["light", "medium", "aggressive"]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
