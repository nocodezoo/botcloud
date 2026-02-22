#!/usr/bin/env node

/**
 * Client to talk to persistent browser server
 */

const net = require('net');

const client = new net.Socket();
let buffer = '';
let resolveFn = null;

client.connect(9999, '127.0.0.1', () => {
  console.error('Connected to browser server');
});

client.on('data', (data) => {
  buffer += data.toString();
  try {
    const result = JSON.parse(buffer);
    buffer = '';
    if (resolveFn) {
      resolveFn(result);
      resolveFn = null;
    }
  } catch {
    // Partial JSON, wait for more
  }
});

client.on('error', (err) => {
  console.error('Connection error:', err.message);
  if (resolveFn) {
    resolveFn({ error: err.message });
    resolveFn = null;
  }
});

function send(cmd) {
  return new Promise((resolve) => {
    resolveFn = resolve;
    client.write(cmd + '\n');
    
    // Timeout after 30 seconds
    setTimeout(() => {
      if (resolveFn) {
        resolveFn({ error: 'Timeout' });
        resolveFn = null;
      }
    }, 30000);
  });
}

// Run command from CLI
const cmd = process.argv.slice(2).join(' ');
send(cmd).then(result => {
  console.log(JSON.stringify(result, null, 2));
  client.destroy();
  process.exit(0);
});
