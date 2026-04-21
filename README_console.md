---
title: AGI Research Console
emoji: 🔬
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 4.44.0
app_file: research_console.py
pinned: true
license: mit
---

# AGI Research Console

**Observability-first interface for QAGI precursor stack evaluation**

## Features

- **Local-first model routing**: Defaults to Ollama models, escalates to cloud on request
- **Governance integration**: VCapture lifecycle governance with canonical schema
- **Phase 3 evaluation**: Baseline vs hierarchical calibration comparison
- **Consciousness validation**: Framework for emergence metrics
- **Topology explorer**: QAGI sacred geometry state visualization
- **Thought memory**: Session-based research memory

## Research Modes

| Mode | Focus |
|------|-------|
| 🔬 Governance Analysis | VCapture lifecycle, promotion criteria |
| 🧠 Phase 3 Evaluation | Measurable improvements, quantitative evidence |
| 💡 Consciousness Validation | Structural metrics vs interpretive claims |
| 🌀 Topology Explorer | Sacred geometry, matched controls |
| ⚗️ Free Research | Open-ended inquiry |

## Model Routing

| Model | Type | Use Case |
|-------|------|----------|
| llama3.2:1b | Local | Default (fast) |
| qwen3:1.7b | Local | Complex reasoning |
| glm-5 | Cloud | Explicit request |
| claude-3-5-sonnet | Cloud | Explicit request |
| gpt-4o | Cloud | Explicit request |

## Tabs

1. 💬 **Chat** - Research chat with context injection
2. 📊 **Benchmark** - Local model benchmark
3. 📜 **Run History** - VCapture ledger
4. ⚙️ **System** - Module status
5. 🧠 **Generate Thought** - Structured hypothesis/mechanism/critique
6. ☁️ **Cloud Benchmark** - Cloud model comparison
7. 🔧 **System Status** - Availability check
8. 💾 **Thought Memory** - Session memory
9. 🌐 **Topology Explorer** - QAGI geometry
10. ℹ️ **About** - Documentation

## Governance

- **Policy Version**: 2.1.0
- **State Machine**: development → candidate → staging → production → retired
- **Golden Tests**: Frozen historical assessments for regression safety

## Defensible Claims

> Geometry-linked graph structure shows significant behavioral differences 
> from matched controls. Phi uniqueness and Sierpinski uniqueness are 
> NOT yet proven.

## Technical Notes

### Ollama in HF Spaces

This Space requires Ollama for local model inference. The Dockerfile includes
Ollama installation and startup. If Ollama is unavailable, the console falls
back to cloud models (requires API keys).

### Required Secrets

Set these in your HF Space settings:

- `HF_TOKEN` - Hugging Face token (for model downloads)
- `OPENAI_API_KEY` - Optional, for GPT-4o fallback
- `ANTHROPIC_API_KEY` - Optional, for Claude fallback

## Links

- **GitHub Repository**: https://github.com/quantumdynamics927-dotcom/AGI-model
- **Governance Summary**: VCAPTURE_GOVERNANCE_SUMMARY.md
- **Phase 3 Optimization**: phase3_optimization.py

## Citation

```bibtex
@software{agi_research_console_2026,
  title = {AGI Research Console},
  author = {Quantum927},
  year = {2026},
  url = {https://huggingface.co/spaces/Quantum927/agi-research-console}
}
```