/**
 * Glass Cutting Program - Visualization JavaScript
 * Nesting Canvas Drawing
 */

// Canvas settings
const SHEET_WIDTH = 6000;  // mm
const SHEET_HEIGHT = 3000;  // mm

let canvas = null;
let ctx = null;
let scale = 7.5;  // px per mm
let showGrid = true;
let showDefects = false;
let placedParts = [];
let defects = [];
// currentOrders is global from app.js

// Shared utility functions (from app.js)
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.classList.add('active');
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.classList.remove('active');
}

// Colors
const COLORS = {
    sheet: '#334155',
    sheetBorder: '#3b82f6',
    part: {
        float: 'rgba(59, 130, 246, 0.5)',
        laminated: 'rgba(34, 197, 94, 0.5)',
        tempered: 'rgba(245, 158, 11, 0.5)'
    },
    partBorder: '#f8fafc',
    defect: {
        scratch: 'rgba(245, 158, 11, 0.7)',
        bubble: 'rgba(59, 130, 246, 0.7)',
        crack: 'rgba(239, 68, 68, 0.9)',
        inclusion: 'rgba(168, 85, 247, 0.7)'
    },
    grid: 'rgba(100, 116, 139, 0.2)',
    path: '#22c55e',
    text: '#f8fafc'
};

// ==================== Canvas Setup ====================

function initCanvas() {
    canvas = document.getElementById('nestingCanvas');
    if (!canvas) return;

    ctx = canvas.getContext('2d');

    // Set canvas size
    canvas.width = 800;
    canvas.height = 400;

    // Calculate scale
    scale = canvas.width / SHEET_WIDTH;

    // Initial draw
    drawSheet();

    // Load data if available
    if (placedParts.length > 0) {
        drawNesting(placedParts);
    }
}

// ==================== Drawing Functions ====================

function drawSheet() {
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw sheet background
    ctx.fillStyle = COLORS.sheet;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw sheet border
    ctx.strokeStyle = COLORS.sheetBorder;
    ctx.lineWidth = 3;
    ctx.strokeRect(0, 0, canvas.width, canvas.height);

    // Draw grid
    if (showGrid) {
        drawGrid();
    }

    // Draw dimensions
    ctx.fillStyle = COLORS.text;
    ctx.font = '12px Inter';
    ctx.fillText(`${SHEET_WIDTH}mm`, canvas.width - 60, canvas.height - 10);
    ctx.fillText(`${SHEET_HEIGHT}mm`, 10, 20);
}

function drawGrid() {
    ctx.strokeStyle = COLORS.grid;
    ctx.lineWidth = 0.5;

    // Vertical lines (every 500mm)
    for (let x = 0; x <= SHEET_WIDTH; x += 500) {
        const px = x * scale;
        ctx.beginPath();
        ctx.moveTo(px, 0);
        ctx.lineTo(px, canvas.height);
        ctx.stroke();
    }

    // Horizontal lines (every 500mm)
    for (let y = 0; y <= SHEET_HEIGHT; y += 500) {
        const py = y * scale;
        ctx.beginPath();
        ctx.moveTo(0, py);
        ctx.lineTo(canvas.width, py);
        ctx.stroke();
    }
}

function drawNesting(parts) {
    if (!ctx) return;

    placedParts = parts || [];
    drawSheet();

    // Draw each part
    placedParts.forEach((part, index) => {
        drawPart(part, index);
    });

    // Draw defects if enabled
    if (showDefects) {
        drawDefects();
    }

    // Draw cutting path
    drawCuttingPath();
}

function drawPart(part, index) {
    const x = part.x * scale;
    const y = part.y * scale;
    const w = (part.placed_width || part.width) * scale;
    const h = (part.placed_height || part.height) * scale;

    // Get glass type color
    const glassType = part.glass_type || 'float';
    const color = COLORS.part[glassType] || COLORS.part.float;

    // Draw part fill
    ctx.fillStyle = color;
    ctx.fillRect(x, y, w, h);

    // Draw part border
    ctx.strokeStyle = COLORS.partBorder;
    ctx.lineWidth = 1;
    ctx.strokeRect(x, y, w, h);

    // Draw part label
    ctx.fillStyle = COLORS.text;
    ctx.font = '10px Inter';
    const label = part.order_id || part.part_id || `P${index + 1}`;
    ctx.fillText(label, x + 2, y + 12);

    // Draw dimensions
    ctx.font = '8px Inter';
    const dimText = `${Math.round(w / scale)}x${Math.round(h / scale)}`;
    ctx.fillText(dimText, x + 2, y + h - 5);

    // Draw rotation indicator
    if (part.rotated) {
        ctx.fillStyle = 'rgba(255,255,255,0.5)';
        ctx.fillText('↻', x + w - 10, y + 12);
    }
}

function drawDefects() {
    if (!defects || defects.length === 0) return;

    defects.forEach(defect => {
        const x = defect.x * scale;
        const y = defect.y * scale;
        const r = defect.radius * scale;

        // Get defect type color
        const color = COLORS.defect[defect.type] || COLORS.defect.crack;

        // Draw defect circle
        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();

        // Draw center point
        ctx.beginPath();
        ctx.arc(x, y, 2, 0, Math.PI * 2);
        ctx.fillStyle = defect.severity > 0.5 ? '#ef4444' : '#f59e0b';
        ctx.fill();

        // Draw severity indicator
        ctx.fillStyle = COLORS.text;
        ctx.font = '8px Inter';
        ctx.fillText(defect.type.substring(0, 3), x - 8, y - r - 2);
    });
}

