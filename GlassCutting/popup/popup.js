// GlassCutting - Popup JavaScript
// Lisec GFB-60/30RE Cam Kesme Makinesi Chrome Eklentisi

document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initGCodeEditor();
  initParameters();
  initSimulation();
  initMachine();
  loadSettings();
});

// ==================== TAB YÖNETİMİ ====================
function initTabs() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.dataset.tab;

      // Tüm tab'ları gizle
      tabButtons.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      // Seçili tab'ı göster
      btn.classList.add('active');
      document.getElementById(tabId).classList.add('active');

      // Simülasyon tab'ı seçildiğinde canvas'ı yeniden boyutlandır
      if (tabId === 'simulation') {
        setTimeout(() => resizeCanvas(), 100);
      }
    });
  });
}

// ==================== G-KOD EDİTÖRÜ ====================
let gcodeContent = '';

function initGCodeEditor() {
  const editor = document.getElementById('gcodeEditor');
  const lineNumbers = document.getElementById('lineNumbers');
  const stats = document.getElementById('gcodeStats');

  // Satır numaralarını güncelle
  function updateLineNumbers() {
    const lines = editor.value.split('\n').length;
    lineNumbers.innerHTML = Array(lines).fill(0).map((_, i) => i + 1).join('<br>');
  }

  // İstatistikleri güncelle
  function updateStats() {
    const lines = editor.value.split('\n').length;
    const chars = editor.value.length;
    stats.textContent = `Satır: ${lines} | Karakter: ${chars}`;
    gcodeContent = editor.value;
  }

  editor.addEventListener('input', () => {
    updateLineNumbers();
    updateStats();
  });

  editor.addEventListener('scroll', () => {
    lineNumbers.scrollTop = editor.scrollTop;
  });

  // Buton eventleri
  document.getElementById('btnNew').addEventListener('click', newGCode);
  document.getElementById('btnLoad').addEventListener('click', loadGCode);
  document.getElementById('btnSave').addEventListener('click', saveGCode);
  document.getElementById('btnRun').addEventListener('click', runGCode);

  // Örnek G-kod yükle
  loadSampleGCode();
}

function newGCode() {
  if (confirm('Mevcut G-kodu silinecek. Emin misiniz?')) {
    document.getElementById('gcodeEditor').value = '';
    updateStats();
  }
}

function loadGCode() {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.nc,.txt,.gcode,.ngc';

  input.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        document.getElementById('gcodeEditor').value = event.target.result;
        updateStats();
      };
      reader.readAsText(file);
    }
  });

  input.click();
}

function saveGCode() {
  const content = document.getElementById('gcodeEditor').value;
  const blob = new Blob([content], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);

  chrome.downloads.download({
    url: url,
    filename: 'program.nc',
    saveAs: true
  });
}

function runGCode() {
  const content = document.getElementById('gcodeEditor').value;
  if (!content.trim()) {
    alert('Lütfen önce bir G-kod yükleyin veya yazın.');
    return;
  }

  // Simülasyon tab'ına geç
  document.querySelector('[data-tab="simulation"]').click();

  // Simülasyonu başlat
  startSimulation(content);
}

function loadSampleGCode() {
  const sampleCode = `; Lisec GFB-60/30RE - Örnek Kesim Programı
; Malzeme: Float Cam 6mm
; Boyut: 2000x1500mm

G21 ; Metrik birimler
G90 ; Mutlak konumlandırma

; Güvenlik pozisyonu
G0 Z50

; Başlangıç pozisyonu
G0 X0 Y0

; Kesim başlangıcı
G1 Z5 F500 ; Kesim derinliği
G1 X2000 F3000 ; X ekseni kesim
G1 Y1500 ; Y ekseni kesim
G1 X0 ; Geri dönüş
G1 Y0 ; Başlangıca dönüş

; Kesim sonu
G0 Z50 ; Güvenlik pozisyonu
M30 ; Program sonu`;

  document.getElementById('gcodeEditor').value = sampleCode;
  updateStats();
}

