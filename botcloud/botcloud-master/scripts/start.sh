#!/bin/bash
# BotCloud Start Script
# Starts all BotCloud services

# Create logs directory
mkdir -p ~/botcloud/logs

echo "🤖 Starting BotCloud..."

# Kill any existing processes
pkill -f "python3.*main.py" 2>/dev/null
pkill -f "python3.*example" 2>/dev/null
pkill -f "http.server.*9090" 2>/dev/null
sleep 1

# Start API server
echo "📡 Starting API server..."
cd ~/botcloud/api
nohup python3 main.py > ~/botcloud/logs/api.log 2>&1 &
sleep 2

# Check if API is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API server running on port 8001"
else
    echo "❌ API server failed to start"
fi

# Start dashboard
echo "🌐 Starting dashboard..."
cd ~
nohup python3 -m http.server 9090 > ~/botcloud/logs/dashboard.log 2>&1 &
sleep 1

echo "✅ BotCloud started!"
echo ""
echo "Access:"
echo "  Dashboard: http://localhost:9090/dashboard.html"
echo "  API: http://localhost:8000/health"
echo ""
echo "To stop: ~/botcloud/scripts/stop.sh"
