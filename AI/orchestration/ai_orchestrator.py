#!/usr/bin/env python3
"""
Alibaba Cloud DashScope AI Model Orchestrator

Bu script, birden fazla AI modelini paralel olarak kullanarak
görevleri dağıtır ve sonuçları birleştirir.

Kullanım:
    python ai_orchestrator.py --prompt "Soru veya göreviniz"
    python ai_orchestrator.py --config config.json --prompt "Soru"
    python ai_orchestrator.py --parallel --models qwen3.5-plus,qwen3-max --prompt "Soru"
"""

import asyncio
import aiohttp
import json
import argparse
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ModelConfig:
    """Model yapılandırma sınıfı"""
    model_id: str
    api_key: str
    api_endpoint: str = "https://coding-intl.dashscope.aliyuncs.com/v1"
    temperature: float = 0.7
    max_tokens: int = 2048
    system_prompt: str = ""


@dataclass
class ModelResponse:
    """Model yanıt sınıfı"""
    model_id: str
    content: str
    status: str
    latency_ms: float
    error: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


MODEL_ALIASES = {
    "qwen35": "qwen3.5-plus",
    "qwen3.5": "qwen3.5-plus",
    "qwen3.5-plus": "qwen3.5-plus",
    "qwenmax": "qwen3-max-2026-01-23",
    "qwen3-max": "qwen3-max-2026-01-23",
    "qwen3-max-2026-01-23": "qwen3-max-2026-01-23",
    "coder": "qwen3-coder-plus",
    "qwen-coder": "qwen3-coder-plus",
    "qwen3-coder-plus": "qwen3-coder-plus",
    "qwen3-coder-next": "qwen3-coder-next",
    "glm": "glm-5",
    "glm5": "glm-5",
    "glm-5": "glm-5",
    "kimi": "kimi-k2.5",
    "kimi-k2.5": "kimi-k2.5",
    "minimax": "MiniMax-M2.5",
    "minimax-m2.5": "MiniMax-M2.5",
    "minimax-m2": "MiniMax-M2.5",
    "MiniMax-M2.5": "MiniMax-M2.5",
}


DEFAULT_PIPELINE = {
    "analysis": ["qwen3-max-2026-01-23", "qwen3.5-plus"],
    "implementation": ["qwen3-coder-plus", "qwen3-coder-next"],
    "review": ["glm-5", "MiniMax-M2.5"],
    "documentation": ["kimi-k2.5"],
}


def normalize_model_name(model_name: str) -> str:
    """Normalize user-friendly aliases to canonical model ids."""
    return MODEL_ALIASES.get(model_name.strip(), model_name.strip())


def resolve_model_indices(configs: List["ModelConfig"], requested_models: Optional[List[str]]) -> Optional[List[int]]:
    """Resolve requested model ids/aliases to config indices."""
    if not requested_models:
        return None

    normalized = {normalize_model_name(model) for model in requested_models}
    indices = [
        idx for idx, config in enumerate(configs)
        if config.model_id in normalized
    ]
    return indices or None


def load_raw_config(config_path: str) -> Dict[str, Any]:
    """Load raw configuration json for routing and pipeline metadata."""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