function updateStats() {
  const editor = document.getElementById('gcodeEditor');
  const stats = document.getElementById('gcodeStats');
  const lines = editor.value.split('\n').length;
  const chars = editor.value.length;
  stats.textContent = `Satır: ${lines} | Karakter: ${chars}`;
  gcodeContent = editor.value;
}

// ==================== PARAMETRELER ====================
let defaultParams = {};

function initParameters() {
  // Varsayılan değerleri kaydet
  const inputs = document.querySelectorAll('#params input, #params select');
  inputs.forEach(input => {
    defaultParams[input.id] = input.value;
  });

  document.getElementById('btnApplyParams').addEventListener('click', applyParams);
  document.getElementById('btnResetParams').addEventListener('click', resetParams);
  document.getElementById('btnSavePreset').addEventListener('click', savePreset);
}

function applyParams() {
  const params = {
    glass: {
      width: parseFloat(document.getElementById('glassWidth').value),
      height: parseFloat(document.getElementById('glassHeight').value),
      thickness: parseFloat(document.getElementById('glassThickness').value),
      type: document.getElementById('glassType').value
    },
    cutting: {
      speed: parseFloat(document.getElementById('cutSpeed').value),
      pressure: parseFloat(document.getElementById('cutPressure').value),
      angle: parseFloat(document.getElementById('cutAngle').value),
      kerfCompensation: document.getElementById('kerfCompensation').value
    },
    axes: {
      xMaxSpeed: parseFloat(document.getElementById('xMaxSpeed').value),
      yMaxSpeed: parseFloat(document.getElementById('yMaxSpeed').value),
      zReference: parseFloat(document.getElementById('zReference').value)
    },
    ecam: {
      sync: document.getElementById('ecamSync').value === 'enabled',
      profile: document.getElementById('ecamProfile').value
    }
  };

  // Background'a parametreleri gönder
  chrome.runtime.sendMessage({
    action: 'updateParams',
    params: params
  }, (response) => {
    if (response && response.success) {
      showNotification('Parametreler uygulandı', 'success');
    }
  });

  // Simülasyon parametrelerini güncelle
  updateSimulationParams(params);
}

function resetParams() {
  Object.keys(defaultParams).forEach(id => {
    const input = document.getElementById(id);
    if (input) {
      input.value = defaultParams[id];
    }
  });
}

function savePreset() {
  const presetName = prompt('Preset adı girin:');
  if (presetName) {
    const params = {};
    const inputs = document.querySelectorAll('#params input, #params select');
    inputs.forEach(input => {
      params[input.id] = input.value;
    });

    chrome.storage.local.get('presets', (data) => {
      const presets = data.presets || {};
      presets[presetName] = params;
      chrome.storage.local.set({ presets }, () => {
        showNotification(`Preset "${presetName}" kaydedildi`, 'success');
      });
    });
  }
}

function showNotification(message, type = 'info') {
  // Basit bildirim (console'da göster)
  console.log(`[${type.toUpperCase()}] ${message}`);
}

// ==================== SİMÜLASYON ====================
let simCanvas, simCtx;
let simRunning = false;
let simPaused = false;
let simPosition = { x: 0, y: 0 };
let simSpeed = 5;
let simDistance = 0;
let simStartTime = 0;
let simAnimationId = null;
let simGCode = '';

function initSimulation() {
  simCanvas = document.getElementById('simCanvas');
  simCtx = simCanvas.getContext('2d');

  // Canvas boyutlandırma
  resizeCanvas();

  // Event listeners
  document.getElementById('btnSimStart').addEventListener('click', toggleSimulation);
  document.getElementById('btnSimPause').addEventListener('click', pauseSimulation);
  document.getElementById('btnSimReset').addEventListener('click', resetSimulation);
  document.getElementById('simSpeed').addEventListener('input', updateSimSpeed);

  // İlk çizim
  drawSimulationArea();
}

function resizeCanvas() {
  const container = document.querySelector('.simulation-container');
  if (container) {
    const rect = container.getBoundingClientRect();
    simCanvas.width = Math.min(500, rect.width - 200);
    simCanvas.height = 400;
    drawSimulationArea();
  }
}

