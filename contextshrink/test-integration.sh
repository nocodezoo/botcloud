#!/bin/bash
# ContextShrink Integration Test with OpenClaw
# This script simulates how ContextShrink would compress OpenClaw session messages

echo "========================================"
echo "ContextShrink x OpenClaw Integration"
echo "========================================"
echo ""

# Get current session messages (simulated)
# In real use, you'd get these from OpenClaw's session API

MESSAGES='[
  {"role": "system", "content": "You are Claw, a helpful AI assistant running on OpenClaw."},
  {"role": "user", "content": "Hello! I want to build a SaaS business."},
  {"role": "assistant", "content": "Great idea! What kind of SaaS were you thinking?"},
  {"role": "user", "content": "An AI agent infrastructure tool. Something that helps developers build agents faster."},
  {"role": "assistant", "content": "That is a huge market! There are many companies building agent frameworks."},
  {"role": "user", "content": "I want to focus on context compression. Helping LLMs remember more for less."},
  {"role": "assistant", "content": "Excellent idea! Token costs add up quickly for long conversations."},
  {"role": "user", "content": "Exactly! I think we can save developers 70% on API costs."},
  {"role": "assistant", "content": "That is very compelling. What is your business model?"},
  {"role": "user", "content": "Freemium. Free tier, then $19/month indie, $49 pro."},
  {"role": "assistant", "content": "Good freemium model. You could also offer enterprise self-hosted."},
  {"role": "user", "content": "Yes! Docker image for self-hosted is the plan."},
  {"role": "assistant", "content": "Great plan. Let me help you build ContextShrink."},
  {"role": "user", "content": "Perfect. How does the compression algorithm work?"},
  {"role": "assistant", "content": "It uses recency bias - keeping recent messages, summarizing older ones."},
  {"role": "user", "content": "What about entity extraction?"},
  {"role": "assistant", "content": "It extracts key topics, actions, and decisions from the conversation."},
  {"role": "user", "content": "Can you show me the code?"},
  {"role": "assistant", "content": "Absolutely! Here is how it works..."}
]'

echo "Testing ContextShrink API..."
echo ""

# Call the compression API
RESULT=$(curl -s -X POST "http://localhost:8000/compress" \
  -H "Content-Type: application/json" \
  -d "{\"messages\": $MESSAGES, \"mode\": \"medium\", \"preserve_last\": 5}")

# Parse results
ORIGINAL=$(echo $RESULT | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['stats']['original_tokens'])")
COMPRESSED=$(echo $RESULT | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['stats']['compressed_tokens'])")
SAVINGS=$(echo $RESULT | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['stats']['savings_percent'])")

echo "========================================"
echo "RESULTS"
echo "========================================"
echo "Original tokens:   $ORIGINAL"
echo "Compressed tokens: $COMPRESSED"
echo "SAVINGS:          $SAVINGS%"
echo ""

# Cost savings
echo "========================================"
echo "COST SAVINGS (GPT-4 pricing)"
echo "========================================"
ORIG_COST=$(python3 -c "print(f'{$ORIGINAL / 1000000 * 10:.4f}')")
NEW_COST=$(python3 -c "print(f'{$COMPRESSED / 1000000 * 10:.4f}')")
SAVED_COST=$(python3 -c "print(f'{($ORIGINAL - $COMPRESSED) / 1000000 * 10:.4f}')")

echo "Per conversation:"
echo "  Before: \$$ORIG_COST"
echo "  After:  \$$NEW_COST"
echo "  Saved:  \$$SAVED_COST"
echo ""
echo "Daily (1000 users):"
echo "  Saved: \$(python3 -c \"print(f'{($ORIGINAL - $COMPRESSED) / 1000000 * 10 * 1000:.2f}')\")"
echo ""

# Show the compressed output
echo "========================================"
echo "COMPRESSED OUTPUT"
echo "========================================"
echo "$RESULT" | python3 -m json.tool | head -30
