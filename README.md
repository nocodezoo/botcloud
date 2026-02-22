# OpenClaw Workspace

Personal AI assistant workspace for Ryan.

## Skills

### PostGenie Automation
- `skills/postgenie/` - Automate PostGenie for bulk creating Instagram/TikTok posts
- Uses custom persistent browser to bypass OpenClaw browser relay bug

## Tools

- `tools/pb.js` - Main persistent browser automation tool
- `tools/pbs.js` - Persistent browser server (experimental)
- `tools/persistent-browser.js` - Browser server implementation

## Setup

### PostGenie Automation

1. Start Chrome with debugging:
```bash
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/vm-chrome --no-sandbox --disable-gpu --headless=new --disable-dev-shm-usage --no-first-run --remote-allow-origins=*
```

2. Log into PostGenie

3. Automate:
```bash
node tools/pb.js open https://postgenie.app/dashboard
node tools/pb.js click "View Media Collections"
```

## History

### 2026-02-22 - Browser Automation Fix

The OpenClaw built-in browser tool has a bug where it dies after exactly 2 actions. Error: "Can't reach the OpenClaw browser control service. Restart the OpenClaw gateway."

**Root cause:** The browser relay on port 18792 returns "Unauthorized" when trying to check status after 2 actions. This is a bug in OpenClaw's gateway code, not the Chrome extension.

**Solution:** Built a custom persistent browser tool (`pb.js`) that:
1. Connects to Chrome directly via CDP (Chrome DevTools Protocol)
2. Keeps the browser alive between commands
3. Works with any Chrome profile (including logged-in sessions)
4. Bypasses the broken OpenClaw relay entirely

The tool requires Chrome to be started with `--remote-debugging-port=9222` manually, but once running, it works reliably for any number of actions.
