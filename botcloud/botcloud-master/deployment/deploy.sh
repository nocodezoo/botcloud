#!/bin/bash
# BotCloud Deployment Script for Apache2

echo "BotCloud Apache2 Deployment"
echo "==========================="

# Install dependencies
echo "Installing Python dependencies..."
cd /home/openryanclaw/.openclaw/workspace/botcloud/api
pip3 install -q fastapi uvicorn pydantic

# Enable required Apache modules
echo "Enabling Apache modules..."
a2enmod proxy proxy_http proxy_wstunnel rewrite ssl 2>/dev/null

# Copy config
echo "Copying Apache config..."
sudo cp /home/openryanclaw/.openclaw/workspace/botcloud/deployment/botcloud.conf /etc/apache2/sites-available/botcloud.conf

# Enable site
echo "Enabling BotCloud site..."
sudo a2ensite botcloud.conf

# Copy service file
echo "Copying systemd service..."
sudo cp /home/openryanclaw/.openclaw/workspace/botcloud/deployment/botcloud.service /etc/systemd/system/botcloud.service

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

# Start BotCloud
echo "Starting BotCloud..."
sudo systemctl start botcloud

# Restart Apache
echo "Restarting Apache..."
sudo systemctl restart apache2

echo ""
echo "BotCloud deployed!"
echo "API: http://localhost:8000"
echo "WebSocket: ws://localhost:8001"
echo ""
echo "To check status:"
echo "  systemctl status botcloud"
echo "  apachectl status"