function drawCuttingPath() {
    if (!placedParts || placedParts.length < 2) return;

    ctx.strokeStyle = COLORS.path;
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 3]);

    // Draw path between parts
    ctx.beginPath();

    // Start from origin
    ctx.moveTo(0, 0);

    placedParts.forEach((part, i) => {
        const x = part.x * scale;
        const y = part.y * scale;
        ctx.lineTo(x, y);

        // Draw to part center
        const cx = (part.x + (part.placed_width || part.width) / 2) * scale;
        const cy = (part.y + (part.placed_height || part.height) / 2) * scale;
        ctx.lineTo(cx, cy);
    });

    // Return to origin
    ctx.lineTo(0, 0);
    ctx.stroke();
    ctx.setLineDash([]);
}

// ==================== Controls ====================

function zoomIn() {
    scale *= 1.2;
    redraw();
    showToast('Zoom: +' + Math.round(scale * 100) + '%', 'success');
}

function zoomOut() {
    scale *= 0.8;
    scale = Math.max(0.05, scale);  // Minimum scale
    redraw();
    showToast('Zoom: -' + Math.round(scale * 100) + '%', 'success');
}

function resetZoom() {
    scale = canvas.width / SHEET_WIDTH;
    redraw();
    showToast('Zoom reset', 'success');
}

function toggleGrid() {
    showGrid = !showGrid;
    redraw();
    showToast('Grid: ' + (showGrid ? 'ON' : 'OFF'), 'success');
}

function toggleDefects() {
    showDefects = !showDefects;

    if (showDefects) {
        loadDefects().then(d => {
            defects = d;
            redraw();
        });
    } else {
        redraw();
    }

    showToast('Kusurlar: ' + (showDefects ? 'Göster' : 'Gizle'), 'success');
}

function redraw() {
    if (placedParts.length > 0) {
        drawNesting(placedParts);
    } else {
        drawSheet();
    }
}

function refreshVisualization() {
    runNestingOnly();
}

function runPathOptimization() {
    showToast('Yol optimizasyonu (TSP 2-opt)', 'warning');
}

function exportImage() {
    if (!canvas) return;

    // Create download link
    const link = document.createElement('a');
    link.download = 'nesting_preview.png';
    link.href = canvas.toDataURL('image/png');
    link.click();

    showToast('Görsel indirildi', 'success');
}

// ==================== Data Loading ====================

async function refreshVisualizationStats() {
    try {
        // Check if we have optimization result
        const response = await fetch('/api/optimize/nesting', {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            placedParts = result.placed_parts;
            drawNesting(placedParts);

            // Update stats
            const placedCount = document.getElementById('placedCount');
            if (placedCount) placedCount.textContent = placedParts.length;

            const utilizationRate = document.getElementById('utilizationRate');
            if (utilizationRate) utilizationRate.textContent =
                `${(result.utilization * 100).toFixed(1)}%`;

            const algorithmUsed = document.getElementById('algorithmUsed');
            if (algorithmUsed) algorithmUsed.textContent = result.algorithm;
        }

    } catch (error) {
        console.log('Visualization waiting for optimization');
    }
}

// ==================== Mouse Interaction ====================

function setupMouseEvents() {
    if (!canvas) return;

    canvas.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;

        // Convert to mm
        const mmX = Math.round(mx / scale);
        const mmY = Math.round(my / scale);

        // Update cursor position (could show tooltip)
        // console.log(`Position: ${mmX}mm, ${mmY}mm`);
    });

    canvas.addEventListener('click', (e) => {
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;

        // Find clicked part
        const mmX = mx / scale;
        const mmY = my / scale;

        const clickedPart = placedParts.find(part => {
            const px = part.x;
            const py = part.y;
            const pw = part.placed_width || part.width;
            const ph = part.placed_height || part.height;

            return mmX >= px && mmX <= px + pw && mmY >= py && mmY <= py + ph;
        });

        if (clickedPart) {
            showToast(`Parça: ${clickedPart.order_id || clickedPart.part_id}`, 'success');
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initCanvas();
    setupMouseEvents();
    refreshVisualizationStats();
});

// ==================== Global Functions (for onclick handlers) ====================
window.zoomIn = zoomIn;
window.zoomOut = zoomOut;
window.resetZoom = resetZoom;
window.toggleGrid = toggleGrid;
window.toggleDefects = toggleDefects;
window.redraw = redraw;
window.refreshVisualization = refreshVisualization;
window.runNestingOnly = runNestingOnly;
window.runPathOptimization = runPathOptimization;
window.exportImage = exportImage;
window.drawNesting = drawNesting;
window.initCanvas = initCanvas;

// These functions are in app.js, but we need local versions for visualization page
// API_BASE from app.js (window.API_BASE)
const API_BASE_LOCAL = window.API_BASE || '/api';

async function runNestingOnly() {
    if (!currentOrders || currentOrders.length === 0) {
        // Try to load from API
        try {
            const response = await fetch('/api/orders');
            const data = await response.json();
            currentOrders = data.orders || [];
        } catch (e) {
            showToast('Sipariş yok', 'warning');
            return;
        }
    }

    showLoading();

    try {
        const response = await fetch(`${API_BASE_LOCAL}/optimize/nesting`, {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            placedParts = result.placed_parts;
            drawNesting(placedParts);

            showToast('Nesting tamamlandı', 'success');
        }
    } catch (error) {
        showToast('Hata: ' + error.message, 'error');
    }

    hideLoading();
}

function runPathOptimization() {
    showToast('Yol optimizasyonu (TSP 2-opt)', 'warning');
}