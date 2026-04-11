/**
 * Glass Cutting Program - Settings JavaScript
 * AI Models & API Key Configuration
 */

// Default settings
const DEFAULT_SETTINGS = {
    api_key: '',
    api_endpoint: 'https://coding-intl.dashscope.aliyuncs.com/v1',
    mode: 'offline',
    models: [
        {
            model_id: 'qwen3.5-plus',
            enabled: true,
            temperature: 0.7,
            max_tokens: 2048,
            use_case: 'general'
        },
        {
            model_id: 'qwen3-max-2026-01-23',
            enabled: true,
            temperature: 0.5,
            max_tokens: 4096,
            use_case: 'complex'
        },
        {
            model_id: 'qwen3-coder-plus',
            enabled: true,
            temperature: 0.2,
            max_tokens: 8192,
            use_case: 'code'
        },
        {
            model_id: 'qwen3-coder-next',
            enabled: true,
            temperature: 0.3,
            max_tokens: 4096,
            use_case: 'advanced_coding'
        },
        {
            model_id: 'glm-4.7',
            enabled: true,
            temperature: 0.6,
            max_tokens: 2048,
            use_case: 'validation'
        },
        {
            model_id: 'kimi-k2.5',
            enabled: true,
            temperature: 0.5,
            max_tokens: 4096,
            use_case: 'documentation'
        }
    ],
    routing: {
        nesting: 'qwen3-max-2026-01-23,qwen3-coder-plus',
        gcode: 'qwen3-coder-plus,qwen3-coder-next',
        lamine: 'qwen3.5-plus',
        validation: 'glm-4.7,kimi-k2.5'
    },
    parallel: {
        max_parallel: 3,
        timeout: 90,
        retry: 2,
        fallback: true
    }
};

// Current settings
let currentSettings = {};

// ==================== Initialization ====================

function initSettings() {
    // Load from localStorage
    loadSettings();
    
    // Apply to UI
    applySettingsToUI();
    
    // Update preview
    updateConfigPreview();
    
    // Check API status
    checkApiStatus();
    
    // Setup event listeners
    setupEventListeners();
    
    addLogEntry('Settings initialized');
}

// ==================== Load/Save ====================

function loadSettings() {
    const stored = localStorage.getItem('glassCuttingSettings');
    
    if (stored) {
        try {
            currentSettings = JSON.parse(stored);
            showToast('Ayalar yüklenildi', 'success');
        } catch (e) {
            currentSettings = DEFAULT_SETTINGS;
            showToast('Ayalar parse hatası, defaults kullanılıyor', 'warning');
        }
    } else {
        currentSettings = DEFAULT_SETTINGS;
        showToast('Varsayılan ayalar yüklenildi', 'success');
    }
    
    applySettingsToUI();
    updateConfigPreview();
}

function saveSettings() {
    // Gather from UI
    gatherSettingsFromUI();
    
    // Save to localStorage
    localStorage.setItem('glassCuttingSettings', JSON.stringify(currentSettings));
    
    // Save to backend (if online)
    if (navigator.onLine) {
        saveToBackend();
    }
    
    updateConfigPreview();
    showToast('Ayalar kaydedildi!', 'success');
    addLogEntry('Settings saved');
}

async function saveToBackend() {
    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(currentSettings)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Ayalar backend'e kaydedildi', 'success');
        }
    } catch (error) {
        console.log('Backend save failed (offline):', error);
    }
}

function resetToDefaults() {
    if (!confirm('Varsayılan ayalara dönmek istediğinize emin misiniz?')) return;
    
    currentSettings = DEFAULT_SETTINGS;
    localStorage.setItem('glassCuttingSettings', JSON.stringify(currentSettings));
    
    applySettingsToUI();
    updateConfigPreview();
    
    showToast('Varsayılan ayalar uygulandı', 'warning');
    addLogEntry('Settings reset to defaults');
}

// ==================== UI Binding ====================

