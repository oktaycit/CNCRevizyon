#!/usr/bin/env python3
"""
FreeCAD MCP Integration Module

FreeCAD'i MCP üzerinden kontrol etmek için Python API ve CLI desteği.

Kullanım:
- FreeCAD Python API ile doğrudan modelleme
- FreeCAD CLI ile script çalıştırma
- Assembly4 entegrasyonu
- STEP/DXF/STL export
"""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# Proje FreeCAD dizini
PROJECT_ROOT = "/Users/oktaycit/Projeler/CNCRevizyon"
FREECAD_DIR = os.path.join(PROJECT_ROOT, "CAD", "FreeCAD")
FREECAD_EXPORTS_DIR = os.path.join(FREECAD_DIR, "07_Exports")

# FreeCAD CLI komutu (macOS)
FREECAD_CLI = "FreeCAD"


@dataclass
class FreeCADResponse:
    status: str
    output: str
    error: Optional[str] = None
    execution_time_ms: float = 0
    file_path: Optional[str] = None


class FreeCADController:
    """FreeCAD MCP Controller - API ve CLI desteği"""

    def __init__(self):
        self.freecad_path = FREECAD_DIR
        self.exports_path = FREECAD_EXPORTS_DIR
        self._ensure_directories()

    def _ensure_directories(self):
        """Gerekli dizinleri oluştur"""
        dirs = [
            self.freecad_path,
            self.exports_path,
            os.path.join(self.exports_path, "STEP"),
            os.path.join(self.exports_path, "DXF"),
            os.path.join(self.exports_path, "STL"),
            os.path.join(self.exports_path, "PNG"),
        ]
        for d in dirs:
            os.makedirs(d, exist_ok=True)

    async def run_script(
        self,
        script_content: str,
        script_name: str = "temp_script",
        timeout: int = 120
    ) -> FreeCADResponse:
        """
        FreeCAD CLI ile Python script çalıştır

        Args:
            script_content: Çalıştırılacak Python kodu
            script_name: Script dosya adı
            timeout: Maksimum çalışma süresi (saniye)

        Returns:
            FreeCADResponse: Çalıştırma sonucu
        """
        import time
        start_time = time.time()

        # Geçici script dosyası oluştur
        script_path = os.path.join(
            tempfile.gettempdir(),
            f"freecad_mcp_{script_name}_{int(time.time())}.py"
        )

        try:
            # Script'i yaz
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            # FreeCAD CLI ile çalıştır
            cmd = [
                FREECAD_CLI,
                "--console",  # GUI olmadan çalıştır
                "--script",
                script_path
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.freecad_path
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )

                execution_time = (time.time() - start_time) * 1000

                return FreeCADResponse(
                    status="success" if process.returncode == 0 else "error",
                    output=stdout.decode("utf-8") if stdout else "",
                    error=stderr.decode("utf-8") if stderr else None,
                    execution_time_ms=execution_time
                )

            except asyncio.TimeoutError:
                process.kill()
                await process.communicate()
                return FreeCADResponse(
                    status="timeout",
                    output="",
                    error=f"Script {timeout} saniye içinde tamamlanmadı",
                    execution_time_ms=timeout * 1000
                )

        except Exception as e:
            return FreeCADResponse(
                status="error",
                output="",
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000
            )

        finally:
            # Geçici dosyayı temizle
            if os.path.exists(script_path):
                os.remove(script_path)

    async def open_document(
        self,
        file_path: str,
        readonly: bool = False
    ) -> FreeCADResponse:
        """FreeCAD dosyası aç"""

        # Mutlak yol oluştur
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.freecad_path, file_path)

        script = f"""#!/usr/bin/env python3
import FreeCAD as App
import sys

try:
    doc = App.open("{file_path}")
    print(f"✅ Dosya açıldı: {{doc.Name}}")
    print(f"📄 Label: {{doc.Label}}")
    print(f"📁 Objeler: {{len(doc.Objects)}}")

    # Objeleri listele
    for obj in doc.Objects:
        print(f"   - {{obj.Name}} ({{obj.Label}}) [{{obj.TypeId}}]")

except Exception as e:
    print(f"❌ Hata: {{e}}", file=sys.stderr)
    sys.exit(1)
"""

        return await self.run_script(script, "open_document")

    async def create_part(
        self,
        part_type: str,
        parameters: Dict[str, Any],
        output_file: str
    ) -> FreeCADResponse:
        """
        Yeni bir parça oluştur

        Args:
            part_type: Parça tipi (box, cylinder, sphere, cone, torus)
            parameters: Boyut parametreleri
            output_file: Kayıt dosya adı
        """

        script = f"""#!/usr/bin/env python3
import FreeCAD as App
import Part

# Yeni document oluştur
doc = App.newDocument("MCP_Part")

# Parça tipi: {part_type}
try:
"""

        if part_type == "box":
            script += f"""
    length = {parameters.get('length', 100)}
    width = {parameters.get('width', 50)}
    height = {parameters.get('height', 30)}
    box = Part.makeBox(length, width, height)
    shape_obj = doc.addObject("Part::Feature", "Box")
    shape_obj.Shape = box
"""

        elif part_type == "cylinder":
            script += f"""
    radius = {parameters.get('radius', 25)}
    height = {parameters.get('height', 100)}
    cylinder = Part.makeCylinder(radius, height)
    shape_obj = doc.addObject("Part::Feature", "Cylinder")
    shape_obj.Shape = cylinder
"""

        elif part_type == "sphere":
            script += f"""
    radius = {parameters.get('radius', 25)}
    sphere = Part.makeSphere(radius)
    shape_obj = doc.addObject("Part::Feature", "Sphere")
    shape_obj.Shape = sphere
"""

        elif part_type == "cone":
            script += f"""
    radius1 = {parameters.get('radius1', 30)}
    radius2 = {parameters.get('radius2', 15)}
    height = {parameters.get('height', 100)}
    cone = Part.makeCone(radius1, radius2, height)
    shape_obj = doc.addObject("Part::Feature", "Cone")
    shape_obj.Shape = cone
"""

        script += f"""
    # STEP export
    output_path = "{os.path.join(self.exports_path, 'STEP', output_file)}"
    Part.export(shape_obj, output_path)
    print(f"✅ Parça oluşturuldu: {part_type}")
    print(f"📁 Export: {{output_path}}")

    # Document'i kaydet
    fcstd_path = "{os.path.join(self.freecad_path, output_file.replace('.stp', '.FCStd'))}"
    doc.saveAs(fcstd_path)
    print(f"💾 Kaydedildi: {{fcstd_path}}")

except Exception as e:
    import sys
    print(f"❌ Hata: {{e}}", file=sys.stderr)
    sys.exit(1)
"""

        return await self.run_script(script, f"create_{part_type}")

    async def export_file(
        self,
        input_file: str,
        output_format: str,
        output_file: Optional[str] = None
    ) -> FreeCADResponse:
        """
        FreeCAD dosyasını export et

        Args:
            input_file: Kaynak FCStd dosyası
            output_format: STEP, DXF, STL, PNG
            output_file: Çıktı dosya adı (opsiyonel)
        """

        if output_format.upper() not in ["STEP", "DXF", "STL", "PNG"]:
            return FreeCADResponse(
                status="error",
                output="",
                error=f"Desteklenmeyen format: {output_format}"
            )

        # Mutlak yol oluştur
        if not os.path.isabs(input_file):
            input_file = os.path.join(self.freecad_path, input_file)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not output_file:
            base_name = os.path.basename(input_file).replace(".FCStd", "")
            output_file = f"{base_name}_{timestamp}.{output_format.lower()}"

        script = f"""#!/usr/bin/env python3
import FreeCAD as App
import Part
import sys

try:
    # Dosyayı aç
    doc = App.open("{input_file}")
    print(f"✅ Dosya açıldı: {{doc.Label}}")

    # Export dizini
    export_dir = "{os.path.join(self.exports_path, output_format.upper())}"

    # Tüm objeleri export et
    exported_files = []
    for obj in doc.Objects:
        output_path = os.path.join(export_dir, "{output_file}")
        if len(doc.Objects) > 1:
            base_name = os.path.splitext("{output_file}")[0]
            ext = os.path.splitext("{output_file}")[1]
            output_path = os.path.join(export_dir, f"{{obj.Name}}_{{base_name}}{{ext}}")

"""

        if output_format.upper() == "STEP":
            script += """
        Part.export(obj, output_path)
"""
        elif output_format.upper() == "STL":
            script += """
        Part.export(obj, output_path)
"""
        elif output_format.upper() == "DXF":
            script += """
        # DXF için Mesh kullan
        import Mesh
        mesh = Mesh.PartMesh(obj.Shape)
        Mesh.export(mesh, output_path)
"""
        elif output_format.upper() == "PNG":
            script += """
        # PNG render için
        import FreeCADGui as Gui
        Gui.ActiveDocument = doc
        Gui.SendMsgToActiveView("ViewFit")
        Gui.activeDocument().activeView().saveImage(output_path, 1920, 1080, "Current")
"""

        script += f"""
        exported_files.append(output_path)
        print(f"✅ Export: {{output_path}}")

    print(f"\\n📊 Toplam {{len(exported_files)}} dosya export edildi")

except Exception as e:
    print(f"❌ Hata: {{e}}", file=sys.stderr)
    sys.exit(1)
"""

        return await self.run_script(script, f"export_{output_format.lower()}")

    async def list_documents(self) -> FreeCADResponse:
        """FreeCAD dizinindeki tüm .FCStd dosyalarını listele"""

        script = f"""#!/usr/bin/env python3
import os

freecad_dir = "{self.freecad_path}"

print("📁 FreeCAD Dosyaları:")
print("=" * 60)

fcstd_files = []
for root, dirs, files in os.walk(freecad_dir):
    for file in files:
        if file.endswith(".FCStd") and not file.endswith(".FCBak"):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, freecad_dir)
            fcstd_files.append(rel_path)
            print(f"  📄 {{rel_path}}")

print("=" * 60)
print(f"Toplam: {{len(fcstd_files)}} dosya")

# JSON output için
import json
print("\\n---JSON_START---")
print(json.dumps(fcstd_files))
print("---JSON_END---")
"""

        return await self.run_script(script, "list_documents")

    async def get_assembly_info(self, assembly_file: str) -> FreeCADResponse:
        """Assembly4 dosyasından bilgi al"""

        if not os.path.isabs(assembly_file):
            assembly_file = os.path.join(self.freecad_path, assembly_file)

        script = f"""#!/usr/bin/env python3
import FreeCAD as App
import sys

try:
    doc = App.open("{assembly_file}")
    print("📊 Assembly Bilgisi")
    print("=" * 60)

    # Assembly4 kontrolü
    has_assembly4 = False
    for obj in doc.Objects:
        if hasattr(obj, 'AssemblyType'):
            has_assembly4 = True
            print(f"✅ Assembly4 Tespit Edildi")
            print(f"   Type: {{obj.AssemblyType}}")
            break

    if not has_assembly4:
        print("⚠️ Assembly4 bulunamadı")

    # Objeleri listele
    print(f"\\n📁 Toplam Obje: {{len(doc.Objects)}}")
    for obj in doc.Objects:
        print(f"   - {{obj.Name}}: {{obj.Label}} ({{obj.TypeId}})")

    # Bağlantıları bul
    print("\\n🔗 Bağlantılar:")
    for obj in doc.Objects:
        if hasattr(obj, 'Constraints') and obj.Constraints:
            print(f"   📌 {{obj.Name}}: {{len(obj.Constraints)}} constraint")

except Exception as e:
    print(f"❌ Hata: {{e}}", file=sys.stderr)
    sys.exit(1)
"""

        return await self.run_script(script, "assembly_info")

    async def create_assembly4_part(
        self,
        part_name: str,
        part_type: str,
        parameters: Dict[str, Any],
        assembly_file: str
    ) -> FreeCADResponse:
        """
        Assembly4 montajına yeni parça ekle

        Args:
            part_name: Parça adı
            part_type: Parça tipi
            parameters: Boyut parametreleri
            assembly_file: Hedef Assembly4 dosyası
        """

        if not os.path.isabs(assembly_file):
            assembly_file = os.path.join(self.freecad_path, assembly_file)

        script = f"""#!/usr/bin/env python3
import FreeCAD as App
import Part
import sys

try:
    # Assembly dosyasını aç
    doc = App.open("{assembly_file}")
    print(f"✅ Assembly açıldı: {{doc.Label}}")

    # Yeni parça oluştur
"""

        if part_type == "box":
            script += f"""
    box = Part.makeBox(
        {parameters.get('length', 100)},
        {parameters.get('width', 50)},
        {parameters.get('height', 30)}
    )
    shape_obj = doc.addObject("Part::Feature", "{part_name}")
    shape_obj.Shape = box
"""

        elif part_type == "cylinder":
            script += f"""
    cylinder = Part.makeCylinder(
        {parameters.get('radius', 25)},
        {parameters.get('height', 100)}
    )
    shape_obj = doc.addObject("Part::Feature", "{part_name}")
    shape_obj.Shape = cylinder
"""

        script += f"""
    # Assembly4 Link oluştur
    link_obj = doc.addObject("Part::FeaturePython", "{part_name}_Link")
    link_obj.Label = "{part_name} (Link)"

    # Document'i kaydet
    doc.save()
    print(f"✅ Parça eklendi: {part_name}")
    print(f"💾 Assembly kaydedildi")

except Exception as e:
    print(f"❌ Hata: {{e}}", file=sys.stderr)
    sys.exit(1)
"""

        return await self.run_script(script, f"assembly4_{part_name}")


