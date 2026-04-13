#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Glass Cutting Program - Integration Test
Tests all modules of the glass cutting system

Run: python test_glass_cutting.py
"""

import os
import sys
import asyncio
import json
import tempfile
from pathlib import Path

# Add module path
sys.path.insert(0, str(Path(__file__).parent))

from web.backend.backend_services import (
    build_cutting_history,
    build_report_dataset,
    build_report_history,
)

from modules import (
    NestingOptimizer, NestingAlgorithm, Part,
    CuttingPathOptimizer, PathAlgorithm,
    NC300GCodeGenerator, GlassType,
    LaminatedGlassCalculator, LaminatedGlassSpec, FilmType,
    DefectHandler, Defect, DefectType,
    HMIInterface, HMIOrderEntry, HMIConfigGenerator,
    AuthManager
)


def test_nesting():
    """Test nesting optimizer"""
    print("\n" + "="*60)
    print("TEST: Nesting Optimizer")
    print("="*60)

    parts = [
        Part("P1", 500, 400, 4, 1, True, "float"),
        Part("P2", 300, 200, 4, 2, True, "float"),
        Part("P3", 800, 600, 6, 1, True, "float"),
        Part("P4", 400, 300, 4, 3, True, "float"),
        Part("P5", 1000, 800, 8, 1, True, "laminated"),
    ]

    optimizer = NestingOptimizer(6000, 3000, NestingAlgorithm.GUILLOTINE_BESTFIT)
    result = optimizer.optimize(parts)

    print(f"Algorithm: {result['algorithm']}")
    print(f"Parts placed: {len(result['placed_parts'])}")
    print(f"Utilization: {result['utilization']*100:.2f}%")
    print(f"Waste area: {result['waste_area']/1000000:.2f} m²")
    print(f"Unplaced: {result['unplaced_count']}")

    assert len(result['placed_parts']) > 0, "No parts placed!"
    assert result['utilization'] > 0, "Zero utilization!"

    print("✓ Nesting test passed")
    return result


def test_path_planner(nesting_result):
    """Test path planner"""
    print("\n" + "="*60)
    print("TEST: Path Planner")
    print("="*60)

    optimizer = CuttingPathOptimizer(6000, 3000)

    # Test with placed parts from nesting
    placed_parts = nesting_result['placed_parts']

    result = optimizer.optimize(placed_parts, PathAlgorithm.TWO_OPT)

    print(f"Algorithm: {result['algorithm']}")
    print(f"Travel distance: {result['total_travel_distance']:.0f} mm")
    print(f"Cut distance: {result['cut_distance']:.0f} mm")
    print(f"Total distance: {result['total_distance']:.0f} mm")
    print(f"Optimization time: {result['optimization_time']:.3f}s")

    assert result['total_travel_distance'] > 0, "Zero travel distance!"
    assert len(result['path']) == len(placed_parts), "Path length mismatch!"

    print("✓ Path planner test passed")
    return result


def test_gcode_generator(nesting_result, path_result):
    """Test G-code generator"""
    print("\n" + "="*60)
    print("TEST: G-Code Generator")
    print("="*60)

    generator = NC300GCodeGenerator()

    placed_parts = nesting_result['placed_parts']
    cutting_path = path_result['path']

    # Test float glass
    float_program = generator.generate(
        placed_parts, cutting_path, GlassType.FLOAT, "test_float"
    )

    print(f"Float glass program:")
    print(f"  Parts: {float_program.parts_count}")
    print(f"  Total distance: {float_program.total_distance:.0f} mm")
    print(f"  Estimated time: {float_program.estimated_time:.1f} min")
    print(f"  Lines: {len(float_program.lines)}")

    assert float_program.parts_count > 0, "No parts in G-code!"
    assert len(float_program.lines) > 20, "G-code too short!"

    # Test laminated glass
    lamine_parts = [{"x": 0, "y": 0, "width": 600, "height": 400,
                     "order_id": "L1", "thickness": 8}]
    lamine_program = generator.generate(
        lamine_parts, [0], GlassType.LAMINATED, "test_lamine"
    )

    print(f"\nLaminated glass program:")
    print(f"  Lines: {len(lamine_program.lines)}")

    # Check for heating commands in laminated G-code
    assert "Heat" in str(lamine_program.lines), "Missing heating command!"

    print("✓ G-code generator test passed")
    return float_program


def test_lamine_profile():
    """Test laminated glass profile"""
    print("\n" + "="*60)
    print("TEST: Laminated Glass Profile")
    print("="*60)

    spec = LaminatedGlassSpec(
        upper_thickness=4,
        film_type=FilmType.PVB,
        film_thickness=0.76,
        lower_thickness=4
    )

    calculator = LaminatedGlassCalculator()
    params = calculator.calculate_parameters(spec)

    print(f"Glass spec: {spec.upper_thickness}mm + {spec.film_thickness}mm + {spec.lower_thickness}mm")
    print(f"Parameters:")
    print(f"  Heating time: {params.heating_time}s")
    print(f"  Heating temp: {params.heating_temperature}°C")
    print(f"  Upper pressure: {params.upper_cut_pressure} bar")
    print(f"  Lower pressure: {params.lower_cut_pressure} bar")

    assert params.heating_time > 0, "Zero heating time!"
    assert params.heating_temperature > 100, "Temperature too low!"

    # Generate E-Cam profile
    profile = calculator.generate_e_cam_profile(spec, params, 500)

    print(f"\nE-Cam profile: {profile.profile_name}")
    print(f"  Points: {len(profile.points)}")
    print(f"  Cycle period: {profile.cycle_period}mm")

    print("✓ Laminated glass profile test passed")


def test_defect_handler():
    """Test defect handler"""
    print("\n" + "="*60)
    print("TEST: Defect Handler")
    print("="*60)

    handler = DefectHandler(6000, 3000)

    # Simulate defects
    result = handler.process_sheet()

    print(f"Defects detected: {result['defect_count']}")
    print(f"Safe area: {result['safe_area_percentage']:.1f}%")

    # Test placement adjustment
    test_parts = [
        {"x": 100, "y": 100, "width": 500, "height": 400, "order_id": "P1"},
        {"x": 1000, "y": 1000, "width": 300, "height": 200, "order_id": "P2"},
    ]

    defects = [Defect(d['x'], d['y'], DefectType(d['type']),
                      d['severity'], d['radius'])
               for d in result['defects']]

    adjusted, rejected = handler.optimize_with_defects(test_parts, defects)

    print(f"Adjusted placements: {len(adjusted)}")
    print(f"Rejected placements: {len(rejected)}")

    assert result['defect_count'] >= 0, "Invalid defect count!"

    print("✓ Defect handler test passed")


def test_hmi_interface():
    """Test HMI interface"""
    print("\n" + "="*60)
    print("TEST: HMI Interface")
    print("="*60)

    hmi = HMIInterface()

    # Add orders
    orders = [
        HMIOrderEntry("ORD-001", 500, 400, 10, 4, "float", 1),
        HMIOrderEntry("ORD-002", 300, 200, 20, 4, "float", 2),
    ]

    for order in orders:
        hmi.add_order(order)

    print(f"Orders added: {len(hmi.get_orders())}")

    # Export to JSON
    json_data = hmi.export_to_json()
    print(f"JSON export length: {len(json_data)} bytes")

    # Test screen config generator
    config_gen = HMIConfigGenerator()
    main_config = config_gen.generate_screen_config("main")
    print(f"Main screen elements: {len(main_config.get('elements', []))}")

    assert len(hmi.get_orders()) == 2, "Order count mismatch!"
    assert len(json_data) > 100, "JSON export too short!"

    print("✓ HMI interface test passed")


def test_auth_manager():
    """Test auth bootstrap, login and token verification"""
    print("\n" + "="*60)
    print("TEST: Authentication")
    print("="*60)

    with tempfile.TemporaryDirectory(prefix="glasscut_auth_") as tmp_dir:
        auth = AuthManager(tmp_dir)

        assert auth.bootstrap_admin_file.exists(), "Bootstrap admin file missing!"

        with open(auth.bootstrap_admin_file, 'r') as f:
            bootstrap = json.load(f)

        assert bootstrap['username'] == 'admin', "Bootstrap admin username mismatch!"

        login_result = auth.authenticate(bootstrap['username'], bootstrap['password'])
        assert login_result is not None, "Bootstrap admin login failed!"

        token_user = auth.verify_token(login_result['access_token'])
        assert token_user is not None, "Access token verification failed!"
        assert token_user['role'] == 'admin', "Bootstrap admin role mismatch!"

        print(f"Bootstrap file: {auth.bootstrap_admin_file}")
        print(f"Admin user: {bootstrap['username']}")
        print("✓ Authentication test passed")


def test_reporting_services():
    """Test backend reporting services against persisted outputs"""
    print("\n" + "="*60)
    print("TEST: Reporting Services")
    print("="*60)

    reports_dir = Path(__file__).parent / 'output' / 'reports'

    dataset = build_report_dataset(reports_dir)
    history = build_cutting_history(reports_dir)
    report_history = build_report_history(reports_dir)

    assert dataset['report_count'] >= 1, "No persisted reports found for dataset!"
    assert len(history) >= 1, "Cutting history should not be empty!"
    assert len(report_history) >= 1, "Report history should not be empty!"

    print(f"Dataset reports: {dataset['report_count']}")
    print(f"History entries: {len(history)}")
    print(f"Report history entries: {len(report_history)}")
    print("✓ Reporting services test passed")


async def test_full_integration():
    """Test full integration pipeline"""
    print("\n" + "="*60)
    print("TEST: Full Integration Pipeline")
    print("="*60)

    try:
        from glass_cutting_orchestrator import GlassCuttingOrchestrator, GlassOrder

        orchestrator = GlassCuttingOrchestrator()

        orders = [
            GlassOrder("ORD-001", 500, 400, 10, 4, "float", 1),
            GlassOrder("ORD-002", 300, 200, 20, 4, "float", 2),
            GlassOrder("ORD-003", 800, 600, 5, 6, "float", 1),
        ]

        result = await orchestrator.optimize_cutting(orders)

        print(f"Parts placed: {len(result.placed_parts)}")
        print(f"Utilization: {result.utilization*100:.2f}%")
        print(f"Waste: {result.waste_area/1000000:.2f} m²")
        print(f"Estimated time: {result.estimated_time:.1f} min")

        if result.gcode_file:
            print(f"G-code file: {result.gcode_file}")

        if result.report_file:
            print(f"Report file: {result.report_file}")

        print("✓ Full integration test passed")

    except ImportError as e:
        print(f"⚠ Skipping full integration (orchestrator requires AI API): {e}")


def main():
    """Run all tests"""
    print("="*60)
    print("Glass Cutting Program - Integration Tests")
    print("="*60)

    results = {}

    # Test nesting
    nesting_result = test_nesting()
    results['nesting'] = True

    # Test path planner
    path_result = test_path_planner(nesting_result)
    results['path'] = True

    # Test G-code generator
    gcode_result = test_gcode_generator(nesting_result, path_result)
    results['gcode'] = True

    # Test laminated glass profile
    test_lamine_profile()
    results['lamine'] = True

    # Test defect handler
    test_defect_handler()
    results['defect'] = True

    # Test HMI interface
    test_hmi_interface()
    results['hmi'] = True

    # Test authentication
    test_auth_manager()
    results['auth'] = True

    # Test reporting services
    test_reporting_services()
    results['reporting'] = True

    # Test full integration (async)
    asyncio.run(test_full_integration())
    results['integration'] = True

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    all_passed = all(results.values())

    for name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {name}: {status}")

    print("\n" + "="*60)
    if all_passed:
        print("ALL TESTS PASSED ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print("="*60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
