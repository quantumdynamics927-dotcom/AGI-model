"""
AGI-Model Research Console
===========================
Local-first Gradio interface for governed quantum AGI research.

Model routing:
  - llama3.2:1b  → default (fast, always-on)
  - qwen3:1.7b   → escalation (complex reasoning)
  - cloud models → explicit user request only

Integrated backends:
  - VCapture lifecycle governance
  - Phase 3 optimization
  - Consciousness validation framework
  - QAGI sacred geometry (topology explorer)
  - Golden test suite
  - Run history ledger
"""

import gradio as gr
import json
import datetime
import traceback
from pathlib import Path
from typing import Optional, Dict, Any, List

# ── Ollama local model client ──────────────────────────────────────────────
try:
    import ollama
    OLLAMA_AVAILABLE = True
    print("✅ Ollama Python client successfully imported")
except ImportError as e:
    OLLAMA_AVAILABLE = False
    print(f"❌ Ollama Python client import failed: {e}")

# ── Local backend imports (graceful degradation) ───────────────────────────
try:
    from vcapture_lifecycle_governance import VCaptureLifecycleGovernance
    GOVERNANCE_AVAILABLE = True
except ImportError:
    GOVERNANCE_AVAILABLE = False

try:
    from vcapture_canonical_schema import CanonicalGovernanceOutput
    CANONICAL_AVAILABLE = True
except ImportError:
    CANONICAL_AVAILABLE = False

try:
    from phase3_optimization import Phase3Optimizer
    PHASE3_AVAILABLE = True
except ImportError:
    PHASE3_AVAILABLE = False

try:
    from consciousness_validation_framework import ConsciousnessValidator
    CONSCIOUSNESS_AVAILABLE = True
except ImportError:
    CONSCIOUSNESS_AVAILABLE = False

try:
    from qagi_sacred_geometry_native import QAGISacredGeometrySystem
    TOPOLOGY_AVAILABLE = True
except ImportError:
    TOPOLOGY_AVAILABLE = False

try:
    from vcapture_golden_tests import GoldenTestSuite
    GOLDEN_TESTS_AVAILABLE = True
except ImportError:
    GOLDEN_TESTS_AVAILABLE = False

# ── Constants ──────────────────────────────────────────────────────────────
PHI = 1.6180339887498948482
LOCAL_MODELS = ["llama3.2:1b", "qwen3:1.7b"]
CLOUD_MODELS = ["glm-5", "claude-3-5-sonnet", "gpt-4o"]
RESEARCH_MODES = [
    "🔬 Governance Analysis",
    "🧠 Phase 3 Evaluation",
    "💡 Consciousness Validation",
    "🌀 Topology Explorer",
    "⚗️ Free Research",
]
RUN_HISTORY_PATH = Path("raw_hardware/vcapture_ledger_report.json")
LIFECYCLE_REPORT_PATH = Path("raw_hardware/lifecycle_assessment_v2.json")
PAIRED_FIXTURES_PATH = Path("paired_fixtures/index.json")

# ── Run history store (in-memory) ─────────────────────────────────────────
_run_history: List[Dict[str, Any]] = []


# ══════════════════════════════════════════════════════════════════════════
# MODEL ROUTING
# ══════════════════════════════════════════════════════════════════════════

def route_model(requested_model: str, complexity: str = "normal") -> str:
    """
    Local-first routing.
    - Default: llama3.2:1b
    - Complex queries: qwen3:1.7b
    - Cloud: only if user explicitly selects a cloud model
    """
    if requested_model in CLOUD_MODELS:
        return requested_model  # explicit cloud request
    if complexity == "complex":
        return "qwen3:1.7b"
    return "llama3.2:1b"


def detect_complexity(prompt: str) -> str:
    """Heuristic: escalate to qwen3 for long or technical prompts."""
    technical_keywords = [
        "quantum", "consciousness", "convergence", "sierpinski",
        "phi", "calibration", "governance", "entanglement", "hierarchical"
    ]
    if len(prompt) > 300:
        return "complex"
    if sum(1 for kw in technical_keywords if kw in prompt.lower()) >= 2:
        return "complex"
    return "normal"