function drawSimulationArea() {
  const ctx = simCtx;
  const width = simCanvas.width;
  const height = simCanvas.height;

  // Arka plan
  ctx.fillStyle = '#1a1a2e';
  ctx.fillRect(0, 0, width, height);

  // Grid çizgileri
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

  // Cam alanı
  const glassWidth = parseFloat(document.getElementById('glassWidth').value) || 3000;
  const glassHeight = parseFloat(document.getElementById('glassHeight').value) || 2000;
  const scaleX = (width - 40) / glassWidth;
  const scaleY = (height - 40) / glassHeight;
  const scale = Math.min(scaleX, scaleY);

  ctx.strokeStyle = '#4CAF50';
  ctx.lineWidth = 2;
  ctx.strokeRect(20, 20, glassWidth * scale, glassHeight * scale);

  // Eksen okları
  ctx.strokeStyle = '#ff6b6b';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(20, height - 20);
  ctx.lineTo(width - 20, height - 20); // X ekseni
  ctx.stroke();

  ctx.strokeStyle = '#4ecdc4';
  ctx.beginPath();
  ctx.moveTo(20, height - 20);
  ctx.lineTo(20, 20); // Y ekseni
  ctx.stroke();

  // X etiketi
  ctx.fillStyle = '#ff6b6b';
  ctx.font = '12px Arial';
  ctx.fillText('X', width - 30, height - 25);

  // Y etiketi
  ctx.fillStyle = '#4ecdc4';
  ctx.fillText('Y', 25, 30);

  // Kesim başlangıç noktası
  ctx.fillStyle = '#ffe66d';
  ctx.beginPath();
  ctx.arc(20, height - 20, 5, 0, Math.PI * 2);
  ctx.fill();
}

function startSimulation(gcode) {
  simGCode = gcode || gcodeContent;
  if (!simGCode.trim()) {
    alert('Simülasyon için G-kod gerekli');
    return;
  }

  simRunning = true;
  simPaused = false;
  simStartTime = Date.now();
  simPosition = { x: 0, y: 0 };
  simDistance = 0;

  parseAndSimulate(simGCode);
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
  document.getElementById('btnSimPause').textContent = simPaused ? '▶ Devam' : '⏸ Duraklat';
}

