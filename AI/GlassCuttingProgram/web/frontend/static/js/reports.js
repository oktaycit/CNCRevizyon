/**
 * Reports & Analytics - JavaScript
 * Generate and export reports
 */

let currentReport = null;
let utilizationChart = null;
let wasteChart = null;

// ==================== Initialization ====================

function initReports() {
    // Set default dates
    const today = new Date();
    document.getElementById('startDate').valueAsDate = today;
    document.getElementById('endDate').valueAsDate = today;
    
    // Load report history
    loadReportHistory();
}

// ==================== Report Generation ====================

function selectReportType(type) {
    // Update active button
    document.querySelectorAll('.report-type-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Update date range based on type
    const today = new Date();
    let start = new Date();
    
    if (type === 'daily') {
        start = today;
    } else if (type === 'weekly') {
        start = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    } else if (type === 'monthly') {
        start = new Date(today.getFullYear(), today.getMonth(), 1);
    }
    
    document.getElementById('startDate').valueAsDate = start;
    document.getElementById('endDate').valueAsDate = today;
}

async function generateReport() {
    showLoading();
    
    const reportType = document.querySelector('.report-type-btn.active')?.textContent?.trim() || 'daily';
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    const requestData = {
        type: getReportTypeKey(reportType),
        start_date: startDate,
        end_date: endDate
    };
    
    try {
        const response = await fetch('/api/reports/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentReport = result.report;
            displayReport(result.report);
            showToast('Rapor oluşturuldu', 'success');
        } else {
            showToast('Hata: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Hata: ' + error.message, 'error');
    }
    
    hideLoading();
}

function getReportTypeKey(text) {
    const types = {
        '📅 Günlük': 'daily',
        '📆 Haftalık': 'weekly',
        '📆 Aylık': 'monthly',
        '♻️ Fire Analizi': 'waste',
        '📋 Sipariş Durumu': 'orders'
    };
    return types[text] || 'daily';
}

function displayReport(report) {
    const summaryDiv = document.getElementById('reportSummary');
    if (!summaryDiv) return;
    
    summaryDiv.innerHTML = `
        <h3>${report.title}</h3>
        <div class="summary-grid">
            ${Object.entries(report.summary).map(([key, value]) => `
                <div class="summary-item">
                    <span class="summary-label">${formatLabel(key)}</span>
                    <span class="summary-value">${formatValue(key, value)}</span>
                </div>
            `).join('')}
        </div>
    `;
    
    // Update charts
    updateCharts(report.data);
}

function formatLabel(key) {
    return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatValue(key, value) {
    if (typeof value === 'number') {
        if (key.includes('utilization') || key.includes('efficiency')) {
            return (value * 100).toFixed(1) + '%';
        } else if (key.includes('waste') || key.includes('area')) {
            return (value / 1000000).toFixed(2) + ' m²';
        } else if (key.includes('time')) {
            return value.toFixed(0) + ' dk';
        } else {
            return value.toLocaleString('tr-TR');
        }
    }
    return value;
}

// ==================== Export ====================

async function exportReport(format) {
    if (!currentReport) {
        showToast('Önce rapor oluşturun', 'warning');
        return;
    }
    
    showLoading();
    
    const requestData = {
        type: currentReport.type
    };
    
    try {
        const response = await fetch(`/api/reports/export/${format}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Download file
            window.open(result.download_url, '_blank');
            showToast(`${format.toUpperCase()} olarak indirildi`, 'success');
        } else {
            showToast('Hata: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Hata: ' + error.message, 'error');
    }
    
    hideLoading();
}

// ==================== Charts ====================

function updateCharts(data) {
    // Utilization chart
    const utilCtx = document.getElementById('utilizationChart');
    if (utilCtx) {
        if (utilizationChart) {
            utilizationChart.destroy();
        }
        
        utilizationChart = new Chart(utilCtx, {
            type: 'bar',
            data: {
                labels: data.orders?.map(o => o.order_id) || [],
                datasets: [{
                    label: 'Utilization',
                    data: data.orders?.map(o => o.utilization * 100) || [],
                    backgroundColor: 'rgba(59, 130, 246, 0.5)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Utilization %'
                        }
                    }
                }
            }
        });
    }
    
    // Waste chart
    const wasteCtx = document.getElementById('wasteChart');
    if (wasteCtx) {
        if (wasteChart) {
            wasteChart.destroy();
        }
        
        wasteChart = new Chart(wasteCtx, {
            type: 'pie',
            data: {
                labels: ['Kullanılan', 'Fire'],
                datasets: [{
                    data: [
                        (data.avg_utilization || 0) * 100,
                        (1 - (data.avg_utilization || 0)) * 100
                    ],
                    backgroundColor: [
                        'rgba(34, 197, 94, 0.5)',
                        'rgba(239, 68, 68, 0.5)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// ==================== Report History ====================

async function loadReportHistory() {
    // TODO: Implement API endpoint for history
    const historyDiv = document.getElementById('reportHistory');
    if (!historyDiv) return;
    
    // Sample history
    historyDiv.innerHTML = `
        <div class="history-item">
            <span class="history-icon">📄</span>
            <span class="history-info">
                <strong>Günlük Rapor</strong><br>
                <small>${new Date().toLocaleDateString('tr-TR')}</small>
            </span>
            <button class="btn small" onclick="downloadHistory()">⬇️</button>
        </div>
    `;
}

function downloadHistory() {
    showToast('İndiriliyor...', 'info');
}