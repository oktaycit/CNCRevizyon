#!/usr/bin/env python3
"""
CNC AI Orchestrator - MCP Server (Enhanced for Lite Plan)

Bu MCP server, VS Code'taki Cline'ın tüm AI modellerini
paralel olarak kullanmasını sağlar.

FreeCAD Entegrasyonu:
- FreeCAD CLI ile script çalıştırma
- FreeCAD Python API ile modelleme
- Assembly4 desteği
- STEP/DXF/STL/PNG export

Kurulum:
1. pip install -r requirements.txt
2. Cline MCP ayarlarında bu server aktif

Kullanım:
- Cline'dan MCP tool'ları ile erişilebilir
"""

import asyncio
import json
import re
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

# FreeCAD MCP modülünü içe aktar
try:
    from freecad_mcp import FreeCADController, get_freecad_tools, handle_freecad_tool
    FREECAD_AVAILABLE = True
except ImportError:
    FREECAD_AVAILABLE = False
    print("FreeCAD MCP modülü bulunamadı (freecad_mcp.py)")


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
- glm-5: Eleştirel review ve doğrulama
- kimi-k2.5: Uzun doküman ve teslim notları
- MiniMax-M2.5: Alternatif çözüm ve ikinci görüş
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
        "id": "glm-5",
        "name": "GLM 5",
        "description": "Eleştirel review ve çapraz doğrulama",
        "temperature": 0.4,
        "max_tokens": 4096,
        "system_prompt": "Sen teknik review, risk analizi ve doğrulama konusunda uzman bir AI asistansısın.",
        "use_case": "validation"
    },
    {
        "id": "kimi-k2.5",
        "name": "Kimi K2.5",
        "description": "Uzun bağlam - Dokümantasyon",
        "temperature": 0.5,
        "max_tokens": 4096,
        "system_prompt": "Sen uzun dokümanları analiz eden, özetleyen ve teknik dokümantasyon hazırlayan bir AI asistansısın.",
        "use_case": "documentation"
    },
    {
        "id": "MiniMax-M2.5",
        "name": "MiniMax M2.5",
        "description": "Alternatif yaklaşım ve ikinci görüş",
        "temperature": 0.5,
        "max_tokens": 4096,
        "system_prompt": "Sen alternatif çözüm varyantları ve ikinci görüş üretimi konusunda uzman bir teknik AI asistansısın.",
        "use_case": "alternate"
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
    "complex": [1, 4],        # max, glm
    "validation": [4, 6],     # glm, minimax
    "review": [4, 6],         # glm, minimax
    "alternate": [6, 0]       # minimax, plus
}


MODEL_NAME_ALIASES = {
    "qwen35": "qwen3.5-plus",
    "qwen3.5": "qwen3.5-plus",
    "plus": "qwen3.5-plus",
    "max": "qwen3-max-2026-01-23",
    "coder": "qwen3-coder-plus",
    "next": "qwen3-coder-next",
    "glm": "glm-5",
    "glm5": "glm-5",
    "kimi": "kimi-k2.5",
    "minimax": "MiniMax-M2.5",
}


COMMAND_PATTERNS = {
    "code": [
        "kod yaz", "script yaz", "fonksiyon yaz", "implement", "uygula",
        "patch", "refactor", "freecad script", "gcode yaz", "plc yaz"
    ],
    "debug": [
        "debug", "hata", "hata ayıkla", "çök", "crash", "neden", "kök neden",
        "alarm", "sorun", "bozul", "regresyon"
    ],
    "optimize": [
        "optimize", "iyileştir", "hızlandır", "performans", "verim", "nesting",
        "optimizasyon", "fire azalt"
    ],
    "design": [
        "tasarla", "tasarım", "braket", "mekanik", "cad", "montaj", "yerleşim"
    ],
    "documentation": [
        "doküman", "readme", "özet", "teslim notu", "açıkla", "kılavuz", "rapor"
    ],
    "complex": [
        "analiz", "karşılaştır", "tradeoff", "mimari", "strateji", "plan",
        "yaklaşım", "incele"
    ],
    "validation": [
        "review", "kontrol et", "doğrula", "risk", "denetle", "eleştir",
        "eksik", "test açığı"
    ],
    "review": [
        "code review", "incele", "riskleri bul", "bulgular", "bug bul",
        "regresyon kontrol"
    ],
    "alternate": [
        "alternatif", "başka yaklaşım", "ikinci görüş", "varyant"
    ]
}


