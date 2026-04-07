#!/usr/bin/env python3
"""
CNC AI Orchestrator - MCP Server (Enhanced for Lite Plan)

Bu MCP server, VS Code'taki Cline'ın tüm AI modellerini
paralel olarak kullanmasını sağlar.

Kurulum:
1. pip install -r requirements.txt
2. Cline MCP ayarlarında bu server aktif

Kullanım:
- Cline'dan MCP tool'ları ile erişilebilir
"""

import asyncio
import json
import sys
import time
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

KULLANILABİLECEK MODELLER:
- qwen3.5-plus: Genel amaçlı, hızlı
- qwen3-max-2026-01-23: Karmaşık analiz
- qwen3-coder-plus: Kod yazma (Python, FreeCAD, G-code, PLC)
- qwen3-coder-next: İleri düzey kod
- glm-4.7: Alternatif model (Zhipu)
- kimi-k2.5: Uzun doküman (MiniMax)
"""

# Model Ayarları
MODEL_CONFIGS = [
    {
        "id": "qwen3.5-plus",
        "name": "Qwen 3.5 Plus",
        "description": "Genel amaçlı, hızlı yanıt",
        "temperature": 0.7,
        "max_tokens": 2048,
        "system_prompt": "Sen endüstriyel otomasyon uzmanı yardımsever bir AI asistansısın.",
        "use_case": "general"
    },
    {
        "id": "qwen3-max-2026-01-23",
        "name": "Qwen 3 Max",
        "description": "Karmaşık analiz ve problem çözme",
        "temperature": 0.5,
        "max_tokens": 4096,
        "system_prompt": "Sen karmaşık teknik analizler yapan kıdemli bir mühendisisin.",
        "use_case": "complex"
    },
    {
        "id": "qwen3-coder-plus",
        "name": "Qwen 3 Coder",
        "description": "Kod yazma için uzmanlaşmış",
        "temperature": 0.2,
        "max_tokens": 8192,
        "system_prompt": "Sen endüstriyel otomasyon ve CNC sistemleri konusunda uzman bir yazılım mühendisisin. Kod yazarken açık, yorumlu ve best-practice uygularsın.",
        "use_case": "coding"
    },
    {
        "id": "qwen3-coder-next",
        "name": "Qwen 3 Coder Next",
        "description": "İleri düzey kod üretimi",
        "temperature": 0.3,
        "max_tokens": 4096,
        "system_prompt": "Sen ileri düzey kod üretimi yapan, modern tasarım desenleri uygulayan bir AI geliştiricisin.",
        "use_case": "advanced_coding"
    },
    {
        "id": "glm-4.7",
        "name": "GLM 4.7 (Zhipu)",
        "description": "Alternatif model - Çapraz doğrulama",
        "temperature": 0.6,
        "max_tokens": 2048,
        "system_prompt": "Sen çok yönlü bir AI asistansısın. Teknik konularda pratik çözümler sunarsın.",
        "use_case": "validation"
    },
    {
        "id": "kimi-k2.5",
        "name": "Kimi K2.5 (MiniMax)",
        "description": "Uzun bağlam - Dokümantasyon",
        "temperature": 0.5,
        "max_tokens": 4096,
        "system_prompt": "Sen uzun dokümanları analiz eden, özetleyen ve teknik dokümantasyon hazırlayan bir AI asistansısın.",
        "use_case": "documentation"
    }
]

# Görev tipine göre model eşleme
TASK_MODEL_MAPPING = {
    "general": [0],           # qwen3.5-plus
    "code": [2, 3],           # coder-plus, coder-next
    "debug": [2, 1],          # coder-plus, max
    "optimize": [2, 1],       # coder-plus, max
    "design": [0, 1],         # plus, max
    "documentation": [5, 0],  # kimi, plus
    "complex": [1, 0],        # max, plus
    "validation": [4, 5]      # glm, kimi
}

API_KEY = "sk-sp-1dfff295506a4cbba9c3745dd54e5796"
API_ENDPOINT = "https://coding-intl.dashscope.aliyuncs.com/v1"


@dataclass
class ModelResponse:
    model_id: str
    content: str
    status: str
    latency_ms: float
    tokens_used: int = 0
    error: Optional[str] = None


class DashScopeClient:
    def __init__(self, api_key: str, api_endpoint: str):
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-SSE": "enable"
        }

    async def generate(
        self,
        model_id: str,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        session: Optional[aiohttp.ClientSession] = None
    ) -> ModelResponse:
        start_time = time.time()
        close_session = False

        if session is None:
            session = aiohttp.ClientSession()
            close_session = True

        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        try:
            async with session.post(
                f"{self.api_endpoint}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                latency = (time.time() - start_time) * 1000

                if response.status == 200:
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    tokens_used = data.get("usage", {}).get("total_tokens", 0)
                    return ModelResponse(
                        model_id=model_id,
                        content=content,
                        status="success",
                        latency_ms=latency,
                        tokens_used=tokens_used
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
                latency_ms=(time.time() - start_time) * 1000,
                error="Request timeout (120s)"
            )
        except Exception as e:
            return ModelResponse(
                model_id=model_id,
                content="",
                status="error",
                latency_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
        finally:
            if close_session:
                await session.close()


class CNCOrchestrator:
    def __init__(self):
        self.client = DashScopeClient(API_KEY, API_ENDPOINT)
        self.models = MODEL_CONFIGS

    def get_model_indices_for_task(self, task_type: str) -> List[int]:
        """Görev tipine göre model index'lerini döndür"""
        return TASK_MODEL_MAPPING.get(task_type, [0])

    async def ask_single(
        self,
        question: str,
        model_index: int = 0,
        system_prompt_override: Optional[str] = None
    ) -> ModelResponse:
        model = self.models[model_index]
        system_prompt = system_prompt_override or model["system_prompt"]
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{PROJECT_CONTEXT}\n\nSoru: {question}"}
        ]
        return await self.client.generate(
            model["id"],
            messages,
            model["temperature"],
            model["max_tokens"]
        )

    async def ask_parallel(
        self,
        question: str,
        model_indices: Optional[List[int]] = None,
        max_parallel: int = 3
    ) -> List[ModelResponse]:
        """Paralel model çağrısı - Lite plan için optimize edilmiş"""
        if model_indices is None:
            model_indices = list(range(len(self.models)))
        
        # Lite plan için paralellik sınırı
        model_indices = model_indices[:max_parallel]

        async with aiohttp.ClientSession() as session:
            tasks = []
            for idx in model_indices:
                m = self.models[idx]
                messages = [
                    {"role": "system", "content": m["system_prompt"]},
                    {"role": "user", "content": f"{PROJECT_CONTEXT}\n\nSoru: {question}"}
                ]
                tasks.append(
                    self.client.generate(
                        m["id"],
                        messages,
                        m["temperature"],
                        m["max_tokens"],
                        session=session
                    )
                )
            
            # Semaphore ile eşzamanlılığı sınırla
            semaphore = asyncio.Semaphore(max_parallel)
            
            async def limited_task(task):
                async with semaphore:
                    return await task
            
            limited_tasks = [limited_task(t) for t in tasks]
            return await asyncio.gather(*limited_tasks, return_exceptions=True)

    async def ask_smart(
        self,
        question: str,
        task_type: str = "general"
    ) -> List[ModelResponse]:
        """Akıllı model seçimi - Görev tipine göre en uygun modelleri kullan"""
        model_indices = self.get_model_indices_for_task(task_type)
        return await self.ask_parallel(question, model_indices)

    async def ask_with_fallback(
        self,
        question: str,
        primary_model_index: int = 0,
        fallback_indices: Optional[List[int]] = None
    ) -> ModelResponse:
        """Öncelikli model dene, başarısız olursa fallback"""
        if fallback_indices is None:
            fallback_indices = [0]  # Default to first model
        
        # Primary attempt
        response = await self.ask_single(question, primary_model_index)
        if response.status == "success":
            return response
        
        # Fallback attempts
        for idx in fallback_indices:
            response = await self.ask_single(question, idx)
            if response.status == "success":
                return response
        
        return response

    def format_parallel_response(self, responses: List[ModelResponse]) -> str:
        """Paralel yanıtları formatla"""
        result = []
        result.append(f"📊 **Paralel Model Yanıtları** ({len(responses)} model)\n")
        
        for i, r in enumerate(responses, 1):
            status_icon = "✅" if r.status == "success" else "❌"
            result.append(f"\n{'='*60}")
            result.append(f"{status_icon} **{i}. {r.model_id}**")
            result.append(f"{'='*60}")
            result.append(f"⏱️ Latency: {r.latency_ms:.0f}ms")
            if r.tokens_used > 0:
                result.append(f"📝 Tokens: {r.tokens_used}")
            
            if r.status == "success":
                result.append(f"\n{r.content}")
            else:
                result.append(f"\n⚠️ Hata: {r.error}")
        
        return "\n".join(result)

    def compare_responses(self, responses: List[ModelResponse]) -> str:
        """Yanıtları karşılaştırma tablosu olarak formatla"""
        successful = [r for r in responses if r.status == "success"]
        
        if not successful:
            return "Tüm modeller başarısız oldu."
        
        lines = ["## 📊 Model Karşılaştırması\n"]
        lines.append("| Model | Latency | Tokens | Yanıt (Özet) |")
        lines.append("|-------|---------|--------|--------------|")
        
        for r in successful:
            content_preview = r.content[:80].replace("\n", " ")
            if len(r.content) > 80:
                content_preview += "..."
            lines.append(
                f"| {r.model_id} | {r.latency_ms:.0f}ms | {r.tokens_used} | {content_preview} |"
            )
        
        lines.append("\n\n## 🏆 En Hızlı: " + min(successful, key=lambda r: r.latency_ms).model_id)
        
        return "\n".join(lines)


