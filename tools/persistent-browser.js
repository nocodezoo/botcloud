#!/usr/bin/env node

const { chromium } = require('playwright');

let browser = null;
let page = null;

async function getBrowser() {
  if (!browser) {
    // Connect to existing Chrome with debugging, or launch new
    try {
      // Try connecting to existing Chrome on common ports
      browser = await chromium.connectOverCDP('http://localhost:9222');
    } catch {
      // Launch new browser if no existing
      browser = await chromium.launch({ 
        headless: false,
        args: ['--start-maximized']
      });
    }
  }
  return browser;
}

async function ensurePage() {
  const b = await getBrowser();
  if (!page) {
    const context = await b.newContext({
      viewport: { width: 1280, height: 800 }
    });
    page = await context.newPage();
  }
  return page;
}

async function handleCommand(args) {
  await ensurePage();
  const cmd = args[0];
  
  switch(cmd) {
    case 'open':
      await page.goto(args[1], { waitUntil: 'networkidle' });
      console.log(JSON.stringify({ url: page.url() }));
      break;
      
    case 'click':
      await page.click(args[1]);
      console.log(JSON.stringify({ ok: true }));
      break;
      
    case 'fill':
      await page.fill(args[1], args.slice(2).join(' '));
      console.log(JSON.stringify({ ok: true }));
      break;
      
    case 'type':
      await page.type(args[1], args.slice(2).join(' '));
      console.log(JSON.stringify({ ok: true }));
      break;
      
    case 'snapshot':
      const tree = await page.accessibility.snapshot();
      console.log(JSON.stringify(tree, null, 2));
      break;
      
    case 'screenshot':
      await page.screenshot({ path: args[1] || 'screenshot.png' });
      console.log(JSON.stringify({ ok: true, path: args[1] || 'screenshot.png' }));
      break;
      
    case 'evaluate':
      const result = await page.evaluate(args[1]);
      console.log(JSON.stringify(result));
      break;
      
    case 'wait':
      await page.waitForTimeout(parseInt(args[1]) || 1000);
      console.log(JSON.stringify({ ok: true }));
      break;
      
    case 'close':
      if (page) {
        await page.close();
        page = null;
      }
      console.log(JSON.stringify({ ok: true }));
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
}

// Run command from CLI args
handleCommand(process.argv.slice(2)).catch(err => {
  console.error(JSON.stringify({ error: err.message }));
  process.exit(1);
});
