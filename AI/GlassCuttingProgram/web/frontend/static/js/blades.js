/**
 * Blade Management - JavaScript
 * Blade life tracking and spin control
 */

// Blade state
let bladeData = {};
let activeBlade = null;
let blades = {};
let alerts = [];
let statistics = {};

// ==================== Load Blade Data ====================

async function loadBladeData() {
    try {
        const response = await fetch('/api/blades');
        const data = await response.json();
        
        if (data.success) {
            bladeData = data;
            blades = data.blades || {};
            activeBlade = data.active_blade;
            alerts = data.alerts || [];
            statistics = data.statistics || {};
            
            updateBladeUI();
            updateAlertsUI();
            updateStatsUI();
        }
    } catch (error) {
        console.error('Blade data load error:', error);
    }
}

// ==================== Update UI ====================

function updateBladeUI() {
    const infoDiv = document.getElementById('activeBladeInfo');
    if (!infoDiv) return;
    
    if (!activeBlade) {
        infoDiv.innerHTML = `
            <div class="empty-state">
                <span>Aktif bıçak yok</span>
                <button class="btn primary" onclick="showInstallModal()">➕ Bıçak Tak</button>
            </div>
        `;
        return;
    }
    
    // Status indicator
    const statusIndicator = document.getElementById('bladeStatusIndicator');
    const statusDot = statusIndicator.querySelector('.status-dot');
    const statusText = statusIndicator.querySelector('.status-text');
    
    statusDot.className = 'status-dot ' + activeBlade.status;
    statusText.textContent = getStatusText(activeBlade.status);
    
    // Details
    document.getElementById('bladeId').textContent = activeBlade.blade_id;
    document.getElementById('bladeType').textContent = getBladeTypeText(activeBlade.blade_type);
    document.getElementById('bladeLife').textContent = 
        `${activeBlade.used_life.toFixed(1)} / ${activeBlade.total_life} m`;
    document.getElementById('bladeRemaining').textContent = 
        `${activeBlade.remaining_life.toFixed(1)} m`;
    document.getElementById('bladeSpin').textContent = activeBlade.spin_count;
    
    // Progress bar
    const progressFill = document.getElementById('bladeLifeProgress');
    const progressText = document.getElementById('bladeLifePercent');
    
    progressFill.style.width = activeBlade.life_percentage + '%';
    progressText.textContent = activeBlade.life_percentage.toFixed(1) + '%';
    
    // Color based on life
    if (activeBlade.life_percentage > 50) {
        progressFill.style.background = '#22c55e';
    } else if (activeBlade.life_percentage > 20) {
        progressFill.style.background = '#f59e0b';
    } else {
        progressFill.style.background = '#ef4444';
    }
    
    // Spin button
    const spinBtn = document.getElementById('spinBtn');
    spinBtn.disabled = !activeBlade.needs_spin;
}

function updateAlertsUI() {
    const list = document.getElementById('alertsList');
    if (!list) return;
    
    if (alerts.length === 0) {
        list.innerHTML = '<div class="empty-state"><span>Uyarı yok</span></div>';
        return;
    }
    
    list.innerHTML = alerts.map(alert => `
        <div class="alert-item ${alert.type}">
            <span class="alert-icon">${getAlertIcon(alert.type)}</span>
            <span class="alert-message">${alert.message}</span>
            ${alert.action === 'spin' ? 
                `<button class="btn small" onclick="spinBlade()">🔄 Döndür</button>` : 
                ''}
        </div>
    `).join('');
}

function updateStatsUI() {
    if (!statistics) return;
    
    document.getElementById('totalBlades').textContent = statistics.total_blades || 0;
    document.getElementById('activeBlades').textContent = statistics.active_blades || 0;
    document.getElementById('expiredBlades').textContent = statistics.expired_blades || 0;
    document.getElementById('totalCuts').textContent = statistics.total_cuts || 0;
    document.getElementById('totalLength').textContent = 
        (statistics.total_cut_length || 0).toFixed(0) + 'm';
    document.getElementById('avgCut').textContent = 
        (statistics.average_cut_length || 0).toFixed(1) + 'm';
    
    document.getElementById('bladeCountText').textContent = 
        Object.keys(blades).length + ' bıçak';
    
    // Update blade list
    updateBladeList();
}

