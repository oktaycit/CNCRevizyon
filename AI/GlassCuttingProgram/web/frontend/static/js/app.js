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

        document.getElementById('orderCount')?.textContent = orderCount;
        document.getElementById('partsCount')?.textContent = partsCount;

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

    document.getElementById('placedCount')?.textContent = currentResult.placed_parts?.length || 0;
    document.getElementById('utilizationRate')?.textContent =
        `${(currentResult.utilization * 100).toFixed(1)}%`;
    document.getElementById('wasteArea')?.textContent =
        `${(currentResult.waste_area / 1000000).toFixed(2)} m²`;
    document.getElementById('cutCount')?.textContent = currentResult.total_cuts || 0;
    document.getElementById('totalDistance')?.textContent = '-';
    document.getElementById('estimatedTime')?.textContent =
        `${currentResult.estimated_time?.toFixed(1)} dk`;
    document.getElementById('algorithmUsed')?.textContent = 'Guillotine BestFit';
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
        rotate_allowed: document.getElementById('rotateAllowed')?.checked
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

    list.innerHTML = currentOrders.map(order => `
        <div class="order-item">
            <span class="id">${order.order_id}</span>
            <span class="size">${order.width}x${order.height}</span>
            <span class="qty">${order.quantity}</span>
            <span class="type">${order.glass_type}</span>
            <span class="priority ${order.priority === 1 ? 'high' : order.priority === 2 ? 'medium' : 'low'}">
                ${order.priority === 1 ? 'Yüksek' : order.priority === 2 ? 'Normal' : 'Düşük'}
            </span>
            <button class="delete-btn" onclick="deleteOrder('${order.order_id}')">🗑️</button>
        </div>
    `).join('');
}

function clearForm() {
    document.getElementById('orderId')?.value = '';
    document.getElementById('width')?.value = 500;
    document.getElementById('height')?.value = 400;
    document.getElementById('quantity')?.value = 1;
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
            document.getElementById('utilization')?.textContent =
                `${(currentResult.utilization * 100).toFixed(1)}%`;
            document.getElementById('estimatedTime')?.textContent =
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

            document.getElementById('currentFile')?.textContent = filename;
            document.getElementById('fileLines')?.textContent = `${result.lines} satır`;
            document.getElementById('gcodeContent')?.textContent = result.content;

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
            document.getElementById('gcodeContent')?.textContent = result.gcode;
            document.getElementById('fileLines')?.textContent = `${result.lines} satır`;
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