PIPELINE_TRIGGER_PAIRS = [
    ("incele", "uygula"),
    ("analiz", "uygula"),
    ("analiz", "düzelt"),
    ("debug", "düzelt"),
    ("incele", "düzelt"),
    ("review", "uygula"),
]


DOMAIN_PATTERNS = {
    "cad": [
        "freecad", "cad", "assembly", "montaj", "braket", "mekanik",
        "step", "stp", "dxf"
    ],
    "electrical": [
        "electrical", "şema", "schema", "wiring", "sto", "ethercat", "r1-ec",
        "terminal", "i/o", "io", "pilz"
    ],
    "firmware": [
        "firmware", "nc300", "register", "simulator", "ladder", "plc",
        "structured text", "st", "servo alarm"
    ],
    "ai": [
        "ai", "gcode", "nesting", "optimizer", "path planner", "orchestrator",
        "glasscutting", "model", "prompt"
    ],
    "documentation": [
        "readme", "doküman", "rapor", "kılavuz", "delivery", "teslim notu", "özet"
    ],
}


OUTPUT_PATTERNS = {
    "review": [
        "review", "incele", "riskleri bul", "bulgular", "bug bul", "regresyon",
        "kontrol et"
    ],
    "patch": [
        "düzelt", "uygula", "patch", "refactor", "ekle", "güncelle", "değiştir"
    ],
    "plan": [
        "plan", "yaklaşım", "strateji", "aşamalar", "nasıl yapalım"
    ],
    "report": [
        "rapor", "özet", "teslim notu", "karşılaştırma", "dokümante et", "readme"
    ],
}


PATH_HINT_PATTERN = re.compile(
    r"(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+(?:\.[A-Za-z0-9_.-]+)?|"
    r"(?:AI|CAD|Electrical|Firmware|Documentation|Delivery)/[^\s,;:]+"
)


def normalize_model_name(model_name: str) -> str:
    """Normalize short aliases to model ids."""
    return MODEL_NAME_ALIASES.get(model_name.strip().lower(), model_name.strip())


def detect_task_type(command: str) -> str:
    """Detect the dominant task type from a user command."""
    lowered = command.lower()
    scores = {task_type: 0 for task_type in COMMAND_PATTERNS}

    for task_type, patterns in COMMAND_PATTERNS.items():
        for pattern in patterns:
            if pattern in lowered:
                scores[task_type] += 1

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    best_task, best_score = ranked[0]
    return best_task if best_score > 0 else "general"


def detect_domains(command: str, file_paths: List[str]) -> List[str]:
    """Detect relevant repo domains from keywords and referenced paths."""
    lowered = command.lower()
    detected = set()

    for domain, patterns in DOMAIN_PATTERNS.items():
        if any(pattern in lowered for pattern in patterns):
            detected.add(domain)

    for path in file_paths:
        lowered_path = path.lower()
        if lowered_path.startswith("cad/"):
            detected.add("cad")
        elif lowered_path.startswith("electrical/"):
            detected.add("electrical")
        elif lowered_path.startswith("firmware/"):
            detected.add("firmware")
        elif lowered_path.startswith("ai/"):
            detected.add("ai")
        elif lowered_path.startswith("documentation/") or lowered_path.startswith("delivery/"):
            detected.add("documentation")

    if not detected:
        detected.add("ai")

    return sorted(detected)


def detect_output_format(command: str) -> str:
    """Infer the preferred response/output format from the command."""
    lowered = command.lower()
    scores = {output_type: 0 for output_type in OUTPUT_PATTERNS}

    for output_type, patterns in OUTPUT_PATTERNS.items():
        for pattern in patterns:
            if pattern in lowered:
                scores[output_type] += 1

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    best_output, best_score = ranked[0]
    return best_output if best_score > 0 else "answer"


