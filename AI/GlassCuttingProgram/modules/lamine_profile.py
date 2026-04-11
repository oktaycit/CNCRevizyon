#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Laminated Glass Profile Module
E-Cam Profile Generation for LiSEC GFB-60/30RE

Features:
- Upper/lower glass cutting synchronization
- Heating parameters calculation
- PVB/EVA/SGP film handling
- Break-out sequence

Uses: qwen3.5-plus (quick parameter calculation)
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class FilmType(Enum):
    """Interlayer film types"""
    PVB = "PVB"  # Polyvinyl butyral (standard)
    EVA = "EVA"  # Ethylene vinyl acetate
    SGP = "SGP"  # SentryGlas Plus (structural)
    TPU = "TPU"  # Thermoplastic polyurethane


@dataclass
class LaminatedGlassSpec:
    """Laminated glass specification"""
    upper_thickness: float  # mm
    film_type: FilmType
    film_thickness: float  # mm
    lower_thickness: float  # mm
    total_thickness: float = field(init=False)  # mm (calculated)

    def __post_init__(self):
        self.total_thickness = self.upper_thickness + self.film_thickness + self.lower_thickness

    @property
    def asymmetry(self) -> bool:
        """Check if glass is asymmetric"""
        return self.upper_thickness != self.lower_thickness


@dataclass
class CuttingParameters:
    """Cutting parameters for laminated glass"""
    heating_time: float  # seconds
    heating_temperature: float  # Celsius
    upper_cut_pressure: float  # bar
    lower_cut_pressure: float  # bar
    separation_pressure: float  # bar
    break_pressure: float  # bar
    cutting_speed: float  # mm/min
    upper_offset_x: float  # mm
    upper_offset_y: float  # mm
    lower_offset_x: float  # mm
    lower_offset_y: float  # mm


@dataclass
class ECamProfile:
    """E-Cam profile for NC300"""
    profile_name: str
    points: List[Tuple[float, float]]  # (position, value) pairs
    cycle_period: float  # mm
    sync_angle: float  # degrees


