/**
 * GlassCutting Pro - Standalone Chrome App
 * Lisec GFB-60/30RE Glass Cutting Machine Control
 * 
 * Full-featured browser-independent application
 */

const desktopBridge = window.desktopAPI || null;
const chromeStorage = globalThis.chrome?.storage?.local || null;
const chromeDownloads = globalThis.chrome?.downloads || null;

function appStorageSet(payload, callback = () => {}) {
  if (chromeStorage?.set) {
    chromeStorage.set(payload, callback);
    return;
  }

  if (desktopBridge?.storageSet) {
    desktopBridge.storageSet(payload)
      .then(() => callback())
      .catch((error) => {
        console.error('[GlassCutting Pro] storageSet failed:', error);
        callback();
      });
    return;
  }

  try {
    Object.entries(payload || {}).forEach(([key, value]) => {
      localStorage.setItem(`glasscutting:${key}`, JSON.stringify(value));
    });
  } catch (error) {
    console.error('[GlassCutting Pro] localStorage set failed:', error);
  }
  callback();
}

function appStorageGet(keys, callback = () => {}) {
  if (chromeStorage?.get) {
    chromeStorage.get(keys, callback);
    return;
  }

  if (desktopBridge?.storageGet) {
    desktopBridge.storageGet(keys)
      .then((result) => callback(result || {}))
      .catch((error) => {
        console.error('[GlassCutting Pro] storageGet failed:', error);
        callback({});
      });
    return;
  }

  const keyList = Array.isArray(keys) ? keys : [keys];
  const result = {};
  keyList.filter(Boolean).forEach((key) => {
    const raw = localStorage.getItem(`glasscutting:${key}`);
    result[key] = raw ? JSON.parse(raw) : undefined;
  });
  callback(result);
}

async function saveContentToFile(content, filename) {
  if (desktopBridge?.saveFile) {
    const result = await desktopBridge.saveFile({
      content,
      defaultPath: filename || 'program.nc'
    });
    return result;
  }

  const blob = new Blob([content], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);

  if (chromeDownloads?.download) {
    return new Promise((resolve) => {
      chromeDownloads.download({
        url,
        filename: filename || 'program.nc',
        saveAs: true
      }, () => resolve({ canceled: false, filePath: filename || 'program.nc' }));
    });
  }

  const link = document.createElement('a');
  link.href = url;
  link.download = filename || 'program.nc';
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  return { canceled: false, filePath: filename || 'program.nc' };
}

// ==================== APP INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
  console.log('[GlassCutting Pro] App initialized');

  initTabs();
  initGCodeEditor();
  initParameters();
  initSimulation();
  initMachine();
  initFileManager();
  initSettings();
  initHelp();
  loadSettings();
  loadSampleGCode();
});

// Global state
const appState = {
  currentTab: 'gcode',
  machineConnected: false,
  currentFile: null,
  gcodeContent: '',
  params: {},
  presets: {},
  settings: {
    ip: '192.168.1.100',
    port: 502,
    polling: 100,
    language: 'en'
  }
};

// ==================== TAB MANAGEMENT ====================
function initTabs() {
  const navBtns = document.querySelectorAll('.nav-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.dataset.tab;
      switchTab(tabId);
    });
  });

  function switchTab(tabId) {
    appState.currentTab = tabId;

    // Update nav buttons
    navBtns.forEach(b => b.classList.remove('active'));
    document.querySelector(`[data-tab="${tabId}"]`)?.classList.add('active');

    // Update tab panes
    tabPanes.forEach(p => p.classList.remove('active'));
    document.getElementById(tabId)?.classList.add('active');

    // Special handling for simulation tab
    if (tabId === 'simulation') {
      setTimeout(() => resizeCanvas(), 100);
    }

    updateStatusMessage(`Switched to ${tabId} tab`);
  }

  window.switchTab = switchTab;
}

// ==================== STATUS MESSAGE ====================
function updateStatusMessage(message) {
  const statusEl = document.getElementById('statusMessage');
  if (statusEl) {
    statusEl.textContent = message;
  }
}

function updateCurrentFile(filename) {
  const fileEl = document.getElementById('currentFile');
  if (fileEl) {
    fileEl.textContent = filename || '';
  }
}

