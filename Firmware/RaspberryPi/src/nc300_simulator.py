"""
Delta NC300 orta seviye kontrol simülatörü.

Amaç:
- Register tabanlı hareket komutlarını taklit etmek
- X/Y/Z/V eksenlerini basit bir motion loop ile güncellemek
- Lamine çevrim fazlarını I/O koşullarıyla birlikte simüle etmek
- FreeCAD ya da HMI katmanına bağlanabilecek sade bir Python arayüzü sağlamak
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, Optional
import argparse
import json
import math
import time


class LamineState(str, Enum):
    IDLE = "IDLE"
    LOADING = "LOADING"
    HEATING = "HEATING"
    UPPER_CUT = "UPPER_CUT"
    LOWER_CUT = "LOWER_CUT"
    SEPARATING = "SEPARATING"
    BREAKING = "BREAKING"
    UNLOADING = "UNLOADING"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"


@dataclass
class AxisState:
    name: str
    position_mm: float = 0.0
    target_mm: float = 0.0
    speed_mm_s: float = 0.0
    max_travel_mm: float = 0.0
    servo_enabled: bool = False
    in_position: bool = True

    def update(self, dt: float) -> None:
        if not self.servo_enabled:
            self.in_position = math.isclose(self.position_mm, self.target_mm, abs_tol=0.01)
            return

        delta = self.target_mm - self.position_mm
        max_step = self.speed_mm_s * dt
        if abs(delta) <= max_step:
            self.position_mm = self.target_mm
            self.in_position = True
            return

        direction = 1.0 if delta > 0 else -1.0
        self.position_mm += direction * max_step
        self.in_position = False


@dataclass
class LamineProcess:
    state: LamineState = LamineState.IDLE
    state_started_at: float = 0.0
    state_message: str = "Hazır"
    cycle_counter: int = 0


@dataclass
class NC300Simulator:
    update_period_s: float = 0.05
    time_s: float = 0.0
    freecad_callback: Optional[Callable[[Dict[str, float]], None]] = None
    axes: Dict[str, AxisState] = field(default_factory=dict)
    di: Dict[str, bool] = field(default_factory=dict)
    do: Dict[str, bool] = field(default_factory=dict)
    registers: Dict[int, int] = field(default_factory=dict)
    lamine: LamineProcess = field(default_factory=LamineProcess)

    # Modbus-benzeri register adresleri
    REG_TARGET_X = 0x1000
    REG_TARGET_Y = 0x1001
    REG_TARGET_Z = 0x1002
    REG_TARGET_V = 0x1003
    REG_SPEED_X = 0x1010
    REG_SPEED_Y = 0x1011
    REG_SPEED_Z = 0x1012
    REG_SPEED_V = 0x1013
    REG_START_MOVE = 0x2000
    REG_START_LAMINE = 0x2001
    REG_RESET = 0x2002
    REG_POS_X = 0x3000
    REG_POS_Y = 0x3001
    REG_POS_Z = 0x3002
    REG_POS_V = 0x3003
    REG_STATUS_WORD = 0x3010
    REG_ACTIVE_STATE = 0x3011
    REG_ALARM_CODE = 0x3012

    STATUS_READY = 0x0001
    STATUS_MOVING = 0x0002
    STATUS_LAMINE_ACTIVE = 0x0004
    STATUS_ALARM = 0x0008
    STATUS_CYCLE_COMPLETE = 0x0010

    ALARM_NONE = 0
    ALARM_SAFETY = 10
    ALARM_VACUUM = 20
    ALARM_AIR = 21

    STATE_CODES = {
        LamineState.IDLE: 0,
        LamineState.LOADING: 10,
        LamineState.HEATING: 20,
        LamineState.UPPER_CUT: 30,
        LamineState.LOWER_CUT: 40,
        LamineState.SEPARATING: 50,
        LamineState.BREAKING: 60,
        LamineState.UNLOADING: 70,
        LamineState.COMPLETE: 80,
        LamineState.ERROR: 99,
    }

    def __post_init__(self) -> None:
        self.axes = {
            "X": AxisState("X", speed_mm_s=800.0, max_travel_mm=6000.0),
            "Y": AxisState("Y", speed_mm_s=600.0, max_travel_mm=3000.0),
            "Z": AxisState("Z", position_mm=300.0, target_mm=300.0, speed_mm_s=80.0, max_travel_mm=300.0),
            "V": AxisState("V", speed_mm_s=200.0, max_travel_mm=300.0),
        }
        self.di = {
            "ESTOP_OK": True,
            "DOOR_CLOSED": True,
            "AIR_PRESSURE_OK": True,
            "VACUUM_OK": False,
            "GLASS_DETECT": False,
            "TEMP_READY": False,
            "UPPER_CUT_OK": False,
            "LOWER_CUT_OK": False,
            "SEPARATION_OK": False,
            "BREAK_OK": False,
            "UNLOAD_READY": False,
        }
        self.do = {
            "SERVO_ENABLE_X": False,
            "SERVO_ENABLE_Y": False,
            "SERVO_ENABLE_Z": False,
            "SERVO_ENABLE_V": False,
            "VACUUM_PUMP": False,
            "HEATER_ENABLE": False,
            "UPPER_CUT_ENABLE": False,
            "LOWER_CUT_ENABLE": False,
            "SEPARATING_BLADE": False,
            "BREAKING_BAR": False,
            "PRESSURE_ROLLER": False,
            "ALARM": False,
        }
        self._write_axis_registers()
        self._write_status_registers(self.ALARM_NONE)

    def set_input(self, signal: str, value: bool) -> None:
        if signal not in self.di:
            raise KeyError(f"Bilinmeyen DI: {signal}")
        self.di[signal] = value

    def write_register(self, address: int, value: int) -> None:
        self.registers[address] = value
        if address == self.REG_TARGET_X:
            self.axes["X"].target_mm = self._clamp(value / 1000.0, 0.0, self.axes["X"].max_travel_mm)
        elif address == self.REG_TARGET_Y:
            self.axes["Y"].target_mm = self._clamp(value / 1000.0, 0.0, self.axes["Y"].max_travel_mm)
        elif address == self.REG_TARGET_Z:
            self.axes["Z"].target_mm = self._clamp(value / 1000.0, 0.0, self.axes["Z"].max_travel_mm)
        elif address == self.REG_TARGET_V:
            self.axes["V"].target_mm = self._clamp(value / 1000.0, 0.0, self.axes["V"].max_travel_mm)
        elif address == self.REG_SPEED_X:
            self.axes["X"].speed_mm_s = max(1.0, value / 1000.0)
        elif address == self.REG_SPEED_Y:
            self.axes["Y"].speed_mm_s = max(1.0, value / 1000.0)
        elif address == self.REG_SPEED_Z:
            self.axes["Z"].speed_mm_s = max(1.0, value / 1000.0)
        elif address == self.REG_SPEED_V:
            self.axes["V"].speed_mm_s = max(1.0, value / 1000.0)
        elif address == self.REG_START_MOVE and value:
            self._start_motion()
        elif address == self.REG_START_LAMINE and value:
            self._start_lamine_cycle()
        elif address == self.REG_RESET and value:
            self.reset_faults()

    def read_register(self, address: int) -> int:
        return self.registers.get(address, 0)

    def tick(self, dt: Optional[float] = None) -> None:
        dt = dt if dt is not None else self.update_period_s
        self.time_s += dt
        self._sync_servo_enables()

        for axis in self.axes.values():
            axis.update(dt)

        self._update_motion_status()
        self._update_lamine_state_machine()
        self._write_axis_registers()

        if self.freecad_callback:
            self.freecad_callback(self.get_positions())

    def run_for(self, seconds: float) -> None:
        steps = max(1, int(seconds / self.update_period_s))
        for _ in range(steps):
            self.tick(self.update_period_s)

    def get_positions(self) -> Dict[str, float]:
        return {name: axis.position_mm for name, axis in self.axes.items()}

    def get_snapshot(self) -> Dict[str, object]:
        return {
            "time_s": round(self.time_s, 3),
            "positions_mm": self.get_positions(),
            "targets_mm": {name: axis.target_mm for name, axis in self.axes.items()},
            "di": dict(self.di),
            "do": dict(self.do),
            "lamine_state": self.lamine.state.value,
            "lamine_message": self.lamine.state_message,
            "registers": {
                hex(addr): value for addr, value in sorted(self.registers.items())
            },
        }

    def move_absolute(self, x: float, y: float, z: float, v: Optional[float] = None) -> None:
        changed = False
        changed |= self._set_axis_target("X", x)
        changed |= self._set_axis_target("Y", y)
        changed |= self._set_axis_target("Z", z)
        if v is not None:
            changed |= self._set_axis_target("V", v)
        if changed:
            self.write_register(self.REG_START_MOVE, 1)

    def reset_faults(self) -> None:
        self.do["ALARM"] = False
        self.lamine.state = LamineState.IDLE
        self.lamine.state_message = "Reset sonrası hazır"
        self._write_status_registers(self.ALARM_NONE)
        self.registers[self.REG_RESET] = 0

    def _start_motion(self) -> None:
        for axis in self.axes.values():
            axis.in_position = False
        self._write_status_registers(self.ALARM_NONE)
        self.registers[self.REG_START_MOVE] = 0

    def _start_lamine_cycle(self) -> None:
        if not self._safety_ok():
            self._trip_alarm(self.ALARM_SAFETY, "Lamine start engellendi: safety chain açık")
            return
        self.lamine.state = LamineState.LOADING
        self.lamine.state_started_at = self.time_s
        self.lamine.state_message = "Cam yükleme bekleniyor"
        self.di["GLASS_DETECT"] = False
        self.di["VACUUM_OK"] = False
        self.di["TEMP_READY"] = False
        self.di["UPPER_CUT_OK"] = False
        self.di["LOWER_CUT_OK"] = False
        self.di["SEPARATION_OK"] = False
        self.di["BREAK_OK"] = False
        self.di["UNLOAD_READY"] = False
        self.do["VACUUM_PUMP"] = False
        self.do["HEATER_ENABLE"] = False
        self.do["UPPER_CUT_ENABLE"] = False
        self.do["LOWER_CUT_ENABLE"] = False
        self.do["SEPARATING_BLADE"] = False
        self.do["BREAKING_BAR"] = False
        self.do["PRESSURE_ROLLER"] = False
        self.registers[self.REG_START_LAMINE] = 0
        self._write_status_registers(self.ALARM_NONE)

    def _sync_servo_enables(self) -> None:
        self.axes["X"].servo_enabled = self.do["SERVO_ENABLE_X"]
        self.axes["Y"].servo_enabled = self.do["SERVO_ENABLE_Y"]
        self.axes["Z"].servo_enabled = self.do["SERVO_ENABLE_Z"]
        self.axes["V"].servo_enabled = self.do["SERVO_ENABLE_V"]

    def _update_motion_status(self) -> None:
        moving = any(not axis.in_position for axis in self.axes.values())
        alarm_code = self.read_register(self.REG_ALARM_CODE)
        status = self.STATUS_READY
        if moving:
            status |= self.STATUS_MOVING
        if self.lamine.state not in (LamineState.IDLE, LamineState.COMPLETE):
            status |= self.STATUS_LAMINE_ACTIVE
        if alarm_code != self.ALARM_NONE:
            status |= self.STATUS_ALARM
        if self.lamine.state == LamineState.COMPLETE:
            status |= self.STATUS_CYCLE_COMPLETE
        self.registers[self.REG_STATUS_WORD] = status
        self.registers[self.REG_ACTIVE_STATE] = self.STATE_CODES[self.lamine.state]

    def _update_lamine_state_machine(self) -> None:
        if self.lamine.state in (LamineState.IDLE, LamineState.COMPLETE, LamineState.ERROR):
            self._update_motion_status()
            return

        if not self._safety_ok():
            self._trip_alarm(self.ALARM_SAFETY, "Safety interlock açıldı")
            return

        if self.lamine.state == LamineState.LOADING:
            self.do["PRESSURE_ROLLER"] = True
            self.di["GLASS_DETECT"] = True
            self.do["VACUUM_PUMP"] = True
            self.di["VACUUM_OK"] = True
            if self.di["GLASS_DETECT"] and self.di["VACUUM_OK"]:
                self._goto_state(LamineState.HEATING, "Isıtma fazı başladı")

        elif self.lamine.state == LamineState.HEATING:
            self.do["HEATER_ENABLE"] = True
            if self.time_s - self.lamine.state_started_at >= 1.5:
                self.di["TEMP_READY"] = True
            if self.di["TEMP_READY"]:
                self.move_absolute(500.0, 500.0, 284.0, 0.0)
                self.do["UPPER_CUT_ENABLE"] = True
                self._goto_state(LamineState.UPPER_CUT, "Üst kesim başlatıldı")

        elif self.lamine.state == LamineState.UPPER_CUT:
            self.move_absolute(2000.0, 1400.0, 284.0, 0.0)
            if self._axes_in_position("X", "Y", "Z"):
                self.di["UPPER_CUT_OK"] = True
                self.move_absolute(2000.0, 1400.0, 284.0, 120.0)
                self.do["LOWER_CUT_ENABLE"] = True
                self._goto_state(LamineState.LOWER_CUT, "Alt kesim senkronizasyonu başladı")

        elif self.lamine.state == LamineState.LOWER_CUT:
            self.move_absolute(3500.0, 2300.0, 284.0, 250.0)
            if self._axes_in_position("X", "Y", "Z", "V"):
                self.di["LOWER_CUT_OK"] = True
                self.do["UPPER_CUT_ENABLE"] = False
                self.do["LOWER_CUT_ENABLE"] = False
                self.move_absolute(3500.0, 2300.0, 300.0, 0.0)
                self._goto_state(LamineState.SEPARATING, "Ayırma fazı başladı")

        elif self.lamine.state == LamineState.SEPARATING:
            self.do["SEPARATING_BLADE"] = True
            if self._axes_in_position("Z", "V"):
                self.di["SEPARATION_OK"] = True
                self.do["SEPARATING_BLADE"] = False
                self.do["BREAKING_BAR"] = True
                self._goto_state(LamineState.BREAKING, "Kırma fazı başladı")

        elif self.lamine.state == LamineState.BREAKING:
            self.di["BREAK_OK"] = True
            if self.di["BREAK_OK"]:
                self.do["BREAKING_BAR"] = False
                self.do["PRESSURE_ROLLER"] = False
                self.do["VACUUM_PUMP"] = False
                self.di["VACUUM_OK"] = False
                self.move_absolute(500.0, 500.0, 300.0, 0.0)
                self._goto_state(LamineState.UNLOADING, "Boşaltma fazı başladı")

        elif self.lamine.state == LamineState.UNLOADING:
            if self._axes_in_position("X", "Y", "Z", "V"):
                self.di["UNLOAD_READY"] = True
                self.do["HEATER_ENABLE"] = False
                self.lamine.cycle_counter += 1
                self.lamine.state = LamineState.COMPLETE
                self.lamine.state_message = "Lamine çevrim tamamlandı"

        self._update_motion_status()

    def _goto_state(self, state: LamineState, message: str) -> None:
        self.lamine.state = state
        self.lamine.state_started_at = self.time_s
        self.lamine.state_message = message

    def _trip_alarm(self, code: int, message: str) -> None:
        self.do["ALARM"] = True
        self.do["VACUUM_PUMP"] = False
        self.do["HEATER_ENABLE"] = False
        self.do["UPPER_CUT_ENABLE"] = False
        self.do["LOWER_CUT_ENABLE"] = False
        self.do["SEPARATING_BLADE"] = False
        self.do["BREAKING_BAR"] = False
        self.lamine.state = LamineState.ERROR
        self.lamine.state_message = message
        self.registers[self.REG_ALARM_CODE] = code
        self._update_motion_status()

    def _write_axis_registers(self) -> None:
        self.registers[self.REG_POS_X] = int(self.axes["X"].position_mm * 1000)
        self.registers[self.REG_POS_Y] = int(self.axes["Y"].position_mm * 1000)
        self.registers[self.REG_POS_Z] = int(self.axes["Z"].position_mm * 1000)
        self.registers[self.REG_POS_V] = int(self.axes["V"].position_mm * 1000)

    def _write_status_registers(self, alarm_code: int) -> None:
        self.registers[self.REG_ALARM_CODE] = alarm_code
        self._update_motion_status()

    def _axes_in_position(self, *axis_names: str) -> bool:
        return all(self.axes[name].in_position for name in axis_names)

    def _safety_ok(self) -> bool:
        return self.di["ESTOP_OK"] and self.di["DOOR_CLOSED"] and self.di["AIR_PRESSURE_OK"]

    def _set_axis_target(self, axis_name: str, target_mm: float) -> bool:
        axis = self.axes[axis_name]
        clamped = self._clamp(target_mm, 0.0, axis.max_travel_mm)
        if math.isclose(axis.target_mm, clamped, abs_tol=0.001):
            return False
        axis.target_mm = clamped
        register_map = {
            "X": self.REG_TARGET_X,
            "Y": self.REG_TARGET_Y,
            "Z": self.REG_TARGET_Z,
            "V": self.REG_TARGET_V,
        }
        self.registers[register_map[axis_name]] = int(clamped * 1000)
        return True

    @staticmethod
    def _clamp(value: float, min_value: float, max_value: float) -> float:
        return max(min_value, min(max_value, value))


def _format_snapshot(snapshot: Dict[str, object]) -> str:
    return json.dumps(snapshot, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Delta NC300 orta seviye simülatör")
    parser.add_argument("--demo", action="store_true", help="Lamine çevrim demosu çalıştır")
    parser.add_argument("--seconds", type=float, default=8.0, help="Demo çalışma süresi")
    parser.add_argument("--json", action="store_true", help="Son durumu JSON bas")
    args = parser.parse_args()

    sim = NC300Simulator()
    sim.do["SERVO_ENABLE_X"] = True
    sim.do["SERVO_ENABLE_Y"] = True
    sim.do["SERVO_ENABLE_Z"] = True
    sim.do["SERVO_ENABLE_V"] = True

    if args.demo:
        sim.write_register(sim.REG_START_LAMINE, 1)
        sim.run_for(args.seconds)
    else:
        sim.move_absolute(1000.0, 500.0, 150.0, 50.0)
        sim.run_for(args.seconds)

    if args.json:
        print(_format_snapshot(sim.get_snapshot()))
    else:
        snapshot = sim.get_snapshot()
        print(f"State   : {snapshot['lamine_state']}")
        print(f"Message : {snapshot['lamine_message']}")
        print(f"Pos     : {snapshot['positions_mm']}")
        print(f"Alarm   : {snapshot['registers'].get(hex(sim.REG_ALARM_CODE), 0)}")


if __name__ == "__main__":
    main()