# MCP Tool tanımları için helper fonksiyonlar
def get_freecad_tools():
    """FreeCAD MCP tool tanımlarını döndür"""
    from mcp.types import Tool

    return [
        Tool(
            name="freecad_run_script",
            description="FreeCAD CLI ile Python script çalıştır",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "Çalıştırılacak Python script içeriği"
                    },
                    "script_name": {
                        "type": "string",
                        "description": "Script adı",
                        "default": "temp_script"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Maksimum çalışma süresi (saniye)",
                        "default": 120
                    }
                },
                "required": ["script"]
            }
        ),
        Tool(
            name="freecad_open",
            description="FreeCAD dosyası aç ve içeriğini listele",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Açılacak .FCStd dosya yolu"
                    },
                    "readonly": {
                        "type": "boolean",
                        "description": "Salt okunur aç",
                        "default": False
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="freecad_create_part",
            description="Yeni 3D parça oluştur (box, cylinder, sphere, cone)",
            inputSchema={
                "type": "object",
                "properties": {
                    "part_type": {
                        "type": "string",
                        "description": "Parça tipi: box, cylinder, sphere, cone",
                        "enum": ["box", "cylinder", "sphere", "cone"]
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Boyut parametreleri"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Çıktı dosya adı"
                    }
                },
                "required": ["part_type", "parameters", "output_file"]
            }
        ),
        Tool(
            name="freecad_export",
            description="FreeCAD dosyasını export et (STEP, DXF, STL, PNG)",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string",
                        "description": "Kaynak .FCStd dosyası"
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Export formatı",
                        "enum": ["STEP", "DXF", "STL", "PNG"]
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Çıktı dosya adı (opsiyonel)"
                    }
                },
                "required": ["input_file", "output_format"]
            }
        ),
        Tool(
            name="freecad_list_documents",
            description="FreeCAD dizinindeki tüm dosyaları listele",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="freecad_assembly_info",
            description="Assembly4 dosyasından bilgi al",
            inputSchema={
                "type": "object",
                "properties": {
                    "assembly_file": {
                        "type": "string",
                        "description": "Assembly4 .FCStd dosya yolu"
                    }
                },
                "required": ["assembly_file"]
            }
        ),
        Tool(
            name="freecad_assembly4_add_part",
            description="Assembly4 montajına yeni parça ekle",
            inputSchema={
                "type": "object",
                "properties": {
                    "part_name": {
                        "type": "string",
                        "description": "Parça adı"
                    },
                    "part_type": {
                        "type": "string",
                        "description": "Parça tipi: box, cylinder",
                        "enum": ["box", "cylinder"]
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Boyut parametreleri"
                    },
                    "assembly_file": {
                        "type": "string",
                        "description": "Hedef Assembly4 dosyası"
                    }
                },
                "required": ["part_name", "part_type", "parameters", "assembly_file"]
            }
        )
    ]