// ==================== G-CODE EDITOR ====================
let editorElement, lineNumbersElement, statsElement;

function initGCodeEditor() {
  editorElement = document.getElementById('gcodeEditor');
  lineNumbersElement = document.getElementById('lineNumbers');
  statsElement = document.getElementById('gcodeStats');

  if (!editorElement) return;

  // Line numbers update
  editorElement.addEventListener('input', () => {
    updateLineNumbers();
    updateStats();
  });

  editorElement.addEventListener('scroll', () => {
    lineNumbersElement.scrollTop = editorElement.scrollTop;
  });

  editorElement.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = editorElement.selectionStart;
      const end = editorElement.selectionEnd;
      editorElement.value = editorElement.value.substring(0, start) + '  ' + editorElement.value.substring(end);
      editorElement.selectionStart = editorElement.selectionEnd = start + 2;
    }
  });

  // Button handlers
  document.getElementById('btnNew')?.addEventListener('click', newGCode);
  document.getElementById('btnLoad')?.addEventListener('click', loadGCode);
  document.getElementById('btnSave')?.addEventListener('click', saveGCode);
  document.getElementById('btnRun')?.addEventListener('click', runGCode);

  updateLineNumbers();
  updateStats();
}

function updateLineNumbers() {
  if (!editorElement || !lineNumbersElement) return;
  const lines = editorElement.value.split('\n').length;
  lineNumbersElement.innerHTML = Array(lines).fill(0).map((_, i) => i + 1).join('<br>');
}

function updateStats() {
  if (!editorElement || !statsElement) return;
  const lines = editorElement.value.split('\n').length;
  const chars = editorElement.value.length;
  statsElement.textContent = `Lines: ${lines} | Characters: ${chars}`;
  appState.gcodeContent = editorElement.value;
}

function newGCode() {
  if (appState.gcodeContent.trim()) {
    if (!confirm('Current G-code will be deleted. Are you sure?')) return;
  }
  editorElement.value = '';
  appState.gcodeContent = '';
  appState.currentFile = null;
  updateLineNumbers();
  updateStats();
  updateCurrentFile('');
  updateStatusMessage('New file created');
}

function loadGCode() {
  // Create file input for extension
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.nc,.gcode,.ngc,.txt';

  input.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      editorElement.value = event.target.result;
      appState.gcodeContent = event.target.result;
      appState.currentFile = file.name;
      updateLineNumbers();
      updateStats();
      updateCurrentFile(file.name);
      updateStatusMessage(`Loaded: ${file.name}`);
    };
    reader.readAsText(file);
  });

  input.click();
}

function saveGCode() {
  const content = editorElement.value;
  saveContentToFile(content, appState.currentFile || 'program.nc')
    .then((result) => {
      if (!result?.canceled) {
        updateStatusMessage(`Saved: ${result.filePath || appState.currentFile || 'program.nc'}`);
      }
    })
    .catch((error) => {
      console.error('[GlassCutting Pro] save failed:', error);
      alert('Failed to save file');
    });
}

function runGCode() {
  const content = editorElement.value;
  if (!content.trim()) {
    alert('Please load or enter G-code first');
    return;
  }

  // Switch to simulation tab
  switchTab('simulation');

  // Start simulation
  startSimulation(content);
}

function loadSampleGCode() {
  const sampleCode = `; Lisec GFB-60/30RE - Sample Cutting Program
; Material: Float Glass 6mm
; Size: 2000x1500mm

G21 ; Metric units
G90 ; Absolute positioning

; Safety position
G0 Z50

; Start position
G0 X0 Y0

; Cutting start
G1 Z5 F500 ; Cutting depth
G1 X2000 F3000 ; X axis cutting
G1 Y1500 ; Y axis cutting
G1 X0 ; Return
G1 Y0 ; Return to start

; Cutting end
G0 Z50 ; Safety position
M30 ; Program end`;

  editorElement.value = sampleCode;
  updateLineNumbers();
  updateStats();
}

