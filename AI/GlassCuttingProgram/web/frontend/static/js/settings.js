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
    integration: {
        herofis_base_url: 'https://herofis.com',
        herofis_username: '',
        herofis_password: '',
        verify_ssl: false,
        default_target_status_id: 20,
        test_order_no: '',
        status_override: ''
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
            const parsed = JSON.parse(stored);
            currentSettings = {
                ...DEFAULT_SETTINGS,
                ...parsed,
                integration: {
                    ...DEFAULT_SETTINGS.integration,
                    ...(parsed.integration || {})
                },
                routing: {
                    ...DEFAULT_SETTINGS.routing,
                    ...(parsed.routing || {})
                },
                parallel: {
                    ...DEFAULT_SETTINGS.parallel,
                    ...(parsed.parallel || {})
                }
            };
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
            showToast('Ayarlar backend\'e kaydedildi', 'success');
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

    // Integration
    const integration = currentSettings.integration || DEFAULT_SETTINGS.integration;
    document.getElementById('herofisBaseUrl').value = integration.herofis_base_url || DEFAULT_SETTINGS.integration.herofis_base_url;
    document.getElementById('herofisUsername').value = integration.herofis_username || '';
    document.getElementById('herofisPassword').value = integration.herofis_password || '';
    document.getElementById('herofisVerifySsl').checked = Boolean(integration.verify_ssl);
    document.getElementById('integrationDefaultStatusId').value = integration.default_target_status_id ?? 20;
    document.getElementById('integrationTestOrderNo').value = integration.test_order_no || '';
    document.getElementById('integrationStatusOverride').value = integration.status_override || '';

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

    // Integration
    currentSettings.integration = {
        herofis_base_url: document.getElementById('herofisBaseUrl').value.trim(),
        herofis_username: document.getElementById('herofisUsername').value.trim(),
        herofis_password: document.getElementById('herofisPassword').value,
        verify_ssl: document.getElementById('herofisVerifySsl').checked,
        default_target_status_id: parseInt(document.getElementById('integrationDefaultStatusId').value || '20', 10),
        test_order_no: document.getElementById('integrationTestOrderNo').value.trim(),
        status_override: document.getElementById('integrationStatusOverride').value.trim()
    };

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

function toggleHerofisPasswordVisibility() {
    const input = document.getElementById('herofisPassword');
    input.type = input.type === 'password' ? 'text' : 'password';
}

function updateIntegrationStatus(status, lastOrder = '-', lastResult = '-') {
    const statusEl = document.getElementById('herofisConnectionStatus');
    const orderEl = document.getElementById('integrationLastOrder');
    const resultEl = document.getElementById('integrationLastResult');

    if (statusEl) statusEl.textContent = status;
    if (orderEl) orderEl.textContent = lastOrder;
    if (resultEl) resultEl.textContent = lastResult;
}

function getIntegrationRequestConfig() {
    gatherSettingsFromUI();

    const integration = currentSettings.integration || {};
    const orderNo = integration.test_order_no;

    if (!integration.herofis_username || !integration.herofis_password) {
        throw new Error('Herofis kullanıcı ve şifre gerekli');
    }

    if (!orderNo) {
        throw new Error('Test sipariş numarası gerekli');
    }

    const body = {
        username: integration.herofis_username,
        password: integration.herofis_password,
        orderNo,
        baseUrl: integration.herofis_base_url || 'https://herofis.com',
        verifySsl: integration.verify_ssl
    };

    return { integration, orderNo, body };
}

async function testHerofisConnection() {
    try {
        const { integration, orderNo, body } = getIntegrationRequestConfig();
        updateIntegrationStatus('Bağlanıyor...', orderNo, '-');

        const response = await fetch('/api/herofis/fetch-live-order', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Bağlantı başarısız');
        }

        const payload = result.payload || {};
        const lineCount = (payload.lines || []).length;
        const statusText = payload.order?.status || 'Baglandi';
        updateIntegrationStatus(`Bağlı (${statusText})`, orderNo, `${lineCount} satır`);
        showToast('Herofis bağlantısı başarılı', 'success');
        addLogEntry(`Herofis test başarılı: ${orderNo}, ${lineCount} satır`);

        currentSettings.integration = {
            ...integration,
            test_order_no: orderNo
        };
        updateConfigPreview();
    } catch (error) {
        updateIntegrationStatus(`Hata: ${error.message}`);
        showToast(`Herofis test hatası: ${error.message}`, 'error');
    }
}

async function testHerofisFetchOrder() {
    try {
        const { orderNo, body } = getIntegrationRequestConfig();
        updateIntegrationStatus('Sipariş çekiliyor...', orderNo, '-');

        const response = await fetch('/api/orders/import-live-herofis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ...body,
                replaceExisting: true
            })
        });
        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Sipariş çekilemedi');
        }

        const importedCount = result.imported || 0;
        const customerName = result.customerName || '-';
        updateIntegrationStatus('Sipariş aktarıldı', orderNo, `${importedCount} satır / ${customerName}`);
        showToast(`Siparişler ekranına aktarıldı: ${orderNo}`, 'success');
        addLogEntry(`Herofis sipariş aktarıldı: ${orderNo} / ${importedCount} satır`);
        setTimeout(() => {
            window.location.href = '/orders';
        }, 500);
    } catch (error) {
        updateIntegrationStatus(`Hata: ${error.message}`);
        showToast(`Sipariş çekme hatası: ${error.message}`, 'error');
    }
}

