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
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
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
            }
        ],
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
        choices=["single", "parallel", "sequential", "voting", "aggregate"],
        default="parallel",
        help="Çalışma modu"
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
    if args.config:
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
            )
        ]
    
    orchestrator = AIOrchestrator(configs)
    
    # Model filtreleme
    model_indices = None
    if args.models:
        selected_models = [m.strip() for m in args.models.split(",")]
        model_indices = []
        for i, config in enumerate(configs):
            if config.model_id in selected_models:
                model_indices.append(i)
        if not model_indices:
            print(f"Uyarı: Seçilen modeller yapılandırmada bulunamadı: {selected_models}")
            model_indices = list(range(len(configs)))
    
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