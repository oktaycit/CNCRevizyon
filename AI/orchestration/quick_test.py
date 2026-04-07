#!/usr/bin/env python3
"""
Hızlı Test Script - AI Model Paralel Kullanım

Kullanım:
    python quick_test.py
    python quick_test.py --mode parallel
    python quick_test.py --mode single
    python quick_test.py --models "qwen3-coder-plus,qwen3-max-2026-01-23"
"""

import asyncio
import sys
import time
from pathlib import Path

# Üst dizini sys.path'e ekle
sys.path.insert(0, str(Path(__file__).parent))

from ai_orchestrator import AIOrchestrator, ModelConfig, load_config_from_file


# Test soruları
TEST_PROMPTS = {
    "general": "Servo motor nedir ve nasıl çalışır?",
    "code": "Python'da PID kontrolcü fonksiyonu yaz",
    "debug": "ASDA-A3-E AL013 (Position Error) hatası nasıl çözülür?",
    "optimization": "6000x3000mm cam için kesim yerleşimi optimize et",
}


async def test_single_model():
    """Tek model testi"""
    print("\n" + "="*60)
    print("📍 TEK MODEL TESTİ")
    print("="*60)
    
    configs = [
        ModelConfig(
            model_id="qwen3.5-plus",
            api_key="sk-sp-1dfff295506a4cbba9c3745dd54e5796",
            api_endpoint="https://coding-intl.dashscope.aliyuncs.com/v1",
            system_prompt="Sen yardımsever bir AI asistansısın."
        )
    ]
    
    orchestrator = AIOrchestrator(configs)
    
    start = time.time()
    response = await orchestrator.run_single_model(TEST_PROMPTS["general"], 0)
    elapsed = time.time() - start
    
    print(f"\n✅ Model: {response.model_id}")
    print(f"⏱️ Süre: {elapsed:.2f}s ({response.latency_ms:.0f}ms)")
    print(f"📝 Yanıt (ilk 300 karakter):\n{response.content[:300]}...")


async def test_parallel_models():
    """Paralel model testi"""
    print("\n" + "="*60)
    print("🚀 PARALEL MODEL TESTİ")
    print("="*60)
    
    configs = [
        ModelConfig(
            model_id="qwen3.5-plus",
            api_key="sk-sp-1dfff295506a4cbba9c3745dd54e5796",
            api_endpoint="https://coding-intl.dashscope.aliyuncs.com/v1",
            system_prompt="Sen yardımsever bir AI asistansısın."
        ),
        ModelConfig(
            model_id="qwen3-coder-plus",
            api_key="sk-sp-1dfff295506a4cbba9c3745dd54e5796",
            api_endpoint="https://coding-intl.dashscope.aliyuncs.com/v1",
            temperature=0.3,
            system_prompt="Sen uzman bir yazılım geliştirme asistanısın."
        ),
        ModelConfig(
            model_id="qwen3-max-2026-01-23",
            api_key="sk-sp-1dfff295506a4cbba9c3745dd54e5796",
            api_endpoint="https://coding-intl.dashscope.aliyuncs.com/v1",
            system_prompt="Sen karmaşık analizler yapan bir mühendissin."
        ),
    ]
    
    orchestrator = AIOrchestrator(configs)
    
    start = time.time()
    responses = await orchestrator.run_parallel(TEST_PROMPTS["debug"])
    elapsed = time.time() - start
    
    print(f"\n⏱️ Toplam Süre: {elapsed:.2f}s")
    print(f"\n📊 Model Sonuçları:\n")
    
    for i, response in enumerate(responses, 1):
        status = "✅" if response.status == "success" else "❌"
        print(f"{i}. {status} {response.model_id}")
        print(f"   ⏱️ Latency: {response.latency_ms:.0f}ms")
        if response.error:
            print(f"   ⚠️ Hata: {response.error}")
        else:
            preview = response.content[:150].replace('\n', ' ')
            print(f"   📝 Yanıt: {preview}...")
        print()