# MCP Server Tanımı
if MCP_AVAILABLE:
    app = Server("cnc-ai-orchestrator")
    orchestrator = CNCOrchestrator()

    @app.list_tools()
    async def list_tools() -> List[Tool]:
        return [
            Tool(
                name="ai_ask",
                description="Tek bir AI modeline soru sor",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "AI'ya sorulacak soru"},
                        "model": {"type": "string", "description": "Model: qwen3.5-plus, qwen3-max-2026-01-23, qwen3-coder-plus, qwen3-coder-next, glm-4.7, kimi-k2.5", "default": "qwen3.5-plus"}
                    },
                    "required": ["question"]
                }
            ),
            Tool(
                name="ai_ask_parallel",
                description="Tüm modellere paralel soru sor (max 3 aynı anda)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "AI modellerine sorulacak soru"},
                        "max_parallel": {"type": "integer", "description": "Maksimum paralel model sayısı", "default": 3, "maximum": 6}
                    },
                    "required": ["question"]
                }
            ),
            Tool(
                name="ai_ask_smart",
                description="Görev tipine göre en uygun modelleri otomatik seç ve paralel çalıştır",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "Soru veya görev"},
                        "task_type": {"type": "string", "description": "Görev tipi: general, code, debug, optimize, design, documentation, complex, validation", "default": "general"}
                    },
                    "required": ["question", "task_type"]
                }
            ),
            Tool(
                name="ai_code",
                description="Kod yazdır (Python, FreeCAD, G-code, PLC) - 2 model paralel",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task": {"type": "string", "description": "Yazılmasını istediğiniz kod"},
                        "language": {"type": "string", "description": "Dil: python, freecad, gcode, plc, stir", "default": "python"}
                    },
                    "required": ["task"]
                }
            ),
            Tool(
                name="ai_debug",
                description="Hata ayıklama - 2 model paralel analiz",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "error_code": {"type": "string", "description": "Hata kodu veya açıklama"},
                        "axis": {"type": "string", "description": "İlgili eksen: X, Y, Z, Alt, CNC"}
                    },
                    "required": ["error_code"]
                }
            ),
            Tool(
                name="ai_optimize",
                description="Kesim optimizasyonu - 2 model paralel",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task": {"type": "string", "description": "Optimizasyon görevi"},
                        "material_size": {"type": "string", "description": "Malzeme boyutu (örn: 6000x3000)"},
                        "part_sizes": {"type": "string", "description": "Parça boyutları (örn: 500x400,300x300)"}
                    },
                    "required": ["task"]
                }
            ),
            Tool(
                name="ai_compare",
                description="Modeller arası karşılaştırma - Tablo formatında",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "Karşılaştırılacak soru"}
                    },
                    "required": ["question"]
                }
            ),
            Tool(
                name="ai_list_models",
                description="Kullanılabilir AI modellerini ve kullanım alanlarını listele",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]

    @app.call_tool()
    async def call_tool(name: str, arguments: Any) -> List[TextContent]:
        if name == "ai_list_models":
            models_info = "**📋 Kullanılabilir AI Modelleri (Alibaba Cloud Lite Plan)**\n\n"
            for i, m in enumerate(MODEL_CONFIGS, 1):
                models_info += f"**{i}. {m['name']}** (`{m['id']}`)\n"
                models_info += f"   - {m['description']}\n"
                models_info += f"   - Kullanım: {m['use_case']}\n"
                models_info += f"   - Temp: {m['temperature']} | Max Tokens: {m['max_tokens']}\n\n"
            return [TextContent(type="text", text=models_info)]

        elif name == "ai_ask":
            question = arguments.get("question", "")
            model_id = arguments.get("model", "qwen3.5-plus")

            model_index = 0
            for i, m in enumerate(MODEL_CONFIGS):
                if m["id"] == model_id:
                    model_index = i
                    break

            response = await orchestrator.ask_single(question, model_index)
            result = f"**Model:** {response.model_id}\n"
            result += f"**Durum:** {response.status}\n"
            result += f"**⏱️ Latency:** {response.latency_ms:.0f}ms\n"
            if response.tokens_used > 0:
                result += f"**📝 Tokens:** {response.tokens_used}\n\n"
            result += response.content if response.status == "success" else f"⚠️ Hata: {response.error}"
            return [TextContent(type="text", text=result)]

        elif name == "ai_ask_parallel":
            question = arguments.get("question", "")
            max_parallel = min(arguments.get("max_parallel", 3), 6)
            responses = await orchestrator.ask_parallel(question, max_parallel=max_parallel)
            
            # Handle exceptions
            formatted = []
            for i, r in enumerate(responses):
                if isinstance(r, Exception):
                    formatted.append(ModelResponse(
                        model_id=f"model_{i}",
                        content="",
                        status="error",
                        latency_ms=0,
                        error=str(r)
                    ))
                else:
                    formatted.append(r)
            
            result = orchestrator.format_parallel_response(formatted)
            return [TextContent(type="text", text=result)]

        elif name == "ai_ask_smart":
            question = arguments.get("question", "")
            task_type = arguments.get("task_type", "general")
            responses = await orchestrator.ask_smart(question, task_type)
            
            formatted = []
            for r in responses:
                if isinstance(r, Exception):
                    formatted.append(ModelResponse(
                        model_id="unknown",
                        content="",
                        status="error",
                        latency_ms=0,
                        error=str(r)
                    ))
                else:
                    formatted.append(r)
            
            result = orchestrator.format_parallel_response(formatted)
            return [TextContent(type="text", text=result)]

        elif name == "ai_code":
            task = arguments.get("task", "")
            language = arguments.get("language", "python")

            task_prompts = {
                "python": "Python fonksiyonu veya script yaz",
                "freecad": "FreeCAD Assembly4 için Python script yaz",
                "gcode": "Delta NC300 için G-kod programı yaz",
                "plc": "Delta NC300 PLC için ladder/ST programı yaz",
                "stir": "ST (Structured Text) PLC kodu yaz"
            }

            full_task = f"{task_prompts.get(language, 'Kod yaz')}: {task}"
            responses = await orchestrator.ask_smart(full_task, "code")
            
            formatted = []
            for r in responses:
                if isinstance(r, Exception):
                    formatted.append(ModelResponse(
                        model_id="unknown",
                        content="",
                        status="error",
                        latency_ms=0,
                        error=str(r)
                    ))
                else:
                    formatted.append(r)
            
            result = orchestrator.format_parallel_response(formatted)
            return [TextContent(type="text", text=result)]

        elif name == "ai_debug":
            error_code = arguments.get("error_code", "")
            axis = arguments.get("axis", "")

            full_task = f"Hata kodu: {error_code}"
            if axis:
                full_task += f"\nEksen: {axis}"

            responses = await orchestrator.ask_smart(full_task, "debug")
            
            formatted = []
            for r in responses:
                if isinstance(r, Exception):
                    formatted.append(ModelResponse(
                        model_id="unknown",
                        content="",
                        status="error",
                        latency_ms=0,
                        error=str(r)
                    ))
                else:
                    formatted.append(r)
            
            result = orchestrator.format_parallel_response(formatted)
            return [TextContent(type="text", text=result)]

        elif name == "ai_optimize":
            task = arguments.get("task", "")
            material = arguments.get("material_size", "")
            parts = arguments.get("part_sizes", "")

            full_task = f"Görev: {task}"
            if material:
                full_task += f"\nMalzeme: {material}"
            if parts:
                full_task += f"\nParçalar: {parts}"

            responses = await orchestrator.ask_smart(full_task, "optimize")
            
            formatted = []
            for r in responses:
                if isinstance(r, Exception):
                    formatted.append(ModelResponse(
                        model_id="unknown",
                        content="",
                        status="error",
                        latency_ms=0,
                        error=str(r)
                    ))
                else:
                    formatted.append(r)
            
            result = orchestrator.format_parallel_response(formatted)
            return [TextContent(type="text", text=result)]

        elif name == "ai_compare":
            question = arguments.get("question", "")
            responses = await orchestrator.ask_parallel(question)
            
            formatted = []
            for r in responses:
                if isinstance(r, Exception):
                    formatted.append(ModelResponse(
                        model_id="unknown",
                        content="",
                        status="error",
                        latency_ms=0,
                        error=str(r)
                    ))
                else:
                    formatted.append(r)
            
            result = orchestrator.compare_responses(formatted)
            return [TextContent(type="text", text=result)]

        return [TextContent(type="text", text=f"⚠️ Bilinmeyen tool: {name}")]

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
