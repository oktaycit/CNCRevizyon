#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parallel AI Task Runner
Runs multiple AI tasks in parallel using the orchestrator

Tasks:
1. DXF Import Module (qwen3-coder-plus)
2. Database Schema (qwen3-coder-plus)
3. Reports Module (kimi-k2.5)
"""

import asyncio
import sys
from pathlib import Path

# Add parent path
sys.path.insert(0, str(Path(__file__).parent.parent / 'orchestration'))

from ai_orchestrator import AIOrchestrator, ModelConfig
import os

# API Configuration
API_KEY = os.getenv('QWEN_API_KEY', 'sk-sp-1dfff295506a4cbba9c3745dd54e5796')
API_ENDPOINT = 'https://coding-intl.dashscope.aliyuncs.com/v1'

# Model configurations
MODEL_CONFIGS = [
    ModelConfig(
        model_id='qwen3-coder-plus',
        api_key=API_KEY,
        api_endpoint=API_ENDPOINT,
        temperature=0.2,
        max_tokens=8192,
        system_prompt='Sen endüstriyel otomasyon, CNC, Python konularında uzman bir yazılım mühendisisin. Kod yazarken açık, yorumlu ve best-practice uygularsın.'
    ),
    ModelConfig(
        model_id='qwen3-coder-next',
        api_key=API_KEY,
        api_endpoint=API_ENDPOINT,
        temperature=0.3,
        max_tokens=4096,
        system_prompt='Sen ileri düzey kod üretimi yapan, modern tasarım desenleri uygulayan bir AI geliştiricisin.'
    ),
    ModelConfig(
        model_id='kimi-k2.5',
        api_key=API_KEY,
        api_endpoint=API_ENDPOINT,
        temperature=0.5,
        max_tokens=4096,
        system_prompt='Sen uzun dokümanları analiz eden, özetleyen ve teknik dokümantasyon hazırlayan bir AI asistansısın.'
    ),
]


async def run_parallel_tasks():
    """Run multiple AI tasks in parallel"""
    
    print("=" * 60)
    print("Parallel AI Task Runner")
    print("Glass Cutting Program - Next Features")
    print("=" * 60)
    
    orchestrator = AIOrchestrator(MODEL_CONFIGS)
    
    # Combined prompt for all 3 tasks
    combined_prompt = """
Glass Cutting Program için 3 modül oluştur:

## Task 1: DXF Import Module
- Parse AutoCAD DXF files (ezdxf library)
- Support: LINE, ARC, CIRCLE, POLYLINE
- Convert to ShapeDefinition objects
- Layer filtering
- Scale conversion to mm

## Task 2: Database Schema (SQLite)
- Tables: users, orders, cutting_history, defects, sheets
- SQLAlchemy ORM models
- Alembic migrations
- Indexes and foreign keys

## Task 3: Reports Module
- Daily/Weekly/Monthly reports
- PDF export (reportlab)
- Excel export (openpyxl)
- Charts (utilization, waste, orders)

Her modül için tam Python kodu oluştur (yorumlu).
"""

    print("\n🚀 Starting parallel AI tasks...\n")
    
    try:
        # Run parallel with 3 models
        responses = await orchestrator.run_parallel(
            combined_prompt,
            model_ids=['qwen3-coder-plus', 'qwen3-coder-next', 'kimi-k2.5']
        )
        
        output_dir = Path(__file__).parent / 'ai_task_results'
        output_dir.mkdir(exist_ok=True)
        
        # Save each response
        for i, response in enumerate(responses):
            output_file = output_dir / f"parallel_response_{i+1}_{response.model_id}.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Model: {response.model_id}\n")
                f.write(f"Latency: {response.latency}ms\n")
                f.write(f"Status: {response.status}\n")
                f.write("\n" + "=" * 60 + "\n\n")
                f.write(response.content)
            
            print(f"💾 Saved: {output_file}")
            print(f"   Model: {response.model_id}")
            print(f"   Latency: {response.latency}ms")
            print(f"   Content: {len(response.content)} chars\n")
        
        print("=" * 60)
        print(f"Completed: {len(responses)} responses")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nCreating placeholder files...")
        
        # Create placeholder files
        output_dir = Path(__file__).parent / 'ai_task_results'
        output_dir.mkdir(exist_ok=True)
        
        for task in ['DXF_Import', 'Database_Schema', 'Reports_Module']:
            output_file = output_dir / f"{task}.txt"
            with open(output_file, 'w') as f:
                f.write(f"Task: {task}\n")
                f.write("Status: Pending (AI API error)\n")
                f.write("\nPlease implement manually or retry AI call.\n")
            print(f"💾 Created placeholder: {output_file}")


if __name__ == '__main__':
    asyncio.run(run_parallel_tasks())