async function runHerofisLiveOptimize() {
    try {
        const { integration, orderNo, body } = getIntegrationRequestConfig();
        updateIntegrationStatus('Optimizasyon çalışıyor...', orderNo, '-');

        const statusOverride = integration.status_override;
        const requestBody = {
            ...body,
            targetStatusId: statusOverride
                ? parseInt(statusOverride, 10)
                : parseInt(integration.default_target_status_id || 20, 10)
        };

        const response = await fetch('/api/integration/herofis-live-optimize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });
        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Optimizasyon başarısız');
        }

        const efficiency = result.summary?.efficiency ?? '-';
        updateIntegrationStatus('Optimize edildi', orderNo, `%${efficiency}`);
        showToast(`Sipariş optimize edildi: ${orderNo}`, 'success');
        addLogEntry(`Herofis optimize: ${orderNo} / ${result.optimizationRunId}`);
    } catch (error) {
        updateIntegrationStatus(`Hata: ${error.message}`);
        showToast(`Optimizasyon hatası: ${error.message}`, 'error');
    }
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
    gatherSettingsFromUI();
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

    [
        'herofisBaseUrl',
        'herofisUsername',
        'herofisPassword',
        'herofisVerifySsl',
        'integrationDefaultStatusId',
        'integrationTestOrderNo',
        'integrationStatusOverride'
    ].forEach(id => {
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
    const routing = currentSettings.routing || {};
    return routing[task] || 'local';
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

// ==================== Global Functions (for onclick handlers) ====================
window.initSettings = initSettings;
window.loadSettings = loadSettings;
window.saveSettings = saveSettings;
window.resetToDefaults = resetToDefaults;
window.setMode = setMode;
window.testApiConnection = testApiConnection;
window.toggleApiKeyVisibility = toggleApiKeyVisibility;
window.toggleHerofisPasswordVisibility = toggleHerofisPasswordVisibility;
window.exportSettings = exportSettings;
window.importSettings = importSettings;
window.closeModal = closeModal;
window.doImport = doImport;
window.updateConfigPreview = updateConfigPreview;
window.checkApiStatus = checkApiStatus;
window.testHerofisConnection = testHerofisConnection;
window.testHerofisFetchOrder = testHerofisFetchOrder;
window.runHerofisLiveOptimize = runHerofisLiveOptimize;
