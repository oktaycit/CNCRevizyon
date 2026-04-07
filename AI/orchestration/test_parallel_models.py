#!/usr/bin/env python3
"""
Test Script for Parallel AI Model Orchestrator

Bu script, paralel model kullanımını test eder.

Kullanım:
    python test_parallel_models.py
"""

import asyncio
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_orchestrator import (
    AIOrchestrator,
    ModelConfig,
    DashScopeClient
)


# Test Configuration
API_KEY = "sk-sp-1dfff295506a4cbba9c3745dd54e5796"
API_ENDPOINT = "https://coding-intl.dashscope.aliyuncs.com/v1"

TEST_MODELS = [
    ModelConfig(
        model_id="qwen3.5-plus",
        api_key=API_KEY,
        api_endpoint=API_ENDPOINT,
        temperature=0.7,
        system_prompt="Sen yardımsever bir AI asistansısın."
    ),
    ModelConfig(
        model_id="qwen3-max-2026-01-23",
        api_key=API_KEY,
        api_endpoint=API_ENDPOINT,
        temperature=0.5,
        system_prompt="Sen karmaşık teknik analizler yapan bir mühendissin."
    ),
    ModelConfig(
        model_id="qwen3-coder-plus",
        api_key=API_KEY,
        api_endpoint=API_ENDPOINT,
        temperature=0.2,
        system_prompt="Sen uzman bir yazılım geliştirme asistanısın."
    )
]

TEST_PROMPTS = {
    "general": "EtherCAT communication cycle nedir?",
    "code": "Python'da decorator nedir? Basit bir örnek ver.",
    "technical": "Delta ASDA-A3-E servo sürücülerde EtherCAT cycle time nasıl ayarlanır?"
}


async def test_single_model():
    """Tek model testi"""
    print("\n" + "="*60)
    print("🧪 TEST 1: Tek Model Çalıştırma")
    print("="*60)
    
    orchestrator = AIOrchestrator([TEST_MODELS[0]])
    
    start_time = time.time()
    response = await orchestrator.run_single_model(
        TEST_PROMPTS["general"],
        model_index=0
    )
    total_time = time.time() - start_time
    
    print(f"\n✅ Model: {response.model_id}")
    print(f"⏱️ Response Time: {response.latency_ms:.0f}ms")
    print(f"⏱️ Total Time: {total_time:.2f}s")
    print(f"📊 Status: {response.status}")
    if response.error:
        print(f"❌ Error: {response.error}")
    else:
        print(f"\n📝 Yanıt (ilk 200 karakter):\n{response.content[:200]}...")
    
    return response.status == "success"


async def test_parallel_models():
    """Paralel model testi"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Paralel Model Çalıştırma (3 model)")
    print("="*60)
    
    orchestrator = AIOrchestrator(TEST_MODELS)
    
    start_time = time.time()
    responses = await orchestrator.run_parallel(
        TEST_PROMPTS["technical"],
        model_indices=[0, 1, 2]
    )
    total_time = time.time() - start_time
    
    print(f"\n📊 Toplam Süre: {total_time:.2f}s")
    print(f"📊 Model Sayısı: {len(responses)}")
    
    success_count = 0
    for i, response in enumerate(responses, 1):
        status_icon = "✅" if response.status == "success" else "❌"
        print(f"\n{status_icon} Model {i}: {response.model_id}")
        print(f"   ⏱️ Latency: {response.latency_ms:.0f}ms")
        if response.status == "success":
            success_count += 1
            print(f"   📝 Tokens: ~{len(response.content) // 4}")
        else:
            print(f"   ❌ Error: {response.error}")
    
    print(f"\n📈 Başarılı: {success_count}/{len(responses)}")
    
    return success_count >= 2


async def test_voting_mode():
    """Voting mode testi"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Voting Mode (En hızlı başarılı yanıt)")
    print("="*60)
    
    orchestrator = AIOrchestrator(TEST_MODELS)
    
    start_time = time.time()
    result = await orchestrator.run_with_voting(
        TEST_PROMPTS["general"],
        model_indices=[0, 1, 2]
    )
    total_time = time.time() - start_time
    
    if result["winner"]:
        print(f"\n🏆 Kazanan Model: {result['winner']}")
        print(f"⏱️ Kazanan Latency: {result['latency_ms']:.0f}ms")
        print(f"⏱️ Total Time: {total_time:.2f}s")
        print(f"\n📝 Yanıt (ilk 300 karakter):\n{result['content'][:300]}...")
    else:
        print("\n❌ Tüm modeller başarısız")
    
    return result["winner"] is not None