class LaminatedGlassCalculator:
    """
    Calculate cutting parameters for laminated glass
    Based on LiSEC E-Cam technology
    """

    # Film type properties
    FILM_PROPERTIES = {
        FilmType.PVB: {
            "melting_temp": 120,
            "optimal_temp": 135,
            "heating_time_factor": 1.0,
            "separation_force": 2.5,
        },
        FilmType.EVA: {
            "melting_temp": 80,
            "optimal_temp": 100,
            "heating_time_factor": 0.7,
            "separation_force": 2.0,
        },
        FilmType.SGP: {
            "melting_temp": 140,
            "optimal_temp": 160,
            "heating_time_factor": 1.5,
            "separation_force": 4.0,
        },
        FilmType.TPU: {
            "melting_temp": 90,
            "optimal_temp": 110,
            "heating_time_factor": 0.8,
            "separation_force": 2.2,
        },
    }

    # Base parameters for standard glass
    BASE_PARAMS = {
        "min_heating_time": 3.0,  # seconds
        "max_heating_time": 8.0,
        "min_heating_temp": 100,
        "max_heating_temp": 180,
        "base_cut_pressure": 3.0,  # bar
        "base_break_pressure": 3.5,
        "base_cutting_speed": 2000,  # mm/min
    }

    def __init__(self):
        """Initialize calculator"""
        pass

    def calculate_parameters(self, spec: LaminatedGlassSpec) -> CuttingParameters:
        """
        Calculate optimal cutting parameters

        Args:
            spec: Laminated glass specification

        Returns:
            CuttingParameters object
        """
        film_props = self.FILM_PROPERTIES.get(spec.film_type, self.FILM_PROPERTIES[FilmType.PVB])

        # Heating time calculation
        # More thickness = more heating time
        heating_time = self.BASE_PARAMS["min_heating_time"] + \
                      (spec.total_thickness / 10) * film_props["heating_time_factor"]
        heating_time = min(heating_time, self.BASE_PARAMS["max_heating_time"])

        # Heating temperature
        heating_temp = film_props["optimal_temp"]

        # Cut pressure scales with glass thickness
        thickness_factor = spec.upper_thickness / 4.0  # normalized to 4mm

        upper_cut_pressure = self.BASE_PARAMS["base_cut_pressure"] * thickness_factor
        lower_cut_pressure = self.BASE_PARAMS["base_cut_pressure"] * (spec.lower_thickness / 4.0)

        # Separation pressure
        separation_pressure = film_props["separation_force"]

        # Break pressure
        break_pressure = self.BASE_PARAMS["base_break_pressure"] * (spec.total_thickness / 8.0)

        # Cutting speed - slower for thicker glass
        cutting_speed = self.BASE_PARAMS["base_cutting_speed"] / (spec.total_thickness / 8.0)

        # Offsets for upper/lower alignment
        # Upper glass needs slight offset due to film compression
        offset_factor = spec.film_thickness / 0.76  # normalized to standard 0.76mm PVB
        upper_offset_x = 0.02 * offset_factor
        upper_offset_y = -0.01 * offset_factor
        lower_offset_x = 0.0
        lower_offset_y = 0.0

        return CuttingParameters(
            heating_time=heating_time,
            heating_temperature=heating_temp,
            upper_cut_pressure=upper_cut_pressure,
            lower_cut_pressure=lower_cut_pressure,
            separation_pressure=separation_pressure,
            break_pressure=break_pressure,
            cutting_speed=cutting_speed,
            upper_offset_x=upper_offset_x,
            upper_offset_y=upper_offset_y,
            lower_offset_x=lower_offset_x,
            lower_offset_y=lower_offset_y
        )

    def generate_e_cam_profile(self,
                               spec: LaminatedGlassSpec,
                               params: CuttingParameters,
                               cut_length: float) -> ECamProfile:
        """
        Generate E-Cam profile for NC300

        The E-Cam profile synchronizes upper and lower cutting heads

        Args:
            spec: Glass specification
            params: Cutting parameters
            cut_length: Length of cut (mm)

        Returns:
            ECamProfile object
        """
        # Profile points: (position_mm, sync_value)
        # The sync_value controls the phase between upper and lower heads

        points = []

        # Initial approach (0-100mm)
        approach_length = min(100, cut_length * 0.1)
        points.append((0, 0))  # Start position
        points.append((approach_length, 1))  # Sync starts

        # Cutting phase (approach_length to cut_length - approach_length)
        cut_start = approach_length
        cut_end = cut_length - approach_length

        # Number of sync points during cut
        num_points = int((cut_end - cut_start) / 50)  # Every 50mm
        num_points = max(num_points, 5)

        for i in range(num_points):
            pos = cut_start + (cut_end - cut_start) * i / num_points
            # Sync value oscillates slightly for optimal separation
            sync_value = 1 + 0.02 * math.sin(math.pi * i / num_points)
            points.append((pos, sync_value))

        # Heating position (center of cut)
        heating_pos = cut_length / 2
        points.append((heating_pos - 50, 2))  # Heating approach
        points.append((heating_pos, 3))  # Heating peak

        # End approach
        points.append((cut_length - approach_length, 1))
        points.append((cut_length, 0))  # End position

        return ECamProfile(
            profile_name=f"lamine_{spec.upper_thickness}_{spec.film_type.value}_{spec.lower_thickness}",
            points=points,
            cycle_period=cut_length,
            sync_angle=180  # 180 degree phase difference
        )

    def get_cutting_sequence(self,
                             spec: LaminatedGlassSpec,
                             params: CuttingParameters) -> List[Dict]:
        """
        Generate cutting sequence steps

        Args:
            spec: Glass specification
            params: Cutting parameters

        Returns:
            List of sequence steps
        """
        sequence = [
            {
                "step": 1,
                "action": "approach",
                "description": "Move to cutting start position",
                "speed": "rapid",
                "position": "start"
            },
            {
                "step": 2,
                "action": "upper_cut_start",
                "description": f"Start upper glass cut ({spec.upper_thickness}mm)",
                "pressure": params.upper_cut_pressure,
                "speed": params.cutting_speed,
                "offset": (params.upper_offset_x, params.upper_offset_y)
            },
            {
                "step": 3,
                "action": "upper_cut",
                "description": "Cut upper glass perimeter",
                "z_depth": spec.upper_thickness * 0.95  # Almost through
            },
            {
                "step": 4,
                "action": "position_heat",
                "description": "Move to heating position",
                "speed": "rapid",
                "position": "center"
            },
            {
                "step": 5,
                "action": "heat",
                "description": f"Heat film layer ({params.heating_time}s at {params.heating_temperature}°C)",
                "duration": params.heating_time,
                "temperature": params.heating_temperature
            },
            {
                "step": 6,
                "action": "lower_cut_start",
                "description": f"Start lower glass cut ({spec.lower_thickness}mm)",
                "pressure": params.lower_cut_pressure,
                "speed": params.cutting_speed
            },
            {
                "step": 7,
                "action": "lower_cut",
                "description": "Cut lower glass perimeter",
                "z_depth": spec.lower_thickness * 0.95
            },
            {
                "step": 8,
                "action": "separation",
                "description": "Apply separation pressure",
                "pressure": params.separation_pressure
            },
            {
                "step": 9,
                "action": "break",
                "description": "Apply break pressure",
                "pressure": params.break_pressure
            },
            {
                "step": 10,
                "action": "retract",
                "description": "Retract cutting heads",
                "speed": "rapid"
            }
        ]

        return sequence

    def export_nc300_e_cam(self, profile: ECamProfile) -> str:
        """
        Export E-Cam profile in NC300 format

        Args:
            profile: ECamProfile object

        Returns:
            NC300 E-Cam program string
        """
        lines = [
            f"; E-Cam Profile: {profile.profile_name}",
            f"; Cycle Period: {profile.cycle_period} mm",
            f"; Sync Angle: {profile.sync_angle}°",
            "",
            "; Profile points (position, sync_value)",
            "#ECAM_START",
        ]

        for pos, value in profile.points:
            lines.append(f"ECAM_P {pos:.2f} {value:.3f}")

        lines.extend([
            "#ECAM_END",
            "",
            f"; Sync configuration",
            f"ECAM_SYNC {profile.sync_angle}",
        ])

        return '\n'.join(lines)


