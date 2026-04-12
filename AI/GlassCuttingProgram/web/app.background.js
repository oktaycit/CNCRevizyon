/**
 * GlassCutting Pro - Chrome Extension Background Script
 * Service Worker for machine communication and app management
 */

// Machine connection state
let machineConnection = {
  connected: false,
  ip: '192.168.1.100',
  port: 502,
  lastUpdate: null
};

// Machine status
let machineStatus = {
  axes: { x: 0, y: 0, z: 50, alt: 0, cnc: 0 },
  inputs: new Array(8).fill(false),
  outputs: new Array(8).fill(false),
  alarms: [],
  programRunning: false
};

console.log('[GlassCutting Pro] Background script initialized');

// Message listener
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  handleMessage(request, sender, sendResponse);
  return true;
});

async function handleMessage(request, sender, sendResponse) {
  console.log('[Background] Message:', request.action);

  switch (request.action) {
    case 'connect':
      await connectToMachine(request.ip, request.port);
      sendResponse({ success: machineConnection.connected });
      break;

    case 'disconnect':
      disconnectFromMachine();
      sendResponse({ success: true });
      break;

    case 'getStatus':
      sendResponse({ status: machineStatus, connection: machineConnection });
      break;

    case 'updateParams':
      sendResponse({ success: true });
      break;

    case 'openApp':
      openAppWindow();
      sendResponse({ success: true });
      break;

    default:
      sendResponse({ error: 'Unknown action' });
  }
}

// Connect to machine
async function connectToMachine(ip, port) {
  machineConnection.ip = ip || machineConnection.ip;
  machineConnection.port = port || machineConnection.port;

  try {
    console.log(`Connecting to ${machineConnection.ip}:${machineConnection.port}`);
    await sleep(500);
    machineConnection.connected = true;
    machineConnection.lastUpdate = Date.now();
    console.log('[Background] Connected');
  } catch (error) {
    console.error('[Background] Connection failed:', error);
    machineConnection.connected = false;
  }
}

function disconnectFromMachine() {
  machineConnection.connected = false;
  console.log('[Background] Disconnected');
}

// Open app in new tab
function openAppWindow() {
  chrome.tabs.create({
    url: chrome.runtime.getURL('app.html'),
    active: true
  });
}

// Install handler
chrome.runtime.onInstalled.addListener((details) => {
  console.log('[Background] Installed:', details.reason);

  // Set default settings
  chrome.storage.local.set({
    settings: {
      ip: '192.168.1.100',
      port: 502,
      polling: 100,
      language: 'en'
    },
    presets: {},
    params: {}
  });
});

// Utility
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
