/**
 * Glass Cutting Program - Main JavaScript
 * LiSEC GFB-60/30RE Web Interface
 * 
 * Offline Support: Works without internet
 * - Local algorithms (Guillotine, TSP) work offline
 * - AI API calls gracefully fail with fallback
 */

// API Base URL
const API_BASE = '/api';
window.API_BASE = API_BASE;  // Make global for other scripts

// Current state
let currentOrders = [];
let currentResult = null;
let currentGcode = '';

// Offline mode flag
let isOffline = !navigator.onLine;

// ==================== Offline Detection ====================

window.addEventListener('online', () => {
    isOffline = false;
    hideOfflineBanner();
    showToast('Internet bağlantısı geldi', 'success');
    addLogEntry('Online mode');
});

window.addEventListener('offline', () => {
    isOffline = true;
    showOfflineBanner();
    showToast('Offline mode - Local algoritmalar çalışır', 'warning');
    addLogEntry('Offline mode activated');
});

function showOfflineBanner() {
    const banner = document.getElementById('offlineBanner');
    if (banner) {
        banner.style.display = 'block';
    }

    // Update AI model status
    const modelStatuses = document.querySelectorAll('.model-status');
    modelStatuses.forEach(status => {
        status.textContent = 'Offline';
        status.classList.remove('active');
        status.classList.add('inactive');
    });
}

function hideOfflineBanner() {
    const banner = document.getElementById('offlineBanner');
    if (banner) {
        banner.style.display = 'none';
    }

    // Restore AI model status
    const modelStatuses = document.querySelectorAll('.model-status');
    modelStatuses.forEach(status => {
        status.textContent = 'Aktif';
        status.classList.remove('inactive');
        status.classList.add('active');
    });
}

// Check initial online status
if (!navigator.onLine) {
    isOffline = true;
    document.addEventListener('DOMContentLoaded', showOfflineBanner);
}

// ==================== Utility Functions ====================

function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => toast.remove(), 3000);
}

function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

function updateTime() {
    const el = document.getElementById('currentTime');
    if (el) {
        el.textContent = new Date().toLocaleTimeString('tr-TR');
    }
}

function addLogEntry(message) {
    const log = document.getElementById('activityLog');
    if (!log) return;

    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerHTML = `
        <span class="log-time">${new Date().toLocaleTimeString('tr-TR')}</span>
        <span class="log-msg">${message}</span>
    `;
    log.insertBefore(entry, log.firstChild);

    // Keep only last 20 entries
    while (log.children.length > 20) {
        log.removeChild(log.lastChild);
    }
}

// ==================== Stats Functions ====================

async function updateStats() {
    try {
        // Get orders
        const ordersRes = await fetch(`${API_BASE}/orders`);
        const ordersData = await ordersRes.json();
        currentOrders = ordersData.orders || [];

        // Update counts
        const orderCount = currentOrders.length;
        const partsCount = currentOrders.reduce((sum, o) => sum + o.quantity, 0);

        const orderCountEl = document.getElementById('orderCount');
        if (orderCountEl) orderCountEl.textContent = orderCount;

        const partsCountEl = document.getElementById('partsCount');
        if (partsCountEl) partsCountEl.textContent = partsCount;

        // Update order count text
        const orderCountText = document.getElementById('orderCountText');
        if (orderCountText) {
            orderCountText.textContent = `${orderCount} sipariş`;
        }

        // Update total parts and area
        const totalParts = document.getElementById('totalParts');
        const totalArea = document.getElementById('totalArea');
        if (totalParts) totalParts.textContent = partsCount;
        if (totalArea) {
            const area = currentOrders.reduce((sum, o) =>
                sum + (o.width * o.height * o.quantity / 1000000), 0);
            totalArea.textContent = `${area.toFixed(2)} m²`;
        }

    } catch (error) {
        console.error('Stats update error:', error);
    }
}