def extract_file_paths(command: str) -> List[str]:
    """Extract likely repo-relative file or directory paths from the command."""
    matches = PATH_HINT_PATTERN.findall(command)
    cleaned = []
    for match in matches:
        normalized = match.strip("`\"'()[]{}.,;:")
        if normalized and normalized not in cleaned:
            cleaned.append(normalized)
    return cleaned


def build_execution_prompt(plan: Dict[str, Any]) -> str:
    """Build a richer execution prompt from the routing plan."""
    lines = [
        PROJECT_CONTEXT,
        "",
        "KOMUT:",
        plan["command"],
        "",
        f"GÖREV TİPİ: {plan['task_type']}",
        f"ÇIKTI BİÇİMİ: {plan['output_format']}",
        f"ETKİ ALANLARI: {', '.join(plan['domains'])}",
    ]

    if plan["file_paths"]:
        lines.append("İLGİLİ DOSYA/YOL İPUÇLARI:")
        lines.extend(f"- {path}" for path in plan["file_paths"])

    lines.extend([
        "",
        "ÇALIŞMA PRENSİPLERİ:",
        "- Yanıtı seçilen görev tipine uygun üret.",
        "- Yalnızca belirtilen alanlara odaklan.",
        "- Çıktıyı istenen biçimde ver.",
    ])

    if plan["output_format"] == "review":
        lines.extend([
            "- Önce bulguları önem sırasıyla ver.",
            "- Bug, regresyon ve eksik test risklerini vurgula.",
            "- Gereksiz genel özetten kaçın.",
        ])
    elif plan["output_format"] == "patch":
        lines.extend([
            "- Uygulanabilir çözüm veya patch önerisi üret.",
            "- Davranış değişikliği varsa açıkça belirt.",
            "- Gerekirse kısa doğrulama adımı ekle.",
        ])
    elif plan["output_format"] == "plan":
        lines.extend([
            "- Kısa aşamalı plan ver.",
            "- Riskli kararları ve varsayımları açıkla.",
        ])
    elif plan["output_format"] == "report":
        lines.extend([
            "- Başlıkları net kullan.",
            "- Kısa ama teknik bir rapor veya özet üret.",
        ])

    return "\n".join(lines)


def should_use_pipeline(command: str) -> bool:
    """Detect commands that benefit from staged analysis -> implement -> review flow."""
    lowered = command.lower()
    return any(
        first in lowered and second in lowered
        for first, second in PIPELINE_TRIGGER_PAIRS
    )


def extract_model_preferences(command: str) -> List[str]:
    """Detect explicit user model mentions inside the command."""
    lowered = command.lower()
    detected = []
    for alias, model_id in MODEL_NAME_ALIASES.items():
        if alias in lowered and model_id not in detected:
            detected.append(model_id)
    return detected