function resetSimulation() {
  simRunning = false;
  simPaused = false;
  simPosition = { x: 0, y: 0 };
  simDistance = 0;

  if (simAnimationId) {
    cancelAnimationFrame(simAnimationId);
  }

  updateSimDisplay(0, 0, 0, '0:00');
  drawSimulationArea();
  drawPosition(0, 0);
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
  let spindleSpeed = 0;  // Mil devri (RPM)
  let spindleOn = false; // Mil durumu
  let vacuumOn = false;  // Vakum durumu

  lines.forEach(line => {
    line = line.trim();
    if (!line || line.startsWith(';')) return;

    // G-kod parse
    const parts = line.split(/\s+/);
    let command = '';
    let newPos = { ...currentPos };
    let newFeed = feedRate;
    let hasMovement = false;

    parts.forEach(part => {
      const code = part.substring(0, 2).toUpperCase();
      const value = parseFloat(part.substring(2));

      if (code === 'G') {
        command = `G${Math.floor(value)}`;
        hasMovement = true;
      } else if (code === 'X') {
        newPos.x = value;
        hasMovement = true;
      } else if (code === 'Y') {
        newPos.y = value;
        hasMovement = true;
      } else if (code === 'Z') {
        newPos.z = value;
        hasMovement = true;
      } else if (code === 'F') {
        newFeed = value;
      } else if (code === 'S') {
        // Mil devri (Spindle speed)
        spindleSpeed = value;
        console.log(`[Sim] Spindle speed: ${spindleSpeed} RPM`);
      } else if (code === 'M') {
        // M kodları - yardımcı fonksiyonlar
        if (value === 3) {
          // M03: Mil saat yönünde başlat (Spindle CW)
          spindleOn = true;
          console.log(`[Sim] Spindle ON (CW) - ${spindleSpeed} RPM`);
        } else if (value === 5) {
          // M05: Mil durdur
          spindleOn = false;
          console.log('[Sim] Spindle OFF');
        } else if (value === 10) {
          // M10: Lama sıyırma/wiper AÇIK (eski sistem)
          console.log('[Sim] Blade wipe ON (M10)');
        } else if (value === 11) {
          // M11: Lama sıyırma/wiper KAPALI (eski sistem)
          console.log('[Sim] Blade wipe OFF (M11)');
        } else if (value === 12) {
          // M12: Vakum emiş AÇIK (taşlama tozu için)
          vacuumOn = true;
          console.log('[Sim] Vacuum ON (M12)');
        } else if (value === 13) {
          // M13: Vakum emiş KAPALI
          vacuumOn = false;
          console.log('[Sim] Vacuum OFF (M13)');
        } else if (value === 30) {
          // M30: Program sonu
          console.log('[Sim] Program end (M30)');
        }
      }
    });

    // Sadece hareket komutlarını ekle (G0, G1, X, Y, Z)
    if (hasMovement && (command === 'G0' || command === 'G1')) {
      const dx = newPos.x - currentPos.x;
      const dy = newPos.y - currentPos.y;
      const dz = newPos.z - currentPos.z;
      const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);

      if (distance > 0) {
        movements.push({
          from: { ...currentPos },
          to: { ...newPos },
          distance: distance,
          feedRate: command === 'G0' ? 5000 : newFeed,
          type: command,
          spindleOn: spindleOn,
          spindleSpeed: spindleSpeed,
          vacuumOn: vacuumOn
        });
        currentPos = newPos;
        feedRate = newFeed;
      }
    }
  });

  // Animasyonu başlat
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
    return;
  }

  const movement = movements[0];
  const speedMultiplier = simSpeed * 0.1;
  const step = movement.feedRate * speedMultiplier / 60; // mm per frame

  if (simDistance + step >= movement.distance) {
    // Hareket tamamlandı
    simPosition = { x: movement.to.x, y: movement.to.y };
    simDistance = 0;
    movements.shift();

    // Pozisyonu güncelle
    const elapsed = (Date.now() - simStartTime) / 1000;
    const totalDistance = getTotalDistance(movements, movement.to);
    updateSimDisplay(
      simPosition.x,
      simPosition.y,
      totalDistance,
      formatTime(elapsed)
    );

    drawSimulationArea();
    drawPosition(simPosition.x, simPosition.y);
  } else {
    // Hareket devam ediyor
    const ratio = (simDistance + step) / movement.distance;
    simPosition.x = movement.from.x + (movement.to.x - movement.from.x) * ratio;
    simPosition.y = movement.from.y + (movement.to.y - movement.from.y) * ratio;
    simDistance += step;

    const elapsed = (Date.now() - simStartTime) / 1000;
    const totalDistance = getTotalDistance(movements, simPosition);
    updateSimDisplay(
      simPosition.x,
      simPosition.y,
      totalDistance,
      formatTime(elapsed)
    );

    drawSimulationArea();
    drawPosition(simPosition.x, simPosition.y);
  }

  simAnimationId = requestAnimationFrame(() => animateSimulation(movements));
}

function getTotalDistance(remainingMovements, currentPos) {
  let total = 0;
  let pos = currentPos;

  remainingMovements.forEach(m => {
    const dx = m.to.x - pos.x;
    const dy = m.to.y - pos.y;
    total += Math.sqrt(dx * dx + dy * dy);
    pos = m.to;
  });

  return total;
}

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function updateSimDisplay(x, y, distance, time) {
  document.getElementById('simPosX').textContent = `${x.toFixed(2)}`;
  document.getElementById('simPosY').textContent = `${y.toFixed(2)}`;
  document.getElementById('simDistance').textContent = `${distance.toFixed(2)}`;
  document.getElementById('simTime').textContent = time;
}