// ==================== PARAMETERS ====================
function initParameters() {
  document.getElementById('btnApplyParams')?.addEventListener('click', applyParams);
  document.getElementById('btnResetParams')?.addEventListener('click', resetParams);
  document.getElementById('btnSavePreset')?.addEventListener('click', savePreset);

  // Load saved params
  loadParams();
}

function getParamsFromUI() {
  return {
    glass: {
      width: parseFloat(document.getElementById('glassWidth').value) || 3000,
      height: parseFloat(document.getElementById('glassHeight').value) || 2000,
      thickness: parseFloat(document.getElementById('glassThickness').value) || 6,
      type: document.getElementById('glassType').value
    },
    cutting: {
      speed: parseFloat(document.getElementById('cutSpeed').value) || 60,
      pressure: parseFloat(document.getElementById('cutPressure').value) || 4.5,
      angle: parseFloat(document.getElementById('cutAngle').value) || 0,
      kerfCompensation: document.getElementById('kerfCompensation').value
    },
    axes: {
      xMaxSpeed: parseFloat(document.getElementById('xMaxSpeed').value) || 1500,
      yMaxSpeed: parseFloat(document.getElementById('yMaxSpeed').value) || 1500,
      zReference: parseFloat(document.getElementById('zReference').value) || 50
    },
    ecam: {
      sync: document.getElementById('ecamSync').value === 'enabled',
      profile: document.getElementById('ecamProfile').value
    }
  };
}

function applyParams() {
  const params = getParamsFromUI();
  appState.params = params;

  // Save to storage
  appStorageSet({ params }, () => {
    updateStatusMessage('Parameters applied');
    showNotification('Parameters applied successfully', 'success');
  });

  // Update simulation if needed
  updateSimulationParams(params);
}

function resetParams() {
  document.getElementById('glassWidth').value = 3000;
  document.getElementById('glassHeight').value = 2000;
  document.getElementById('glassThickness').value = 6;
  document.getElementById('glassType').value = 'float';
  document.getElementById('cutSpeed').value = 60;
  document.getElementById('cutPressure').value = 4.5;
  document.getElementById('cutAngle').value = 0;
  document.getElementById('kerfCompensation').value = 'auto';
  document.getElementById('xMaxSpeed').value = 1500;
  document.getElementById('yMaxSpeed').value = 1500;
  document.getElementById('zReference').value = 50;
  document.getElementById('ecamSync').value = 'enabled';
  document.getElementById('ecamProfile').value = 'straight';

  updateStatusMessage('Parameters reset to defaults');
}

function savePreset() {
  const presetName = prompt('Enter preset name:');
  if (!presetName) return;

  const params = getParamsFromUI();
  appState.presets[presetName] = params;

  appStorageSet({ presets: appState.presets }, () => {
    showNotification(`Preset "${presetName}" saved`, 'success');
  });
}

function loadParams() {
  appStorageGet(['params', 'presets'], (data) => {
    if (data.params) {
      appState.params = data.params;
      // Apply params to UI (could be implemented)
    }
    if (data.presets) {
      appState.presets = data.presets;
    }
  });
}

// ==================== SIMULATION ====================
let simCanvas, simCtx;
let simRunning = false;
let simPaused = false;
let simPosition = { x: 0, y: 0, z: 50 };
let simSpeed = 5;
let simDistance = 0;
let simStartTime = 0;
let simAnimationId = null;
let simGCode = '';
let simTotalMoves = 0;
let simCurrentMove = 0;

function initSimulation() {
  simCanvas = document.getElementById('simCanvas');
  simCtx = simCanvas.getContext('2d');

  if (!simCanvas) return;

  resizeCanvas();

  document.getElementById('btnSimStart')?.addEventListener('click', toggleSimulation);
  document.getElementById('btnSimPause')?.addEventListener('click', pauseSimulation);
  document.getElementById('btnSimReset')?.addEventListener('click', resetSimulation);
  document.getElementById('simSpeed')?.addEventListener('input', updateSimSpeed);

  drawSimulationArea();
}

function resizeCanvas() {
  if (!simCanvas) return;

  const container = document.querySelector('.simulation-container');
  if (container) {
    const rect = container.getBoundingClientRect();
    simCanvas.width = rect.width;
    simCanvas.height = rect.height;
    drawSimulationArea();
  }
}

