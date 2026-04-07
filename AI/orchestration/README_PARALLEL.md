# CNC AI Orchestrator - Parallel Model Usage

## 🚀 Quick Start

### Test Parallel Model Usage
```bash
cd AI/orchestration

# Test with a simple question using 3 models in parallel
python ai_orchestrator.py --parallel \
  --models qwen3.5-plus,qwen3-max-2026-01-23,qwen3-coder-plus \
  --prompt "Explain EtherCAT communication cycle"
```

### Test MCP Server
```bash
# Start MCP server manually for testing
python mcp_server.py
```

## 📋 Available Models (Alibaba Cloud Lite Plan)

| Model ID | Provider | Best For | Temperature |
|----------|----------|----------|-------------|
| `qwen3.5-plus` | Qwen | General purpose, fast responses | 0.7 |
| `qwen3-max-2026-01-23` | Qwen | Complex analysis, problem solving | 0.5 |
| `qwen3-coder-plus` | Qwen | Code generation (Python, FreeCAD, G-code, PLC) | 0.2 |
| `qwen3-coder-next` | Qwen | Advanced code generation | 0.3 |
| `glm-4.7` | Zhipu | Alternative model, cross-validation | 0.6 |
| `kimi-k2.5` | MiniMax | Long context, documentation | 0.5 |

## 🎯 Usage Examples

### 1. Single Model Query (Fastest, Token Efficient)
```bash
python ai_orchestrator.py --mode single \
  --model qwen3.5-plus \
  --prompt "What is EtherCAT cycle time?"
```

### 2. Parallel Models (Best for Critical Decisions)
```bash
python ai_orchestrator.py --mode parallel \
  --models qwen3.5-plus,qwen3-max-2026-01-23,qwen3-coder-plus \
  --prompt "How to tune servo motor parameters for Delta ASDA-A3-E?"
```

### 3. Smart Task Routing (Automatic Model Selection)
```bash
# For coding tasks - automatically uses coder models
python ai_orchestrator.py --mode parallel \
  --task-type code \
  --prompt "Write Python function for linear interpolation"
```

### 4. Voting Mode (Fastest Successful Response Wins)
```bash
python ai_orchestrator.py --mode voting \
  --models qwen3.5-plus,qwen3-max-2026-01-23,qwen3-coder-plus \
  --prompt "Explain G53 vs G54 G-code commands"
```

### 5. Comparison Mode (Side-by-Side Table)
```bash
python ai_orchestrator.py --mode aggregate \
  --aggregate-method compare \
  --models qwen3.5-plus,qwen3-max-2026-01-23 \
  --prompt "What are the differences between EtherCAT and Profinet?"
```

## 🔧 Configuration

Edit `orchestrator_config.json`:

```json
{
  "lite_plan_optimized": true,
  "max_concurrent_requests": 3,
  "rate_limit_per_minute": 60,
  
  "parallel_settings": {
    "default_mode": "parallel",
    "max_parallel_models": 3,
    "timeout_seconds": 90,
    "retry_on_failure": true,
    "fallback_model": "qwen3.5-plus"
  }
}
```

## 📊 Performance Tips

### For Lite Basic Plan:
1. **Use 2-3 models max** in parallel to stay within rate limits
2. **Use `qwen3.5-plus`** for routine questions (fastest, cheapest)
3. **Use `ai_code` tool** for coding tasks (auto-selects best models)
4. **Use `ai_debug` tool** for error troubleshooting (dual model analysis)
5. **Set `max_parallel=3`** to avoid overwhelming the API

### Token Optimization:
- Single model: ~500-1000 tokens
- Parallel (3 models): ~1500-3000 tokens
- Use smart routing to minimize unnecessary model calls

## 🛠️ MCP Tools in Cline

When using VS Code with Cline extension:

1. **ai_ask** - Single model query
2. **ai_ask_parallel** - Parallel multi-model query
3. **ai_ask_smart** - Smart task routing
4. **ai_code** - Code generation (2 models parallel)
5. **ai_debug** - Error debugging (2 models parallel)
6. **ai_optimize** - Optimization tasks (2 models parallel)
7. **ai_compare** - Model comparison table
8. **ai_list_models** - List available models

## 📈 Monitoring

Each response includes:
- ⏱️ **Latency:** Response time in milliseconds
- 📝 **Tokens:** Token count used
- ✅/❌ **Status:** Success or error

## 🔍 Troubleshooting

### Connection Issues
```bash
# Check Python version (should be 3.8+)
python3 --version

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### API Errors
- Verify API key in `orchestrator_config.json`
- Check rate limits (60 requests/minute for Lite plan)
- Reduce `max_parallel_models` if hitting limits

### Timeout Errors
- Increase `timeout_seconds` in config (default: 90)
- Reduce number of parallel models
- Check network connection

## 📝 Example Output

```
📊 Parallel Model Responses (3 models)

============================================================
✅ 1. qwen3.5-plus (1250ms)
============================================================
EtherCAT cycle time refers to the communication interval...

============================================================
✅ 2. qwen3-max-2026-01-23 (2100ms)
============================================================
In-depth analysis: EtherCAT cycle time impacts system...

============================================================
✅ 3. qwen3-coder-plus (1800ms)
============================================================
For Delta NC300: Parameters for 100μs cycle time...
```

---

**Version:** 2.0 (Lite Plan Optimized)  
**Last Updated:** 2026-04-07