function drawPosition(x, y) {
  const glassWidth = parseFloat(document.getElementById('glassWidth').value) || 3000;
  const glassHeight = parseFloat(document.getElementById('glassHeight').value) || 2000;
  const scaleX = (simCanvas.width - 40) / glassWidth;
  const scaleY = (simCanvas.height - 40) / glassHeight;
  const scale = Math.min(scaleX, scaleY);

  const canvasX = 20 + x * scale;
  const canvasY = simCanvas.height - 20 - y * scale;

  const ctx = simCtx;

  // Kesim izi
  ctx.strokeStyle = '#ffe66d';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(20, simCanvas.height - 20);
  ctx.lineTo(canvasX, canvasY);
  ctx.stroke();

  // Mevcut pozisyon
  ctx.fillStyle = '#ff6b6b';
  ctx.beginPath();
  ctx.arc(canvasX, canvasY, 6, 0, Math.PI * 2);
  ctx.fill();

  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 2;
  ctx.stroke();
}

function updateSimulationParams(params) {
  // Parametre değiştiğinde simülasyonu güncelle
  drawSimulationArea();
}

// ==================== MAKİNE DURUMU ====================
function initMachine() {
  // Makine durumu güncelleme interval'i
  setInterval(updateMachineStatus, 1000);
}

function updateMachineStatus() {
  // Gerçek makine bağlantısı için burada API çağrıları yapılacak
  // Şimdilik simüle edilmiş veri gösteriyoruz

  // Servo pozisyonlarını güncelle
  const baseX = parseFloat(document.getElementById('servoX').textContent) || 0;
  const baseY = parseFloat(document.getElementById('servoY').textContent) || 0;

  // Rastgele küçük değişiklikler (simülasyon)
  if (Math.random() > 0.7) {
    const newX = baseX + (Math.random() - 0.5) * 0.1;
    const newY = baseY + (Math.random() - 0.5) * 0.1;

    document.getElementById('servoX').textContent = `${newX.toFixed(2)} mm`;
    document.getElementById('servoY').textContent = `${newY.toFixed(2)} mm`;
  }

  // I/O LED'lerini güncelle (simülasyon)
  updateIOLeds();
}

function updateIOLeds() {
  const inputLeds = document.querySelectorAll('#inputLeds .led');
  const outputLeds = document.querySelectorAll('#outputLeds .led');

  // Rastgele LED yak/söndür
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

// ==================== AYARLAR ====================
function loadSettings() {
  chrome.storage.local.get(['settings', 'lastParams'], (data) => {
    if (data.settings) {
      applySettings(data.settings);
    }

    if (data.lastParams) {
      applyParams(data.lastParams);
    }
  });
}

function applySettings(settings) {
  // Makine bağlantı ayarları
  if (settings.machineIP) {
    console.log('Machine IP:', settings.machineIP);
  }
}

// Background'dan mesaj dinle
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'machineStatus') {
    updateMachineStatusFromData(request.status);
    sendResponse({ success: true });
  }
});

function updateMachineStatusFromData(status) {
  // Makine durumunu güncelle
  if (status.connected) {
    document.querySelector('.status-indicator').classList.remove('offline');
    document.querySelector('.status-indicator').classList.add('online');
    document.querySelector('.status-text').textContent = 'Bağlı';
  }

  if (status.axes) {
    if (status.axes.x !== undefined) {
      document.getElementById('servoX').textContent = `${status.axes.x.toFixed(2)} mm`;
    }
    if (status.axes.y !== undefined) {
      document.getElementById('servoY').textContent = `${status.axes.y.toFixed(2)} mm`;
    }
    if (status.axes.z !== undefined) {
      document.getElementById('servoZ').textContent = `${status.axes.z.toFixed(2)} mm`;
    }
  }

  if (status.alarms && status.alarms.length > 0) {
    updateAlarms(status.alarms);
  }
}

function updateAlarms(alarms) {
  const alarmList = document.getElementById('alarmList');
  alarmList.innerHTML = '';

  alarms.forEach(alarm => {
    const div = document.createElement('div');
    div.className = `alarm-item ${alarm.severity}`;
    div.textContent = `[${alarm.code}] ${alarm.message}`;
    alarmList.appendChild(div);
  });
}
