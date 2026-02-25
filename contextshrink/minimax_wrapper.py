#!/usr/bin/env python3
"""
ContextShrink Middleware for MiniMax API
Wraps LLM calls to compress context before sending

Usage:
  python minimax_wrapper.py "Your prompt here"
"""

import os
import sys
import json
import requests
from typing import List, Dict, Any

CONTEXTSHINK_URL = "http://localhost:8000"
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimax.chat/v1"

# Sample conversation history (would come from actual session)
DEFAULT_MESSAGES = [
    {"role": "system", "content": "You are Claw, a helpful AI assistant."},
    {"role": "user", "content": "Hello! I want to build a SaaS business."},
    {"role": "assistant", "content": "Great idea! What kind of SaaS?"},
    {"role": "user", "content": "An AI agent infrastructure tool for developers."},
    {"role": "assistant", "content": "That is a huge market. There are many companies building agent frameworks."},
    {"role": "user", "content": "I want to focus on context compression. Helping LLMs remember more."},
    {"role": "assistant", "content": "Excellent idea! Token costs add up quickly for long conversations."},
    {"role": "user", "content": "Exactly! I think we can save developers 70% on API costs."},
    {"role": "assistant", "content": "That is very compelling. What is your business model?"},
    {"role": "user", "content": "Freemium. Free tier, then $19/month indie, $49 pro."},
    {"role": "assistant", "content": "Good freemium model. You could also offer enterprise self-hosted."},
    {"role": "user", "content": "Yes! Docker image for self-hosted is the plan."},
    {"role": "assistant", "content": "Great plan. Let me help you build ContextShrink."},
    {"role": "user", "content": "Perfect. How does the compression algorithm work?"},
    {"role": "assistant", "content": "It uses recency bias - keeping recent messages at full fidelity, summarizing older ones."},
    {"role": "user", "content": "What about entity extraction?"},
    {"role": "assistant", "content": "It extracts key topics, actions, and decisions from the conversation."},
]


def compress_messages(messages: List[Dict], mode: str = "medium", preserve_last: int = 5) -> Dict:
    """Compress messages using ContextShrink API"""
    try:
        resp = requests.post(
            f"{CONTEXTSHINK_URL}/compress",
            json={"messages": messages, "mode": mode, "preserve_last": preserve_last},
            timeout=10
        )
        return resp.json()
    except Exception as e:
        print(f"Compression error: {e}")
        return {"compressed_messages": messages, "stats": {"savings_percent": 0}}


def estimate_tokens(text: str) -> int:
    """Simple token estimation"""
    return len(text.split()) * 3 // 4


def call_minimax(messages: List[Dict], user_prompt: str) -> str:
    """Call MiniMax API with messages"""
    if not MINIMAX_API_KEY:
        return "MINIMAX_API_KEY not set"
    
    # Add user prompt
    full_messages = messages + [{"role": "user", "content": user_prompt}]
    
    payload = {
        "model": "MiniMax-M2.5",
        "messages": full_messages,
        "temperature": 0.7
    }
    
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        resp = requests.post(
            f"{MINIMAX_BASE_URL}/text/chatcompletion_v2",
            json=payload,
            headers=headers,
            timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "No response")
        else:
            return f"Error: {resp.status_code} - {resp.text}"
    except Exception as e:
        return f"API Error: {e}"


def demo():
    """Demonstrate ContextShrink with MiniMax"""
    print("=" * 60)
    print("ContextShrink x MiniMax Demo")
    print("=" * 60)
    print()
    
    # Show original context size
    total_tokens = sum(estimate_tokens(m.get("content", "")) for m in DEFAULT_MESSAGES)
    print(f"Original conversation: {len(DEFAULT_MESSAGES)} messages, ~{total_tokens} tokens")
    print()
    
    # Compress
    print("Compressing with ContextShrink...")
    result = compress_messages(DEFAULT_MESSAGES, mode="medium", preserve_last=5)
    
    stats = result.get("stats", {})
    print(f"Compressed: ~{stats.get('compressed_tokens', '?')} tokens")
    print(f"SAVINGS: {stats.get('savings_percent', 0)}%")
    print()
    
    # Show summary
    print("Summary generated:")
    print(f"  {result.get('summary', 'N/A')[:100]}...")
    print()
    
    print("Entities extracted:")
    ents = result.get("entities", {})
    print(f"  Topics: {ents.get('topics', [])}")
    print(f"  Actions: {ents.get('actions', [])}")
    print()
    
    # Note about MiniMax API
    print("-" * 60)
    print("Note: To actually call MiniMax, set MINIMAX_API_KEY env var")
    print("  export MINIMAX_API_KEY='your-key-here'")
    print("-" * 60)


if __name__ == "__main__":
    demo()