async def test_with_voting():
    """Voting testi - en iyi yanıtı seç"""
    print("\n" + "="*60)
    print("🏆 VOTING TESTİ (En İyi Yanıt)")
    print("="*60)
    
    configs = [
        ModelConfig(
            model_id="qwen3.5-plus",
            api_key="sk-sp-1dfff295506a4cbba9c3745dd54e5796",
            api_endpoint="https://coding-intl.dashscope.aliyuncs.com/v1",
            system_prompt="Sen yardımsever bir AI asistansısın."
        ),
        ModelConfig(
            model_id="qwen3-coder-plus",
            api_key="sk-sp-1dfff295506a4cbba9c3745dd54e5796",
            api_endpoint="https://coding-intl.dashscope.aliyuncs.com/v1",
            temperature=0.3,
            system_prompt="Sen uzman bir yazılım geliştirme asistanısın."
        ),
    ]
    
    orchestrator = AIOrchestrator(configs)
    
    start = time.time()
    result = await orchestrator.run_with_voting(TEST_PROMPTS["code"])
    elapsed = time.time() - start
    
    print(f"\n⏱️ Toplam Süre: {elapsed:.2f}s")
    print(f"🏆 Kazanan: {result.get('winner', 'N/A')}")
    print(f"⏱️ Kazanan Latency: {result.get('latency_ms', 0):.0f}ms")
    print(f"\n📝 Kazanan Yanıt (ilk 400 karakter):\n{result.get('content', '')[:400]}...")


async def test_comparison_table():
    """Karşılaştırma tablosu testi"""
    print("\n" + "="*60)
    print("📊 KARŞILAŞTIRMA TABLOSU")
    print("="*60)
    
    configs = [
        ModelConfig(
            model_id="qwen3.5-plus",
            api_key="sk-sp-1dfff295506a4cbba9c3745dd54e5796",
            api_endpoint="https://coding-intl.dashscope.aliyuncs.com/v1",
            system_prompt="Sen yardımsever bir AI asistansısın."
        ),
        ModelConfig(
            model_id="qwen3-max-2026-01-23",
            api_key="sk-sp-1dfff295506a4cbba9c3745dd54e5796",
            api_endpoint="https://coding-intl.dashscope.aliyuncs.com/v1",
            system_prompt="Sen teknik analiz uzmanısın."
        ),
    ]
    
    orchestrator = AIOrchestrator(configs)
    
    start = time.time()
    result = await orchestrator.run_with_aggregation(
        TEST_PROMPTS["optimization"],
        aggregation_method="compare"
    )
    elapsed = time.time() - start
    
    print(f"\n⏱️ Toplam Süre: {elapsed:.2f}s")
    print(f"\n📊 Karşılaştırma:\n")
    print(result.get("aggregated_content", ""))


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Model Hızlı Test")
    parser.add_argument(
        "--mode", "-m",
        type=str,
        choices=["single", "parallel", "voting", "compare"],
        default="parallel",
        help="Test modu"
    )
    parser.add_argument(
        "--models",
        type=str,
        default=None,
        help="Modeller (virgülle ayrılmış)"
    )
    parser.add_argument(
        "--prompt", "-p",
        type=str,
        default=None,
        help="Test prompt'u"
    )
    
    args = parser.parse_args()
    
    print("\n" + "🤖 "*20)
    print("ALIBABA CLOUD LITE PLAN - AI MODEL TEST")
    print("🤖 "*20)
    
    if args.prompt:
        TEST_PROMPTS["custom"] = args.prompt
    
    if args.mode == "single":
        await test_single_model()
    elif args.mode == "parallel":
        await test_parallel_models()
    elif args.mode == "voting":
        await test_with_voting()
    elif args.mode == "compare":
        await test_comparison_table()
    
    print("\n" + "="*60)
    print("✅ TEST TAMAMLANDI")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