function updateBladeList() {
    const list = document.getElementById('bladeList');
    if (!list) return;
    
    const bladeArray = Object.values(blades);
    
    if (bladeArray.length === 0) {
        list.innerHTML = '<div class="empty-state"><span>Henüz bıçak yok</span></div>';
        return;
    }
    
    list.innerHTML = bladeArray.map(blade => `
        <div class="blade-list-item">
            <span class="blade-id">${blade.blade_id}</span>
            <span class="blade-type">${getBladeTypeText(blade.blade_type)}</span>
            <span class="blade-life">${blade.used_life.toFixed(0)}/${blade.total_life}m</span>
            <span class="blade-status ${blade.status}">${getStatusText(blade.status)}</span>
            <button class="btn small ${blade.blade_id === activeBlade?.blade_id ? 'active' : ''}" 
                    onclick="setActiveBlade('${blade.blade_id}')">
                ${blade.blade_id === activeBlade?.blade_id ? '✓ Aktif' : 'Aktif Yap'}
            </button>
        </div>
    `).join('');
}

// ==================== Helper Functions ====================

function getStatusText(status) {
    const texts = {
        new: 'Yeni',
        active: 'Aktif',
        warning: 'Uyarı',
        expired: 'Süresi Dolmuş',
        spin_required: 'Spin Gerekli'
    };
    return texts[status] || status;
}

function getBladeTypeText(type) {
    const texts = {
        standard: 'Standart',
        laminated: 'Lamine',
        tempered: 'Temperli',
        diamond: 'Elmas',
        carbide: 'Karbür'
    };
    return texts[type] || type;
}

function getAlertIcon(type) {
    const icons = {
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    return icons[type] || '•';
}

// ==================== Actions ====================

function showInstallModal() {
    document.getElementById('installModal').style.display = 'flex';
}

function closeInstallModal() {
    document.getElementById('installModal').style.display = 'none';
    // Clear inputs
    document.getElementById('newBladeId').value = '';
}

async function installBlade() {
    showLoading();
    
    const data = {
        blade_id: document.getElementById('newBladeId').value || undefined,
        blade_type: document.getElementById('newBladeType').value,
        total_life: parseFloat(document.getElementById('bladeTotalLife').value),
        spin_interval: parseFloat(document.getElementById('bladeSpinInterval').value)
    };
    
    try {
        const response = await fetch('/api/blades/install', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Bıçak takıldı', 'success');
            closeInstallModal();
            loadBladeData();
        } else {
            showToast('Hata: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Hata: ' + error.message, 'error');
    }
    
    hideLoading();
}

function showReplaceModal() {
    document.getElementById('replaceModal').style.display = 'flex';
}

function closeReplaceModal() {
    document.getElementById('replaceModal').style.display = 'none';
    document.getElementById('replaceBladeId').value = '';
}

async function replaceBlade() {
    showLoading();
    
    const newBladeId = document.getElementById('replaceBladeId').value;
    
    if (!newBladeId) {
        showToast('Yeni bıçak ID girin', 'warning');
        hideLoading();
        return;
    }
    
    try {
        const response = await fetch('/api/blades/replace', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                new_blade_id: newBladeId,
                blade_type: 'standard'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Bıçak değiştirildi', 'success');
            closeReplaceModal();
            loadBladeData();
        } else {
            showToast('Hata: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Hata: ' + error.message, 'error');
    }
    
    hideLoading();
}

async function spinBlade() {
    showLoading();
    
    try {
        const response = await fetch('/api/blades/spin', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Bıçak döndürüldü', 'success');
            loadBladeData();
        } else {
            showToast(result.error || 'Spin başarısız', 'error');
        }
    } catch (error) {
        showToast('Hata: ' + error.message, 'error');
    }
    
    hideLoading();
}

async function setActiveBlade(bladeId) {
    showLoading();
    
    // This would need a new API endpoint
    showToast('Bıçak değiştiriliyor...', 'info');
    
    setTimeout(() => {
        loadBladeData();
        hideLoading();
    }, 500);
}

// ==================== Grinding Allowance Preview ====================

function updateGrindingPreview() {
    const type = document.getElementById('grindingType').value;
    
    const allowances = {
        none: { x: 0, y: 0 },
        grinding: { x: 4, y: 4 },
        fine_grinding: { x: 2, y: 2 },
        polishing: { x: 3, y: 3 },
        bevelling: { x: 6, y: 6 },
        edge_sealing: { x: 1, y: 1 }
    };
    
    const allowance = allowances[type] || allowances.none;
    
    // Original: 500x400 -> preview 100x80 (scale 0.2)
    const originalW = 100;
    const originalH = 80;
    
    // Cutting size with allowance
    const cuttingW = originalW + allowance.x * 0.2;
    const cuttingH = originalH + allowance.y * 0.2;
    
    document.getElementById('previewCuttingBox').style.width = cuttingW + 'px';
    document.getElementById('previewCuttingBox').style.height = cuttingH + 'px';
    document.getElementById('previewCuttingSize').textContent = 
        `${500 + allowance.x}x${400 + allowance.y}`;
    
    document.getElementById('xAddition').textContent = `+${allowance.x}mm`;
    document.getElementById('yAddition').textContent = `+${allowance.y}mm`;
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateGrindingPreview();
});