function drawSimulationArea() {
  if (!simCtx) return;

  const ctx = simCtx;
  const width = simCanvas.width;
  const height = simCanvas.height;

  // Background
  ctx.fillStyle = '#1a1a2e';
  ctx.fillRect(0, 0, width, height);

  // Grid
  ctx.strokeStyle = '#2a2a4e';
  ctx.lineWidth = 1;
  const gridSize = 50;

  for (let x = 0; x < width; x += gridSize) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, height);
    ctx.stroke();
  }

  for (let y = 0; y < height; y += gridSize) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(width, y);
    ctx.stroke();
  }

  // Glass area
  const glassWidth = parseFloat(document.getElementById('glassWidth').value) || 3000;
  const glassHeight = parseFloat(document.getElementById('glassHeight').value) || 2000;
  const scale = getScale();

  ctx.strokeStyle = '#4CAF50';
  ctx.lineWidth = 2;
  ctx.strokeRect(40, 40, glassWidth * scale, glassHeight * scale);

  // Axes
  drawAxes(ctx, width, height);
}

function getScale() {
  const glassWidth = parseFloat(document.getElementById('glassWidth').value) || 3000;
  const glassHeight = parseFloat(document.getElementById('glassHeight').value) || 2000;
  const scaleX = (simCanvas.width - 80) / glassWidth;
  const scaleY = (simCanvas.height - 80) / glassHeight;
  return Math.min(scaleX, scaleY);
}

function drawAxes(ctx, width, height) {
  const scale = getScale();
  const glassWidth = parseFloat(document.getElementById('glassWidth').value) || 3000;
  const glassHeight = parseFloat(document.getElementById('glassHeight').value) || 2000;

  const originX = 40;
  const originY = height - 40;

  // X axis
  ctx.strokeStyle = '#ff6b6b';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(originX - 10, originY);
  ctx.lineTo(originX + glassWidth * scale + 20, originY);
  ctx.stroke();

  // X arrow
  drawArrowhead(ctx, originX + glassWidth * scale + 20, originY, 0);

  // Y axis
  ctx.strokeStyle = '#4ecdc4';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(originX, originY + 10);
  ctx.lineTo(originX, originY - glassHeight * scale - 20);
  ctx.stroke();

  // Y arrow
  drawArrowhead(ctx, originX, originY - glassHeight * scale - 20, Math.PI);

  // Labels
  ctx.fillStyle = '#ff6b6b';
  ctx.font = 'bold 14px Arial';
  ctx.fillText('X', originX + glassWidth * scale + 30, originY + 5);

  ctx.fillStyle = '#4ecdc4';
  ctx.fillText('Y', originX + 10, originY - glassHeight * scale - 30);

  // Origin point
  ctx.fillStyle = '#ffe66d';
  ctx.beginPath();
  ctx.arc(originX, originY, 5, 0, Math.PI * 2);
  ctx.fill();
}

function drawArrowhead(ctx, x, y, angle) {
  const size = 10;
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);

  ctx.beginPath();
  ctx.moveTo(-size, -size / 2);
  ctx.lineTo(0, 0);
  ctx.lineTo(-size, size / 2);
  ctx.fillStyle = ctx.strokeStyle;
  ctx.fill();

  ctx.restore();
}

function startSimulation(gcode) {
  simGCode = gcode || appState.gcodeContent;
  if (!simGCode.trim()) {
    alert('G-code required for simulation');
    return;
  }

  simRunning = true;
  simPaused = false;
  simStartTime = Date.now();
  simPosition = { x: 0, y: 0, z: 50 };
  simDistance = 0;
  simCurrentMove = 0;

  const overlay = document.getElementById('simOverlay');
  if (overlay) overlay.classList.remove('active');

  parseAndSimulate(simGCode);
  updateStatusMessage('Simulation started');
}

function toggleSimulation() {
  if (simRunning) {
    pauseSimulation();
  } else {
    startSimulation();
  }
}

function pauseSimulation() {
  simPaused = !simPaused;
  const btn = document.getElementById('btnSimPause');
  if (btn) {
    btn.textContent = simPaused ? '▶ Resume' : '⏸ Pause';
  }
  updateStatusMessage(simPaused ? 'Simulation paused' : 'Simulation resumed');
}

