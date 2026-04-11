/**
 * DXF Import - JavaScript
 * AutoCAD DXF file import and preview
 */

// DXF state
let dxfFile = null;
let dxfResult = null;
let dxfShapes = [];
let selectedLayers = [];
let canvas = null;
let ctx = null;
let scale = 1;
let offsetX = 0;
let offsetY = 0;

// ==================== Initialization ====================

function initDXFUpload() {
    canvas = document.getElementById('dxfCanvas');
    if (canvas) {
        ctx = canvas.getContext('2d');
    }
    
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('dxfFileInput');
    
    if (uploadArea) {
        // Click to upload
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelect(files[0]);
            }
        });
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });
    }
}

// ==================== File Handling ====================

function handleFileSelect(file) {
    if (!file.name.toLowerCase().endsWith('.dxf')) {
        showToast('Lütfen .dxf dosyası seçin', 'error');
        return;
    }
    
    dxfFile = file;
    
    // Update UI
    const uploadText = document.querySelector('.upload-text h3');
    if (uploadText) {
        uploadText.textContent = file.name;
    }
    
    document.getElementById('parseBtn').disabled = false;
    
    showToast('Dosya yüklendi: ' + file.name, 'success');
}

// ==================== Parse DXF ====================

async function parseDXF() {
    if (!dxfFile) {
        showToast('Dosya seçin', 'warning');
        return;
    }
    
    showLoading();
    
    const formData = new FormData();
    formData.append('file', dxfFile);
    formData.append('units', document.getElementById('dxfUnits').value);
    formData.append('scale', document.getElementById('dxfScale').value);
    
    try {
        const response = await fetch('/api/dxf/parse', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            dxfResult = result;
            dxfShapes = result.shapes || [];
            selectedLayers = result.layers || [];
            
            displayFileInfo(result.file_info);
            displayLayers(result.layers);
            displayShapes(result.shapes);
            drawPreview(result.shapes);
            updatePreviewStats(result.shapes);
            
            document.getElementById('importBtn').disabled = dxfShapes.length === 0;
            
            showToast(`Parse başarılı: ${result.total_shapes} şekil`, 'success');
        } else {
            showToast('Parse hatası: ' + (result.error || 'Bilinmeyen hata'), 'error');
        }
    } catch (error) {
        showToast('Hata: ' + error.message, 'error');
    }
    
    hideLoading();
}

