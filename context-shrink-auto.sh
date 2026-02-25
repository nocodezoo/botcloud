#!/bin/bash
# ContextShrink Auto-Compression Script
# Called by cron job to compress session if tokens exceed threshold

CONTEXTSHRINK_API="http://localhost:8000"
THRESHOLD=50  # Compress if > 50 tokens

echo "========================================"
echo "ContextShrink Auto-Compression"
echo "========================================"

# Get recent conversation messages (simulated - in production would pull from session)
# For now, this is a placeholder that demonstrates the concept

# Check if ContextShrink API is running
if ! curl -s "$CONTEXTSHRINK_API/health" > /dev/null 2>&1; then
    echo "❌ ContextShrink API not running"
    exit 1
fi

# In production: Get session messages from OpenClaw
# For demo: Use sample messages
MESSAGES='[
    {"role": "system", "content": "You are Claw."},
    {"role": "user", "content": "Test message 1"},
    {"role": "assistant", "content": "Response 1"},
    {"role": "user", "content": "Test message 2"},
    {"role": "assistant", "content": "Response 2"},
    {"role": "user", "content": "Test message 3"},
    {"role": "assistant", "content": "Response 3"},
    {"role": "user", "content": "Test message 4"},
    {"role": "assistant", "content": "Response 4"},
    {"role": "user", "content": "Test message 5"}
]'

# Estimate tokens
RESULT=$(curl -s -X POST "$CONTEXTSHRINK_API/estimate" \
    -H "Content-Type: application/json" \
    -d "{\"messages\": $MESSAGES}")

ORIGINAL=$(echo $RESULT | python3 -c "import sys,json; print(json.load(sys.stdin).get('original_tokens', 0))" 2>/dev/null)
MEDIUM=$(echo $RESULT | python3 -c "import sys,json; print(json.load(sys.stdin).get('estimated_medium', 0))" 2>/dev/null)

echo "Original tokens: $ORIGINAL"
echo "After compression: $MEDIUM"

if [ "$ORIGINAL" -gt "$THRESHOLD" ]; then
    echo "Threshold exceeded! Compressing..."
    
    # Actually compress
    COMPRESS_RESULT=$(curl -s -X POST "$CONTEXTSHRINK_API/compress" \
        -H "Content-Type: application/json" \
        -d "{\"messages\": $MESSAGES, \"mode\": \"medium\", \"preserve_last\": 3}")
    
    SAVINGS=$(echo $COMPRESS_RESULT | python3 -c "import sys,json; print(json.load(sys.stdin).get('stats', {}).get('savings_percent', 0))" 2>/dev/null)
    
    echo "✅ Compressed! Savings: $SAVINGS%"
else
    echo "✅ Under threshold, no compression needed"
fi
