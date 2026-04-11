/**
 * WebSocket Client
 * Real-time machine status and notifications
 */

// WebSocket connection
let socket = null;
let isConnected = false;
let subscribedChannels = new Set();

// Machine state
let machineState = {
    status: 'idle',
    position: { x: 0, y: 0, z: 0 },
    progress: 0,
    currentOrder: null,
    currentJob: null,
    alarms: []
};

// Callbacks
const callbacks = {
    connect: [],
    disconnect: [],
    machine_status: [],
    position_update: [],
    progress_update: [],
    alarm: [],
    queue_update: [],
    order_update: [],
    blade_alert: [],
    cut_complete: []
};

// ==================== Connection ====================

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/socket.io/?EIO=4&transport=websocket`;
    
    console.log('Connecting to WebSocket:', wsUrl);
    
    // Use Socket.IO client if available, otherwise use native WebSocket
    if (typeof io !== 'undefined') {
        socket = io(window.location.origin, {
            transports: ['websocket', 'polling']
        });
        
        setupSocketIOListeners();
    } else {
        // Fallback to native WebSocket
        socket = new WebSocket(wsUrl);
        setupNativeWebSocketListeners();
    }
}

function setupSocketIOListeners() {
    socket.on('connect', () => {
        console.log('WebSocket connected');
        isConnected = true;
        triggerCallback('connect', { type: 'socketio' });
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', () => {
        console.log('WebSocket disconnected');
        isConnected = false;
        triggerCallback('disconnect', {});
        updateConnectionStatus(false);
    });
    
    socket.on('message', (data) => {
        handleMessage(data);
    });
    
    // Socket.IO specific events
    socket.on('machine_status', (data) => {
        machineState = { ...machineState, ...data };
        triggerCallback('machine_status', data);
    });
    
    socket.on('position_update', (data) => {
        machineState.position = data;
        triggerCallback('position_update', data);
    });
    
    socket.on('progress_update', (data) => {
        machineState.progress = data.progress;
        triggerCallback('progress_update', data);
    });
    
    socket.on('alarm', (data) => {
        machineState.alarms.push(data);
        triggerCallback('alarm', data);
        showAlarmNotification(data);
    });
    
    socket.on('queue_update', (data) => {
        triggerCallback('queue_update', data);
    });
    
    socket.on('order_update', (data) => {
        triggerCallback('order_update', data);
    });
    
    socket.on('blade_alert', (data) => {
        triggerCallback('blade_alert', data);
    });
    
    socket.on('cut_complete', (data) => {
        triggerCallback('cut_complete', data);
    });
}

function setupNativeWebSocketListeners() {
    socket.onopen = () => {
        console.log('WebSocket connected');
        isConnected = true;
        triggerCallback('connect', { type: 'native' });
        updateConnectionStatus(true);
    };
    
    socket.onclose = () => {
        console.log('WebSocket disconnected');
        isConnected = false;
        triggerCallback('disconnect', {});
        updateConnectionStatus(false);
        
        // Auto-reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
    };
    
    socket.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
    
    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            handleMessage(data);
        } catch (error) {
            console.error('Error parsing message:', error);
        }
    };
}

function handleMessage(data) {
    const type = data.type;
    const payload = data.data;
    
    if (callbacks[type]) {
        triggerCallback(type, payload);
    }
    
    // Update machine state
    switch (type) {
        case 'machine_status':
            machineState = { ...machineState, ...payload };
            break;
        case 'position_update':
            machineState.position = payload;
            break;
        case 'progress_update':
            machineState.progress = payload.progress;
            break;
        case 'alarm':
            machineState.alarms.push(payload);
            break;
    }
}

// ==================== Callbacks ====================

function on(event, callback) {
    if (callbacks[event]) {
        callbacks[event].push(callback);
    }
    return () => off(event, callback);
}

function off(event, callback) {
    if (callbacks[event]) {
        callbacks[event] = callbacks[event].filter(cb => cb !== callback);
    }
}

function triggerCallback(event, data) {
    if (callbacks[event]) {
        callbacks[event].forEach(cb => {
            try {
                cb(data);
            } catch (error) {
                console.error('Error in callback:', error);
            }
        });
    }
}

// ==================== Subscription ====================

function subscribe(channel) {
    if (socket && socket.emit) {
        socket.emit('subscribe', { channel });
        subscribedChannels.add(channel);
    }
}

function unsubscribe(channel) {
    if (socket && socket.emit) {
        socket.emit('unsubscribe', { channel });
        subscribedChannels.delete(channel);
    }
}

function subscribeToAll() {
    ['machine', 'progress', 'alarms', 'queue', 'orders', 'blades'].forEach(subscribe);
}

// ==================== UI Updates ====================

function updateConnectionStatus(connected) {
    const indicator = document.getElementById('wsStatusIndicator');
    const text = document.getElementById('wsStatusText');
    
    if (indicator) {
        indicator.className = connected ? 'status-connected' : 'status-disconnected';
    }
    
    if (text) {
        text.textContent = connected ? 'Connected' : 'Disconnected';
    }
}

function showAlarmNotification(alarm) {
    const toast = document.createElement('div');
    toast.className = `toast ${alarm.severity || 'error'}`;
    toast.innerHTML = `
        <strong>⚠️ Alarm ${alarm.code}</strong><br>
        ${alarm.message}
    `;
    
    const container = document.getElementById('toastContainer');
    if (container) {
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 5000);
    }
}

// ==================== Machine State ====================

function getMachineState() {
    return { ...machineState };
}

function getPosition() {
    return machineState.position;
}

function getProgress() {
    return machineState.progress;
}

function getCurrentOrder() {
    return machineState.currentOrder;
}

function getAlarms() {
    return machineState.alarms;
}

function clearAlarms() {
    machineState.alarms = [];
}

// ==================== Display Functions ====================

function updateMachineDisplay(data) {
    // Position display
    const posX = document.getElementById('machineX');
    const posY = document.getElementById('machineY');
    const posZ = document.getElementById('machineZ');
    
    if (posX) posX.textContent = data.x?.toFixed(2) || '0.00';
    if (posY) posY.textContent = data.y?.toFixed(2) || '0.00';
    if (posZ) posZ.textContent = data.z?.toFixed(2) || '0.00';
    
    // Status display
    const statusEl = document.getElementById('machineStatus');
    if (statusEl && data.status) {
        statusEl.className = `status-indicator ${data.status}`;
    }
    
    // Progress display
    const progressEl = document.getElementById('cuttingProgress');
    if (progressEl) {
        progressEl.style.width = `${data.progress || 0}%`;
    }
}

// ==================== Initialization ====================

function initWebSocket() {
    connectWebSocket();
    
    // Subscribe to all channels after connection
    setTimeout(subscribeToAll, 1000);
    
    console.log('WebSocket client initialized');
}

// Export for use in other scripts
window.ws = {
    connect: connectWebSocket,
    on: on,
    off: off,
    subscribe: subscribe,
    unsubscribe: unsubscribe,
    getState: getMachineState,
    getPosition: getPosition,
    getProgress: getProgress,
    getAlarms: getAlarms,
    clearAlarms: clearAlarms,
    init: initWebSocket
};