class LamineCuttingOptimizer:
    """
    Optimize laminated glass cutting
    Combines parameter calculation with sequence optimization
    """

    def __init__(self, sheet_width: float = 6000, sheet_height: float = 3000):
        self.sheet_width = sheet_width
        self.sheet_height = sheet_height
        self.calculator = LaminatedGlassCalculator()

    def optimize_lamine_cut(self,
                            parts: List[Dict],
                            spec: LaminatedGlassSpec) -> Dict:
        """
        Optimize laminated glass cutting for multiple parts

        Args:
            parts: List of placed laminated glass parts
            spec: Glass specification

        Returns:
            Optimization result
        """
        # Calculate parameters
        params = self.calculator.calculate_parameters(spec)

        # Generate sequences for each part
        sequences = []
        total_heating_time = 0

        for part in parts:
            w = part.get("placed_width", part.get("width", 100))
            h = part.get("placed_height", part.get("height", 100))

            # Use longest edge as cut length
            cut_length = max(w, h)

            # Generate E-Cam profile
            profile = self.calculator.generate_e_cam_profile(spec, params, cut_length)

            # Generate sequence
            sequence = self.calculator.get_cutting_sequence(spec, params)
            sequence[0]["position"] = (part["x"], part["y"])

            sequences.append({
                "part_id": part.get("order_id", part.get("part_id")),
                "sequence": sequence,
                "e_cam_profile": profile,
                "nc300_code": self.calculator.export_nc300_e_cam(profile)
            })

            total_heating_time += params.heating_time

        return {
            "glass_spec": {
                "upper_thickness": spec.upper_thickness,
                "film_type": spec.film_type.value,
                "film_thickness": spec.film_thickness,
                "lower_thickness": spec.lower_thickness,
                "total_thickness": spec.total_thickness,
                "asymmetric": spec.asymmetry
            },
            "parameters": {
                "heating_time": params.heating_time,
                "heating_temperature": params.heating_temperature,
                "upper_cut_pressure": params.upper_cut_pressure,
                "lower_cut_pressure": params.lower_cut_pressure,
                "separation_pressure": params.separation_pressure,
                "break_pressure": params.break_pressure,
                "cutting_speed": params.cutting_speed
            },
            "sequences": sequences,
            "total_heating_time": total_heating_time,
            "estimated_total_time": len(parts) * 2 + total_heating_time / 60  # minutes
        }


def demo():
    """Demo usage"""
    print("=" * 60)
    print("Laminated Glass Profile Demo")
    print("=" * 60)

    # Create glass specification
    spec = LaminatedGlassSpec(
        upper_thickness=4,
        film_type=FilmType.PVB,
        film_thickness=0.76,
        lower_thickness=4
    )

    print(f"\nGlass Spec:")
    print(f"  Upper: {spec.upper_thickness}mm")
    print(f"  Film: {spec.film_thickness}mm ({spec.film_type.value})")
    print(f"  Lower: {spec.lower_thickness}mm")
    print(f"  Total: {spec.total_thickness}mm")

    # Calculate parameters
    calculator = LaminatedGlassCalculator()
    params = calculator.calculate_parameters(spec)

    print(f"\nCutting Parameters:")
    print(f"  Heating time: {params.heating_time}s")
    print(f"  Heating temp: {params.heating_temperature}°C")
    print(f"  Upper pressure: {params.upper_cut_pressure} bar")
    print(f"  Lower pressure: {params.lower_cut_pressure} bar")
    print(f"  Separation pressure: {params.separation_pressure} bar")
    print(f"  Break pressure: {params.break_pressure} bar")
    print(f"  Cutting speed: {params.cutting_speed} mm/min")

    # Generate E-Cam profile
    profile = calculator.generate_e_cam_profile(spec, params, 500)
    print(f"\nE-Cam Profile: {profile.profile_name}")
    print(f"  Points: {len(profile.points)}")
    print(f"  Cycle period: {profile.cycle_period}mm")

    # Generate sequence
    sequence = calculator.get_cutting_sequence(spec, params)
    print(f"\nCutting Sequence ({len(sequence)} steps):")
    for step in sequence[:5]:
        print(f"  Step {step['step']}: {step['action']} - {step['description']}")


if __name__ == "__main__":
    demo()