class DashScopeClient:
    """DashScope API istemcisi"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate(self, prompt: str, session: aiohttp.ClientSession) -> ModelResponse:
        """Tek bir model için yanıt üret"""
        start_time = datetime.now()
        
        messages = []
        if self.config.system_prompt:
            messages.append({"role": "system", "content": self.config.system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.config.model_id,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
        
        try:
            async with session.post(
                f"{self.config.api_endpoint}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                latency = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    return ModelResponse(
                        model_id=self.config.model_id,
                        content=content,
                        status="success",
                        latency_ms=latency
                    )
                else:
                    error_text = await response.text()
                    return ModelResponse(
                        model_id=self.config.model_id,
                        content="",
                        status="error",
                        latency_ms=latency,
                        error=f"HTTP {response.status}: {error_text}"
                    )
        except asyncio.TimeoutError:
            return ModelResponse(
                model_id=self.config.model_id,
                content="",
                status="timeout",
                latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
                error="Request timeout"
            )
        except Exception as e:
            return ModelResponse(
                model_id=self.config.model_id,
                content="",
                status="error",
                latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
                error=str(e)
            )


class AIOrchestrator:
    """AI Model Orkestratörü"""
    
    def __init__(self, configs: List[ModelConfig]):
        self.configs = configs
        self.clients = [DashScopeClient(config) for config in configs]
    
    async def run_single_model(
        self, 
        prompt: str, 
        model_index: int = 0
    ) -> ModelResponse:
        """Tek bir model ile çalış"""
        client = self.clients[model_index]
        async with aiohttp.ClientSession() as session:
            return await client.generate(prompt, session)
    
    async def run_parallel(
        self, 
        prompt: str,
        model_indices: Optional[List[int]] = None
    ) -> List[ModelResponse]:
        """Birden fazla modeli paralel çalıştır"""
        if model_indices is None:
            model_indices = list(range(len(self.clients)))
        
        selected_clients = [self.clients[i] for i in model_indices]
        
        async with aiohttp.ClientSession() as session:
            tasks = [client.generate(prompt, session) for client in selected_clients]
            responses = await asyncio.gather(*tasks)
            return list(responses)
    
    async def run_sequential(
        self, 
        prompt: str,
        model_indices: Optional[List[int]] = None
    ) -> List[ModelResponse]:
        """Modelleri sırayla çalıştır (her biri öncekinin çıktısını görür)"""
        if model_indices is None:
            model_indices = list(range(len(self.clients)))
        
        responses = []
        current_prompt = prompt
        
        for i in model_indices:
            client = self.clients[i]
            async with aiohttp.ClientSession() as session:
                response = await client.generate(current_prompt, session)
                responses.append(response)
                if response.status == "success":
                    current_prompt = f"Önceki yanıt: {response.content}\n\n{prompt}"
        
        return responses
    
    async def run_with_voting(
        self,
        prompt: str,
        model_indices: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Birden fazla modeli çalıştır ve en iyi yanıtı seç
        (Basit voting mekanizması - en hızlı başarılı yanıt)
        """
        responses = await self.run_parallel(prompt, model_indices)
        
        successful = [r for r in responses if r.status == "success"]
        
        if not successful:
            return {
                "winner": None,
                "content": "Tüm modeller başarısız",
                "all_responses": responses
            }
        
        # En hızlı başarılı yanıtı seç
        winner = min(successful, key=lambda r: r.latency_ms)
        
        return {
            "winner": winner.model_id,
            "content": winner.content,
            "latency_ms": winner.latency_ms,
            "all_responses": responses
        }
    
    async def run_with_aggregation(
        self,
        prompt: str,
        model_indices: Optional[List[int]] = None,
        aggregation_method: str = "concat"
    ) -> Dict[str, Any]:
        """
        Birden fazla modelin yanıtını birleştir
        aggregation_method: "concat", "compare", "json_merge"
        """
        responses = await self.run_parallel(prompt, model_indices)
        
        successful = [r for r in responses if r.status == "success"]
        
        if aggregation_method == "concat":
            aggregated = "\n\n".join([
                f"### {r.model_id} ###\n{r.content}" for r in successful
            ])
        elif aggregation_method == "compare":
            aggregated = self._create_comparison_table(successful)
        elif aggregation_method == "json_merge":
            aggregated = json.dumps({
                r.model_id: r.content for r in successful
            }, ensure_ascii=False, indent=2)
        else:
            aggregated = "Geçersiz aggregation yöntemi"
        
        return {
            "aggregated_content": aggregated,
            "method": aggregation_method,
            "all_responses": responses
        }
    
    def _create_comparison_table(self, responses: List[ModelResponse]) -> str:
        """Yanıtları karşılaştırma tablosu olarak formatla"""
        lines = ["| Model | Yanıt (Özet) | Latency |", "|-------|--------------|---------|"]
        for r in responses:
            content_preview = r.content[:100] + "..." if len(r.content) > 100 else r.content
            content_preview = content_preview.replace("\n", " ")
            lines.append(f"| {r.model_id} | {content_preview} | {r.latency_ms:.0f}ms |")
        return "\n".join(lines)