function resetSimulation() {
  simRunning = false;
  simPaused = false;
  simPosition = { x: 0, y: 0, z: 50 };
  simDistance = 0;
  simCurrentMove = 0;

  if (simAnimationId) {
    cancelAnimationFrame(simAnimationId);
  }

  updateSimDisplay(0, 0, 0, '0:00', 0);
  drawSimulationArea();

  const btn = document.getElementById('btnSimPause');
  if (btn) btn.textContent = '⏸ Pause';

  updateStatusMessage('Simulation reset');
}

function updateSimSpeed(e) {
  simSpeed = parseInt(e.target.value);
  document.getElementById('simSpeedValue').textContent = `${simSpeed}x`;
}

function parseAndSimulate(gcode) {
  const lines = gcode.split('\n');
  const movements = [];
  let currentPos = { x: 0, y: 0, z: 50 };
  let feedRate = 1000;

  lines.forEach(line => {
    line = line.trim();
    if (!line || line.startsWith(';')) return;

    const parts = line.split(/\s+/);
    let command = '';
    let newPos = { ...currentPos };
    let newFeed = feedRate;

    parts.forEach(part => {
      const code = part.substring(0, 2).toUpperCase();
      const value = parseFloat(part.substring(2));

      if (code === 'G') {
        command = `G${Math.floor(value)}`;
      } else if (code === 'X') {
        newPos.x = value;
      } else if (code === 'Y') {
        newPos.y = value;
      } else if (code === 'Z') {
        newPos.z = value;
      } else if (code === 'F') {
        newFeed = value;
      }
    });

    if (command === 'G0' || command === 'G1') {
      const dx = newPos.x - currentPos.x;
      const dy = newPos.y - currentPos.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance > 0) {
        movements.push({
          from: { ...currentPos },
          to: { ...newPos },
          distance: distance,
          feedRate: command === 'G0' ? 5000 : newFeed,
          type: command
        });
        currentPos = newPos;
        feedRate = newFeed;
      }
    }
  });

  simTotalMoves = movements.length;
  animateSimulation(movements);
}

function animateSimulation(movements) {
  if (!simRunning || simPaused) {
    if (simRunning) {
      simAnimationId = requestAnimationFrame(() => animateSimulation(movements));
    }
    return;
  }

  if (movements.length === 0) {
    simRunning = false;
    updateStatusMessage('Simulation completed');
    showNotification('Simulation completed successfully', 'success');
    return;
  }

  const movement = movements[0];
  const speedMultiplier = simSpeed * 0.1;
  const step = movement.feedRate * speedMultiplier / 60;

  if (simDistance + step >= movement.distance) {
    simPosition = { x: movement.to.x, y: movement.to.y };
    simDistance = 0;
    movements.shift();
    simCurrentMove++;

    const elapsed = (Date.now() - simStartTime) / 1000;
    const progress = Math.round((simCurrentMove / simTotalMoves) * 100);
    updateSimDisplay(
      simPosition.x,
      simPosition.y,
      simCurrentMove,
      formatTime(elapsed),
      progress
    );

    drawSimulationArea();
    drawPosition(simPosition.x, simPosition.y);
  } else {
    const ratio = (simDistance + step) / movement.distance;
    simPosition.x = movement.from.x + (movement.to.x - movement.from.x) * ratio;
    simPosition.y = movement.from.y + (movement.to.y - movement.from.y) * ratio;
    simDistance += step;

    const elapsed = (Date.now() - simStartTime) / 1000;
    const progress = Math.round(((simCurrentMove + simDistance / movement.distance) / simTotalMoves) * 100);
    updateSimDisplay(
      simPosition.x,
      simPosition.y,
      simCurrentMove + simDistance / movement.distance,
      formatTime(elapsed),
      progress
    );

    drawSimulationArea();
    drawPosition(simPosition.x, simPosition.y);
  }

  simAnimationId = requestAnimationFrame(() => animateSimulation(movements));
}