function updateVisualizationStats() {
    if (!currentResult) return;

    const placedCount = document.getElementById('placedCount');
    if (placedCount) placedCount.textContent = currentResult.placed_parts?.length || 0;

    const utilizationRate = document.getElementById('utilizationRate');
    if (utilizationRate) utilizationRate.textContent =
        `${(currentResult.utilization * 100).toFixed(1)}%`;

    const wasteArea = document.getElementById('wasteArea');
    if (wasteArea) wasteArea.textContent =
        `${(currentResult.waste_area / 1000000).toFixed(2)} m²`;

    const cutCount = document.getElementById('cutCount');
    if (cutCount) cutCount.textContent = currentResult.total_cuts || 0;

    const totalDistance = document.getElementById('totalDistance');
    if (totalDistance) totalDistance.textContent = '-';

    const estimatedTime = document.getElementById('estimatedTime');
    if (estimatedTime) estimatedTime.textContent =
        `${currentResult.estimated_time?.toFixed(1)} dk`;

    const algorithmUsed = document.getElementById('algorithmUsed');
    if (algorithmUsed) algorithmUsed.textContent = 'Guillotine BestFit';
}

// ==================== Order Functions ====================

async function loadOrders() {
    showLoading();

    try {
        const response = await fetch(`${API_BASE}/orders`);
        const data = await response.json();
        currentOrders = data.orders || [];

        renderOrderList();
        updateStats();
        addLogEntry(`${currentOrders.length} sipariş yüklenildi`);

    } catch (error) {
        showToast('Sipariş yüklenemedi', 'error');
    }

    hideLoading();
}

async function addOrder() {
    showLoading();

    const orderData = {
        order_id: document.getElementById('orderId')?.value || '',
        width: document.getElementById('width')?.value,
        height: document.getElementById('height')?.value,
        quantity: document.getElementById('quantity')?.value,
        thickness: document.getElementById('thickness')?.value,
        glass_type: document.getElementById('glassType')?.value,
        priority: document.getElementById('priority')?.value,
        rotate_allowed: document.getElementById('rotateAllowed')?.checked,
        // Blade management options
        grinding_allowance: document.getElementById('grindingAllowance')?.value || 'none',
        blade_delete_enabled: document.getElementById('bladeDeleteEnabled')?.checked || false,
        trimming_enabled: document.getElementById('trimmingEnabled')?.checked || false
    };

    try {
        const response = await fetch(`${API_BASE}/orders`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(orderData)
        });

        const result = await response.json();

        if (result.success) {
            showToast('Sipariş eklendi!', 'success');
            loadOrders();
            clearForm();
            addLogEntry(`Sipariş ${result.order.order_id} eklendi`);
        } else {
            showToast('Hata: ' + result.error, 'error');
        }

    } catch (error) {
        showToast('API hatası', 'error');
    }

    hideLoading();
}