async def test_comparison_mode():
    """Comparison mode testi"""
    print("\n" + "="*60)
    print("🧪 TEST 4: Comparison Mode (Karşılaştırma Tablosu)")
    print("="*60)
    
    orchestrator = AIOrchestrator(TEST_MODELS)
    
    start_time = time.time()
    result = await orchestrator.run_with_aggregation(
        TEST_PROMPTS["technical"],
        model_indices=[0, 1, 2],
        aggregation_method="compare"
    )
    total_time = time.time() - start_time
    
    print(f"\n⏱️ Total Time: {total_time:.2f}s")
    print(f"\n{result['aggregated_content']}")
    
    return True


async def test_all_models_individually():
    """Her modeli tek tek test et"""
    print("\n" + "="*60)
    print("🧪 TEST 5: Bireysel Model Testi (Tüm modeller)")
    print("="*60)
    
    test_prompt = "Python'da list comprehension nedir? Örnek ver."
    
    for i, model_config in enumerate(TEST_MODELS):
        print(f"\n🔍 Test ediliyor: {model_config.model_id}")
        
        orchestrator = AIOrchestrator([model_config])
        response = await orchestrator.run_single_model(test_prompt, 0)
        
        status_icon = "✅" if response.status == "success" else "❌"
        print(f"   {status_icon} Status: {response.status}")
        print(f"   ⏱️ Latency: {response.latency_ms:.0f}ms")
        if response.error:
            print(f"   ❌ Error: {response.error}")
    
    return True


async def run_all_tests():
    """Tüm testleri çalıştır"""
    print("\n" + "🚀"*30)
    print("CNC AI Orchestrator - Parallel Model Test Suite")
    print("🚀"*30)
    
    results = {
        "single_model": False,
        "parallel_models": False,
        "voting_mode": False,
        "comparison_mode": False,
        "all_models_individual": False
    }
    
    # Test 1: Single Model
    try:
        results["single_model"] = await test_single_model()
    except Exception as e:
        print(f"\n TEST 1 FAILED: {e}")
    
    # Test 2: Parallel Models
    try:
        results["parallel_models"] = await test_parallel_models()
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}")
    
    # Test 3: Voting Mode
    try:
        results["voting_mode"] = await test_voting_mode()
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {e}")
    
    # Test 4: Comparison Mode
    try:
        results["comparison_mode"] = await test_comparison_mode()
    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {e}")
    
    # Test 5: All Models Individual
    try:
        results["all_models_individual"] = await test_all_models_individually()
    except Exception as e:
        print(f"\n❌ TEST 5 FAILED: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📈 Toplam: {passed}/{total} test başarılı")
    
    if passed == total:
        print("\n🎉 TÜM TESTLER BAŞARILI!")
    else:
        print(f"\n⚠️ {total - passed} test başarısız oldu.")
    
    return passed == total


def main():
    """Ana fonksiyon"""
    print("\n" + "="*60)
    print("CNC AI Orchestrator - Parallel Model Test")
    print("="*60)
    print("\n⚠️ Bu test API kullanacaktır. Devam etmek istiyor musunuz?")
    print("   Not: Lite plan limitlerine dikkat edin (60 istek/dakika)")
    print()
    
    response = input("Testleri çalıştırmak için Enter'a basın (q ile çık): ")
    if response.lower() == 'q':
        print("❌ Test iptal edildi.")
        return
    
    # Run async tests
    success = asyncio.run(run_all_tests())
    
    # Exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
