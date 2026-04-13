#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
"""
WebSocket Module
Real-time machine status and notifications for glass cutting program

Features:
- Live machine position streaming
- Cutting progress updates
- Alarm notifications
- Queue status updates
- Order status changes
- Blade life alerts
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Set, Optional, Any
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    WebSocketServerProtocol = Any
    print("Warning: websockets not installed. Run: pip install websockets")

try:
    from flask_socketio import SocketIO, emit, join_room, leave_room
    FLASK_SOCKETIO_AVAILABLE = True
except ImportError:
    FLASK_SOCKETIO_AVAILABLE = False
    print("Warning: flask-socketio not installed. Run: pip install flask-socketio")


class MessageType(Enum):
    """WebSocket message types"""
    MACHINE_STATUS = "machine_status"
    POSITION_UPDATE = "position_update"
    PROGRESS_UPDATE = "progress_update"
    ALARM = "alarm"
    QUEUE_UPDATE = "queue_update"
    ORDER_UPDATE = "order_update"
    BLADE_ALERT = "blade_alert"
    CUT_COMPLETE = "cut_complete"
    SYSTEM_STATUS = "system_status"


@dataclass
class MachinePosition:
    """Machine position data"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    velocity: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "velocity": self.velocity,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class MachineStatus:
    """Machine status data"""
    status: str = "idle"  # idle, running, paused, alarm, estop
    mode: str = "auto"  # auto, manual, jog
    position: MachinePosition = field(default_factory=MachinePosition)
    current_order: Optional[str] = None
    current_job: Optional[str] = None
    progress: float = 0.0  # 0-100%
    cutting_speed: float = 0.0  # mm/min
    spindle_speed: float = 0.0  # RPM
    alarms: list = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "status": self.status,
            "mode": self.mode,
            "position": self.position.to_dict(),
            "current_order": self.current_order,
            "current_job": self.current_job,
            "progress": self.progress,
            "cutting_speed": self.cutting_speed,
            "spindle_speed": self.spindle_speed,
            "alarms": self.alarms,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class WebSocketMessage:
    """WebSocket message structure"""
    type: MessageType
    data: Dict
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_json(self) -> str:
        return json.dumps({
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        })


class WebSocketManager:
    """Manage WebSocket connections and messages"""
    
    def __init__(self):
        self.clients: Set[WebSocketServerProtocol] = set()
        self.rooms: Dict[str, Set[WebSocketServerProtocol]] = {}
        self.machine_status = MachineStatus()
        self.message_history: list = []
        self.max_history = 100
        
        # Subscriptions
        self.subscriptions: Dict[WebSocketServerProtocol, Set[str]] = {}
    
    async def register(self, websocket: WebSocketServerProtocol):
        """Register new client"""
        self.clients.add(websocket)
        self.subscriptions[websocket] = set()
        print(f"Client connected: {websocket.remote_address}")
        
        # Send current status
        await self.send_current_status(websocket)
    
    async def unregister(self, websocket: WebSocketServerProtocol):
        """Unregister client"""
        self.clients.discard(websocket)
        self.subscriptions.pop(websocket, None)
        
        # Remove from all rooms
        for room_clients in self.rooms.values():
            room_clients.discard(websocket)
        
        print(f"Client disconnected: {websocket.remote_address}")
    
    async def subscribe(self, websocket: WebSocketServerProtocol, channel: str):
        """Subscribe to channel"""
        self.subscriptions[websocket].add(channel)
        
        if channel not in self.rooms:
            self.rooms[channel] = set()
        self.rooms[channel].add(websocket)
        
        print(f"Client {websocket.remote_address} subscribed to {channel}")
    
    async def unsubscribe(self, websocket: WebSocketServerProtocol, channel: str):
        """Unsubscribe from channel"""
        self.subscriptions[websocket].discard(channel)
        
        if channel in self.rooms:
            self.rooms[channel].discard(websocket)
    
    async def broadcast(self, message: WebSocketMessage, channel: Optional[str] = None):
        """Broadcast message to clients"""
        message_json = message.to_json()
        
        # Store in history
        self.message_history.append({
            "type": message.type.value,
            "data": message.data,
            "timestamp": message.timestamp.isoformat()
        })
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)
        
        if channel and channel in self.rooms:
            # Send to room subscribers
            clients = self.rooms[channel]
        else:
            # Send to all clients
            clients = self.clients
        
        # Send messages
        if clients:
            await asyncio.gather(
                *[client.send(message_json) for client in clients],
                return_exceptions=True
            )
    
    async def send_to_client(self, websocket: WebSocketServerProtocol, message: WebSocketMessage):
        """Send message to specific client"""
        try:
            await websocket.send(message.to_json())
        except Exception as e:
            print(f"Error sending message: {e}")
    
    async def send_current_status(self, websocket: WebSocketServerProtocol):
        """Send current machine status to client"""
        message = WebSocketMessage(
            type=MessageType.SYSTEM_STATUS,
            data={
                "machine_status": self.machine_status.to_dict(),
                "connected_clients": len(self.clients),
                "available_channels": list(self.rooms.keys())
            }
        )
        await self.send_to_client(websocket, message)
    
    # Convenience methods for specific message types
    
    async def update_position(self, x: float, y: float, z: float, velocity: float = 0.0):
        """Update machine position"""
        self.machine_status.position = MachinePosition(
            x=x, y=y, z=z, velocity=velocity
        )
        
        message = WebSocketMessage(
            type=MessageType.POSITION_UPDATE,
            data=self.machine_status.position.to_dict()
        )
        await self.broadcast(message, "machine")
    
    async def update_status(self, status: str, **kwargs):
        """Update machine status"""
        self.machine_status.status = status
        self.machine_status.timestamp = datetime.now()
        
        for key, value in kwargs.items():
            if hasattr(self.machine_status, key):
                setattr(self.machine_status, key, value)
        
        message = WebSocketMessage(
            type=MessageType.MACHINE_STATUS,
            data=self.machine_status.to_dict()
        )
        await self.broadcast(message, "machine")
    
    async def update_progress(self, progress: float, current_order: str = None):
        """Update cutting progress"""
        self.machine_status.progress = progress
        if current_order:
            self.machine_status.current_order = current_order
        
        message = WebSocketMessage(
            type=MessageType.PROGRESS_UPDATE,
            data={
                "progress": progress,
                "current_order": current_order,
                "timestamp": datetime.now().isoformat()
            }
        )
        await self.broadcast(message, "progress")
    
    async def send_alarm(self, alarm_code: int, message_text: str, severity: str = "error"):
        """Send alarm notification"""
        alarm = {
            "code": alarm_code,
            "message": message_text,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }
        
        self.machine_status.alarms.append(alarm)
        
        message = WebSocketMessage(
            type=MessageType.ALARM,
            data=alarm
        )
        await self.broadcast(message, "alarms")
    
    async def clear_alarm(self, alarm_code: int):
        """Clear alarm"""
        self.machine_status.alarms = [
            a for a in self.machine_status.alarms if a.get('code') != alarm_code
        ]
        
        message = WebSocketMessage(
            type=MessageType.ALARM,
            data={
                "cleared_code": alarm_code,
                "timestamp": datetime.now().isoformat()
            }
        )
        await self.broadcast(message, "alarms")
    
    async def update_queue(self, queue_status: Dict):
        """Update queue status"""
        message = WebSocketMessage(
            type=MessageType.QUEUE_UPDATE,
            data=queue_status
        )
        await self.broadcast(message, "queue")
    
    async def update_order(self, order_id: str, status: str, **kwargs):
        """Update order status"""
        message = WebSocketMessage(
            type=MessageType.ORDER_UPDATE,
            data={
                "order_id": order_id,
                "status": status,
                **kwargs
            }
        )
        await self.broadcast(message, "orders")
    
    async def blade_alert(self, blade_id: str, life_remaining: float, action: str = "warning"):
        """Send blade life alert"""
        message = WebSocketMessage(
            type=MessageType.BLADE_ALERT,
            data={
                "blade_id": blade_id,
                "life_remaining": life_remaining,
                "action": action,
                "timestamp": datetime.now().isoformat()
            }
        )
        await self.broadcast(message, "blades")
    
    async def cut_complete(self, order_id: str, job_id: str, actual_time: float):
        """Notify cut completion"""
        message = WebSocketMessage(
            type=MessageType.CUT_COMPLETE,
            data={
                "order_id": order_id,
                "job_id": job_id,
                "actual_time": actual_time,
                "completed_at": datetime.now().isoformat()
            }
        )
        await self.broadcast(message, "orders")