async function deleteOrder(orderId) {
    try {
        const response = await fetch(`${API_BASE}/orders/${orderId}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success) {
            showToast('Sipariş silindi', 'warning');
            loadOrders();
            addLogEntry(`Sipariş ${orderId} silindi`);
        }

    } catch (error) {
        showToast('Silme hatası', 'error');
    }
}

async function clearAllOrders() {
    if (!confirm('Tüm siparişleri silmek istediğinize emin misiniz?')) return;

    try {
        const response = await fetch(`${API_BASE}/orders/clear`, {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            currentOrders = [];
            renderOrderList();
            updateStats();
            showToast('Tüm siparişler silindi', 'warning');
            addLogEntry('Tüm siparişler silindi');
        }

    } catch (error) {
        showToast('Silme hatası', 'error');
    }
}

async function loadSampleOrders() {
    showLoading();

    try {
        const response = await fetch(`${API_BASE}/orders/load`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: 'orders.json' })
        });

        const result = await response.json();

        if (result.success) {
            currentOrders = result.orders;
            renderOrderList();
            updateStats();
            showToast(`${result.loaded} sipariş yüklenildi`, 'success');
            addLogEntry('Örnek siparişler yüklendi');
        } else {
            showToast('Dosya bulunamadı', 'error');
        }

    } catch (error) {
        showToast('Yükleme hatası', 'error');
    }

    hideLoading();
}

function renderOrderList() {
    const list = document.getElementById('orderList');
    if (!list) return;

    if (currentOrders.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <span class="icon">📭</span>
                <span>Henüz sipariş yok</span>
            </div>
        `;
        return;
    }

    list.innerHTML = currentOrders.map(order => {
        const herofisOptions = order.herofis_options || {};

        // Blade / processing indicators
        const bladeOptions = [];
        if (order.grinding_allowance && order.grinding_allowance !== 'none') {
            bladeOptions.push(`<span class="blade-option-tag" title="Rodaj/Taşlama: ${order.grinding_allowance}">🔧</span>`);
        }
        if (order.blade_delete_enabled) {
            bladeOptions.push(`<span class="blade-option-tag blade-delete" title="Lama Silme Aktif">🔪</span>`);
        }
        if (order.trimming_enabled) {
            bladeOptions.push(`<span class="blade-option-tag trimming" title="Rodaj Aktif">✂️</span>`);
        }
        if (order.edge_processing) {
            bladeOptions.push(`<span class="blade-option-tag rodaj" title="Kenar İşlemi: ${order.edge_processing}">🪟</span>`);
        }
        if (herofisOptions.is_shape) {
            bladeOptions.push(`<span class="blade-option-tag shape" title="Şekilli ürün">⬡</span>`);
        }
        if (herofisOptions.is_warranty) {
            bladeOptions.push(`<span class="blade-option-tag warranty" title="Garanti kapsamında">🛡️</span>`);
        }
        if ((herofisOptions.parameter_keys || []).length > 0) {
            bladeOptions.push(`<span class="blade-option-tag params" title="Herofis opsiyonları: ${(herofisOptions.parameter_keys || []).join(', ')}">🧩</span>`);
        }

        const metaLines = [];
        if (order.source_system === 'herofis') {
            metaLines.push(`<span class="order-meta-chip source">Herofis</span>`);
        }
        if (order.customer_name) {
            metaLines.push(`<span class="order-meta-chip">${order.customer_name}</span>`);
        }
        if (order.process_code) {
            metaLines.push(`<span class="order-meta-chip">Proses: ${order.process_code}</span>`);
        }
        if (order.edge_processing) {
            metaLines.push(`<span class="order-meta-chip">Kenar: ${order.edge_processing}</span>`);
        }
        if (herofisOptions.batch_no) {
            metaLines.push(`<span class="order-meta-chip">Batch: ${herofisOptions.batch_no}</span>`);
        }
        if (herofisOptions.line_note) {
            metaLines.push(`<span class="order-meta-chip">Not: ${herofisOptions.line_note}</span>`);
        }

        return `
        <div class="order-item">
            <div class="order-main">
                <span class="id">${order.order_id}</span>
                <span class="size">${order.width}x${order.height}</span>
                <span class="qty">${order.quantity}</span>
                <span class="type">${order.glass_type}</span>
                <span class="priority ${order.priority === 1 ? 'high' : order.priority === 2 ? 'medium' : 'low'}">
                    ${order.priority === 1 ? 'Yüksek' : order.priority === 2 ? 'Normal' : 'Düşük'}
                </span>
                <div class="blade-options">
                    ${bladeOptions.join('')}
                </div>
                <button class="delete-btn" onclick="deleteOrder('${order.order_id}')">🗑️</button>
            </div>
            ${metaLines.length ? `<div class="order-meta">${metaLines.join('')}</div>` : ''}
        </div>
    `;
    }).join('');
}

function clearForm() {
    const orderId = document.getElementById('orderId');
    if (orderId) orderId.value = '';

    const width = document.getElementById('width');
    if (width) width.value = 500;

    const height = document.getElementById('height');
    if (height) height.value = 400;

    const quantity = document.getElementById('quantity');
    if (quantity) quantity.value = 1;

    // Reset blade options
    const grindingAllowance = document.getElementById('grindingAllowance');
    if (grindingAllowance) grindingAllowance.value = 'none';

    const bladeDeleteEnabled = document.getElementById('bladeDeleteEnabled');
    if (bladeDeleteEnabled) bladeDeleteEnabled.checked = false;

    const trimmingEnabled = document.getElementById('trimmingEnabled');
    if (trimmingEnabled) trimmingEnabled.checked = false;
}

// ==================== Optimization Functions ====================

async function runOptimization() {
    if (currentOrders.length === 0) {
        showToast('Önce sipariş ekleyin', 'warning');
        return;
    }

    showLoading();

    const includeDefects = document.getElementById('includeDefects')?.checked || false;

    // Use local endpoint when offline
    const endpoint = isOffline ? `${API_BASE}/optimize/local` : `${API_BASE}/optimize`;

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ include_defects: includeDefects })
        });

        const result = await response.json();

        if (result.success) {
            currentResult = result.result;

            // Update stats
            const utilizationEl = document.getElementById('utilization');
            if (utilizationEl) utilizationEl.textContent =
                `${(currentResult.utilization * 100).toFixed(1)}%`;

            const estimatedTimeEl = document.getElementById('estimatedTime');
            if (estimatedTimeEl) estimatedTimeEl.textContent =
                `${currentResult.estimated_time?.toFixed(1)}`;

            // Show offline message if needed
            if (result.offline) {
                showToast('Offline optimizasyon tamamlandı (Local)', 'warning');
                addLogEntry(`Offline optimizasyon: ${(currentResult.utilization * 100).toFixed(1)}% kullanım`);
            } else {
                showToast('Optimizasyon tamamlandı!', 'success');
                addLogEntry(`AI optimizasyon: ${(currentResult.utilization * 100).toFixed(1)}% kullanım`);
            }

            // Update visualization if on that page
            if (document.getElementById('nestingCanvas')) {
                drawNesting(currentResult.placed_parts);
            }

            updateVisualizationStats();

        } else {
            showToast('Optimizasyon hatası: ' + result.error, 'error');
        }

    } catch (error) {
        showToast('API hatası: ' + error.message, 'error');
    }

    hideLoading();
}

