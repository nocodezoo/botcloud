#!/usr/bin/env node

/**
 * Persistent Browser Server
 * Keeps browser alive and accepts commands via stdin/stdout
 * Run: node pbs.js
 * Commands: open <url>, click <selector>, fill <selector> <text>, snapshot, quit
 */

const { chromium } = require('playwright');

let browser = null;
let page = null;

async function ensurePage() {
  if (!browser) {
    // Connect to Chrome on port 9222 (our debug-enabled Chrome)
    try {
      browser = await chromium.connectOverCDP('http://localhost:9222');
      console.error('Connected to Chrome');
    } catch (e) {
      console.error('Failed to connect:', e.message);
      return null;
    }
  }
  
  if (!page || page.isClosed()) {
    const pages = browser.contexts()[0]?.pages() || [];
    page = pages[0] || await browser.newPage();
  }
  
  return page;
}

async function execute(cmd, args) {
  const p = await ensurePage();
  if (!p) return { error: 'No browser' };
  
  try {
    switch (cmd) {
      case 'open':
        await p.goto(args[0], { waitUntil: 'networkidle', timeout: 30000 });
        return { url: p.url() };
        
      case 'click':
        await p.click(args[0], { timeout: 15000 });
        return { ok: true };
        
      case 'fill':
        await p.fill(args[0], args.slice(1).join(' '));
        return { ok: true };
        
      case 'wait':
        await p.waitForTimeout(parseInt(args[0]) || 1000);
        return { ok: true };
        
      case 'snapshot':
        return await p.accessibility.snapshot();
        
      case 'screenshot':
        await p.screenshot({ path: args[0] || 'screen.png', fullPage: true });
        return { ok: true, path: args[0] || 'screen.png' };
        
      case 'url':
        return { url: p.url() };
        
      case 'title':
        return { title: await p.title() };
        
      case 'quit':
        if (browser) await browser.close();
        return { ok: true };
        
      default:
        return { error: `Unknown command: ${cmd}` };
    }
  } catch (e) {
    return { error: e.message };
  }
}

const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

rl.on('line', async (line) => {
  const parts = line.trim().split(' ');
  const cmd = parts[0];
  const args = parts.slice(1);
  
  if (cmd === 'quit') {
    await execute('quit');
    process.exit(0);
  }
  
  const result = await execute(cmd, args);
  console.log(JSON.stringify(result));
});

console.error('Persistent Browser Server started on port 9222');