def call_local_model(
    prompt: str,
    model: str,
    temperature: float = 0.7,
    system_prompt: Optional[str] = None
) -> str:
    """Call Ollama local model. Returns response string."""
    print(f"DEBUG: OLLAMA_AVAILABLE = {OLLAMA_AVAILABLE}, model = {model}")
    if not OLLAMA_AVAILABLE:
        return "⚠️ Ollama not available. Install with: pip install ollama"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        response = ollama.chat(
            model=model,
            messages=messages,
            options={"temperature": temperature}
        )
        return response["message"]["content"]
    except Exception as e:
        return f"⚠️ Model error ({model}): {str(e)}"


def get_research_system_prompt(mode: str) -> str:
    """Return mode-specific system prompt enforcing scientific discipline."""
    base = (
        "You are a quantum AGI research assistant operating under strict "
        "scientific governance. Distinguish raw data from derived conclusions. "
        "Cite artifacts when available. Separate hypothesis from evidence. "
        "Never make unsupported claims about consciousness or quantum effects. "
        f"Current date: {datetime.datetime.now().strftime('%Y-%m-%d')}. "
    )
    mode_additions = {
        "🔬 Governance Analysis": (
            "Focus on VCapture calibration lifecycle governance. "
            "Apply the canonical schema: 5 passing gates, 3 warnings "
            "(residual_spread, portability, rank_stability_ci). "
            "Current state: DEVELOPMENT. "
            "Reference promotion criteria explicitly."
        ),
        "🧠 Phase 3 Evaluation": (
            "Evaluate against Phase 3 optimization criteria. "
            "Focus on measurable improvements over Phase 2 baselines. "
            "Require quantitative evidence for any claim."
        ),
        "💡 Consciousness Validation": (
            "Apply the consciousness validation framework. "
            "Distinguish structural metrics from interpretive claims. "
            "Phi-coherence, convergence, and resonance are measurable; "
            "subjective experience claims require explicit epistemic flagging."
        ),
        "🌀 Topology Explorer": (
            "Reason about sacred geometry architecture. "
            "The defensible claim is: geometry-linked graph structure "
            "shows significant behavioral differences from matched controls. "
            "Phi uniqueness and Sierpinski uniqueness are NOT yet proven."
        ),
        "⚗️ Free Research": "",
    }
    return base + mode_additions.get(mode, "")


# ══════════════════════════════════════════════════════════════════════════
# BACKEND INTEGRATIONS
# ══════════════════════════════════════════════════════════════════════════

def run_governance_analysis() -> str:
    """Load and render current lifecycle assessment."""
    if not LIFECYCLE_REPORT_PATH.exists():
        return "⚠️ No lifecycle assessment found. Run vcapture_lifecycle_governance.py first."
    try:
        with open(LIFECYCLE_REPORT_PATH) as f:
            data = json.load(f)
        lines = [
            "## VCapture Lifecycle Assessment",
            f"**State**: {data.get('current_state', 'unknown').upper()}",
            f"**Eligible for promotion**: {data.get('eligible_for_promotion', False)}",
            "",
            "### Gate Summary",
        ]
        gate_summary = data.get("gate_summary", {})
        for gate, result in gate_summary.items():
            status = result.get("status", "unknown")
            value = result.get("value", "N/A")
            threshold = result.get("threshold", "N/A")
            icon = "✅" if status == "pass" else ("⚠️" if status == "warning" else "❌")
            lines.append(f"{icon} **{gate}**: {value} (threshold: {threshold})")
        rec = data.get("recommended_action", "N/A")
        lines.append(f"\n**Recommendation**: `{rec}`")
        return "\n".join(lines)
    except Exception as e:
        return f"⚠️ Error loading assessment: {e}"


def run_golden_tests() -> str:
    """Run golden test suite and return summary."""
    if not GOLDEN_TESTS_AVAILABLE:
        return "⚠️ Golden test suite not available."
    try:
        suite = GoldenTestSuite()
        results = suite.run_all()
        n_pass = sum(1 for r in results if r.get("passed"))
        n_fail = len(results) - n_pass
        lines = [
            f"## Golden Test Suite",
            f"**{n_pass}/{len(results)} passed** | {n_fail} failed",
            "",
        ]
        for r in results:
            icon = "✅" if r.get("passed") else "❌"
            lines.append(f"{icon} {r.get('name', 'unknown')}: {r.get('message', '')}")
        return "\n".join(lines)
    except Exception as e:
        return f"⚠️ Golden test error: {e}"