async function runNestingOnly() {
    if (currentOrders.length === 0) {
        showToast('Önce sipariş ekleyin', 'warning');
        return;
    }

    showLoading();

    try {
        const response = await fetch(`${API_BASE}/optimize/nesting`, {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            currentResult = { placed_parts: result.placed_parts, utilization: result.utilization };

            if (document.getElementById('nestingCanvas')) {
                drawNesting(result.placed_parts);
            }

            showToast('Nesting tamamlandı', 'success');
        }

    } catch (error) {
        showToast('Hata: ' + error.message, 'error');
    }

    hideLoading();
}

// ==================== G-Code Functions ====================

async function loadGcodeFiles() {
    try {
        const response = await fetch(`${API_BASE}/gcode/files`);
        const data = await response.json();

        renderFilesList(data.files);

    } catch (error) {
        console.error('G-code files load error:', error);
    }
}

async function loadGcodeContent(filename) {
    showLoading();

    try {
        const response = await fetch(`${API_BASE}/gcode/file/${filename}`);
        const result = await response.json();

        if (result.success) {
            currentGcode = result.content;

            const currentFile = document.getElementById('currentFile');
            if (currentFile) currentFile.textContent = filename;

            const fileLines = document.getElementById('fileLines');
            if (fileLines) fileLines.textContent = `${result.lines} satır`;

            const gcodeContent = document.getElementById('gcodeContent');
            if (gcodeContent) gcodeContent.textContent = result.content;

            addLogEntry(`G-Code loaded: ${filename}`);
        }

    } catch (error) {
        showToast('G-code yüklenemedi', 'error');
    }

    hideLoading();
}

async function getGcode() {
    try {
        const response = await fetch(`${API_BASE}/gcode`);
        const result = await response.json();

        if (result.success) {
            currentGcode = result.gcode;

            const gcodeContent = document.getElementById('gcodeContent');
            if (gcodeContent) gcodeContent.textContent = result.gcode;

            const fileLines = document.getElementById('fileLines');
            if (fileLines) fileLines.textContent = `${result.lines} satır`;
        }

    } catch (error) {
        showToast('G-code yok', 'warning');
    }
}

function renderFilesList(files) {
    const list = document.getElementById('filesList');
    if (!list) return;

    if (files.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <span>G-Code dosyası yok</span>
            </div>
        `;
        return;
    }

    list.innerHTML = files.map(file => `
        <div class="file-item" onclick="loadGcodeContent('${file.filename}')">
            <span class="filename">${file.filename}</span>
            <span class="meta">${file.size} bytes</span>
        </div>
    `).join('');
}

function copyGcode() {
    if (!currentGcode) {
        showToast('G-code yok', 'warning');
        return;
    }

    navigator.clipboard.writeText(currentGcode);
    showToast('G-code kopyalandı', 'success');
}

async function downloadGcode() {
    try {
        window.open(`${API_BASE}/gcode/download`, '_blank');
        showToast('G-code indiriliyor', 'success');
    } catch (error) {
        showToast('İndirme hatası', 'error');
    }
}

function validateGcode() {
    showToast('G-code doğrulama (AI model ile)', 'warning');
}

// ==================== Navigation Functions ====================

function goToVisualization() {
    window.location.href = '/visualization';
}

function viewGcode() {
    window.location.href = '/gcode';
}

// ==================== Defects Functions ====================

async function loadDefects() {
    try {
        const response = await fetch(`${API_BASE}/defects`);
        const data = await response.json();

        renderDefectsList(data.defects);

        return data.defects;

    } catch (error) {
        console.error('Defects load error:', error);
        return [];
    }
}

function renderDefectsList(defects) {
    const list = document.getElementById('defectsList');
    if (!list) return;

    if (defects.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <span>Kusur yok</span>
            </div>
        `;
        return;
    }

    list.innerHTML = defects.map(d => `
        <div class="defect-item">
            <span class="type">${d.type}</span>
            <span class="pos">(${d.x.toFixed(0)}, ${d.y.toFixed(0)})</span>
            <span class="severity">${d.severity.toFixed(2)}</span>
        </div>
    `).join('');
}

// ==================== Initialize ====================

document.addEventListener('DOMContentLoaded', () => {
    console.log('Glass Cutting Program initialized');
});

// ==================== Herofis Integration ====================

let herofisPreviewData = [];
let herofisSelectedFile = null;

function showHerofisImport() {
    const modal = document.getElementById('herofisModal');
    if (modal) {
        modal.style.display = 'flex';
        loadHerofisHistory();
    }
}

function closeHerofisModal() {
    const modal = document.getElementById('herofisModal');
    if (modal) {
        modal.style.display = 'none';
    }
    // Reset state
    herofisPreviewData = [];
    herofisSelectedFile = null;
    document.getElementById('herofisPreview').style.display = 'none';
    document.getElementById('herofisImportBtn').disabled = true;
    document.getElementById('herofisFileName').textContent = 'Dosya seçilmedi';
}

function handleHerofisFile(event) {
    const file = event.target.files[0];
    if (!file) return;

    herofisSelectedFile = file;
    document.getElementById('herofisFileName').textContent = file.name;

    // Preview the file
    previewHerofisFile(file);
}

async function previewHerofisFile(file) {
    showLoading();

    try {
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE}/herofis/import`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            herofisPreviewData = result.orders_preview || [];

            // Show preview section
            document.getElementById('herofisPreview').style.display = 'block';
            document.getElementById('herofisImportable').textContent =
                `${result.imported} sipariş import edilebilir`;

            if (result.errors && result.errors.length > 0) {
                document.getElementById('herofisErrors').textContent =
                    `${result.skipped} satır hata: ${result.errors.join(', ')}`;
            } else {
                document.getElementById('herofisErrors').textContent = '';
            }

            // Render preview table
            renderHerofisPreview(herofisPreviewData);

            // Enable import button
            document.getElementById('herofisImportBtn').disabled = false;

            showToast(`${result.imported} sipariş önizleme`, 'success');
        } else {
            document.getElementById('herofisPreview').style.display = 'block';
            document.getElementById('herofisImportable').textContent = '0 sipariş';
            document.getElementById('herofisErrors').textContent =
                result.errors ? result.errors.join(', ') : 'Import hatası';
            showToast('CSV parse hatası', 'error');
        }

    } catch (error) {
        showToast('Preview hatası: ' + error.message, 'error');
    }

    hideLoading();
}

function renderHerofisPreview(orders) {
    const tbody = document.getElementById('herofisPreviewBody');
    if (!tbody) return;

    if (!orders || orders.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7">Veri yok</td></tr>';
        return;
    }

    tbody.innerHTML = orders.map(order => `
        <tr>
            <td>${order.order_id || '-'}</td>
            <td>${order.customer || '-'}</td>
            <td>${order.width || '-'}</td>
            <td>${order.height || '-'}</td>
            <td>${order.thickness || '-'} mm</td>
            <td>${order.glass_type || 'float'}</td>
            <td>${order.quantity || 1}</td>
        </tr>
    `).join('');
}

async function importHerofisOrders() {
    if (!herofisSelectedFile) {
        showToast('Dosya seçilmedi', 'warning');
        return;
    }

    showLoading();

    try {
        const formData = new FormData();
        formData.append('file', herofisSelectedFile);

        const response = await fetch(`${API_BASE}/herofis/import`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            showToast(`${result.imported} sipariş import edildi!`, 'success');
            addLogEntry(`Herofis import: ${result.imported} sipariş`);

            // Close modal
            closeHerofisModal();

            // Refresh orders list
            await loadOrders();
        } else {
            showToast('Import hatası: ' + (result.errors ? result.errors.join(', ') : 'Bilinmeyen hata'), 'error');
        }

    } catch (error) {
        showToast('Import hatası: ' + error.message, 'error');
    }

    hideLoading();
}

async function downloadHerofisSample() {
    try {
        const response = await fetch(`${API_BASE}/herofis/sample`);
        const blob = await response.blob();

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'sample_herofis_import.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);

        showToast('Örnek CSV indirildi', 'success');
    } catch (error) {
        showToast('İndirme hatası', 'error');
    }
}

async function loadHerofisHistory() {
    try {
        const response = await fetch(`${API_BASE}/herofis/history`);
        const result = await response.json();

        if (result.success) {
            renderHerofisHistory(result.history);
        }
    } catch (error) {
        console.error('History load error:', error);
    }
}

function renderHerofisHistory(history) {
    const list = document.getElementById('herofisHistoryList');
    if (!list) return;

    if (!history || history.length === 0) {
        list.innerHTML = '<div class="empty-history">Henüz import yapılmadı</div>';
        return;
    }

    list.innerHTML = history.map(entry => `
        <div class="history-item">
            <span class="history-time">${new Date(entry.timestamp).toLocaleString('tr-TR')}</span>
            <span class="history-file">${entry.source_file.split('/').pop()}</span>
            <span class="history-count">${entry.success_rate} sipariş</span>
        </div>
    `).join('');
}

// ==================== Global Functions (for onclick handlers) ====================
// These functions need to be global for HTML onclick attributes

window.loadOrders = loadOrders;
window.loadSampleOrders = loadSampleOrders;
window.addOrder = addOrder;
window.deleteOrder = deleteOrder;
window.clearAllOrders = clearAllOrders;
window.runOptimization = runOptimization;
window.runNestingOnly = runNestingOnly;
window.getGcode = getGcode;
window.downloadGcode = downloadGcode;
window.copyGcode = copyGcode;
window.validateGcode = validateGcode;
window.goToVisualization = goToVisualization;
window.viewGcode = viewGcode;
window.updateTime = updateTime;
window.showToast = showToast;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.addLogEntry = addLogEntry;
