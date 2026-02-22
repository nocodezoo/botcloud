# PostGenie Automation Skill

Automate PostGenie (postgenie.app) for bulk creating Instagram/TikTok posts with UGC videos.

## Why This Skill?

The OpenClaw built-in browser has a bug where it dies after 2 actions. This skill uses a custom persistent browser that connects to Chrome via CDP and stays alive.

## Setup

### 1. Start Debug Chrome

```bash
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/vm-chrome --no-sandbox --disable-gpu --headless=new --disable-dev-shm-usage --no-first-run --remote-allow-origins=*
```

Or in background:
```bash
nohup google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/vm-chrome --no-sandbox --disable-gpu --headless=new --disable-dev-shm-usage --no-first-run --remote-allow-origins=* > /tmp/chrome.log 2>&1 &
```

### 2. Log Into PostGenie

Navigate to https://postgenie.app and log in with your Google account. The session will be saved in the Chrome profile.

### 3. Use the Automation Tool

```bash
# Navigate
node tools/pb.js open https://postgenie.app/dashboard

# Click elements
node tools/pb.js click "View Media Collections"
node tools/pb.js click "UGC - Influencers"

# Fill forms
node tools/pb.js fill "textbox >> nth=0" "Your post content here"

# Wait for page to load
node tools/pb.js wait 2000

# Get page structure
node tools/pb.js snapshot

# Screenshot
node tools/pb.js screenshot output.png
```

## Commands

| Command | Example | Description |
|---------|---------|-------------|
| `open <url>` | `pb.js open https://example.com` | Navigate to URL |
| `click <selector>` | `pb.js click "View Media Collections"` | Click element by text |
| `fill <selector> <text>` | `pb.js fill "input" "hello"` | Fill input field |
| `type <selector> <text>` | `pb.js type "input" "hello"` | Type text |
| `press <selector> <key>` | `pb.js press "input" "Enter"` | Press key |
| `wait <ms>` | `pb.js wait 2000` | Wait milliseconds |
| `snapshot` | `pb.js snapshot` | Get accessibility tree |
| `screenshot [path]` | `pb.js screenshot` | Take screenshot |
| `eval <js>` | `pb.js eval "document.title"` | Run JavaScript |
| `url` | `pb.js url` | Get current URL |
| `title` | `pb.js title` | Get page title |
| `quit` | `pb.js quit` | Close browser |

## Creating Posts (Workflow)

1. **Open PostGenie**
   ```
   node tools/pb.js open https://postgenie.app/dashboard
   ```

2. **Open Media Collections**
   ```
   node tools/pb.js click "View Media Collections"
   ```

3. **Select Collection (UGC - Influencers V1 for short videos)**
   ```
   node tools/pb.js click "UGC - Influencers"
   ```

4. **Select Video** (click download button on video)
   ```
   node tools/pb.js click <video-selector>
   ```

5. **Fill Post Content**
   ```
   node tools/pb.js fill "textbox >> nth=0" "Your message"
   ```

6. **Open Colors & Styles** (optional - for text overlay)
   ```
   node tools/pb.js click "Colors & Styles"
   ```

7. **Set Font** (optional):
   - Font: Roboto
   - Size: 40px
   - Vertical Position: 56%

8. **Add Caption**
   ```
   node tools/pb.js click "Post Caption"
   node tools/pb.js fill "textbox >> nth=1" "Your caption #hashtags"
   ```

9. **Ensure Auto Hashtags is checked**

10. **Save Post**
    ```
    node tools/pb.js click "Save Post"
    ```

## Text Overlay Settings

For consistent text overlay across posts:
- **Font:** Roboto
- **Size:** 40px
- **Vertical Position:** 56%

## Troubleshooting

### Chrome not connecting?
- Make sure Chrome is running with `--remote-debugging-port=9222`
- Check: `curl -s http://127.0.0.1:9222/json`

### Need to log in again?
- Delete the profile and restart: `rm -rf /tmp/vm-chrome`
- Start Chrome fresh and log in

### Port already in use?
- Kill existing Chrome: `pkill -f "vm-chrome"`
- Or use a different port

## Files

- `tools/pb.js` - Main automation tool
- `tools/pbs.js` - Persistent server version (experimental)
- `SKILL.md` - This file

## Notes

- This skill bypasses the OpenClaw browser relay which has a bug causing it to die after 2 actions
- The browser must be started manually before automation
- Uses Playwright to connect to Chrome via Chrome DevTools Protocol (CDP)
- Works with any logged-in Chrome profile