function applySettingsToUI() {
    // API Key
    document.getElementById('apiKey').value = currentSettings.api_key || '';
    document.getElementById('apiEndpoint').value = currentSettings.api_endpoint || DEFAULT_SETTINGS.api_endpoint;
    
    // Mode
    setModeUI(currentSettings.mode || 'offline');
    
    // Models
    currentSettings.models.forEach(model => {
        const toggle = document.querySelector(`[data-model-toggle="${model.model_id}"]`);
        if (toggle) toggle.checked = model.enabled;
        
        const item = document.querySelector(`[data-model="${model.model_id}"]`);
        if (item) {
            const tempInput = item.querySelector('[data-param="temperature"]');
            const tokensInput = item.querySelector('[data-param="max_tokens"]');
            const useCaseSelect = item.querySelector('[data-param="use_case"]');
            
            if (tempInput) tempInput.value = model.temperature;
            if (tokensInput) tokensInput.value = model.max_tokens;
            if (useCaseSelect) useCaseSelect.value = model.use_case;
        }
    });
    
    // Routing
    Object.entries(currentSettings.routing || {}).forEach(([key, value]) => {
        const select = document.querySelector(`[data-routing="${key}"]`);
        if (select) select.value = value;
    });
    
    // Parallel
    document.getElementById('maxParallel').value = currentSettings.parallel?.max_parallel || 3;
    document.getElementById('timeout').value = currentSettings.parallel?.timeout || 90;
    document.getElementById('retryCount').value = currentSettings.parallel?.retry || 2;
    document.getElementById('fallbackEnabled').checked = currentSettings.parallel?.fallback || true;
}

function gatherSettingsFromUI() {
    currentSettings.api_key = document.getElementById('apiKey').value;
    currentSettings.api_endpoint = document.getElementById('apiEndpoint').value;
    currentSettings.mode = document.querySelector('.mode-btn.active').classList.contains('online') ? 'online' : 'offline';
    
    // Models
    currentSettings.models = [];
    document.querySelectorAll('.model-config-item').forEach(item => {
        const modelId = item.dataset.model;
        const toggle = item.querySelector('[data-model-toggle]');
        const tempInput = item.querySelector('[data-param="temperature"]');
        const tokensInput = item.querySelector('[data-param="max_tokens"]');
        const useCaseSelect = item.querySelector('[data-param="use_case"]');
        
        currentSettings.models.push({
            model_id: modelId,
            enabled: toggle ? toggle.checked : true,
            temperature: tempInput ? parseFloat(tempInput.value) : 0.7,
            max_tokens: tokensInput ? parseInt(tokensInput.value) : 2048,
            use_case: useCaseSelect ? useCaseSelect.value : 'general'
        });
    });
    
    // Routing
    currentSettings.routing = {};
    document.querySelectorAll('[data-routing]').forEach(select => {
        currentSettings.routing[select.dataset.routing] = select.value;
    });
    
    // Parallel
    currentSettings.parallel = {
        max_parallel: parseInt(document.getElementById('maxParallel').value),
        timeout: parseInt(document.getElementById('timeout').value),
        retry: parseInt(document.getElementById('retryCount').value),
        fallback: document.getElementById('fallbackEnabled').checked
    };
}

// ==================== Mode Toggle ====================

function setMode(mode) {
    currentSettings.mode = mode;
    setModeUI(mode);
    
    // Update connection status
    if (mode === 'online') {
        testApiConnection();
    } else {
        updateConnectionStatus('offline', 'Offline (Local algorithms)');
    }
    
    showToast(`Mod: ${mode === 'online' ? 'Online (AI)' : 'Offline (Local)'}`, 'success');
    addLogEntry(`Mode changed to ${mode}`);
}

function setModeUI(mode) {
    const offlineBtn = document.querySelector('.mode-btn.offline');
    const onlineBtn = document.querySelector('.mode-btn.online');
    
    if (mode === 'online') {
        offlineBtn.classList.remove('active');
        onlineBtn.classList.add('active');
    } else {
        offlineBtn.classList.add('active');
        onlineBtn.classList.remove('active');
    }
}

// ==================== API Test ====================

async function testApiConnection() {
    const apiKey = document.getElementById('apiKey').value;
    const endpoint = document.getElementById('apiEndpoint').value;
    
    if (!apiKey) {
        showToast('API Key gerekli!', 'error');
        updateConnectionStatus('error', 'API Key gerekli');
        return;
    }
    
    if (!apiKey.startsWith('sk-')) {
        showToast('API Key formatı hatalı (sk- ile başlamalı)', 'error');
        updateConnectionStatus('error', 'Key format hatası');
        return;
    }
    
    showLoading();
    updateConnectionStatus('testing', 'Testing...');
    
    try {
        // Test via backend
        const response = await fetch('/api/settings/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey, api_endpoint: endpoint })
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateConnectionStatus('connected', 'Bağlantı başarılı!');
            document.getElementById('rateLimit').textContent = result.rate_limit || '60 req/min';
            document.getElementById('lastTest').textContent = new Date().toLocaleTimeString('tr-TR');
            showToast('API bağlantısı başarılı!', 'success');
            addLogEntry('API connection test: SUCCESS');
        } else {
            updateConnectionStatus('error', result.error || 'Bağlantı hatası');
            showToast('API hatası: ' + result.error, 'error');
            addLogEntry('API connection test: FAILED');
        }
        
    } catch (error) {
        updateConnectionStatus('error', 'Network hatası');
        showToast('Test hatası: ' + error.message, 'error');
    }
    
    hideLoading();
}