def get_topology_state() -> str:
    """Get current QAGI geometry state."""
    if not TOPOLOGY_AVAILABLE:
        return "⚠️ QAGI sacred geometry module not available."
    try:
        import torch
        qagi = QAGISacredGeometrySystem(dim=64, sierpinski_depth=3)
        test_input = torch.randn(1, 64)
        outputs = qagi.forward(test_input)
        state = qagi.get_geometric_state()
        lines = [
            "## QAGI Topology State",
            f"**Convergence**: {outputs['convergence']:.4f}",
            f"**Coherence**: {outputs['coherence']:.4f}",
            f"**Contained**: {outputs['contained']}",
            "",
            "### Six Node Harmonics",
        ]
        harmonics = state["six_nodes"]
        for node_id, node_data in harmonics.items():
            lines.append(
                f"- **{node_id}**: activation={node_data['activation']:.3f}, "
                f"resonance=φ^{round(node_data['resonance'] / PHI, 2)}"
            )
        lines += [
            "",
            "### Sierpinski Core",
            f"- Depth: {state['sierpinski_core']['depth']}",
            f"- Convergence: {state['sierpinski_core']['convergence']:.4f}",
            "",
            "### Defensible Claim",
            "> Graph structure shows significant behavioral differences from "
            "matched controls. Phi/Sierpinski uniqueness NOT yet proven.",
        ]
        return "\n".join(lines)
    except Exception as e:
        return f"⚠️ Topology error: {e}\n{traceback.format_exc()}"


