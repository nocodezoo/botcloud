#!/bin/bash
# Persistent agent-browser wrapper
# Keeps browser alive and accepts commands via FIFO

BROWSER_CMD="agent-browser"
FIFO="/tmp/browser-fifo-$$"

mkfifo "$FIFO"

# Start agent-browser in background, reading from fifo
while true; do
  if read line < "$FIFO"; then
    echo "Executing: $line" >&2
    $BROWSER_CMD $line 2>&1
    echo "---END---" >&2
  fi
done &

BROWSER_PID=$!

echo "Browser wrapper started, PID: $BROWSER_PID"
echo "FIFO: $FIFO"

# Keepalive
wait
