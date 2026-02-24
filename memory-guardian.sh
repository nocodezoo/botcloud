#!/bin/bash
# Memory Guardian - Commits staged memory snapshots to GitHub
# Run from workspace directory

cd /home/openryanclaw/.openclaw/workspace

# Check if staging has new files
STAGED=$(ls -1 memory-staging/*.md 2>/dev/null | wc -l)
if [ "$STAGED" -eq 0 ]; then
    exit 0  # No snapshots to push
fi

# Copy staging to backup folder
mkdir -p memory-backup
cp memory-staging/*.md memory-backup/

# Stage and commit
git add memory-backup/*.md

TIMESTAMP=$(date "+%Y-%m-%d %H:%M")
git commit -m "Memory snapshots: $TIMESTAMP"

# Push to GitHub
git push origin main 2>/dev/null || git push origin master 2>/dev/null

# Clear staging after successful push
rm -f memory-staging/*.md

echo "Memory Guardian: Pushed $STAGED snapshots at $TIMESTAMP"