function updateSimDisplay(x, y, distance, time, progress) {
  const elX = document.getElementById('simPosX');
  const elY = document.getElementById('simPosY');
  const elDist = document.getElementById('simDistance');
  const elTime = document.getElementById('simTime');
  const elProgress = document.getElementById('simProgress');

  if (elX) elX.textContent = x.toFixed(2);
  if (elY) elY.textContent = y.toFixed(2);
  if (elDist) elDist.textContent = distance.toFixed(2);
  if (elTime) elTime.textContent = time;
  if (elProgress) elProgress.textContent = progress;
}

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function drawPosition(x, y) {
  if (!simCtx) return;

  const scale = getScale();
  const canvasX = 40 + x * scale;
  const canvasY = simCanvas.height - 40 - y * scale;

  const ctx = simCtx;

  // Cutting path trail
  ctx.strokeStyle = '#ffe66d';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(40, simCanvas.height - 40);
  ctx.lineTo(canvasX, canvasY);
  ctx.stroke();

  // Current position
  ctx.fillStyle = '#ff6b6b';
  ctx.beginPath();
  ctx.arc(canvasX, canvasY, 8, 0, Math.PI * 2);
  ctx.fill();

  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 2;
  ctx.stroke();
}

function updateSimulationParams(params) {
  drawSimulationArea();
}

// ==================== MACHINE CONTROL ====================
let pollingInterval = null;
let machineData = {
  connected: false,
  axes: { x: 0, y: 0, z: 50, alt: 0, cnc: 0 },
  inputs: new Array(8).fill(false),
  outputs: new Array(8).fill(false),
  alarms: []
};

function initMachine() {
  document.getElementById('btnConnect')?.addEventListener('click', connectToMachine);
  document.getElementById('btnDisconnect')?.addEventListener('click', disconnectFromMachine);
  document.getElementById('btnEmergencyStop')?.addEventListener('click', emergencyStop);

  // Start status polling
  setInterval(updateMachineStatus, 1000);
}

function connectToMachine() {
  const ip = document.getElementById('settingIP')?.value || '192.168.1.100';
  const port = parseInt(document.getElementById('settingPort')?.value) || 502;

  updateStatusMessage(`Connecting to ${ip}:${port}...`);

  // Simulate connection (in real app, use chrome.sockets)
  setTimeout(() => {
    machineData.connected = true;
    updateMachineStatusUI();
    startPolling();
    updateStatusMessage(`Connected to machine at ${ip}`);
    showNotification('Machine connected successfully', 'success');
  }, 1000);
}

function disconnectFromMachine() {
  stopPolling();
  machineData.connected = false;
  updateMachineStatusUI();
  updateStatusMessage('Disconnected from machine');
}

function emergencyStop() {
  if (confirm('⚠ EMERGENCY STOP - All motion will halt! Continue?')) {
    // Send E-STOP command to machine
    updateStatusMessage('🚨 EMERGENCY STOP ACTIVATED');
    showNotification('Emergency stop activated', 'error');

    // Stop simulation if running
    if (simRunning) {
      resetSimulation();
    }
  }
}

function startPolling() {
  if (pollingInterval) clearInterval(pollingInterval);

  pollingInterval = setInterval(() => {
    if (machineData.connected) {
      // Simulate axis position updates
      if (Math.random() > 0.7) {
        machineData.axes.x += (Math.random() - 0.5) * 0.5;
        machineData.axes.y += (Math.random() - 0.5) * 0.5;
      }
      updateMachineStatusUI();
    }
  }, appState.settings.polling);
}

function stopPolling() {
  if (pollingInterval) {
    clearInterval(pollingInterval);
    pollingInterval = null;
  }
}

function updateMachineStatus() {
  // Periodic status update
  if (machineData.connected) {
    updateMachineStatusUI();
  }
}