def load_config_from_file(config_path: str) -> List[ModelConfig]:
    """Yapılandırma dosyasından model config'leri yükle"""
    config = load_raw_config(config_path)
    
    api_key = config.get("api_key", "")
    api_endpoint = config.get("api_endpoint", "https://coding-intl.dashscope.aliyuncs.com/v1")
    
    configs = []
    for model in config.get("models", []):
        configs.append(ModelConfig(
            model_id=model.get("model_id", "qwen3.5-plus"),
            api_key=model.get("api_key", api_key),
            api_endpoint=model.get("api_endpoint", api_endpoint),
            temperature=model.get("temperature", 0.7),
            max_tokens=model.get("max_tokens", 2048),
            system_prompt=model.get("system_prompt", "")
        ))
    
    return configs


def create_default_config(output_path: str = "orchestrator_config.json"):
    """Varsayılan yapılandırma dosyası oluştur"""
    config = {
        "api_key": "sk-sp-1dfff295506a4cbba9c3745dd54e5796",
        "api_endpoint": "https://coding-intl.dashscope.aliyuncs.com/v1",
        "models": [
            {
                "model_id": "qwen3.5-plus",
                "temperature": 0.7,
                "max_tokens": 2048,
                "system_prompt": "Sen yardımsever bir AI asistansısın."
            },
            {
                "model_id": "qwen3-max-2026-01-23",
                "temperature": 0.7,
                "max_tokens": 2048,
                "system_prompt": "Sen yardımsever bir AI asistansısın."
            },
            {
                "model_id": "qwen3-coder-plus",
                "temperature": 0.3,
                "max_tokens": 4096,
                "system_prompt": "Sen uzman bir yazılım geliştirme asistanısın. Kod yazma ve açıklama konusunda uzmansın."
            },
            {
                "model_id": "glm-5",
                "temperature": 0.4,
                "max_tokens": 4096,
                "system_prompt": "Sen eleştirel düşünen bir teknik reviewer ve doğrulama uzmanısın."
            },
            {
                "model_id": "kimi-k2.5",
                "temperature": 0.5,
                "max_tokens": 4096,
                "system_prompt": "Sen teknik dokümantasyon ve uzun bağlam analizi konusunda uzmansın."
            },
            {
                "model_id": "MiniMax-M2.5",
                "temperature": 0.5,
                "max_tokens": 4096,
                "system_prompt": "Sen alternatif çözüm üreten, karşılaştırmalı düşünen bir teknik AI asistansısın."
            }
        ],
        "task_routing": {
            "general_question": ["qwen3.5-plus"],
            "code_generation": ["qwen3-coder-plus", "qwen3-coder-next"],
            "debug": ["qwen3-max-2026-01-23", "glm-5"],
            "optimization": ["qwen3-max-2026-01-23", "qwen3-coder-plus"],
            "design": ["qwen3.5-plus", "MiniMax-M2.5"],
            "documentation": ["kimi-k2.5", "qwen3.5-plus"],
            "validation": ["glm-5", "MiniMax-M2.5"]
        },
        "pipeline": DEFAULT_PIPELINE,
        "default_mode": "parallel",
        "timeout_seconds": 60
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"Varsayılan yapılandırma dosyası oluşturuldu: {output_path}")
    return config


