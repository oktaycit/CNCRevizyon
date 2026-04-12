// GlassCutting - Background Service Worker
// Makine iletişimi ve API yönetimi

// Makine bağlantı durumu
let machineConnection = {
  connected: false,
  ip: '192.168.1.100',
  port: 502,
  lastUpdate: null
};

// Makine durumu
let machineStatus = {
  axes: {
    x: 0,
    y: 0,
    z: 50,
    alt: 0,
    cnc: 0
  },
  inputs: new Array(8).fill(false),
  outputs: new Array(8).fill(false),
  alarms: [],
  programRunning: false,
  feedOverride: 100,
  speedOverride: 100
};

// Parametreler
let currentParams = null;

// ==================== MESSAGE LISTENER ====================
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  handleMessage(request, sender, sendResponse);
  return true; // Async response
});

async function handleMessage(request, sender, sendResponse) {
  console.log('[Background] Message received:', request);

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
      currentParams = request.params;
      await sendParamsToMachine(request.params);
      sendResponse({ success: true });
      break;

    case 'sendGCode':
      await sendGCodeToMachine(request.gcode);
      sendResponse({ success: true });
      break;

    case 'startProgram':
      await startMachineProgram();
      sendResponse({ success: true });
      break;

    case 'stopProgram':
      await stopMachineProgram();
      sendResponse({ success: true });
      break;

    case 'getPresets':
      getPresets(sendResponse);
      break;

    case 'savePreset':
      await savePreset(request.name, request.params);
      sendResponse({ success: true });
      break;

    default:
      sendResponse({ error: 'Unknown action' });
  }
}

// ==================== MAKİNE BAĞLANTISI ====================
async function connectToMachine(ip, port) {
  machineConnection.ip = ip || machineConnection.ip;
  machineConnection.port = port || machineConnection.port;

  try {
    // Modbus TCP veya EtherCAT bağlantısı burada kurulacak
    // Şimdilik simüle edilmiş bağlantı
    console.log(`Connecting to machine at ${machineConnection.ip}:${machineConnection.port}`);

    // Simüle edilmiş bağlantı gecikmesi
    await sleep(500);

    machineConnection.connected = true;
    machineConnection.lastUpdate = Date.now();

    // Bağlantı kurulduğunu popup'a bildir
    notifyPopup('machineStatus', {
      connected: true,
      axes: machineStatus.axes
    });

    // Durum güncellemelerini başlat
    startStatusPolling();

    console.log('[Background] Machine connected');
  } catch (error) {
    console.error('[Background] Connection failed:', error);
    machineConnection.connected = false;
  }
}

function disconnectFromMachine() {
  stopStatusPolling();
  machineConnection.connected = false;

  notifyPopup('machineStatus', {
    connected: false,
    axes: machineStatus.axes
  });

  console.log('[Background] Machine disconnected');
}

// ==================== STATUS POLLING ====================
let pollingInterval = null;

function startStatusPolling() {
  if (pollingInterval) {
    clearInterval(pollingInterval);
  }

  pollingInterval = setInterval(async () => {
    if (machineConnection.connected) {
      await updateMachineStatus();
    }
  }, 100); // 100ms polling
}

function stopStatusPolling() {
  if (pollingInterval) {
    clearInterval(pollingInterval);
    pollingInterval = null;
  }
}

async function updateMachineStatus() {
  // Gerçek makineden durum okuma (simülasyon)
  // Modbus TCP, EtherCAT veya Delta NC300 API kullanılacak

  // Simüle edilmiş eksen pozisyonları
  if (machineStatus.programRunning) {
    machineStatus.axes.x += Math.random() * 10;
    machineStatus.axes.y += Math.random() * 10;
  }

  // Popup'a durum güncellemesi gönder
  notifyPopup('machineStatus', {
    connected: machineConnection.connected,
    axes: machineStatus.axes,
    inputs: machineStatus.inputs,
    outputs: machineStatus.outputs,
    alarms: machineStatus.alarms,
    programRunning: machineStatus.programRunning
  });

  machineConnection.lastUpdate = Date.now();
}

// ==================== PARAMETRE GÖNDERME ====================
async function sendParamsToMachine(params) {
  currentParams = params;

  // Parametreleri makineye gönder
  // Delta NC300 protokolüne göre kodlama
  console.log('[Background] Sending params to machine:', params);

  // Simülasyon
  await sleep(100);

  // Popup'a onay gönder
  notifyPopup('paramsUpdated', params);
}

// ==================== G-KOD GÖNDERME ====================
async function sendGCodeToMachine(gcode) {
  console.log('[Background] Sending G-code to machine');

  // G-kod'u makineye gönder
  // NC300 formatına dönüştürme

  await sleep(200);
}

async function startMachineProgram() {
  console.log('[Background] Starting machine program');
  machineStatus.programRunning = true;
  startStatusPolling();
}

async function stopMachineProgram() {
  console.log('[Background] Stopping machine program');
  machineStatus.programRunning = false;
}

// ==================== PRESET YÖNETİMİ ====================
function getPresets(callback) {
  chrome.storage.local.get('presets', (data) => {
    callback({ presets: data.presets || {} });
  });
}

async function savePreset(name, params) {
  return new Promise((resolve) => {
    chrome.storage.local.get('presets', (data) => {
      const presets = data.presets || {};
      presets[name] = params;
      chrome.storage.local.set({ presets }, resolve);
    });
  });
}

// ==================== POPUP BİLDİRİMLERİ ====================
function notifyPopup(action, data) {
  chrome.runtime.sendMessage({ action, data }, () => {
    // Popup kapalı olabilir, hata kontrolü
    if (chrome.runtime.lastError) {
      console.log('[Background] Popup not available');
    }
  });
}

// ==================== YARDIMCI FONKSİYONLAR ====================
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ==================== INSTALL/UNINSTALL ====================
chrome.runtime.onInstalled.addListener((details) => {
  console.log('[Background] Extension installed:', details.reason);

  // Varsayılan ayarları yükle
  chrome.storage.local.set({
    settings: {
      machineIP: '192.168.1.100',
      machinePort: 502,
      pollingInterval: 100,
      language: 'tr'
    },
    presets: {}
  });
});

chrome.runtime.onStartup.addListener(() => {
  console.log('[Background] Extension started');
});

// ==================== ALARM YÖNETİMİ ====================
function checkAlarms() {
  // Makine alarmlarını kontrol et
  const alarms = [];

  // Simüle edilmiş alarm kontrolü
  if (machineStatus.axes.x > 6000 || machineStatus.axes.y > 3000) {
    alarms.push({
      code: 'E001',
      message: 'Eksen limit ihlali',
      severity: 'error'
    });
  }

  machineStatus.alarms = alarms;

  if (alarms.length > 0) {
    notifyPopup('alarms', alarms);
  }
}

// Periyodik alarm kontrolü
setInterval(checkAlarms, 1000);

// ==================== KONSOL LOG ====================
console.log('[Background] GlassCutting Service Worker initialized');
