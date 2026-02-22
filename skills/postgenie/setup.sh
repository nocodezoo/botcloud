#!/bin/bash
# PostGenie Automation Setup Script

echo "Setting up PostGenie automation..."

# Install playwright if needed
if [ ! -d "node_modules/playwright" ]; then
    echo "Installing playwright..."
    npm install playwright
fi

# Start Chrome with debugging
echo "Starting Chrome with remote debugging on port 9222..."
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/vm-chrome --no-sandbox --disable-gpu --headless=new --disable-dev-shm-usage --no-first-run --remote-allow-origins=* > /tmp/chrome.log 2>&1 &

sleep 3

# Verify Chrome is running
if curl -s http://127.0.0.1:9222/json > /dev/null 2>&1; then
    echo "✓ Chrome is running with debugging on port 9222"
    echo ""
    echo "Next steps:"
    echo "1. Open http://127.0.0.1:9222 in your browser"
    echo "2. Click the link to open Chrome DevTools"
    echo "3. Log into https://postgenie.app"
    echo "4. Then use: node pb.js open https://postgenie.app/dashboard"
else
    echo "✗ Chrome failed to start. Check /tmp/chrome.log"
fi
