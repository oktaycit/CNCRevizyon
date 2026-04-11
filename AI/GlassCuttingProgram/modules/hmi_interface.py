#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HMI Interface Module
Delta DOP-110CS HMI Integration for Glass Cutting Program

Features:
- Order input interface
- Parameter display
- Status monitoring
- Alarm handling
- Data exchange with NC300

Note: This is a data structure module. Actual HMI programming
requires Delta Screen Editor software.
"""

import json
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class HMIPage(Enum):
    """HMI screen pages"""
    MAIN = "main"
    ORDER_INPUT = "order_input"
    PARAMETER = "parameter"
    OPTIMIZATION = "optimization"
    CUTTING = "cutting"
    ALARM = "alarm"
    MANUAL = "manual"
    SETTINGS = "settings"


class MachineStatus(Enum):
    """Machine status states"""
    IDLE = "idle"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    ALARM = "alarm"
    ESTOP = "estop"
    MAINTENANCE = "maintenance"


@dataclass
class HMIOrderEntry:
    """Order entry from HMI"""
    order_id: str
    width: float  # mm
    height: float  # mm
    quantity: int
    thickness: float  # mm
    glass_type: str  # float, laminated, tempered
    priority: int  # 1-3
    customer: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class HMIStatusData:
    """Machine status data for HMI display"""
    status: MachineStatus
    current_x: float  # mm
    current_y: float  # mm
    current_z: float  # mm
    cutting_speed: float  # mm/min
    parts_completed: int
    parts_remaining: int
    estimated_time_remaining: float  # minutes
    utilization: float  # %
    alarms: List[Dict] = field(default_factory=list)
    last_update: datetime = field(default_factory=datetime.now)


@dataclass
class HMIParameterData:
    """Cutting parameters for HMI"""
    sheet_width: float
    sheet_height: float
    rapid_speed: float
    cut_speed: float
    heating_time: float  # for laminated
    heating_temp: float  # for laminated
    cut_pressure: float
    break_pressure: float


@dataclass
class HMIDataExchange:
    """Data exchange structure between HMI and NC300"""
    # Input from HMI to NC300
    orders: List[HMIOrderEntry]
    start_signal: bool
    pause_signal: bool
    stop_signal: bool
    manual_mode: bool
    parameters: HMIParameterData

    # Output from NC300 to HMI
    status: HMIStatusData
    gcode_file: Optional[str]
    optimization_result: Optional[Dict]


class HMIInterface:
    """
    HMI Interface for Delta DOP-110CS
    Data structure for HMI-NC300 communication
    """

    # PLC addresses for data exchange (example)
    PLC_ADDRESSES = {
        "status": "D100",
        "current_x": "D102",
        "current_y": "D104",
        "current_z": "D106",
        "cutting_speed": "D108",
        "parts_completed": "D110",
        "parts_remaining": "D112",
        "start_signal": "M100",
        "pause_signal": "M101",
        "stop_signal": "M102",
        "alarm_status": "D200",
        "alarm_code": "D202",
    }

    def __init__(self):
        """Initialize HMI interface"""
        self.data_exchange = HMIDataExchange(
            orders=[],
            start_signal=False,
            pause_signal=False,
            stop_signal=False,
            manual_mode=False,
            parameters=HMIParameterData(
                sheet_width=6000,
                sheet_height=3000,
                rapid_speed=80000,
                cut_speed=1000,
                heating_time=4.0,
                heating_temp=135,
                cut_pressure=3.5,
                break_pressure=4.0
            ),
            status=HMIStatusData(
                status=MachineStatus.IDLE,
                current_x=0,
                current_y=0,
                current_z=0,
                cutting_speed=0,
                parts_completed=0,
                parts_remaining=0,
                estimated_time_remaining=0,
                utilization=0
            ),
            gcode_file=None,
            optimization_result=None
        )

    def add_order(self, order: HMIOrderEntry) -> None:
        """Add order from HMI"""
        self.data_exchange.orders.append(order)

    def remove_order(self, order_id: str) -> bool:
        """Remove order by ID"""
        for i, order in enumerate(self.data_exchange.orders):
            if order.order_id == order_id:
                self.data_exchange.orders.pop(i)
                return True
        return False

    def clear_orders(self) -> None:
        """Clear all orders"""
        self.data_exchange.orders = []

    def get_orders(self) -> List[HMIOrderEntry]:
        """Get all orders"""
        return self.data_exchange.orders

    def set_parameters(self, params: HMIParameterData) -> None:
        """Set cutting parameters"""
        self.data_exchange.parameters = params

    def update_status(self, status: HMIStatusData) -> None:
        """Update machine status"""
        self.data_exchange.status = status

    def send_start_signal(self) -> None:
        """Send start signal to NC300"""
        self.data_exchange.start_signal = True
        self.data_exchange.pause_signal = False
        self.data_exchange.stop_signal = False

    def send_pause_signal(self) -> None:
        """Send pause signal"""
        self.data_exchange.start_signal = False
        self.data_exchange.pause_signal = True
        self.data_exchange.stop_signal = False

    def send_stop_signal(self) -> None:
        """Send stop signal"""
        self.data_exchange.start_signal = False
        self.data_exchange.pause_signal = False
        self.data_exchange.stop_signal = True

    def set_manual_mode(self, enabled: bool) -> None:
        """Set manual operation mode"""
        self.data_exchange.manual_mode = enabled

    def add_alarm(self, alarm_code: int, alarm_message: str) -> None:
        """Add alarm to status"""
        alarm = {
            "code": alarm_code,
            "message": alarm_message,
            "timestamp": datetime.now().isoformat(),
            "active": True
        }
        self.data_exchange.status.alarms.append(alarm)
        self.data_exchange.status.status = MachineStatus.ALARM

    def clear_alarm(self, alarm_code: int) -> bool:
        """Clear specific alarm"""
        for alarm in self.data_exchange.status.alarms:
            if alarm["code"] == alarm_code:
                alarm["active"] = False
        # Check if any alarms still active
        active = [a for a in self.data_exchange.status.alarms if a["active"]]
        if not active:
            self.data_exchange.status.status = MachineStatus.IDLE
        return True

    def export_to_json(self) -> str:
        """Export data exchange to JSON"""
        data = {
            "orders": [
                {
                    "order_id": o.order_id,
                    "width": o.width,
                    "height": o.height,
                    "quantity": o.quantity,
                    "thickness": o.thickness,
                    "glass_type": o.glass_type,
                    "priority": o.priority,
                    "customer": o.customer,
                    "notes": o.notes
                }
                for o in self.data_exchange.orders
            ],
            "parameters": {
                "sheet_width": self.data_exchange.parameters.sheet_width,
                "sheet_height": self.data_exchange.parameters.sheet_height,
                "rapid_speed": self.data_exchange.parameters.rapid_speed,
                "cut_speed": self.data_exchange.parameters.cut_speed,
                "heating_time": self.data_exchange.parameters.heating_time,
                "heating_temp": self.data_exchange.parameters.heating_temp,
                "cut_pressure": self.data_exchange.parameters.cut_pressure,
                "break_pressure": self.data_exchange.parameters.break_pressure
            },
            "status": {
                "status": self.data_exchange.status.status.value,
                "current_x": self.data_exchange.status.current_x,
                "current_y": self.data_exchange.status.current_y,
                "current_z": self.data_exchange.status.current_z,
                "cutting_speed": self.data_exchange.status.cutting_speed,
                "parts_completed": self.data_exchange.status.parts_completed,
                "parts_remaining": self.data_exchange.status.parts_remaining,
                "estimated_time_remaining": self.data_exchange.status.estimated_time_remaining,
                "utilization": self.data_exchange.status.utilization,
                "alarms": self.data_exchange.status.alarms
            },
            "signals": {
                "start": self.data_exchange.start_signal,
                "pause": self.data_exchange.pause_signal,
                "stop": self.data_exchange.stop_signal,
                "manual_mode": self.data_exchange.manual_mode
            },
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(data, indent=2)

    def load_from_json(self, json_str: str) -> None:
        """Load data exchange from JSON"""
        data = json.loads(json_str)

        # Load orders
        self.data_exchange.orders = [
            HMIOrderEntry(
                order_id=o["order_id"],
                width=o["width"],
                height=o["height"],
                quantity=o["quantity"],
                thickness=o["thickness"],
                glass_type=o["glass_type"],
                priority=o["priority"],
                customer=o.get("customer"),
                notes=o.get("notes")
            )
            for o in data.get("orders", [])
        ]

        # Load parameters
        if "parameters" in data:
            params = data["parameters"]
            self.data_exchange.parameters = HMIParameterData(
                sheet_width=params["sheet_width"],
                sheet_height=params["sheet_height"],
                rapid_speed=params["rapid_speed"],
                cut_speed=params["cut_speed"],
                heating_time=params["heating_time"],
                heating_temp=params["heating_temp"],
                cut_pressure=params["cut_pressure"],
                break_pressure=params["break_pressure"]
            )

        # Load status
        if "status" in data:
            status = data["status"]
            self.data_exchange.status = HMIStatusData(
                status=MachineStatus(status["status"]),
                current_x=status["current_x"],
                current_y=status["current_y"],
                current_z=status["current_z"],
                cutting_speed=status["cutting_speed"],
                parts_completed=status["parts_completed"],
                parts_remaining=status["parts_remaining"],
                estimated_time_remaining=status["estimated_time_remaining"],
                utilization=status["utilization"],
                alarms=status.get("alarms", [])
            )


class HMIConfigGenerator:
    """
    Generate HMI configuration data
    For use with Delta Screen Editor
    """

    def __init__(self):
        """Initialize config generator"""
        pass

    def generate_screen_config(self, page: HMIPage) -> Dict:
        """
        Generate screen configuration for HMI page

        Args:
            page: HMI page type

        Returns:
            Screen configuration dictionary
        """
        configs = {
            HMIPage.MAIN: self._main_screen(),
            HMIPage.ORDER_INPUT: self._order_input_screen(),
            HMIPage.PARAMETER: self._parameter_screen(),
            HMIPage.OPTIMIZATION: self._optimization_screen(),
            HMIPage.CUTTING: self._cutting_screen(),
            HMIPage.ALARM: self._alarm_screen(),
        }
        return configs.get(page, {})

    def _main_screen(self) -> Dict:
        """Main screen configuration"""
        return {
            "page_id": 1,
            "page_name": "Main",
            "elements": [
                {
                    "type": "button",
                    "id": "btn_start",
                    "position": (100, 50),
                    "size": (120, 50),
                    "text": "START",
                    "address": "M100",
                    "color": "green"
                },
                {
                    "type": "button",
                    "id": "btn_stop",
                    "position": (240, 50),
                    "size": (120, 50),
                    "text": "STOP",
                    "address": "M102",
                    "color": "red"
                },
                {
                    "type": "button",
                    "id": "btn_orders",
                    "position": (100, 120),
                    "size": (120, 50),
                    "text": "Orders",
                    "link_page": 2
                },
                {
                    "type": "display",
                    "id": "status_display",
                    "position": (400, 50),
                    "size": (200, 100),
                    "address": "D100",
                    "format": "status"
                },
                {
                    "type": "display",
                    "id": "position_display",
                    "position": (400, 160),
                    "size": (200, 60),
                    "addresses": ["D102", "D104"],
                    "format": "X: {0}  Y: {1}"
                }
            ]
        }

    def _order_input_screen(self) -> Dict:
        """Order input screen configuration"""
        return {
            "page_id": 2,
            "page_name": "Order Input",
            "elements": [
                {
                    "type": "input",
                    "id": "input_width",
                    "position": (50, 50),
                    "size": (100, 40),
                    "label": "Width (mm)",
                    "address": "D300"
                },
                {
                    "type": "input",
                    "id": "input_height",
                    "position": (180, 50),
                    "size": (100, 40),
                    "label": "Height (mm)",
                    "address": "D302"
                },
                {
                    "type": "input",
                    "id": "input_quantity",
                    "position": (50, 120),
                    "size": (100, 40),
                    "label": "Quantity",
                    "address": "D304"
                },
                {
                    "type": "select",
                    "id": "select_type",
                    "position": (180, 120),
                    "size": (150, 40),
                    "label": "Glass Type",
                    "options": ["Float", "Laminated", "Tempered"],
                    "address": "D306"
                },
                {
                    "type": "button",
                    "id": "btn_add",
                    "position": (50, 200),
                    "size": (100, 50),
                    "text": "Add Order"
                },
                {
                    "type": "list",
                    "id": "order_list",
                    "position": (50, 280),
                    "size": (400, 200),
                    "source": "orders"
                }
            ]
        }

    def _parameter_screen(self) -> Dict:
        """Parameter screen configuration"""
        return {
            "page_id": 3,
            "page_name": "Parameters",
            "elements": [
                {
                    "type": "input",
                    "id": "param_cut_speed",
                    "position": (50, 50),
                    "size": (100, 40),
                    "label": "Cut Speed (mm/min)",
                    "address": "D400",
                    "default": 1000
                },
                {
                    "type": "input",
                    "id": "param_rapid_speed",
                    "position": (200, 50),
                    "size": (100, 40),
                    "label": "Rapid Speed",
                    "address": "D402",
                    "default": 80000
                },
                {
                    "type": "input",
                    "id": "param_heat_time",
                    "position": (50, 120),
                    "size": (100, 40),
                    "label": "Heat Time (s)",
                    "address": "D404",
                    "default": 4.0
                },
                {
                    "type": "input",
                    "id": "param_pressure",
                    "position": (200, 120),
                    "size": (100, 40),
                    "label": "Cut Pressure (bar)",
                    "address": "D406",
                    "default": 3.5
                }
            ]
        }

    def _optimization_screen(self) -> Dict:
        """Optimization screen configuration"""
        return {
            "page_id": 4,
            "page_name": "Optimization",
            "elements": [
                {
                    "type": "button",
                    "id": "btn_optimize",
                    "position": (50, 50),
                    "size": (150, 50),
                    "text": "Run Optimization"
                },
                {
                    "type": "display",
                    "id": "utilization_display",
                    "position": (50, 120),
                    "size": (150, 40),
                    "label": "Utilization",
                    "address": "D500",
                    "format": "{0}%"
                },
                {
                    "type": "display",
                    "id": "parts_display",
                    "position": (220, 120),
                    "size": (150, 40),
                    "label": "Parts Placed",
                    "address": "D502"
                },
                {
                    "type": "display",
                    "id": "time_display",
                    "position": (50, 180),
                    "size": (150, 40),
                    "label": "Est. Time",
                    "address": "D504",
                    "format": "{0} min"
                },
                {
                    "type": "visualization",
                    "id": "nesting_preview",
                    "position": (50, 250),
                    "size": (500, 300),
                    "type": "nesting_preview"
                }
            ]
        }

    def _cutting_screen(self) -> Dict:
        """Cutting progress screen"""
        return {
            "page_id": 5,
            "page_name": "Cutting",
            "elements": [
                {
                    "type": "display",
                    "id": "current_part",
                    "position": (50, 50),
                    "size": (200, 40),
                    "label": "Current Part"
                },
                {
                    "type": "progress",
                    "id": "cut_progress",
                    "position": (50, 100),
                    "size": (500, 30),
                    "address": "D600",
                    "max_value": 100
                },
                {
                    "type": "display",
                    "id": "position_display",
                    "position": (50, 150),
                    "size": (200, 60),
                    "addresses": ["D102", "D104", "D106"],
                    "format": "X:{0} Y:{1} Z:{2}"
                },
                {
                    "type": "display",
                    "id": "speed_display",
                    "position": (300, 150),
                    "size": (100, 40),
                    "address": "D108",
                    "format": "{0} mm/min"
                },
                {
                    "type": "visualization",
                    "id": "cut_preview",
                    "position": (50, 230),
                    "size": (500, 250),
                    "type": "cutting_preview"
                }
            ]
        }

    def _alarm_screen(self) -> Dict:
        """Alarm screen configuration"""
        return {
            "page_id": 6,
            "page_name": "Alarms",
            "elements": [
                {
                    "type": "list",
                    "id": "alarm_list",
                    "position": (50, 50),
                    "size": (500, 300),
                    "source": "alarms",
                    "color_rules": [
                        {"condition": "active", "color": "red"},
                        {"condition": "!active", "color": "gray"}
                    ]
                },
                {
                    "type": "button",
                    "id": "btn_clear",
                    "position": (50, 380),
                    "size": (150, 50),
                    "text": "Clear All"
                },
                {
                    "type": "button",
                    "id": "btn_reset",
                    "position": (250, 380),
                    "size": (150, 50),
                    "text": "Reset Machine"
                }
            ]
        }

    def export_all_configs(self) -> str:
        """Export all screen configurations"""
        configs = {}
        for page in HMIPage:
            config = self.generate_screen_config(page)
            if config:
                configs[page.value] = config
        return json.dumps(configs, indent=2)


def demo():
    """Demo usage"""
    print("=" * 60)
    print("HMI Interface Demo")
    print("=" * 60)

    # Create interface
    hmi = HMIInterface()

    # Add orders
    orders = [
        HMIOrderEntry("ORD-001", 500, 400, 10, 4, "float", 1),
        HMIOrderEntry("ORD-002", 300, 200, 20, 4, "float", 2),
        HMIOrderEntry("ORD-003", 600, 400, 5, 8, "laminated", 1),
    ]

    for order in orders:
        hmi.add_order(order)

    print(f"\nOrders added: {len(hmi.get_orders())}")

    # Update status
    status = HMIStatusData(
        status=MachineStatus.READY,
        current_x=0,
        current_y=0,
        current_z=0,
        cutting_speed=0,
        parts_completed=0,
        parts_remaining=35,
        estimated_time_remaining=45,
        utilization=92.5
    )
    hmi.update_status(status)

    print(f"Status: {status.status.value}")
    print(f"Parts remaining: {status.parts_remaining}")

    # Add alarm
    hmi.add_alarm(13, "Position deviation error")
    print(f"\nAlarm added - Status now: {hmi.data_exchange.status.status.value}")

    # Export to JSON
    print("\n--- Data Exchange JSON ---")
    print(hmi.export_to_json()[:500] + "...")

    # Generate screen configs
    print("\n--- Screen Configurations ---")
    config_gen = HMIConfigGenerator()
    print(config_gen.export_all_configs()[:500] + "...")


if __name__ == "__main__":
    demo()