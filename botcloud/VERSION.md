# BotCloud v1.4.0

## Version History
- v1.4.0 (Current) - Apache2 deployment
- v1.3.0 - Test suite
- v1.2.0 - WebSocket + Discovery + Task Queue
- v1.1.0 - OpenClaw integration + Docker
- v1.0.0 - Initial API

## What's New in v1.4.0

### Apache2 Deployment
- `deployment/botcloud.conf` - Apache VirtualHost config
- `deployment/botcloud.service` - SystemD service
- `deployment/deploy.sh` - One-command deployment script

### Features
- HTTP proxy to port 8000
- WebSocket proxy to port 8001
- SystemD service for auto-start
- Apache2 integration

## Deployment

### Quick Deploy
```bash
cd botcloud
sudo bash deployment/deploy.sh
```

### Manual
1. Install dependencies
2. Enable Apache modules
3. Copy config to sites-available
4. Start service

### Endpoints After Deploy
- API: http://localhost:8000
- WebSocket: ws://localhost:8001
- Discovery: http://localhost:8002
- Task Queue: http://localhost:8003

## Requirements
- Python 3.8+
- Apache2
- systemd