def load_run_history() -> str:
    """Load VCapture ledger as run history."""
    if not RUN_HISTORY_PATH.exists():
        return "No run history found. Run vcapture_measurement_ledger.py first."
    try:
        with open(RUN_HISTORY_PATH) as f:
            data = json.load(f)
        summary = data.get("promoter_backend_summary", [])
        if not summary:
            return "Run history loaded but no promoter-backend summary found."
        lines = ["## Run History (VCapture Ledger)", ""]
        lines.append("| Promoter | Backend | N | Mean φ | Std φ | S/S |")
        lines.append("|---------|---------|---|--------|-------|-----|")
        for row in summary[:20]:
            lines.append(
                f"| {row.get('promoter','')} "
                f"| {row.get('backend','')} "
                f"| {row.get('n','')} "
                f"| {row.get('mean_phi',''):.4f} "
                f"| {row.get('std_phi',''):.6f} "
                f"| {row.get('ss',''):.2f} |"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"⚠️ Error loading run history: {e}"


def get_paired_fixtures_status() -> str:
    """Get paired fixtures comparison status."""
    if not PAIRED_FIXTURES_PATH.exists():
        return "⚠️ No paired fixtures found. Run vcapture_paired_fixtures.py --create first."
    try:
        with open(PAIRED_FIXTURES_PATH) as f:
            data = json.load(f)
        lines = [
            "## Paired Fixtures Status",
            f"**Comparison ID**: {data.get('comparison_id', 'unknown')}",
            f"**Timestamp**: {data.get('timestamp', 'unknown')}",
            f"**Policy Version**: {data.get('policy_version', 'unknown')}",
            "",
            "### Baseline vs Hierarchical",
            f"- **Baseline Hash**: {data.get('baseline_hash', 'unknown')}",
            f"- **Hierarchical Hash**: {data.get('hierarchical_hash', 'unknown')}",
            "",
            "### Gate Counts",
        ]
        baseline_counts = data.get("baseline_gate_counts", {})
        hierarchical_counts = data.get("hierarchical_gate_counts", {})
        lines.append(f"| Metric | Baseline | Hierarchical |")
        lines.append("|--------|----------|--------------|")
        lines.append(f"| Pass | {baseline_counts.get('pass', 0)} | {hierarchical_counts.get('pass', 0)} |")
        lines.append(f"| Warning | {baseline_counts.get('warning', 0)} | {hierarchical_counts.get('warning', 0)} |")
        lines.append(f"| Fail | {baseline_counts.get('fail', 0)} | {hierarchical_counts.get('fail', 0)} |")
        
        lines.append("")
        lines.append("### Improvement Summary")
        improvements = data.get("improvements", {})
        for key, value in improvements.items():
            lines.append(f"- **{key}**: {value}")
        
        return "\n".join(lines)
    except Exception as e:
        return f"⚠️ Error loading paired fixtures: {e}"


def get_system_status() -> str:
    """Get comprehensive system status."""
    lines = [
        "## System Status",
        f"**Timestamp**: {datetime.datetime.now().isoformat()}",
        "",
        "### Module Availability",
        f"- **Governance**: {'✅ Available' if GOVERNANCE_AVAILABLE else '❌ Not available'}",
        f"- **Canonical Schema**: {'✅ Available' if CANONICAL_AVAILABLE else '❌ Not available'}",
        f"- **Phase 3 Optimizer**: {'✅ Available' if PHASE3_AVAILABLE else '❌ Not available'}",
        f"- **Consciousness Validator**: {'✅ Available' if CONSCIOUSNESS_AVAILABLE else '❌ Not available'}",
        f"- **Topology Explorer**: {'✅ Available' if TOPOLOGY_AVAILABLE else '❌ Not available'}",
        f"- **Golden Tests**: {'✅ Available' if GOLDEN_TESTS_AVAILABLE else '❌ Not available'}",
        f"- **Ollama**: {'✅ Available' if OLLAMA_AVAILABLE else '❌ Not available'}",
        "",
        "### File Status",
        f"- **Lifecycle Report**: {'✅ Present' if LIFECYCLE_REPORT_PATH.exists() else '❌ Missing'}",
        f"- **Run History**: {'✅ Present' if RUN_HISTORY_PATH.exists() else '❌ Missing'}",
        f"- **Paired Fixtures**: {'✅ Present' if PAIRED_FIXTURES_PATH.exists() else '❌ Missing'}",
        "",
        "### Session Stats",
        f"- **Queries this session**: {len(_run_history)}",
    ]
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════
# CHAT HANDLER
# ══════════════════════════════════════════════════════════════════════════

def chat_handler(
    message: str,
    history: List[Dict[str, str]],
    research_mode: str,
    model_choice: str,
    temperature: float,
    use_cloud: bool,
) -> tuple:
    """Main chat handler with local-first routing."""
    if not message.strip():
        return history, ""

    # Route model
    if use_cloud and model_choice in CLOUD_MODELS:
        active_model = model_choice
        model_type = "cloud"
    else:
        complexity = detect_complexity(message)
        active_model = route_model(model_choice, complexity)
        model_type = "local"

    # Build context-aware prompt
    system_prompt = get_research_system_prompt(research_mode)

    # Inject governance context if relevant
    context_injection = ""
    if "governance" in message.lower() or research_mode == "🔬 Governance Analysis":
        context_injection = run_governance_analysis()
    elif "topology" in message.lower() or research_mode == "🌀 Topology Explorer":
        context_injection = get_topology_state()
    elif "phase 3" in message.lower() or research_mode == "🧠 Phase 3 Evaluation":
        context_injection = get_paired_fixtures_status()

    full_prompt = message
    if context_injection:
        full_prompt = f"[CONTEXT]\n{context_injection}\n\n[QUERY]\n{message}"

    # Call model
    if model_type == "local":
        response = call_local_model(
            full_prompt, active_model, temperature, system_prompt
        )
    else:
        response = f"⚠️ Cloud model routing not yet implemented for {active_model}. Using local fallback.\n\n"
        response += call_local_model(
            full_prompt, "llama3.2:1b", temperature, system_prompt
        )

    # Append model tag
    response_with_tag = (
        f"{response}\n\n---\n"
        f"*Model: `{active_model}` ({model_type}) | "
        f"Mode: {research_mode} | "
        f"Temp: {temperature}*"
    )

    # Store in run history
    _run_history.append({
        "timestamp": datetime.datetime.now().isoformat(),
        "mode": research_mode,
        "model": active_model,
        "model_type": model_type,
        "prompt_length": len(message),
        "response_length": len(response),
    })

    history = history or []
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response_with_tag})
    return history, ""


# ══════════════════════════════════════════════════════════════════════════
# THOUGHT GENERATOR
# ══════════════════════════════════════════════════════════════════════════

