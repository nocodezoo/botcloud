#!/bin/bash
# BotCloud Stop Script
# Stops all BotCloud services

echo "🛑 Stopping BotCloud..."

# Kill API server
pkill -f "python3.*main.py" 2>/dev/null
echo "✅ API server stopped"

# Kill workers
pkill -f "python3.*example" 2>/dev/null
pkill -f "python3.*worker" 2>/dev/null
pkill -f "python3.*fullstack" 2>/dev/null
echo "✅ Workers stopped"

# Kill dashboard
pkill -f "http.server.*9090" 2>/dev/null
echo "✅ Dashboard stopped"

echo ""
echo "BotCloud stopped!"