function clearDXF() {
    dxfFile = null;
    dxfResult = null;
    dxfShapes = [];
    selectedLayers = [];
    
    // Reset UI
    const uploadText = document.querySelector('.upload-text h3');
    if (uploadText) {
        uploadText.textContent = 'DXF Dosyası Sürükle Bırak';
    }
    
    document.getElementById('dxfFileInput').value = '';
    document.getElementById('parseBtn').disabled = true;
    document.getElementById('importBtn').disabled = true;
    
    document.getElementById('fileInfo').innerHTML = '<div class="empty-state"><span>Dosya yüklenmedi</span></div>';
    document.getElementById('layersList').innerHTML = '<div class="empty-state"><span>Katman yok</span></div>';
    document.getElementById('shapesList').innerHTML = '<div class="empty-state"><span>Henüz şekil yok</span></div>';
    
    if (ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    
    showToast('Temizlendi', 'warning');
}

// ==================== Display Functions ====================

function displayFileInfo(fileInfo) {
    const div = document.getElementById('fileInfo');
    if (!div || !fileInfo) return;
    
    div.innerHTML = `
        <div class="file-detail">
            <div class="detail-row">
                <span class="label">Dosya:</span>
                <span class="value">${fileInfo.filename}</span>
            </div>
            <div class="detail-row">
                <span class="label">DXF Versiyon:</span>
                <span class="value">${fileInfo.dxf_version || '-'}</span>
            </div>
            <div class="detail-row">
                <span class="label">Birim:</span>
                <span class="value">${fileInfo.units}</span>
            </div>
            <div class="detail-row">
                <span class="label">Scale:</span>
                <span class="value">${fileInfo.scale}</span>
            </div>
            <div class="detail-row">
                <span class="label">Toplam Entity:</span>
                <span class="value">${fileInfo.entity_count}</span>
            </div>
            <div class="detail-row">
                <span class="label">Import Edilen:</span>
                <span class="value">${fileInfo.imported_count}</span>
            </div>
        </div>
    `;
}

function displayLayers(layers) {
    const list = document.getElementById('layersList');
    if (!list || !layers) return;
    
    list.innerHTML = layers.map(layer => `
        <div class="layer-item">
            <label class="checkbox-option">
                <input type="checkbox" value="${layer}" checked onchange="updateLayerFilter()" />
                ${layer}
            </label>
        </div>
    `).join('');
}

function displayShapes(shapes) {
    const list = document.getElementById('shapesList');
    if (!list || !shapes) return;
    
    document.getElementById('shapesCountText').textContent = shapes.length + ' şekil';
    
    list.innerHTML = shapes.map((shape, i) => `
        <div class="shape-list-item">
            <span class="shape-icon">${getShapeIcon(shape.shape_type)}</span>
            <span class="shape-info">
                <strong>${shape.shape_id}</strong><br>
                <small>${shape.shape_type} • ${shape.layer} • ${shape.points?.length || 0} nokta</small>
            </span>
            <span class="shape-perimeter">${shape.perimeter?.toFixed(1) || 0} mm</span>
        </div>
    `).join('');
}

function updatePreviewStats(shapes) {
    const totalLength = shapes.reduce((sum, s) => sum + (s.perimeter || 0), 0);
    
    document.getElementById('shapeCount').textContent = shapes.length;
    document.getElementById('totalLength').textContent = totalLength.toFixed(1) + ' mm';
}

function getShapeIcon(type) {
    const icons = {
        line: '📏',
        arc: '◡',
        circle: '⭕',
        polyline: '⬡'
    };
    return icons[type] || '◻';
}

// ==================== Canvas Drawing ====================

function drawPreview(shapes) {
    if (!ctx || !shapes) return;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Calculate bounding box
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    
    shapes.forEach(shape => {
        if (shape.points) {
            shape.points.forEach(([x, y]) => {
                minX = Math.min(minX, x);
                minY = Math.min(minY, y);
                maxX = Math.max(maxX, x);
                maxY = Math.max(maxY, y);
            });
        }
    });
    
    // Calculate scale to fit
    const padding = 40;
    const drawingWidth = maxX - minX || 1;
    const drawingHeight = maxY - minY || 1;
    
    const scaleX = (canvas.width - padding * 2) / drawingWidth;
    const scaleY = (canvas.height - padding * 2) / drawingHeight;
    scale = Math.min(scaleX, scaleY);
    
    // Calculate offset to center
    offsetX = padding - minX * scale;
    offsetY = canvas.height - padding - maxY * scale;
    
    // Draw shapes
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 1.5;
    
    shapes.forEach(shape => {
        drawShape(shape);
    });
}

function drawShape(shape) {
    if (!shape.points || shape.points.length < 2) return;
    
    ctx.beginPath();
    
    const points = shape.points;
    
    // Transform first point
    let x = offsetX + points[0][0] * scale;
    let y = offsetY + points[0][1] * scale;
    
    ctx.moveTo(x, y);
    
    // Draw lines
    for (let i = 1; i < points.length; i++) {
        x = offsetX + points[i][0] * scale;
        y = offsetY + points[i][1] * scale;
        ctx.lineTo(x, y);
    }
    
    // Close shape if needed
    if (shape.shape_type === 'circle' || shape.shape_type === 'polyline') {
        ctx.closePath();
    }
    
    ctx.stroke();
}

// ==================== Zoom Controls ====================

function zoomIn() {
    scale *= 1.2;
    redrawCanvas();
}

function zoomOut() {
    scale *= 0.8;
    redrawCanvas();
}

function resetZoom() {
    if (dxfShapes) {
        drawPreview(dxfShapes);
    }
}

function fitToScreen() {
    if (dxfShapes) {
        drawPreview(dxfShapes);
    }
}

function redrawCanvas() {
    if (!ctx || !dxfShapes) return;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 1.5;
    
    dxfShapes.forEach(shape => {
        if (!shape.points) return;
        
        ctx.beginPath();
        const points = shape.points;
        
        let x = offsetX + points[0][0] * scale;
        let y = offsetY + points[0][1] * scale;
        ctx.moveTo(x, y);
        
        for (let i = 1; i < points.length; i++) {
            x = offsetX + points[i][0] * scale;
            y = offsetY + points[i][1] * scale;
            ctx.lineTo(x, y);
        }
        
        if (shape.shape_type === 'circle' || shape.shape_type === 'polyline') {
            ctx.closePath();
        }
        
        ctx.stroke();
    });
}

// ==================== Layer Filter ====================

function toggleAllLayers() {
    const selectAll = document.getElementById('selectAllLayers');
    const checkboxes = document.querySelectorAll('#layersList input[type="checkbox"]');
    
    checkboxes.forEach(cb => {
        cb.checked = selectAll.checked;
    });
    
    updateLayerFilter();
}

function updateLayerFilter() {
    // This would filter shapes based on selected layers
    // For now, just update the preview
    if (dxfShapes) {
        drawPreview(dxfShapes);
    }
}

// ==================== Import to Shapes ====================

async function importToShapes() {
    if (!dxfShapes || dxfShapes.length === 0) {
        showToast('Şekil yok', 'warning');
        return;
    }
    
    showLoading();
    
    const importData = {
        shapes: dxfShapes,
        placement: document.getElementById('importPlacement').value,
        offset_x: parseFloat(document.getElementById('importOffsetX').value),
        offset_y: parseFloat(document.getElementById('importOffsetY').value),
        grinding_allowance: document.getElementById('importGrinding').value
    };
    
    try {
        const response = await fetch('/api/dxf/import', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(importData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(`${result.imported_count} şekil aktarıldı`, 'success');
            
            // Redirect to shapes page
            setTimeout(() => {
                window.location.href = '/shapes';
            }, 1000);
        } else {
            showToast('Import hatası: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Hata: ' + error.message, 'error');
    }
    
    hideLoading();
}