#!/bin/bash
# ContextShrink Watchdog
# Auto-restarts ContextShrink API if it crashes

API_URL="http://localhost:8000"
API_DIR="/home/openryanclaw/.openclaw/workspace/contextshrink"
LOG_FILE="/home/openryanclaw/.openclaw/workspace/contextshrink/watchdog.log"

echo "$(date): Checking ContextShrink..." >> $LOG_FILE

# Check if API is responding
if curl -s --max-time 3 "$API_URL/health" > /dev/null 2>&1; then
    echo "$(date): ✅ ContextShrink is running" >> $LOG_FILE
    exit 0
fi

# API is down, restart it
echo "$(date): ❌ ContextShrink down! Restarting..." >> $LOG_FILE

# Kill any existing process
pkill -f "python3 main.py" 2>/dev/null
sleep 1

# Start the API
cd $API_DIR
python3 main.py >> $LOG_FILE 2>&1 &
sleep 3

# Verify it started
if curl -s --max-time 3 "$API_URL/health" > /dev/null 2>&1; then
    echo "$(date): ✅ ContextShrink restarted successfully" >> $LOG_FILE
else
    echo "$(date): ⚠️ Failed to restart ContextShrink" >> $LOG_FILE
fi