def generate_thought(
    seed_concept: str,
    thought_mode: str,
    model_choice: str,
    temperature: float,
) -> str:
    """Generate structured research thought from seed concept."""
    if not seed_concept.strip():
        return "Enter a seed concept to generate a thought."

    thought_prompts = {
        "Hypothesis": (
            f"Generate a falsifiable hypothesis about: {seed_concept}\n\n"
            "Requirements:\n"
            "1. State the hypothesis clearly\n"
            "2. Identify independent and dependent variables\n"
            "3. Propose a measurement method\n"
            "4. Define falsification criteria\n"
            "5. Note assumptions and limitations"
        ),
        "Mechanism": (
            f"Propose a mechanism for: {seed_concept}\n\n"
            "Requirements:\n"
            "1. Describe the mechanism step-by-step\n"
            "2. Identify key components\n"
            "3. Explain causal relationships\n"
            "4. Note testable predictions\n"
            "5. Acknowledge alternative mechanisms"
        ),
        "Critique": (
            f"Critically evaluate: {seed_concept}\n\n"
            "Requirements:\n"
            "1. Identify strengths\n"
            "2. Identify weaknesses\n"
            "3. Check for confounding variables\n"
            "4. Assess statistical validity\n"
            "5. Suggest improvements"
        ),
        "Extension": (
            f"Extend the concept: {seed_concept}\n\n"
            "Requirements:\n"
            "1. Identify the core insight\n"
            "2. Propose generalizations\n"
            "3. Consider edge cases\n"
            "4. Suggest new applications\n"
            "5. Note limitations of extension"
        ),
    }

    prompt = thought_prompts.get(thought_mode, thought_prompts["Hypothesis"])
    system_prompt = (
        "You are a rigorous scientific researcher. "
        "Generate structured, falsifiable thoughts. "
        "Distinguish observation from interpretation. "
        "Cite evidence where possible."
    )

    complexity = detect_complexity(seed_concept)
    active_model = route_model(model_choice, complexity)

    response = call_local_model(prompt, active_model, temperature, system_prompt)

    # Store in run history
    _run_history.append({
        "timestamp": datetime.datetime.now().isoformat(),
        "mode": f"Thought: {thought_mode}",
        "model": active_model,
        "model_type": "local",
        "prompt_length": len(seed_concept),
        "response_length": len(response),
    })

    return f"## {thought_mode}: {seed_concept}\n\n{response}"


# ══════════════════════════════════════════════════════════════════════════
# BENCHMARK HANDLERS
# ══════════════════════════════════════════════════════════════════════════

def run_local_benchmark() -> str:
    """Run local model benchmark."""
    if not OLLAMA_AVAILABLE:
        return "⚠️ Ollama not available for local benchmark."

    lines = ["## Local Model Benchmark", ""]
    
    test_prompts = [
        ("Simple", "What is 2+2?"),
        ("Medium", "Explain quantum entanglement in one sentence."),
        ("Complex", "Describe the relationship between phi resonance and consciousness emergence."),
    ]

    for model in LOCAL_MODELS:
        lines.append(f"### {model}")
        for difficulty, prompt in test_prompts:
            try:
                start = datetime.datetime.now()
                response = call_local_model(prompt, model, 0.7)
                elapsed = (datetime.datetime.now() - start).total_seconds()
                lines.append(f"- **{difficulty}**: {elapsed:.2f}s, {len(response)} chars")
            except Exception as e:
                lines.append(f"- **{difficulty}**: Error - {str(e)[:50]}")
        lines.append("")

    return "\n".join(lines)


def run_phase3_evaluation() -> str:
    """Run Phase 3 evaluation against baseline."""
    if not PHASE3_AVAILABLE:
        return "⚠️ Phase 3 optimizer not available."

    lines = [
        "## Phase 3 Evaluation",
        "",
        "### Criteria",
        "1. **Superiority**: At least one primary metric improvement",
        "2. **Non-inferiority**: No degradation in latency/robustness",
        "3. **Effect size**: Meaningful magnitude with confidence intervals",
        "",
        "### Current Status",
    ]

    # Check paired fixtures
    if PAIRED_FIXTURES_PATH.exists():
        lines.append(get_paired_fixtures_status())
    else:
        lines.append("Run `vcapture_paired_fixtures.py --create` to generate comparison.")

    return "\n".join(lines)


def run_consciousness_validation() -> str:
    """Run consciousness validation framework."""
    if not CONSCIOUSNESS_AVAILABLE:
        return "⚠️ Consciousness validation framework not available."

    lines = [
        "## Consciousness Validation Framework",
        "",
        "### Metrics",
        "- **Phi Resonance**: Deviation from φ ≈ 1.618",
        "- **LZ Complexity**: Lempel-Ziv compression complexity",
        "- **Entropy**: Information entropy",
        "- **Emergence Score**: Composite consciousness metric",
        "",
        "### Status",
        "Run `consciousness_validation_framework.py` for full validation.",
    ]
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════
# THOUGHT MEMORY
# ══════════════════════════════════════════════════════════════════════════