# Global WebSocket manager instance
ws_manager = WebSocketManager()


# Flask-SocketIO integration (if using Flask)
socketio = None

def init_socketio(app):
    """Initialize Flask-SocketIO"""
    global socketio
    
    if not FLASK_SOCKETIO_AVAILABLE:
        print("Flask-SocketIO not available")
        return None
    
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
    
    @socketio.on('connect')
    def handle_connect():
        print(f"Client connected: {request.sid}")
        emit('status', {'message': 'Connected'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"Client disconnected: {request.sid}")
    
    @socketio.on('subscribe')
    def handle_subscribe(data):
        channel = data.get('channel')
        if channel:
            join_room(channel)
            print(f"Client {request.sid} joined {channel}")
    
    @socketio.on('unsubscribe')
    def handle_unsubscribe(data):
        channel = data.get('channel')
        if channel:
            leave_room(channel)
    
    return socketio


def simulate_machine_data():
    """Simulate machine data for testing"""
    import random
    
    return {
        "x": random.uniform(0, 6000),
        "y": random.uniform(0, 3000),
        "z": random.uniform(0, 100),
        "velocity": random.uniform(0, 80000),
        "status": random.choice(["idle", "running", "paused"]),
        "progress": random.uniform(0, 100)
    }


async def demo():
    """Demo WebSocket server"""
    print("=" * 60)
    print("WebSocket Demo Server")
    print("=" * 60)
    
    if not WEBSOCKETS_AVAILABLE:
        print("\n❌ websockets not installed!")
        print("   Run: pip install websockets")
        return
    
    async def handler(websocket: WebSocketServerProtocol, path):
        await ws_manager.register(websocket)
        try:
            async for message in websocket:
                data = json.loads(message)
                print(f"Received: {data}")
                
                # Handle message
                if data.get('action') == 'subscribe':
                    await ws_manager.subscribe(websocket, data.get('channel'))
                elif data.get('action') == 'unsubscribe':
                    await ws_manager.unsubscribe(websocket, data.get('channel'))
        finally:
            await ws_manager.unregister(websocket)
    
    print("\n🚀 Starting WebSocket server...")
    print("   ws://localhost:8765")
    print("\n📡 Available channels:")
    print("   - machine")
    print("   - progress")
    print("   - alarms")
    print("   - queue")
    print("   - orders")
    print("   - blades")
    
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(demo())