async def main_async():
    """Ana fonksiyon (async)"""
    parser = argparse.ArgumentParser(
        description="Alibaba Cloud DashScope AI Model Orchestrator"
    )
    parser.add_argument(
        "--prompt", "-p",
        type=str,
        required=True,
        help="AI modellerine gönderilecek prompt"
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        default=None,
        help="Yapılandırma dosyası yolu"
    )
    parser.add_argument(
        "--mode", "-m",
        type=str,
        choices=["single", "parallel", "sequential", "voting", "aggregate", "pipeline"],
        default="parallel",
        help="Çalışma modu"
    )
    parser.add_argument(
        "--task-type",
        type=str,
        default=None,
        help="Routing anahtarı (örn: code_generation, debug, validation)"
    )
    parser.add_argument(
        "--models",
        type=str,
        default=None,
        help="Kullanılacak modeller (virgülle ayrılmış, örn: qwen3.5-plus,qwen3-max)"
    )
    parser.add_argument(
        "--aggregate-method",
        type=str,
        choices=["concat", "compare", "json_merge"],
        default="concat",
        help="Yanıt birleştirme yöntemi"
    )
    parser.add_argument(
        "--create-config",
        action="store_true",
        help="Varsayılan yapılandırma dosyası oluştur"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Sonuçları kaydetmek için dosya yolu"
    )
    
    args = parser.parse_args()
    
    # Varsayılan config oluştur
    if args.create_config:
        create_default_config()
        return
    
    # Yapılandırma yükle
    raw_config = {}
    if args.config:
        raw_config = load_raw_config(args.config)
        configs = load_config_from_file(args.config)
    else:
        # Varsayılan config
        configs = [
            ModelConfig(
                model_id="qwen3.5-plus",
                api_key="sk-sp-1dfff295506a4cbba9c3745dd54e5796",
                system_prompt="Sen yardımsever bir AI asistansısın."
            ),
            ModelConfig(
                model_id="qwen3-max-2026-01-23",
                api_key="sk-sp-1dfff295506a4cbba9c3745dd54e5796",
                system_prompt="Sen yardımsever bir AI asistansısın."
            ),
            ModelConfig(
                model_id="qwen3-coder-plus",
                api_key="sk-sp-1dfff295506a4cbba9c3745dd54e5796",
                temperature=0.3,
                system_prompt="Sen uzman bir yazılım geliştirme asistanısın."
            ),
            ModelConfig(
                model_id="glm-5",
                api_key="sk-sp-1dfff295506a4cbba9c3745dd54e5796",
                temperature=0.4,
                system_prompt="Sen eleştirel düşünen bir teknik reviewer ve doğrulama uzmanısın."
            ),
            ModelConfig(
                model_id="kimi-k2.5",
                api_key="sk-sp-1dfff295506a4cbba9c3745dd54e5796",
                temperature=0.5,
                system_prompt="Sen teknik dokümantasyon ve uzun bağlam analizi konusunda uzmansın."
            ),
            ModelConfig(
                model_id="MiniMax-M2.5",
                api_key="sk-sp-1dfff295506a4cbba9c3745dd54e5796",
                temperature=0.5,
                system_prompt="Sen alternatif çözüm üreten, karşılaştırmalı düşünen bir teknik AI asistansısın."
            )
        ]
        raw_config = {
            "task_routing": {
                "general_question": ["qwen3.5-plus"],
                "code_generation": ["qwen3-coder-plus", "qwen3-coder-next"],
                "debug": ["qwen3-max-2026-01-23", "glm-5"],
                "optimization": ["qwen3-max-2026-01-23", "qwen3-coder-plus"],
                "design": ["qwen3.5-plus", "MiniMax-M2.5"],
                "documentation": ["kimi-k2.5", "qwen3.5-plus"],
                "validation": ["glm-5", "MiniMax-M2.5"]
            },
            "pipeline": DEFAULT_PIPELINE
        }

    orchestrator = AIOrchestrator(configs)
    
    # Model filtreleme
    model_indices = None
    if args.models:
        requested_models = [m.strip() for m in args.models.split(",")]
        model_indices = resolve_model_indices(configs, requested_models)
        if model_indices is None:
            print(f"Uyarı: Seçilen modeller yapılandırmada bulunamadı: {requested_models}")
            model_indices = list(range(len(configs)))
    elif args.task_type:
        routed_models = raw_config.get("task_routing", {}).get(args.task_type, [])
        model_indices = resolve_model_indices(configs, routed_models)
        if model_indices is None:
            print(f"Uyarı: Routing için model bulunamadı: {args.task_type}")
    
    # Çalıştır
    print(f"Çalıştırılıyor: {args.mode} modu")
    print(f"Prompt: {args.prompt[:100]}...")
    print("-" * 50)
    
    result = None
    
    if args.mode == "single":
        response = await orchestrator.run_single_model(args.prompt, 0)
        result = {"response": asdict(response)}
        print(f"Model: {response.model_id}")
        print(f"Durum: {response.status}")
        print(f"Latency: {response.latency_ms:.0f}ms")
        print(f"İçerik:\n{response.content}")
    
    elif args.mode == "parallel":
        responses = await orchestrator.run_parallel(args.prompt, model_indices)
        result = {"responses": [asdict(r) for r in responses]}
        for response in responses:
            print(f"\n{'='*50}")
            print(f"Model: {response.model_id}")
            print(f"Durum: {response.status}")
            print(f"Latency: {response.latency_ms:.0f}ms")
            if response.error:
                print(f"Hata: {response.error}")
            else:
                print(f"İçerik:\n{response.content[:500]}...")
    
    elif args.mode == "sequential":
        responses = await orchestrator.run_sequential(args.prompt, model_indices)
        result = {"responses": [asdict(r) for r in responses]}
        for response in responses:
            print(f"\n{'='*50}")
            print(f"Model: {response.model_id}")
            print(f"Durum: {response.status}")
            print(f"İçerik:\n{response.content[:500]}...")
    
    elif args.mode == "voting":
        result = await orchestrator.run_with_voting(args.prompt, model_indices)
        print(f"Kazanan Model: {result['winner']}")
        print(f"Kazanan İçerik:\n{result['content']}")
    
    elif args.mode == "aggregate":
        result = await orchestrator.run_with_aggregation(
            args.prompt, 
            model_indices,
            args.aggregate_method
        )
        print(f"Birleştirilmiş İçerik ({args.aggregate_method}):")
        print(result["aggregated_content"])
    
    elif args.mode == "pipeline":
        pipeline_config = raw_config.get("pipeline", DEFAULT_PIPELINE)
        pipeline_result = {}
        review_input = ""

        for stage_name in ["analysis", "implementation", "review", "documentation"]:
            stage_models = pipeline_config.get(stage_name, [])
            stage_indices = resolve_model_indices(configs, stage_models)
            if stage_indices is None:
                continue

            if stage_name == "analysis":
                stage_prompt = (
                    "Aşağıdaki görevi analiz et. Kısa riskler, varsayımlar ve önerilen yaklaşımı ver.\n\n"
                    f"Görev:\n{args.prompt}"
                )
            elif stage_name == "implementation":
                stage_prompt = (
                    "Aşağıdaki görev için uygulanabilir çözüm veya kod taslağı üret.\n\n"
                    f"Görev:\n{args.prompt}\n\n"
                    f"Analiz Özeti:\n{review_input or 'Henüz analiz çıktısı yok.'}"
                )
            elif stage_name == "review":
                stage_prompt = (
                    "Aşağıdaki analiz ve uygulama taslağını eleştirel gözle incele. "
                    "Hataları, riskleri, eksik testleri ve daha güvenli alternatifleri belirt.\n\n"
                    f"Görev:\n{args.prompt}\n\n"
                    f"Önceki Çıktılar:\n{review_input}"
                )
            else:
                stage_prompt = (
                    "Aşağıdaki görev için kısa teslim notu veya teknik özet hazırla.\n\n"
                    f"Görev:\n{args.prompt}\n\n"
                    f"Önceki Çıktılar:\n{review_input}"
                )

            responses = await orchestrator.run_parallel(stage_prompt, stage_indices)
            stage_payload = [asdict(r) for r in responses]
            pipeline_result[stage_name] = stage_payload

            successful_contents = [
                f"[{r.model_id}]\n{r.content}"
                for r in responses
                if r.status == "success"
            ]
            if successful_contents:
                review_input = "\n\n".join(successful_contents)

            print(f"\n{'=' * 50}")
            print(f"Pipeline Aşaması: {stage_name}")
            print(f"{'=' * 50}")
            for response in responses:
                print(f"Model: {response.model_id} | Durum: {response.status} | Latency: {response.latency_ms:.0f}ms")
                if response.error:
                    print(f"Hata: {response.error}")
                else:
                    print(f"İçerik:\n{response.content[:500]}...")

        result = {"pipeline": pipeline_result}
    
    # Sonuçları dosyaya kaydet
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nSonuçlar kaydedildi: {args.output}")


def main():
    """Ana fonksiyon"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
