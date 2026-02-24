#!/bin/bash
# Memory Writer - Creates timestamped snapshots every 10 minutes
# Run from workspace directory

cd /home/openryanclaw/.openclaw/workspace
mkdir -p memory-staging

TIMESTAMP=$(date "+%Y-%m-%d_%H-%M")

# Copy current memory to staging with timestamp
cp memory/$(date +%Y-%m-%d).md memory-staging/memory_$TIMESTAMP.md 2>/dev/null
cp MEMORY.md memory-staging/MEMORY_$TIMESTAMP.md 2>/dev/null

echo "Memory Writer: Snapshot created at $TIMESTAMP"
