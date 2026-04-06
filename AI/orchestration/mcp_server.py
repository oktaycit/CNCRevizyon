#!/usr/bin/env python3
"""
CNC AI Orchestrator - MCP Server

Bu MCP server, VS Code'taki Cline veya diğer MCP client'ların
AI modellerini paralel olarak kullanmasını sağlar.

Kurulum:
1. requirements.txt'e ekle: mcp[cli]
2. pip install -r requirements.txt
3. Cline MCP ayarlarına bu server'ı ekle

Kullanım:
- Cline'dan "AI'ya sor" komutu ile kullanılabilir
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    import aiohttp
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP kütüphanesi bulunamadı. Yüklemek için: pip install mcp[cli]")


# Proje Bağlamı
PROJECT_CONTEXT = """
PROJE: LiSEC GFB-60/30RE Cam Kesme Makinesi Revizyonu

TEKNİK ÖZELLİKLER:
- Maksimum Cam: 6000 x 3000 mm | Kesim Hızı: 0-80 m/dk
- Hassasiyet: ±0.05 mm (24-bit encoder) | Eksen: 5 (X, Y, Z, Alt, CNC)
- EtherCAT Cycle: 100μs

KONTROL: Delta NC300 CNC | ASDA-A3-E EtherCAT servo | DOP-110CS HMI | R1-EC Uzak I/O