async def handle_freecad_tool(name: str, arguments: Any, controller: FreeCADController):
    """FreeCAD MCP tool çağrılarını işle"""
    from mcp.types import TextContent

    if name == "freecad_list_documents":
        response = await controller.list_documents()
        return [TextContent(type="text", text=f"📁 FreeCAD Dosyaları:\n{response.output}")]

    elif name == "freecad_open":
        file_path = arguments.get("file_path", "")
        readonly = arguments.get("readonly", False)
        response = await controller.open_document(file_path, readonly)
        return [TextContent(type="text", text=f"📄 FreeCAD Dosyası:\n{response.output}")]

    elif name == "freecad_create_part":
        part_type = arguments.get("part_type", "box")
        parameters = arguments.get("parameters", {})
        output_file = arguments.get("output_file", "part.stp")
        response = await controller.create_part(part_type, parameters, output_file)
        return [TextContent(type="text", text=f"🔧 Parça Oluşturma:\n{response.output}")]

    elif name == "freecad_export":
        input_file = arguments.get("input_file", "")
        output_format = arguments.get("output_format", "STEP")
        output_file = arguments.get("output_file", "")
        response = await controller.export_file(input_file, output_format, output_file)
        return [TextContent(type="text", text=f"📤 Export:\n{response.output}")]

    elif name == "freecad_assembly_info":
        assembly_file = arguments.get("assembly_file", "")
        response = await controller.get_assembly_info(assembly_file)
        return [TextContent(type="text", text=f"🔩 Assembly Bilgisi:\n{response.output}")]

    elif name == "freecad_assembly4_add_part":
        part_name = arguments.get("part_name", "")
        part_type = arguments.get("part_type", "box")
        parameters = arguments.get("parameters", {})
        assembly_file = arguments.get("assembly_file", "")
        response = await controller.create_assembly4_part(
            part_name, part_type, parameters, assembly_file
        )
        return [TextContent(type="text", text=f"🔩 Assembly4 Parça:\n{response.output}")]

    elif name == "freecad_run_script":
        script = arguments.get("script", "")
        script_name = arguments.get("script_name", "temp_script")
        timeout = arguments.get("timeout", 120)
        response = await controller.run_script(script, script_name, timeout)
        return [TextContent(type="text", text=f"🐍 Script Çalıştırma:\n{response.output}")]

    return [TextContent(type="text", text=f"⚠️ Bilinmeyen FreeCAD tool: {name}")]


# Test fonksiyonu
async def test_freecad_mcp():
    """FreeCAD MCP modülünü test et"""
    print("🧪 FreeCAD MCP Test")
    print("=" * 60)

    controller = FreeCADController()

    # Test 1: Dizin listeleme
    print("\n📁 Test 1: Dizin listeleme")
    response = await controller.list_documents()
    print(response.output)

    # Test 2: Basit parça oluşturma
    print("\n🔧 Test 2: Kutu oluşturma")
    response = await controller.create_part(
        "box",
        {"length": 100, "width": 50, "height": 30},
        "test_box.stp"
    )
    print(response.output)

    print("\n" + "=" * 60)
    print("✅ Test tamamlandı")


if __name__ == "__main__":
    asyncio.run(test_freecad_mcp())
