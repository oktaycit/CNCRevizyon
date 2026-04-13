#!/usr/bin/env python3
"""
FreeCAD MCP Test Script

MCP sunucusunun FreeCAD entegrasyonunu test eder.

Kullanım:
    python test_freecad_mcp.py
"""

import asyncio
import sys
import os

# Proje yolunu ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from freecad_mcp import FreeCADController, get_freecad_tools


async def test_freecad_controller():
    """FreeCADController'ı test et"""
    print("=" * 60)
    print("🧪 FreeCAD MCP Test")
    print("=" * 60)

    controller = FreeCADController()

    # Test 1: Dizin listeleme
    print("\n📋 Test 1: FreeCAD dosyalarını listele")
    print("-" * 60)
    response = await controller.list_documents()
    print(response.output)

    if response.error:
        print(f"⚠️ Hata: {response.error}")

    # Test 2: Tool tanımlarını kontrol et
    print("\n📋 Test 2: FreeCAD Tool tanımları")
    print("-" * 60)
    tools = get_freecad_tools()
    print(f"✅ {len(tools)} FreeCAD tool tanımlandı:")
    for tool in tools:
        print(f"   - {tool.name}: {tool.description}")

    # Test 3: Basit script çalıştırma
    print("\n📋 Test 3: Basit Python script çalıştırma")
    print("-" * 60)
    test_script = """
import FreeCAD as App
print("FreeCAD version:", App.Version())
print("Test başarılı!")
"""
    response = await controller.run_script(test_script, "version_test")
    print(f"Output: {response.output}")
    if response.error:
        print(f"Error: {response.error}")
    print(f"Execution time: {response.execution_time_ms:.0f}ms")

    print("\n" + "=" * 60)
    print("✅ Test tamamlandı")
    print("=" * 60)


async def test_mcp_server():
    """MCP sunucusunu test et"""
    print("\n🧪 MCP Server Test")
    print("=" * 60)

    try:
        from mcp_server import FREECAD_AVAILABLE, freecad_controller

        print(f"FreeCAD_available: {FREECAD_AVAILABLE}")
        print(f"FreeCAD Controller: {freecad_controller}")

        if FREECAD_AVAILABLE and freecad_controller:
            # Tool listesini kontrol et
            from mcp_server import get_freecad_tools
            tools = get_freecad_tools()
            print(f"✅ {len(tools)} FreeCAD tool yüklendi")

            # Basit bir tool testi
            print("\n📋 freecad_list_documents testi...")
            from mcp.types import TextContent
            result = await freecad_controller.list_documents()
            print(f"✅ Response: {result.status}")

        else:
            print("⚠️ FreeCAD MCP modülü kullanılamıyor")

    except ImportError as e:
        print(f"⚠️ Import hatası: {e}")

    print("=" * 60)


async def main():
    """Ana test fonksiyonu"""
    print("\n🚀 FreeCAD MCP Entegrasyon Testi\n")

    # Test 1: Controller
    await test_freecad_controller()

    # Test 2: MCP Server
    await test_mcp_server()

    print("\n✅ Tüm testler tamamlandı!\n")


if __name__ == "__main__":
    asyncio.run(main())
