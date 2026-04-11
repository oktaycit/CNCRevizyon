/**
 * Shape Cutting - JavaScript
 * Non-rectangular shape cutting
 */

// Shape state
let currentShapes = [];
let customPoints = [];
let shapeCanvas = null;
let shapeCtx = null;
let shapeScale = 0.1;

// Preview canvas
let previewCanvas = null;
let previewCtx = null;

// ==================== Initialization ====================

function initShapeCanvas() {
    shapeCanvas = document.getElementById('shapeCanvas');
    if (shapeCanvas) {
        shapeCtx = shapeCanvas.getContext('2d');
        drawShapeCanvas();
    }

    previewCanvas = document.getElementById('previewCanvas');
    if (previewCanvas) {
        previewCtx = previewCanvas.getContext('2d');
    }
}

// ==================== Shape Selection ====================

function selectShape(shapeType) {
    // Remove active from all buttons
    document.querySelectorAll('.shape-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Add active to clicked button
    event.target.classList.add('active');

    // Hide all param groups
    document.querySelectorAll('.param-group').forEach(el => {
        el.style.display = 'none';
    });

    // Show selected
    const paramDiv = document.getElementById(shapeType + 'Params');
    if (paramDiv) {
        paramDiv.style.display = 'block';
    }

    // Update preview
    drawPreview(shapeType);
}

// ==================== Preview Drawing ====================

function drawPreview(shapeType) {
    if (!previewCtx) return;

    const w = previewCanvas.width;
    const h = previewCanvas.height;
    const cx = w / 2;
    const cy = h / 2;

    // Clear
    previewCtx.clearRect(0, 0, w, h);
    previewCtx.fillStyle = '#334155';
    previewCtx.fillRect(0, 0, w, h);

    previewCtx.strokeStyle = '#3b82f6';
    previewCtx.lineWidth = 2;
    previewCtx.beginPath();

    if (shapeType === 'circle') {
        previewCtx.arc(cx, cy, 80, 0, Math.PI * 2);
    } else if (shapeType === 'polygon') {
        const sides = parseInt(document.getElementById('polySides')?.value || 6);
        const radius = 80;
        for (let i = 0; i <= sides; i++) {
            const angle = (i * 2 * Math.PI / sides) - Math.PI / 2;
            const x = cx + radius * Math.cos(angle);
            const y = cy + radius * Math.sin(angle);
            if (i === 0) previewCtx.moveTo(x, y);
            else previewCtx.lineTo(x, y);
        }
    } else if (shapeType === 'arc') {
        const startAngle = 0;
        const endAngle = Math.PI / 2;
        previewCtx.arc(cx, cy, 80, startAngle, endAngle);
    } else if (shapeType === 'custom') {
        // Draw custom points
        customPoints.forEach((pt, i) => {
            const x = cx + pt[0] * 0.5;
            const y = cy + pt[1] * 0.5;
            if (i === 0) previewCtx.moveTo(x, y);
            else previewCtx.lineTo(x, y);
        });
        if (customPoints.length > 0) previewCtx.closePath();
    }

    previewCtx.stroke();
}

// ==================== Custom Points ====================

function addCustomPoint() {
    const dx = parseFloat(document.getElementById('customDx')?.value || 0);
    const dy = parseFloat(document.getElementById('customDy')?.value || 0);

    if (dx === 0 && dy === 0) {
        showToast('Nokta koordinatları girin', 'warning');
        return;
    }

    customPoints.push([dx, dy]);

    // Update list
    const list = document.getElementById('customPointsList');
    if (list) {
        list.innerHTML = customPoints.map((pt, i) => `
            <div class="point-item">
                <span>P${i + 1}: (${pt[0]}, ${pt[1]})</span>
                <button class="btn small danger" onclick="removeCustomPoint(${i})">🗑️</button>
            </div>
        `).join('');
    }

    // Clear inputs
    document.getElementById('customDx').value = '';
    document.getElementById('customDy').value = '';

    // Update preview
    drawPreview('custom');
}

function removeCustomPoint(index) {
    customPoints.splice(index, 1);
    addCustomPoint(); // Refresh list (hack)
    const list = document.getElementById('customPointsList');
    if (list && customPoints.length === 0) {
        list.innerHTML = '<div class="empty-state">Nokta yok</div>';
    }
}

// ==================== Shape Generation ====================

function generateShape() {
    showLoading();

    const shapeType = document.querySelector('.shape-btn.active')?.textContent || 'circle';

    let shape = null;

    if (shapeType.includes('Daire')) {
        shape = {
            type: 'circle',
            id: 'C' + (currentShapes.length + 1),
            x: parseFloat(document.getElementById('circleX')?.value || 3000),
            y: parseFloat(document.getElementById('circleY')?.value || 1500),
            radius: parseFloat(document.getElementById('circleRadius')?.value || 500)
        };
    } else if (shapeType.includes('Çokgen')) {
        shape = {
            type: 'polygon',
            id: 'P' + (currentShapes.length + 1),
            x: parseFloat(document.getElementById('polyX')?.value || 1500),
            y: parseFloat(document.getElementById('polyY')?.value || 1500),
            radius: parseFloat(document.getElementById('polyRadius')?.value || 400),
            sides: parseInt(document.getElementById('polySides')?.value || 6)
        };
    } else if (shapeType.includes('Yay')) {
        shape = {
            type: 'arc',
            id: 'A' + (currentShapes.length + 1),
            x: parseFloat(document.getElementById('arcX')?.value || 3000),
            y: parseFloat(document.getElementById('arcY')?.value || 2500),
            radius: parseFloat(document.getElementById('arcRadius')?.value || 600),
            startAngle: parseFloat(document.getElementById('arcStart')?.value || 0),
            endAngle: parseFloat(document.getElementById('arcEnd')?.value || 90),
            direction: document.getElementById('arcDirection')?.value || 'cw'
        };
    } else if (shapeType.includes('Özel')) {
        shape = {
            type: 'custom',
            id: 'S' + (currentShapes.length + 1),
            baseX: parseFloat(document.getElementById('customBaseX')?.value || 0),
            baseY: parseFloat(document.getElementById('customBaseY')?.value || 0),
            points: [...customPoints]
        };
    }

    if (shape) {
        currentShapes.push(shape);
        updateShapesList();
        drawShapeCanvas();
        updateShapeStats();
        showToast('Şekil oluşturuldu', 'success');
    }

    hideLoading();
}

function clearShape() {
    currentShapes = [];
    customPoints = [];
    updateShapesList();
    drawShapeCanvas();
    updateShapeStats();
    showToast('Temizlendi', 'warning');
}

// ==================== Shapes List ====================

function updateShapesList() {
    const list = document.getElementById('shapesList');
    if (!list) return;

    if (currentShapes.length === 0) {
        list.innerHTML = '<div class="empty-state"><span>Henüz şekil oluşturulmadı</span></div>';
        return;
    }

    list.innerHTML = currentShapes.map((shape, i) => `
        <div class="shape-item">
            <span class="shape-icon">${getShapeIcon(shape.type)}</span>
            <span class="shape-info">
                ${shape.id} - ${shape.type} 
                (${shape.x}, ${shape.y})
            </span>
            <button class="btn small danger" onclick="removeShape(${i})">🗑️</button>
        </div>
    `).join('');
}

function removeShape(index) {
    currentShapes.splice(index, 1);
    updateShapesList();
    drawShapeCanvas();
    updateShapeStats();
}

function getShapeIcon(type) {
    const icons = {
        circle: '⭕',
        polygon: '⬡',
        arc: '◡',
        custom: '✏️'
    };
    return icons[type] || '◻';
}

// ==================== Canvas Drawing ====================

function drawShapeCanvas() {
    if (!shapeCtx) return;

    const w = shapeCanvas.width;
    const h = shapeCanvas.height;

    // Clear
    shapeCtx.clearRect(0, 0, w, h);
    shapeCtx.fillStyle = '#334155';
    shapeCtx.fillRect(0, 0, w, h);

    // Draw sheet border
    shapeCtx.strokeStyle = '#3b82f6';
    shapeCtx.lineWidth = 2;
    shapeCtx.strokeRect(0, 0, w, h);

    // Draw shapes
    currentShapes.forEach(shape => {
        drawShape(shape);
    });
}

function drawShape(shape) {
    if (!shapeCtx) return;

    const w = shapeCanvas.width;
    const h = shapeCanvas.height;

    // Scale to fit
    const scaleX = w / 6000;
    const scaleY = h / 3000;
    const scale = Math.min(scaleX, scaleY);

    const x = shape.x * scale;
    const y = (3000 - shape.y) * scale; // Flip Y

    shapeCtx.strokeStyle = '#22c55e';
    shapeCtx.lineWidth = 2;
    shapeCtx.beginPath();

    if (shape.type === 'circle') {
        shapeCtx.arc(x, y, shape.radius * scale, 0, Math.PI * 2);
    } else if (shape.type === 'polygon') {
        const r = shape.radius * scale;
        for (let i = 0; i <= shape.sides; i++) {
            const angle = (i * 2 * Math.PI / shape.sides) - Math.PI / 2;
            const px = x + r * Math.cos(angle);
            const py = y + r * Math.sin(angle);
            if (i === 0) shapeCtx.moveTo(px, py);
            else shapeCtx.lineTo(px, py);
        }
    } else if (shape.type === 'arc') {
        const startRad = shape.startAngle * Math.PI / 180;
        const endRad = shape.endAngle * Math.PI / 180;
        const r = shape.radius * scale;
        shapeCtx.arc(x, y, r, startRad, endRad, shape.direction !== 'cw');
    } else if (shape.type === 'custom') {
        shape.points.forEach((pt, i) => {
            const px = (shape.baseX + pt[0]) * scale;
            const py = (3000 - shape.baseY - pt[1]) * scale;
            if (i === 0) shapeCtx.moveTo(px, py);
            else shapeCtx.lineTo(px, py);
        });
        if (shape.points.length > 1) shapeCtx.closePath();
    }

    shapeCtx.stroke();

    // Draw label
    shapeCtx.fillStyle = '#f8fafc';
    shapeCtx.font = '12px Arial';
    shapeCtx.fillText(shape.id, x + 5, y - 5);
}

// ==================== Stats ====================

function updateShapeStats() {
    const totalEl = document.getElementById('totalShapes');
    const perimeterEl = document.getElementById('totalPerimeter');

    if (totalEl) totalEl.textContent = currentShapes.length;

    if (perimeterEl) {
        let total = 0;
        currentShapes.forEach(shape => {
            if (shape.type === 'circle') {
                total += 2 * Math.PI * shape.radius;
            } else if (shape.type === 'polygon') {
                // Approximate
                total += shape.sides * shape.radius * 2 * Math.sin(Math.PI / shape.sides);
            } else if (shape.type === 'arc') {
                const angle = Math.abs(shape.endAngle - shape.startAngle) * Math.PI / 180;
                total += shape.radius * angle;
            }
        });
        perimeterEl.textContent = total.toFixed(0) + ' mm';
    }
}

// ==================== Zoom Controls ====================

function zoomInShape() {
    shapeScale *= 1.2;
    drawShapeCanvas();
}

function zoomOutShape() {
    shapeScale *= 0.8;
    drawShapeCanvas();
}

function resetShapeZoom() {
    shapeScale = 0.1;
    drawShapeCanvas();
}

// ==================== G-Code Generation ====================

function generateGcodeForShapes() {
    showLoading();

    // TODO: Call API to generate G-code for shapes
    showToast('G-Code oluşturuluyor...', 'success');

    setTimeout(() => {
        hideLoading();
        showToast('G-Code hazır!', 'success');
        window.location.href = '/gcode';
    }, 1000);
}

function downloadGcode() {
    window.open('/api/gcode/download', '_blank');
    showToast('G-code indiriliyor', 'success');
}