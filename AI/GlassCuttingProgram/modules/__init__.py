#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Glass Cutting Program Modules
LiSEC GFB-60/30RE Cam Kesme Makinesi

Available modules:
- nesting_optimizer: 2D Bin packing algorithms
- path_planner: TSP path optimization
- gcode_generator: NC300 G-code generation
- lamine_profile: Laminated glass E-Cam profiles
- defect_handler: Defect detection and avoidance
- hmi_interface: DOP-110CS HMI integration
"""

from .nesting_optimizer import (
    NestingOptimizer,
    NestingAlgorithm,
    Part,
    PlacedPart,
    GuillotineOptimizer,
    GeneticOptimizer,
    MaximalRectsOptimizer
)

from .path_planner import (
    CuttingPathOptimizer,
    PathAlgorithm,
    TSPSolver,
    CutSegment,
    CutPoint
)

from .gcode_generator import (
    NC300GCodeGenerator,
    GCodeProgram,
    GCodeParams,
    GlassType,
    CutType
)

from .lamine_profile import (
    LaminatedGlassCalculator,
    LaminatedGlassSpec,
    CuttingParameters,
    ECamProfile,
    FilmType,
    LamineCuttingOptimizer
)

from .defect_handler import (
    DefectHandler,
    DefectDetector,
    DefectAvoidanceOptimizer,
    DefectMap,
    Defect,
    DefectType
)

from .hmi_interface import (
    HMIInterface,
    HMIOrderEntry,
    HMIStatusData,
    HMIParameterData,
    HMIDataExchange,
    MachineStatus,
    HMIPage,
    HMIConfigGenerator
)

from .herofis_connector import (
    HerofisConnector,
    HerofisOrder,
    ImportResult,
    HEROFIS_COLUMN_MAPPINGS,
    GLASS_TYPE_MAPPINGS
)

__all__ = [
    'NestingOptimizer',
    'NestingAlgorithm',
    'Part',
    'PlacedPart',
    'GuillotineOptimizer',
    'GeneticOptimizer',
    'MaximalRectsOptimizer',
    'CuttingPathOptimizer',
    'PathAlgorithm',
    'TSPSolver',
    'CutSegment',
    'CutPoint',
    'NC300GCodeGenerator',
    'GCodeProgram',
    'GCodeParams',
    'GlassType',
    'CutType',
    'LaminatedGlassCalculator',
    'LaminatedGlassSpec',
    'CuttingParameters',
    'ECamProfile',
    'FilmType',
    'LamineCuttingOptimizer',
    'DefectHandler',
    'DefectDetector',
    'DefectAvoidanceOptimizer',
    'DefectMap',
    'Defect',
    'DefectType',
    'HMIInterface',
    'HMIOrderEntry',
    'HMIStatusData',
    'HMIParameterData',
    'HMIDataExchange',
    'MachineStatus',
    'HMIPage',
    'HMIConfigGenerator',
    'HerofisConnector',
    'HerofisOrder',
    'ImportResult',
    'HEROFIS_COLUMN_MAPPINGS',
    'GLASS_TYPE_MAPPINGS'
]

__version__ = '1.1.0'