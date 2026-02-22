#!/usr/bin/env node

/**
 * Persistent Browser Server
 * Keeps a browser instance alive and accepts commands via stdin/stdout
 * This avoids the OpenClaw browser relay issues
 */

const { chromium } = require('playwright');

let browser = null;
let page = null;

async function ensureBrowser() {
  if (!browser) {
    // Try to connect to existing Chrome with remote debugging
    try {
      console.error('Trying to connect to existing Chrome...');
      browser = await chromium.connectOverCDP('http://localhost:9222');
      console.error('Connected to existing Chrome');
    } catch (e) {
      console.error('Launching new browser...');
      browser = await chromium.launch({ 
        headless: false,
        args: ['--start-maximized']
      });
      console.error('New browser launched');
    }
  }
  return browser;
}

async function ensurePage() {
  await ensureBrowser();
  if (!page) {
    const context = await browser.newContext({
      viewport: { width: 1400, height: 900 }
    });
    page = await context.newPage();
    
    // Log console messages
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.error('[Browser Console Error]:', msg.text());
      }
    });
    
    page.on('pageerror', err => {
      console.error('[Page Error]:', err.message);
    });
  }
  return page;
}

async function execute(cmd, args) {
  const p = await ensurePage();
  
  try {
    switch(cmd) {
      case 'open': {
        await p.goto(args[0], { waitUntil: 'networkidle', timeout: 30000 });
        return { url: p.url() };
      }
      
      case 'click': {
        await p.click(args[0], { timeout: 10000 });
        return { ok: true };
      }
      
      case 'fill': {
        await p.fill(args[0], args.slice(1).join(' '));
        return { ok: true };
      }
      
      case 'type': {
        await p.type(args[0], args.slice(1).join(' '));
        return { ok: true };
      }
      
      case 'press': {
        await p.press(args[0], args[1]);
        return { ok: true };
      }
      
      case 'snapshot': {
        const tree = await p.accessibility.snapshot();
        return tree;
      }
      
      case 'screenshot': {
        const path = args[0] || 'screenshot.png';
        await p.screenshot({ path });
        return { ok: true, path };
      }
      
      case 'evaluate': {
        const result = await p.evaluate(args[0]);
        return result;
      }
      
      case 'wait': {
        await p.waitForTimeout(parseInt(args[0]) || 1000);
        return { ok: true };
      }
      
      case 'waitForSelector': {
        await p.waitForSelector(args[0], { timeout: parseInt(args[1]) || 10000 });
        return { ok: true };
      }
      
      case 'title': {
        return { title: await p.title() };
      }
      
      case 'url': {
        return { url: p.url() };
      }
      
      case 'closePage': {
        if (page) {
          await page.close();
          page = null;
        }
        return { ok: true };
      }
      
      case 'quit': {
        if (browser) {
          await browser.close();
          browser = null;
          page = null;
        }
        return { ok: true };
      }
      
      default:
        return { error: `Unknown command: ${cmd}` };
    }
  } catch (err) {
    return { error: err.message };
  }
}

// Read commands from stdin, write to stdout
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

rl.on('line', async (line) => {
  try {
    const parts = line.trim().split(' ');
    const cmd = parts[0];
    const args = parts.slice(1);
    
    const result = await execute(cmd, args);
    console.log(JSON.stringify(result));
  } catch (err) {
    console.log(JSON.stringify({ error: err.message }));
  }
});

console.error('Persistent Browser Server started');