MOTORLAR:
- X: ECMA-L11845 (4.5kW) | Y: ECMA-E11320 (2.0kW) | Z: ECMA-C11010 (1.0kW, Frenli)
- Alt: ECMA-E11320 (2.0kW) | CNC: ECMA-E11315 (1.5kW, IP67)
"""

# Model Ayarları
MODEL_CONFIGS = [
    {
        "id": "qwen3.5-plus",
        "name": "Qwen 3.5 Plus",
        "description": "Genel amaçlı, hızlı yanıt",
        "temperature": 0.7,
        "system_prompt": "Sen endüstriyel otomasyon uzmanı bir AI asistansısın."
    },
    {
        "id": "qwen3-max-2026-01-23",
        "name": "Qwen 3 Max",
        "description": "Karmaşık analizler için",
        "temperature": 0.7,
        "system_prompt": "Sen karmaşık teknik analizler yapan kıdemli bir mühendissin."
    },
    {
        "id": "qwen3-coder-plus",
        "name": "Qwen 3 Coder",
        "description": "Kod yazma için uzmanlaşmış",
        "temperature": 0.3,
        "system_prompt": "Sen endüstriyel otomasyon ve CNC sistemleri konusunda uzman bir yazılım mühendisisin."
    }
]

API_KEY = "sk-sp-1dfff295506a4cbba9c3745dd54e5796"
API_ENDPOINT = "https://coding-intl.dashscope.aliyuncs.com/v1"


@dataclass
class ModelResponse:
    model_id: str
    content: str
    status: str
    latency_ms: float
    error: Optional[str] = None


class DashScopeClient:
    def __init__(self, api_key: str, api_endpoint: str):
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate(
        self,
        model_id: str,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        session: Optional[aiohttp.ClientSession] = None
    ) -> ModelResponse:
        start_time = datetime.now()
        close_session = False
        
        if session is None:
            session = aiohttp.ClientSession()
            close_session = True
        
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            async with session.post(
                f"{self.api_endpoint}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                latency = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    return ModelResponse(
                        model_id=model_id,
                        content=content,
                        status="success",
                        latency_ms=latency
                    )
                else:
                    error_text = await response.text()
                    return ModelResponse(
                        model_id=model_id,
                        content="",
                        status="error",
                        latency_ms=latency,
                        error=f"HTTP {response.status}: {error_text}"
                    )
        except asyncio.TimeoutError:
            return ModelResponse(
                model_id=model_id,
                content="",
                status="timeout",
                latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
                error="Request timeout"
            )
        except Exception as e:
            return ModelResponse(
                model_id=model_id,
                content="",
                status="error",
                latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
                error=str(e)
            )
        finally:
            if close_session:
                await session.close()


class CNCOrchestrator:
    def __init__(self):
        self.client = DashScopeClient(API_KEY, API_ENDPOINT)
        self.models = MODEL_CONFIGS
    
    async def ask_single(
        self,
        question: str,
        model_index: int = 0
    ) -> ModelResponse:
        model = self.models[model_index]
        messages = [
            {"role": "system", "content": model["system_prompt"]},
            {"role": "user", "content": f"{PROJECT_CONTEXT}\n\nSoru: {question}"}
        ]
        return await self.client.generate(
            model["id"], messages, model["temperature"]
        )
    
    async def ask_parallel(
        self,
        question: str
    ) -> List[ModelResponse]:
        messages_template = [
            {"role": "system", "content": m["system_prompt"]},
            {"role": "user", "content": f"{PROJECT_CONTEXT}\n\nSoru: {question}"}
        ]
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.client.generate(
                    m["id"],
                    [
                        {"role": "system", "content": m["system_prompt"]},
                        {"role": "user", "content": f"{PROJECT_CONTEXT}\n\nSoru: {question}"}
                    ],
                    m["temperature"],
                    session=session
                )
                for m in self.models
            ]
            return await asyncio.gather(*tasks)
    
    async def ask_specialized(
        self,
        question: str,
        task_type: str = "general"
    ) -> ModelResponse:
        # Görev tipine göre en uygun modeli seç
        model_mapping = {
            "code": 2,      # coder
            "design": 0,    # general
            "optimize": 2,  # coder
            "debug": 1,     # max
            "plc": 2,       # coder
            "cam": 2,       # coder
            "gcode": 2,     # coder
            "safety": 1,    # max
            "general": 0    # general
        }
        model_index = model_mapping.get(task_type, 0)
        return await self.ask_single(question, model_index)
    
    def format_response(self, responses: List[ModelResponse]) -> str:
        result = []
        for r in responses:
            status = "✅" if r.status == "success" else "❌"
            result.append(f"\n{'='*50}")
            result.append(f"{status} {r.model_id} ({r.latency_ms:.0f}ms)")
            result.append(f"{'='*50}")
            if r.status == "success":
                result.append(r.content)
            else:
                result.append(f"Hata: {r.error}")
        return "\n".join(result)


# MCP Server Tanımı
if MCP_AVAILABLE:
    app = Server("cnc-ai-orchestrator")
    orchestrator = CNCOrchestrator()
    
    @app.list_tools()
    async def list_tools() -> List[Tool]:
        return [
            Tool(
                name="ai_ask",
                description="AI modellerine soru sor (tek model)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "AI'ya sorulacak soru"
                        },
                        "model": {
                            "type": "string",
                            "description": "Model seçimi: qwen3.5-plus, qwen3-max-2026-01-23, qwen3-coder-plus",
                            "default": "qwen3.5-plus"
                        }
                    },
                    "required": ["question"]
                }
            ),
            Tool(
                name="ai_ask_parallel",
                description="Tüm AI modellerine paralel soru sor ve sonuçları karşılaştır",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "AI modellerine sorulacak soru"
                        }
                    },
                    "required": ["question"]
                }
            ),
            Tool(
                name="ai_code",
                description="Kod yazdır (Python, FreeCAD, G-code, PLC)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "Yazılmasını istediğiniz kod"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programlama dili: python, freecad, gcode, plc",
                            "default": "python"
                        }
                    },
                    "required": ["task"]
                }
            ),
            Tool(
                name="ai_debug",
                description="Hata ayıklama - servo alarm, EtherCAT hatası vb.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "error_code": {
                            "type": "string",
                            "description": "Hata kodu veya açıklama"
                        },
                        "axis": {
                            "type": "string",
                            "description": "İlgili eksen: X, Y, Z, Alt, CNC"
                        }
                    },
                    "required": ["error_code"]
                }
            ),
            Tool(
                name="ai_optimize",
                description="Kesim optimizasyonu - yerleşim, hız, yol",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "Optimizasyon görevi"
                        },
                        "material_size": {
                            "type": "string",
                            "description": "Cam boyutu (örn: 6000x3000)"
                        },
                        "part_sizes": {
                            "type": "string",
                            "description": "Parça boyutları (örn: 500x400,300x300)"
                        }
                    },
                    "required": ["task"]
                }
            ),
            Tool(
                name="ai_list_models",
                description="Kullanılabilir AI modellerini listele",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]
    
    @app.call_tool()
    async def call_tool(name: str, arguments: Any) -> List[TextContent]:
        if name == "ai_list_models":
            models_info = "\n".join([
                f"- {m['id']}: {m['description']} (temp: {m['temperature']})"
                for m in MODEL_CONFIGS
            ])
            return [TextContent(type="text", text=f"Kullanılabilir Modeller:\n{models_info}")]
        
        elif name == "ai_ask":
            question = arguments.get("question", "")
            model_id = arguments.get("model", "qwen3.5-plus")
            
            model_index = 0
            for i, m in enumerate(MODEL_CONFIGS):
                if m["id"] == model_id:
                    model_index = i
                    break
            
            response = await orchestrator.ask_single(question, model_index)
            return [TextContent(
                type="text",
                text=f"Model: {response.model_id}\nDurum: {response.status}\nLatency: {response.latency_ms:.0f}ms\n\n{response.content}"
            )]
        
        elif name == "ai_ask_parallel":
            question = arguments.get("question", "")
            responses = await orchestrator.ask_parallel(question)
            formatted = orchestrator.format_response(responses)
            return [TextContent(type="text", text=formatted)]
        
        elif name == "ai_code":
            task = arguments.get("task", "")
            language = arguments.get("language", "python")
            
            task_prompts = {
                "python": "Python fonksiyonu veya script yaz",
                "freecad": "FreeCAD Assembly4 için Python script yaz",
                "gcode": "Delta NC300 için G-kod programı yaz",
                "plc": "Delta NC300 PLC için ladder/ST programı yaz"
            }
            
            full_task = f"{task_prompts.get(language, 'Kod yaz')}: {task}"
            response = await orchestrator.ask_specialized(full_task, "code")
            return [TextContent(
                type="text",
                text=f"Model: {response.model_id}\n\n{response.content}"
            )]
        
        elif name == "ai_debug":
            error_code = arguments.get("error_code", "")
            axis = arguments.get("axis", "")
            
            full_task = f"Hata kodu: {error_code}"
            if axis:
                full_task += f"\nEksen: {axis}"
            
            response = await orchestrator.ask_specialized(full_task, "debug")
            return [TextContent(
                type="text",
                text=f"Model: {response.model_id}\n\n{response.content}"
            )]
        
        elif name == "ai_optimize":
            task = arguments.get("task", "")
            material = arguments.get("material_size", "")
            parts = arguments.get("part_sizes", "")
            
            full_task = f"Görev: {task}"
            if material:
                full_task += f"\nMalzeme: {material}"
            if parts:
                full_task += f"\nParçalar: {parts}"
            
            response = await orchestrator.ask_specialized(full_task, "optimize")
            return [TextContent(
                type="text",
                text=f"Model: {response.model_id}\n\n{response.content}"
            )]
        
        return [TextContent(type="text", text=f"Bilinmeyen tool: {name}")]
    
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )


if __name__ == "__main__":
    if not MCP_AVAILABLE:
        print("MCP kütüphanesi yüklü değil. Yüklemek için:")
        print("  pip install mcp[cli]")
        sys.exit(1)
    
    asyncio.run(main())