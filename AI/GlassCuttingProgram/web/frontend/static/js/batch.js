/**
 * Batch Processing - JavaScript
 * Multi-sheet optimization and queue management
 */

let sheets = [];
let orders = [];
let jobs = [];
let statistics = {};

// ==================== Initialization ====================

function loadBatchData() {
    loadSheets();
    loadOrders();
    loadStatistics();
}

async function loadSheets() {
    try {
        const response = await fetch('/api/batch/sheets');
        const result = await response.json();
        
        if (result.success) {
            sheets = result.sheets;
            displaySheets(sheets);
            updateSheetsSummary(sheets);
        }
    } catch (error) {
        console.error('Sheets load error:', error);
    }
}

async function loadOrders() {
    try {
        const response = await fetch('/api/batch/orders');
        const result = await response.json();
        
        if (result.success) {
            orders = result.orders;
            displayOrders(orders);
            updateOrdersSummary(orders);
        }
    } catch (error) {
        console.error('Orders load error:', error);
    }
}

async function loadStatistics() {
    try {
        const response = await fetch('/api/batch/statistics');
        const result = await response.json();
        
        if (result.success) {
            statistics = result.statistics;
        }
    } catch (error) {
        console.error('Statistics load error:', error);
    }
}

// ==================== Display Functions ====================

function displaySheets(sheets) {
    const list = document.getElementById('sheetsList');
    if (!list) return;
    
    if (sheets.length === 0) {
        list.innerHTML = '<div class="empty-state"><span>Levha yok</span></div>';
        return;
    }
    
    list.innerHTML = sheets.map(sheet => `
        <div class="sheet-item">
            <div class="sheet-header">
                <span class="sheet-id">${sheet.sheet_id}</span>
                <span class="sheet-status ${sheet.status}">${sheet.status}</span>
            </div>
            <div class="sheet-details">
                <span>${sheet.width}x${sheet.height}mm</span>
                <span>${sheet.thickness}mm</span>
                <span>${sheet.glass_type}</span>
            </div>
            <div class="sheet-progress">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${sheet.utilization * 100}%"></div>
                </div>
                <span class="progress-text">${(sheet.utilization * 100).toFixed(1)}%</span>
            </div>
        </div>
    `).join('');
}

function displayOrders(orders) {
    const list = document.getElementById('ordersList');
    if (!list) return;
    
    if (orders.length === 0) {
        list.innerHTML = '<div class="empty-state"><span>Sipariş yok</span></div>';
        return;
    }
    
    list.innerHTML = orders.map(order => `
        <div class="order-item">
            <div class="order-header">
                <span class="order-id">${order.order_id}</span>
                <span class="order-priority priority-${order.priority}">P${order.priority}</span>
            </div>
            <div class="order-details">
                <span>${order.width}x${order.height}mm</span>
                <span>x${order.quantity}</span>
                <span>${order.glass_type}</span>
            </div>
            <div class="order-status">
                <span class="completed">${order.completed_quantity}/${order.quantity}</span>
                ${order.is_complete ? '<span class="badge complete">✓</span>' : ''}
            </div>
        </div>
    `).join('');
}

function updateSheetsSummary(sheets) {
    document.getElementById('totalSheets').textContent = sheets.length;
    document.getElementById('usedSheets').textContent = 
        sheets.filter(s => s.utilization > 0).length;
}

function updateOrdersSummary(orders) {
    document.getElementById('totalOrders').textContent = orders.length;
    document.getElementById('completedOrders').textContent = 
        orders.filter(o => o.is_complete).length;
    document.getElementById('pendingOrders').textContent = 
        orders.filter(o => !o.is_complete).length;
}

// ==================== Modal Functions ====================

function showAddSheetModal() {
    document.getElementById('addSheetModal').style.display = 'flex';
}

function closeAddSheetModal() {
    document.getElementById('addSheetModal').style.display = 'none';
}

// ==================== Add Functions ====================

async function addSheet() {
    showLoading();
    
    const data = {
        sheet_id: document.getElementById('sheetId').value || undefined,
        width: parseFloat(document.getElementById('sheetWidth').value),
        height: parseFloat(document.getElementById('sheetHeight').value),
        thickness: parseFloat(document.getElementById('sheetThickness').value),
        glass_type: document.getElementById('sheetGlassType').value
    };
    
    try {
        const response = await fetch('/api/batch/sheets', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Levha eklendi', 'success');
            closeAddSheetModal();
            loadSheets();
        } else {
            showToast('Hata: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Hata: ' + error.message, 'error');
    }
    
    hideLoading();
}

async function addOrder() {
    // Similar implementation
    showLoading();
    
    const data = {
        order_id: document.getElementById('orderId')?.value || undefined,
        width: parseFloat(document.getElementById('orderWidth')?.value || 500),
        height: parseFloat(document.getElementById('orderHeight')?.value || 400),
        quantity: parseInt(document.getElementById('orderQuantity')?.value || 1),
        thickness: parseFloat(document.getElementById('orderThickness')?.value || 4),
        glass_type: document.getElementById('orderGlassType')?.value || 'float',
        priority: parseInt(document.getElementById('orderPriority')?.value || 2)
    };
    
    try {
        const response = await fetch('/api/batch/orders', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Sipariş eklendi', 'success');
            loadOrders();
        }
    } catch (error) {
        showToast('Hata: ' + error.message, 'error');
    }
    
    hideLoading();
}

// ==================== Optimization ====================

async function runOptimization() {
    showLoading();
    
    const data = {
        strategy: document.getElementById('optStrategy')?.value || 'efficiency',
        use_remnants: document.getElementById('useRemnants')?.checked,
        auto_queue: document.getElementById('autoQueue')?.checked
    };
    
    try {
        const response = await fetch('/api/batch/optimize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayOptimizationResults(result);
            showToast(`Optimizasyon tamamlandı: ${result.jobs.length} iş`, 'success');
            loadStatistics();
        } else {
            showToast('Hata: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Hata: ' + error.message, 'error');
    }
    
    hideLoading();
}

function displayOptimizationResults(result) {
    const resultsDiv = document.getElementById('optimizationResults');
    if (!resultsDiv) return;
    
    resultsDiv.innerHTML = `
        <div class="results-summary">
            <h3>Optimizasyon Sonuçları</h3>
            <div class="stats-grid">
                <div class="stat-item">
                    <span class="stat-label">İş Sayısı</span>
                    <span class="stat-value">${result.jobs.length}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Kullanılan Levha</span>
                    <span class="stat-value">${result.statistics.used_sheets}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Ort. Verimlilik</span>
                    <span class="stat-value">${(result.statistics.avg_utilization * 100).toFixed(1)}%</span>
                </div>
            </div>
        </div>
        
        <div class="jobs-list">
            ${result.jobs.map(job => `
                <div class="job-item">
                    <span class="job-id">${job.job_id}</span>
                    <span class="job-sheet">${job.sheet_id}</span>
                    <span class="job-orders">${job.orders.length} sipariş</span>
                    <span class="job-time">${job.estimated_time.toFixed(1)} dk</span>
                </div>
            `).join('')}
        </div>
    `;
}

// Show add order modal function
function showAddOrderModal() {
    // Implement modal display
    showToast('Sipariş ekleme modalı yakında eklenecek', 'info');
}