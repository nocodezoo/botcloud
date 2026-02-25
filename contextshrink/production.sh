#!/bin/bash
# ContextShrink Auto-Compression Script - PRODUCTION
# Compresses session memory when threshold is exceeded

CONTEXTSHRINK_API="http://localhost:8000"
THRESHOLD=2000  # Compress if > 2000 tokens (typical LLM context limit)
MODE="medium"
PRESERVE_LAST=5

echo "========================================"
echo "ContextShrink Auto-Compression (PROD)"
echo "========================================"

# Check if ContextShrink API is running
if ! curl -s "$CONTEXTSHRINK_API/health" > /dev/null 2>&1; then
    echo "❌ ContextShrink API not running"
    exit 1
fi

# Get session messages from OpenClaw
# Try to get from session file or environment
SESSION_FILE="${OPENCLAW_SESSION:-/tmp/openclaw_session.json}"

if [ -f "$SESSION_FILE" ]; then
    MESSAGES=$(cat "$SESSION_FILE")
else
    # If no session file, try to get from running session
    # For now, use environment or skip
    echo "No session file found, checking for messages..."
    exit 0
fi

if [ -z "$MESSAGES" ]; then
    echo "No messages to compress"
    exit 0
fi

# Estimate tokens
ESTIMATE=$(curl -s -X POST "$CONTEXTSHRINK_API/estimate" \
    -H "Content-Type: application/json" \
    -d "{\"messages\": $MESSAGES}")

ORIGINAL=$(echo $ESTIMATE | python3 -c "import sys,json; print(json.load(sys.stdin).get('original_tokens', 0))" 2>/dev/null)

echo "Current tokens: $ORIGINAL"

if [ "$ORIGINAL" -gt "$THRESHOLD" ]; then
    echo "Threshold ($THRESHOLD) exceeded! Compressing..."
    
    # Compress
    RESULT=$(curl -s -X POST "$CONTEXTSHRINK_API/compress" \
        -H "Content-Type: application/json" \
        -d "{\"messages\": $MESSAGES, \"mode\": \"$MODE\", \"preserve_last\": $PRESERVE_LAST}")
    
    SAVINGS=$(echo $RESULT | python3 -c "import sys,json; print(json.load(sys.stdin).get('stats', {}).get('savings_percent', 0))" 2>/dev/null)
    COMPRESSED=$(echo $RESULT | python3 -c "import sys,json; print(json.load(sys.stdin).get('stats', {}).get('compressed_tokens', 0))" 2>/dev/null)
    
    # Save compressed messages
    echo "$RESULT" > "${SESSION_FILE}.compressed"
    
    echo "✅ Compressed to $COMPRESSED tokens"
    echo "💰 Savings: $SAVINGS%"
    
    # Announce to user
    echo "COMPRESSION_COMPLETE: $ORIGINAL→$COMPRESSED tokens ($SAVINGS% saved)"
else
    echo "✅ Under threshold ($THRESHOLD), no compression needed"
fi