def build_routing_plan(command: str) -> Dict[str, Any]:
    """Analyze a natural language command and create a routing plan."""
    file_paths = extract_file_paths(command)
    domains = detect_domains(command, file_paths)
    task_type = detect_task_type(command)
    pipeline = should_use_pipeline(command)
    explicit_models = extract_model_preferences(command)
    output_format = detect_output_format(command)

    if explicit_models:
        models = explicit_models
        reason = "Komutta açık model tercihi bulundu."
    else:
        mapped_indices = TASK_MODEL_MAPPING.get(task_type, [0])
        models = [MODEL_CONFIGS[idx]["id"] for idx in mapped_indices]
        reason = f"'{task_type}' görev tipine göre model yönlendirmesi uygulandı."

    execution_mode = "pipeline" if pipeline else ("parallel" if len(models) > 1 else "single")

    if task_type in {"validation", "review"} and not explicit_models:
        summary = "Eleştirel inceleme ve risk odaklı yönlendirme seçildi."
    elif task_type == "documentation":
        summary = "Uzun bağlam ve dokümantasyon odaklı model seçildi."
    elif task_type == "code":
        summary = "Kod üretimi ve ardından ikinci göz için model eşleşmesi seçildi."
    else:
        summary = "Komut, görev tipine göre uygun modellere yönlendirildi."

    return {
        "command": command,
        "task_type": task_type,
        "execution_mode": execution_mode,
        "models": models,
        "domains": domains,
        "file_paths": file_paths,
        "output_format": output_format,
        "reason": reason,
        "summary": summary,
        "pipeline": pipeline,
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

    def get_model_indices_by_ids(self, model_ids: List[str]) -> List[int]:
        """Resolve model ids or aliases to MODEL_CONFIGS indices."""
        normalized = {normalize_model_name(model_id) for model_id in model_ids}
        return [
            idx for idx, model in enumerate(self.models)
            if model["id"] in normalized
        ]

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

    async def dispatch_command(
        self,
        command: str,
        preferred_output: Optional[str] = None,
        execute: bool = False,
        max_parallel: int = 3
    ) -> Dict[str, Any]:
        """Analyze a natural language command and optionally execute it."""
        plan = build_routing_plan(command)
        if preferred_output:
            plan["output_format"] = preferred_output

        if not execute:
            return plan

        model_indices = self.get_model_indices_by_ids(plan["models"])
        if not model_indices:
            model_indices = self.get_model_indices_for_task(plan["task_type"])

        result: Dict[str, Any] = {"plan": plan}

        execution_prompt = build_execution_prompt(plan)

        if plan["execution_mode"] == "single":
            response = await self.ask_single(execution_prompt, model_indices[0])
            result["responses"] = [response]
            return result

        if plan["execution_mode"] == "pipeline":
            stages = []
            stage_definitions = [
                (
                    "analysis",
                    "Görevi analiz et. Amaç, risk, varsayım ve önerilen yaklaşımı çıkar."
                ),
                (
                    "implementation",
                    "Göreve uygun çözüm, patch planı veya uygulanabilir teknik yaklaşım üret."
                ),
                (
                    "review",
                    "Önceki çözümü eleştirel gözle incele; risk, eksik test ve daha güvenli alternatifleri belirt."
                ),
            ]
            accumulated = execution_prompt
            for stage_name, prefix in stage_definitions:
                if stage_name == "analysis":
                    stage_indices = self.get_model_indices_for_task("complex")
                elif stage_name == "implementation":
                    stage_indices = self.get_model_indices_for_task("code")
                else:
                    stage_indices = self.get_model_indices_for_task("review")

                stage_prompt = f"{prefix}\n\nYönlendirilmiş görev:\n{execution_prompt}\n\nÖnceki içerik:\n{accumulated}"
                responses = await self.ask_parallel(stage_prompt, stage_indices, max_parallel=max_parallel)
                normalized_responses = []
                for idx, response in enumerate(responses):
                    if isinstance(response, Exception):
                        normalized_responses.append(
                            ModelResponse(
                                model_id=f"model_{idx}",
                                content="",
                                status="error",
                                latency_ms=0,
                                error=str(response)
                            )
                        )
                    else:
                        normalized_responses.append(response)
                stages.append({"name": stage_name, "responses": normalized_responses})

                successful_texts = [
                    f"[{response.model_id}] {response.content}"
                    for response in normalized_responses
                    if response.status == "success"
                ]
                if successful_texts:
                    accumulated = "\n\n".join(successful_texts)

            result["stages"] = stages
            return result

        responses = await self.ask_parallel(execution_prompt, model_indices, max_parallel=max_parallel)
        normalized_responses = []
        for idx, response in enumerate(responses):
            if isinstance(response, Exception):
                normalized_responses.append(
                    ModelResponse(
                        model_id=f"model_{idx}",
                        content="",
                        status="error",
                        latency_ms=0,
                        error=str(response)
                    )
                )
            else:
                normalized_responses.append(response)

        result["responses"] = normalized_responses
        return result


# MCP Server Tanımı
if MCP_AVAILABLE:
    app = Server("cnc-ai-orchestrator")
    orchestrator = CNCOrchestrator()
    freecad_controller = FreeCADController() if FREECAD_AVAILABLE else None

    @app.list_tools()
    async def list_tools() -> List[Tool]:
        # Temel AI tool'ları
        tools = [
            Tool(
                name="ai_ask",
                description="Tek bir AI modeline soru sor",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "AI'ya sorulacak soru"},
                        "model": {"type": "string", "description": "Model: qwen3.5-plus, qwen3-max-2026-01-23, qwen3-coder-plus, qwen3-coder-next, glm-5, kimi-k2.5, MiniMax-M2.5", "default": "qwen3.5-plus"}
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
                        "task_type": {"type": "string", "description": "Görev tipi: general, code, debug, optimize, design, documentation, complex, validation, review, alternate", "default": "general"}
                    },
                    "required": ["question", "task_type"]
                }
            ),
            Tool(
                name="ai_dispatch",
                description="Doğal dil komutunu analiz eder, uygun görev tipini ve modeli seçer; isterse otomatik çalıştırır",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Doğal dil komutu veya görev tanımı"},
                        "execute": {"type": "boolean", "description": "true ise seçilen görev dağıtımını çalıştırır", "default": False},
                        "max_parallel": {"type": "integer", "description": "Paralel çalıştırma limiti", "default": 3, "maximum": 6},
                        "preferred_output": {"type": "string", "description": "İsteğe bağlı çıktı biçimi zorlaması: answer, review, patch, plan, report"}
                    },
                    "required": ["command"]
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

        # FreeCAD tool'larını ekle (eğer kullanılabilir)
        if FREECAD_AVAILABLE and freecad_controller:
            tools.extend(get_freecad_tools())

        return tools

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

        elif name == "ai_dispatch":
            command = arguments.get("command", "")
            preferred_output = arguments.get("preferred_output")
            execute = arguments.get("execute", False)
            max_parallel = min(arguments.get("max_parallel", 3), 6)
            dispatch_result = await orchestrator.dispatch_command(command, preferred_output, execute, max_parallel)

            plan = dispatch_result["plan"]
            plan_text = [
                "## Komut Analizi",
                f"- Komut: {plan['command']}",
                f"- Görev tipi: {plan['task_type']}",
                f"- Çalışma modu: {plan['execution_mode']}",
                f"- Modeller: {', '.join(plan['models'])}",
                f"- Alanlar: {', '.join(plan['domains'])}",
                f"- Çıktı biçimi: {plan['output_format']}",
                f"- Gerekçe: {plan['reason']}",
                f"- Özet: {plan['summary']}",
            ]
            if plan["file_paths"]:
                plan_text.append(f"- Yol ipuçları: {', '.join(plan['file_paths'])}")

            if not execute:
                plan_text.append("\n`execute=true` ile bu dağıtımı doğrudan çalıştırabilirsiniz.")
                return [TextContent(type="text", text="\n".join(plan_text))]

            if "stages" in dispatch_result:
                stage_lines = ["\n## Pipeline Sonuçları"]
                for stage in dispatch_result["stages"]:
                    stage_lines.append(f"\n### {stage['name']}")
                    for response in stage["responses"]:
                        stage_lines.append(
                            f"- {response.model_id} | {response.status} | {response.latency_ms:.0f}ms"
                        )
                        if response.status == "success":
                            stage_lines.append(response.content[:500])
                        else:
                            stage_lines.append(f"Hata: {response.error}")
                return [TextContent(type="text", text="\n".join(plan_text + stage_lines))]

            formatted = orchestrator.format_parallel_response(dispatch_result.get("responses", []))
            return [TextContent(type="text", text="\n".join(plan_text) + "\n\n" + formatted)]

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

        # FreeCAD tool'larını işle
        elif FREECAD_AVAILABLE and freecad_controller:
            if name.startswith("freecad_"):
                return await handle_freecad_tool(name, arguments, freecad_controller)

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