def get_thought_memory() -> str:
    """Get session thought memory."""
    if not _run_history:
        return "No thoughts recorded this session."

    lines = ["## Thought Memory (Session)", ""]
    for i, entry in enumerate(_run_history, 1):
        lines.append(f"### Entry {i}")
        lines.append(f"- **Time**: {entry['timestamp']}")
        lines.append(f"- **Mode**: {entry['mode']}")
        lines.append(f"- **Model**: {entry['model']} ({entry['model_type']})")
        lines.append(f"- **Prompt Length**: {entry['prompt_length']}")
        lines.append(f"- **Response Length**: {entry['response_length']}")
        lines.append("")

    return "\n".join(lines)


def clear_thought_memory() -> str:
    """Clear session thought memory."""
    global _run_history
    n = len(_run_history)
    _run_history = []
    return f"Cleared {n} entries from thought memory."


# ══════════════════════════════════════════════════════════════════════════
# GRADIO INTERFACE
# ══════════════════════════════════════════════════════════════════════════

def create_interface() -> gr.Blocks:
    """Create the Gradio interface."""
    
    with gr.Blocks(title="AGI-Model Research Console") as app:
        gr.Markdown("""
        # 🤖 AGI-Model Research Console
        **Observability-first demo for QAGI precursor stack evaluation**
        
        Local-first model routing: `llama3.2:1b` (default) → `qwen3:1.7b` (complex) → cloud (explicit)
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                research_mode = gr.Dropdown(
                    choices=RESEARCH_MODES,
                    value="🔬 Governance Analysis",
                    label="Research Mode",
                    info="Select analysis mode"
                )
                model_choice = gr.Dropdown(
                    choices=LOCAL_MODELS + CLOUD_MODELS,
                    value="llama3.2:1b",
                    label="Model",
                    info="Local models preferred"
                )
                temperature = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    value=0.7,
                    step=0.1,
                    label="Temperature",
                    info="Higher = more creative"
                )
                use_cloud = gr.Checkbox(
                    value=False,
                    label="Use Cloud Model",
                    info="Explicitly route to cloud"
                )
        
        with gr.Tabs():
            # Tab 1: Chat
            with gr.TabItem("💬 Chat"):
                chatbot = gr.Chatbot(
                    label="Research Chat",
                    height=500
                )
                with gr.Row():
                    chat_input = gr.Textbox(
                        label="Enter prompt",
                        placeholder="Analyze this experiment against Phase 3 criteria...",
                        scale=4
                    )
                    chat_submit = gr.Button("Send", variant="primary", scale=1)
                chat_clear = gr.Button("Clear Chat")
                
                chat_submit.click(
                    fn=chat_handler,
                    inputs=[chat_input, chatbot, research_mode, model_choice, temperature, use_cloud],
                    outputs=[chatbot, chat_input]
                )
                chat_clear.click(lambda: ([], ""), outputs=[chatbot, chat_input])
            
            # Tab 2: Benchmark
            with gr.TabItem("📊 Benchmark"):
                gr.Markdown("### Local Model Benchmark")
                benchmark_btn = gr.Button("Run Benchmark", variant="primary")
                benchmark_output = gr.Markdown(label="Results")
                benchmark_btn.click(fn=run_local_benchmark, outputs=benchmark_output)
            
            # Tab 3: Run History
            with gr.TabItem("📜 Run History"):
                gr.Markdown("### VCapture Ledger History")
                history_btn = gr.Button("Load History", variant="primary")
                history_output = gr.Markdown(label="Run History")
                history_btn.click(fn=load_run_history, outputs=history_output)
            
            # Tab 4: System
            with gr.TabItem("⚙️ System"):
                gr.Markdown("### System Status")
                system_btn = gr.Button("Refresh Status", variant="primary")
                system_output = gr.Markdown(label="Status")
                system_btn.click(fn=get_system_status, outputs=system_output)
            
            # Tab 5: Generate Thought
            with gr.TabItem("🧠 Generate Thought"):
                gr.Markdown("### Structured Research Thought Generator")
                seed_concept = gr.Textbox(
                    label="Seed Concept",
                    placeholder="e.g., phi resonance in VAE latent space",
                    lines=2
                )
                thought_mode = gr.Dropdown(
                    choices=["Hypothesis", "Mechanism", "Critique", "Extension"],
                    value="Hypothesis",
                    label="Thought Mode"
                )
                thought_btn = gr.Button("Generate Thought", variant="primary")
                thought_output = gr.Markdown(label="Generated Thought")
                thought_btn.click(
                    fn=generate_thought,
                    inputs=[seed_concept, thought_mode, model_choice, temperature],
                    outputs=thought_output
                )
            
            # Tab 6: Cloud Benchmark
            with gr.TabItem("☁️ Cloud Benchmark"):
                gr.Markdown("### Cloud Model Benchmark (Coming Soon)")
                gr.Markdown(
                    "Cloud model routing requires API keys. "
                    "Currently falls back to local models."
                )
                cloud_benchmark_output = gr.Markdown(
                    "Cloud benchmark not yet implemented.\n\n"
                    "Available cloud models:\n"
                    "- glm-5\n"
                    "- claude-3-5-sonnet\n"
                    "- gpt-4o\n\n"
                    "Configure API keys in environment variables."
                )
            
            # Tab 7: System Status
            with gr.TabItem("🔧 System Status"):
                gr.Markdown("### Module and File Status")
                status_btn = gr.Button("Check Status", variant="primary")
                status_output = gr.Markdown(label="Status")
                status_btn.click(fn=get_system_status, outputs=status_output)
            
            # Tab 8: Thought Memory
            with gr.TabItem("💾 Thought Memory"):
                gr.Markdown("### Session Thought Memory")
                with gr.Row():
                    memory_btn = gr.Button("View Memory", variant="primary")
                    clear_memory_btn = gr.Button("Clear Memory", variant="secondary")
                memory_output = gr.Markdown(label="Memory")
                memory_btn.click(fn=get_thought_memory, outputs=memory_output)
                clear_memory_btn.click(fn=clear_thought_memory, outputs=memory_output)
            
            # Tab 9: Topology Explorer
            with gr.TabItem("🌐 Topology Explorer"):
                gr.Markdown("### QAGI Sacred Geometry Topology")
                topology_btn = gr.Button("Explore Topology", variant="primary")
                topology_output = gr.Markdown(label="Topology State")
                topology_btn.click(fn=get_topology_state, outputs=topology_output)
            
            # Tab 10: About
            with gr.TabItem("ℹ️ About"):
                gr.Markdown("""
                ## AGI-Model Research Console
                
                **Version**: 1.0.0
                **Purpose**: Observability-first interface for QAGI precursor stack evaluation
                
                ### Features
                - **Local-first model routing**: Defaults to Ollama models
                - **Governance integration**: VCapture lifecycle governance
                - **Phase 3 evaluation**: Baseline vs hierarchical comparison
                - **Consciousness validation**: Framework for emergence metrics
                - **Topology explorer**: QAGI sacred geometry state
                - **Thought memory**: Session-based research memory
                
                ### Model Routing
                | Model | Type | Use Case |
                |-------|------|----------|
                | llama3.2:1b | Local | Default (fast) |
                | qwen3:1.7b | Local | Complex reasoning |
                | glm-5 | Cloud | Explicit request |
                | claude-3-5-sonnet | Cloud | Explicit request |
                | gpt-4o | Cloud | Explicit request |
                
                ### Governance
                - **Policy Version**: 2.1.0
                - **State Machine**: development → candidate → staging → production → retired
                - **Golden Tests**: Frozen historical assessments for regression safety
                
                ### Defensible Claims
                > Geometry-linked graph structure shows significant behavioral differences 
                > from matched controls. Phi uniqueness and Sierpinski uniqueness are 
                > NOT yet proven.
                
                ### References
                - [VCapture Governance Summary](VCAPTURE_GOVERNANCE_SUMMARY.md)
                - [Phase 3 Optimization](phase3_optimization.py)
                - [Consciousness Validation Framework](consciousness_validation_framework.py)
                """)
        
        gr.Markdown("""
        ---
        **AGI-Model Research Console** | Local-first | Governance-integrated | Observability-first
        """)
    
    return app


def main():
    """Launch the Research Console."""
    app = create_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        theme=gr.themes.Soft(),
        css="""
        .gradio-container { max-width: 1400px !important; }
        .tab-nav { flex-wrap: wrap !important; }
        """
    )


if __name__ == "__main__":
    main()