function checkApiStatus() {
    const apiKey = currentSettings.api_key;
    
    if (apiKey && apiKey.startsWith('sk-')) {
        updateConnectionStatus('ready', 'Ready to connect');
    } else {
        updateConnectionStatus('nokey', 'API Key gerekli');
    }
}

function updateConnectionStatus(status, message) {
    const indicator = document.getElementById('connectionStatus');
    const text = document.getElementById('connectionText');
    const apiStatus = document.getElementById('apiStatus');
    
    // Update indicator color
    indicator.className = 'status-indicator';
    switch (status) {
        case 'connected':
            indicator.classList.add('running');
            break;
        case 'testing':
            indicator.style.animation = 'pulse 1s infinite';
            indicator.style.background = '#3b82f6';
            break;
        case 'error':
            indicator.classList.add('error');
            break;
        case 'offline':
            indicator.classList.add('idle');
            break;
        default:
            indicator.classList.add('idle');
    }
    
    text.textContent = message;
    apiStatus.textContent = message;
}

// ==================== API Key Visibility ====================

function toggleApiKeyVisibility() {
    const input = document.getElementById('apiKey');
    input.type = input.type === 'password' ? 'text' : 'password';
}

// ==================== Export/Import ====================

function exportSettings() {
    gatherSettingsFromUI();
    
    const json = JSON.stringify(currentSettings, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'glass_cutting_settings.json';
    a.click();
    
    URL.revokeObjectURL(url);
    showToast('Settings exported', 'success');
}

function importSettings() {
    document.getElementById('importModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('importModal').style.display = 'none';
}

function doImport() {
    const textarea = document.getElementById('importTextarea');
    const json = textarea.value;
    
    try {
        const imported = JSON.parse(json);
        currentSettings = imported;
        
        localStorage.setItem('glassCuttingSettings', JSON.stringify(currentSettings));
        applySettingsToUI();
        updateConfigPreview();
        
        closeModal();
        showToast('Settings imported successfully', 'success');
        addLogEntry('Settings imported from JSON');
        
    } catch (error) {
        showToast('Import hatası: ' + error.message, 'error');
    }
}

// ==================== Config Preview ====================

function updateConfigPreview() {
    const preview = document.getElementById('configPreview');
    preview.textContent = JSON.stringify(currentSettings, null, 2);
}

// ==================== Event Listeners ====================

function setupEventListeners() {
    // Model toggles
    document.querySelectorAll('[data-model-toggle]').forEach(toggle => {
        toggle.addEventListener('change', () => {
            const modelId = toggle.dataset.modelToggle;
            const item = document.querySelector(`[data-model="${modelId}"]`);
            item.classList.toggle('disabled', !toggle.checked);
        });
    });
    
    // Parameter inputs
    document.querySelectorAll('[data-param]').forEach(input => {
        input.addEventListener('change', updateConfigPreview);
    });
    
    // Routing selects
    document.querySelectorAll('[data-routing]').forEach(select => {
        select.addEventListener('change', updateConfigPreview);
    });
    
    // Parallel inputs
    ['maxParallel', 'timeout', 'retryCount', 'fallbackEnabled'].forEach(id => {
        document.getElementById(id)?.addEventListener('change', updateConfigPreview);
    });
}

// ==================== Get Settings for Other Pages ====================

function getSettings() {
    return currentSettings;
}

function isOnlineMode() {
    return currentSettings.mode === 'online' && currentSettings.api_key;
}

function getEnabledModels() {
    return currentSettings.models.filter(m => m.enabled);
}

function getRoutingForTask(task) {
    return currentSettings.routing?.[task] || 'local';
}

// Export for other scripts
window.glassCuttingSettings = {
    get: getSettings,
    isOnline: isOnlineMode,
    getModels: getEnabledModels,
    getRouting: getRoutingForTask,
    save: saveSettings,
    load: loadSettings
};