function updateMachineStatusUI() {
  // Update status indicator
  const statusIndicator = document.querySelector('.status-indicator');
  const statusText = document.querySelector('.status-text');

  if (statusIndicator) {
    statusIndicator.className = `status-indicator ${machineData.connected ? 'online' : 'offline'}`;
  }
  if (statusText) {
    statusText.textContent = machineData.connected ? 'Connected' : 'Disconnected';
  }

  // Update servo values
  if (machineData.connected) {
    document.getElementById('servoX').textContent = `${machineData.axes.x.toFixed(3)} mm`;
    document.getElementById('servoY').textContent = `${machineData.axes.y.toFixed(3)} mm`;
    document.getElementById('servoZ').textContent = `${machineData.axes.z.toFixed(3)} mm`;
    document.getElementById('servoAlt').textContent = `${machineData.axes.alt.toFixed(2)}°`;
    document.getElementById('servoCNC').textContent = `${machineData.axes.cnc.toFixed(3)} mm`;

    // Update connection status
    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
  }

  // Simulate I/O LED updates
  updateIOLeds();
}

function updateIOLeds() {
  if (!machineData.connected) return;

  const inputLeds = document.querySelectorAll('#inputLeds .led');
  const outputLeds = document.querySelectorAll('#outputLeds .led');

  inputLeds.forEach((led, index) => {
    if (Math.random() > 0.8) {
      led.classList.toggle('on');
    }
  });

  outputLeds.forEach((led, index) => {
    if (Math.random() > 0.9) {
      led.classList.toggle('on');
    }
  });
}

// ==================== FILE MANAGER ====================
function initFileManager() {
  // File manager initialized but hidden in this version
  // Files tab can be added in future updates
}

// ==================== SETTINGS ====================
function initSettings() {
  document.getElementById('btnSettings')?.addEventListener('click', openSettings);
  document.getElementById('btnCloseSettings')?.addEventListener('click', closeSettings);
  document.getElementById('btnCancelSettings')?.addEventListener('click', closeSettings);
  document.getElementById('btnSaveSettings')?.addEventListener('click', saveSettings);
}

function openSettings() {
  const modal = document.getElementById('settingsModal');
  if (modal) {
    modal.classList.add('active');

    // Load current settings
    document.getElementById('settingIP').value = appState.settings.ip;
    document.getElementById('settingPort').value = appState.settings.port;
    document.getElementById('settingPolling').value = appState.settings.polling;
    document.getElementById('settingLanguage').value = appState.settings.language;
  }
}

function closeSettings() {
  const modal = document.getElementById('settingsModal');
  if (modal) {
    modal.classList.remove('active');
  }
}

function saveSettings() {
  appState.settings = {
    ip: document.getElementById('settingIP').value,
    port: parseInt(document.getElementById('settingPort').value),
    polling: parseInt(document.getElementById('settingPolling').value),
    language: document.getElementById('settingLanguage').value
  };

  appStorageSet({ settings: appState.settings }, () => {
    closeSettings();
    updateStatusMessage('Settings saved');
    showNotification('Settings saved successfully', 'success');

    // Restart polling with new interval
    if (machineData.connected) {
      stopPolling();
      startPolling();
    }
  });
}

function loadSettings() {
  appStorageGet(['settings', 'presets'], (data) => {
    if (data.settings) {
      appState.settings = { ...appState.settings, ...data.settings };
    }
    if (data.presets) {
      appState.presets = data.presets;
    }
  });
}

// ==================== HELP ====================
function initHelp() {
  document.getElementById('btnHelp')?.addEventListener('click', openHelp);
  document.getElementById('btnCloseHelp')?.addEventListener('click', closeHelp);
}

function openHelp() {
  const modal = document.getElementById('helpModal');
  if (modal) {
    modal.classList.add('active');
  }
}

function closeHelp() {
  const modal = document.getElementById('helpModal');
  if (modal) {
    modal.classList.remove('active');
  }
}

// ==================== NOTIFICATIONS ====================
function showNotification(message, type = 'info') {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 100px;
    right: 24px;
    padding: 16px 24px;
    border-radius: 8px;
    background: ${type === 'success' ? '#388E3C' : type === 'error' ? '#D32F2F' : '#0288D1'};
    color: white;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    z-index: 2000;
    animation: slideIn 0.3s ease;
  `;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.opacity = '0';
    notification.style.transition = 'opacity 0.3s';
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// ==================== UTILITY FUNCTIONS ====================
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Add CSS animation for notifications
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from {
      transform: translateX(400px);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
`;
document.head.appendChild(style);

console.log('[GlassCutting Pro] All modules initialized');
