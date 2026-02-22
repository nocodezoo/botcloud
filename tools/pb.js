#!/usr/bin/env node

/**
 * Persistent Browser - Connects to your running Chrome via CDP
 * Uses your existing session with all logins
 * 
 * Usage: node pb.js <command> [args...]
 */

const { chromium } = require('playwright');

let browser = null;
let page = null;

// OpenClaw browser relay auth token
const AUTH_TOKEN = 'd97087b544968c9fac58bcf36af8033cc916601fcd53c177';

async function getPage() {
  if (!browser || !page || page.isClosed()) {
    // Try to connect to your running Chrome
    const debugPorts = [18792, 9222, 9223, 9224, 9225];
    
    for (const port of debugPorts) {
      try {
        console.error(`Trying Chrome on port ${port}...`);
        // For OpenClaw relay (18792), we need to get the websocket URL with auth
        if (port === 18792) {
          const response = await fetch(`http://localhost:${port}/json`, {
            headers: { 'Authorization': `Bearer ${AUTH_TOKEN}` }
          });
          if (response.ok) {
            const data = await response.json();
            const wsUrl = data[0]?.webSocketDebuggerUrl;
            if (wsUrl) {
              // Replace http with ws and add auth
              const authWsUrl = wsUrl.replace('ws://', `ws://localhost:${port}/`) 
                                + `?token=${AUTH_TOKEN}`;
              browser = await chromium.connectOverCDP(authWsUrl);
              console.error('Connected to OpenClaw browser!');
              break;
            }
          }
        } else {
          browser = await chromium.connectOverCDP(`http://localhost:${port}`);
          console.error('Connected to Chrome!');
          break;
        }
      } catch (e) {
        console.error(`Port ${port} failed: ${e.message}`);
      }
    }
    
    if (!browser) {
      throw new Error('Could not connect to Chrome. Is it running with --remote-debugging-port?');
    }
    
    // Get first page or create new one
    const context = browser.contexts()[0];
    if (context) {
      page = context.pages()[0];
    }
    if (!page) {
      page = await browser.newPage();
    }
  }
  
  return page;
}

async function run() {
  const args = process.argv.slice(2);
  const cmd = args[0];
  
  try {
    const p = await getPage();
    
    switch (cmd) {
      case 'open':
        await p.goto(args[1], { waitUntil: 'networkidle', timeout: 30000 });
        console.log(JSON.stringify({ url: p.url() }));
        break;
        
      case 'click':
        await p.click(args[1], { timeout: 15000 });
        console.log(JSON.stringify({ ok: true }));
        break;
        
      case 'fill':
        await p.fill(args[1], args.slice(2).join(' '));
        console.log(JSON.stringify({ ok: true }));
        break;
        
      case 'type':
        await p.type(args[1], args.slice(2).join(' '));
        console.log(JSON.stringify({ ok: true }));
        break;
        
      case 'press':
        await p.press(args[1], args[2]);
        console.log(JSON.stringify({ ok: true }));
        break;
        
      case 'wait':
        await p.waitForTimeout(parseInt(args[1]) || 1000);
        console.log(JSON.stringify({ ok: true }));
        break;
        
      case 'snapshot':
        const tree = await p.accessibility.snapshot();
        console.log(JSON.stringify(tree));
        break;
        
      case 'screenshot':
        const path = args[1] || 'screenshot.png';
        await p.screenshot({ path, fullPage: true });
        console.log(JSON.stringify({ ok: true, path }));
        break;
        
      case 'eval':
        const result = await p.evaluate(args[1]);
        console.log(JSON.stringify(result));
        break;
        
      case 'url':
        console.log(JSON.stringify({ url: p.url() }));
        break;
        
      case 'title':
        console.log(JSON.stringify({ title: await p.title() }));
        break;
        
      case 'quit':
        if (browser) {
          await browser.close();
          browser = null;
          page = null;
        }
        console.log(JSON.stringify({ ok: true }));
        break;
        
      default:
        console.log(JSON.stringify({ error: `Unknown command: ${cmd}` }));
    }
  } catch (err) {
    console.log(JSON.stringify({ error: err.message }));
  }
}

run();
