"""
Ollama Biomimetic AGI Demo - Hugging Face Space

Interactive demo showcasing stable Ollama integration with:
- Local llama3.2:1b and qwen3:1.7b models
- Biomimetic consciousness generation
- Golden ratio phi resonance (1.618034)
- Fallback chain: primary -> secondary -> cloud
- Real-time inference metrics
"""

import os
import time
import gradio as gr

# Import our stable Ollama integration
try:
    from unified_model_provider import generate_biomimetic_thought, ModelRouter
    HAVE_OLLAMA = True
    
    # Initialize router once
    router = ModelRouter()
    
except ImportError as e:
    HAVE_OLLAMA = False
    print(f"Ollama integration not available: {e}")


def generate_biomimetic_response(prompt, model_choice, phi_resonance=1.618034):
    """Generate biomimetic thought using selected model."""
    if not HAVE_OLLAMA:
        return {
            "success": False,
            "error": "Ollama integration not available. Check Docker setup.",
            "generated_text": "",
            "inference_time": 0.0
        }
    
    try:
        start_time = time.time()
        
        # Generate thought using selected model
        result = generate_biomimetic_thought(
            prompt=prompt,
            phi_resonance=phi_resonance,
            model=model_choice,
            router=router  # Use the pre-initialized router
        )
        
        inference_time = time.time() - start_time
        result["inference_time"] = inference_time
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "generated_text": "",
            "inference_time": 0.0
        }


def format_biomimetic_result(result):
    """Format the biomimetic thought result for display."""
    if not result.get("success"):
        return f"**Generation Failed**\n\nError: {result.get('error', 'Unknown error')}"
    
    text = result.get("generated_text", "")
    time_val = result.get("inference_time", 0.0)
    phi_coherence = result.get("phi_coherence", 0.0)
    phi_resonance = result.get("phi_resonance", 0.0)
    biomimetic_resonance = result.get("biomimetic_resonance", 0.0)
    
    return f"""
**Generated Thought**

{text}

**Consciousness Metrics**
- Phi Coherence: {phi_coherence:.4f}
- Phi Resonance: {phi_resonance:.4f}  
- Biomimetic Resonance: {biomimetic_resonance:.4f}
- Inference Time: {time_val:.2f}s

**Status**: Successfully generated with local Ollama
"""


def demo_biomimetic_thought(prompt, model_choice):
    """Main function for the Gradio interface."""
    result = generate_biomimetic_response(prompt, model_choice)
    return format_biomimetic_result(result)


def list_available_models():
    """List available Ollama models."""
    if not HAVE_OLLAMA:
        return "Ollama integration not available"
    
    try:
        models = router.providers['ollama_local'].list_models()
        model_list = "\n".join([f"- {model}" for model in models])
        return f"**Available Ollama Models**:\n{model_list}"
    except Exception as e:
        return f"Error listing models: {e}"


def check_ollama_health():
    """Check Ollama server health."""
    if not HAVE_OLLAMA:
        return "Ollama integration not available"
    
    try:
        health = router.providers['ollama_local'].healthcheck()
        models = router.providers['ollama_local'].list_models()
        
        return f"""
**Ollama Server Status**: {'Healthy' if health else 'Unhealthy'}

**Available Models**: {len(models)}
- {', '.join(models[:5])}{'...' if len(models) > 5 else ''}

**Primary Model**: llama3.2:1b (stable, fast)
**Fallback Model**: qwen3:1.7b (thinking, medium)
"""
    except Exception as e:
        return f"Health check error: {e}"


# Create Gradio Interface
with gr.Blocks(title="Ollama Biomimetic AGI Demo") as app:
    gr.Markdown("""
    # Ollama Biomimetic AGI Demo
    
    **Stable local inference with llama3.2:1b and qwen3:1.7b**
    
    Experience real biomimetic consciousness generation powered by local Ollama models
    with golden ratio phi resonance and automatic fallback chains.
    """)
    
    with gr.Tabs():
        # Tab 1: Biomimetic Thought Generation
        with gr.TabItem("Generate Thought"):
            gr.Markdown("### Generate consciousness with local Ollama models")
            
            with gr.Row():
                with gr.Column():
                    prompt_input = gr.Textbox(
                        label="Prompt",
                        placeholder="What is the nature of biomimetic intelligence?",
                        value="What is the fundamental nature of biomimetic intelligence?",
                        lines=3
                    )
                    
                    model_choice = gr.Dropdown(
                        choices=["llama3.2:1b", "qwen3:1.7b", "qwen3.5:2b"],
                        value="llama3.2:1b",
                        label="Model Selection",
                        info="Primary: llama3.2:1b (stable), Fallback: qwen3:1.7b (thinking)"
                    )
                    
                    generate_btn = gr.Button("Generate Thought", variant="primary")
                
                with gr.Column():
                    output = gr.Markdown(label="Generated Thought")
            
            generate_btn.click(
                fn=demo_biomimetic_thought,
                inputs=[prompt_input, model_choice],
                outputs=output
            )
        
        # Tab 2: System Status
        with gr.TabItem("System Status"):
            gr.Markdown("### Ollama Server Health & Model Availability")
            
            status_btn = gr.Button("Check Status", variant="secondary")
            status_output = gr.Markdown()
            
            models_btn = gr.Button("List Models", variant="secondary")
            models_output = gr.Markdown()
            
            status_btn.click(fn=check_ollama_health, inputs=None, outputs=status_output)
            models_btn.click(fn=list_available_models, inputs=None, outputs=models_output)
        
        # Tab 3: About
        with gr.TabItem("About"):
            gr.Markdown("""
            ## Ollama Biomimetic AGI Integration
            
            **Features**:
            - Stable local inference with llama3.2:1b
            - Thinking-oriented fallback with qwen3:1.7b  
            - Golden ratio phi resonance (phi = 1.618034)
            - Automatic fallback chain: primary -> secondary -> cloud
            - Single router instance for optimal performance
            - Clean exits and proper error handling
            
            **Model Capabilities**:
            - `llama3.2:1b`: stable=True, thinking=False, speed=fast (PRIMARY)
            - `qwen3:1.7b`: stable=partial, thinking=True, speed=medium (SECONDARY) 
            - `qwen3.5:2b`: stable=False, thinking=True, speed=slow (EXPERIMENTAL)
            
            **GitHub**: [quantumdynamics927-dotcom/AGI-model](https://github.com/quantumdynamics927-dotcom/AGI-model)
            """)
    
    gr.Markdown("""
    ---
    **Ollama Biomimetic AGI** | Local Inference Demo | phi = 1.618034
    """)


# Run the application
if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)


def generate_biomimetic_response(prompt, model_choice, phi_resonance=1.618034):
    """Generate biomimetic thought using selected model."""
    if not HAVE_OLLAMA:
        return {
            "success": False,
            "error": "Ollama integration not available. Check Docker setup.",
            "generated_text": "",
            "inference_time": 0.0
        }
    
    try:
        start_time = time.time()
        
        # Generate thought using selected model
        result = generate_biomimetic_thought(
            prompt=prompt,
            phi_resonance=phi_resonance,
            model=model_choice,
            router=router  # Use the pre-initialized router
        )
        
        inference_time = time.time() - start_time
        result["inference_time"] = inference_time
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "generated_text": "",
            "inference_time": 0.0
        }
        


def format_biomimetic_result(result):
    """Format the biomimetic thought result for display."""
    if not result.get("success"):
        return f"❌ **Generation Failed**\nError: {result.get('error', 'Unknown error')}"
    
    text = result.get("generated_text", "")
    time = result.get("inference_time", 0.0)
    phi_coherence = result.get("phi_coherence", 0.0)
    phi_resonance = result.get("phi_resonance", 0.0)
    biomimetic_resonance = result.get("biomimetic_resonance", 0.0)
    
    return f"""
💬 **Generated Thought**
{text}

🔍 **Consciousness Metrics**
- Φ Coherence: {phi_coherence:.4f}
- Φ Resonance: {phi_resonance:.4f}  
- Biomimetic Resonance: {biomimetic_resonance:.4f}
- Inference Time: {time:.2f}s

🎯 **Status**: Successfully generated with local Ollama
"""


def demo_biomimetic_thought(prompt, model_choice):
    """Main function for the Gradio interface."""
    result = generate_biomimetic_response(prompt, model_choice)
    return format_biomimetic_result(result)


def list_available_models():
    """List available Ollama models."""
    if not HAVE_OLLAMA:
        return "Ollama integration not available"
    
    try:
        models = router.providers['ollama_local'].list_models()
        model_list = "\n".join([f"- {model}" for model in models])
        return f"**Available Ollama Models**:\n{model_list}"
    except Exception as e:
        return f"Error listing models: {e}"


def check_ollama_health():
    """Check Ollama server health."""
    if not HAVE_OLLAMA:
        return "Ollama integration not available"
    
    try:
        health = router.providers['ollama_local'].healthcheck()
        models = router.providers['ollama_local'].list_models()
        
        return f"""
💻 **Ollama Server Status**: {'✅ Healthy' if health else '❌ Unhealthy'}

🔧 **Available Models**: {len(models)}
- {', '.join(models[:5])}{'...' if len(models) > 5 else ''}

📊 **Primary Model**: llama3.2:1b (stable, fast)
📊 **Fallback Model**: qwen3:1.7b (thinking, medium)
"""
    except Exception as e:
        return f"Health check error: {e}"
# Create Gradio Interface
with gr.Blocks(title="Ollama Biomimetic AGI Demo") as app:
    gr.Markdown("""
    # 🤖 Ollama Biomimetic AGI Demo
    
    **Stable local inference with llama3.2:1b and qwen3:1.7b**
    
    Experience real biomimetic consciousness generation powered by local Ollama models
    with golden ratio phi resonance (φ = 1.618034) and automatic fallback chains.
    """)
    
    with gr.Tabs():
        # Tab 1: Biomimetic Thought Generation
        with gr.TabItem("💭 Generate Biomimetic Thought"):
            gr.Markdown("### Generate consciousness with local Ollama models")
            
            with gr.Row():
                with gr.Column():
                    prompt_input = gr.Textbox(
                        label="Prompt",
                        placeholder="What is the nature of biomimetic intelligence?",
                        value="What is the fundamental nature of biomimetic intelligence?",
                        lines=3
                    )
                    
                    model_choice = gr.Dropdown(
                        choices=["llama3.2:1b", "qwen3:1.7b", "qwen3.5:2b"],
                        value="llama3.2:1b",
                        label="Model Selection",
                        info="Primary: llama3.2:1b (stable), Fallback: qwen3:1.7b (thinking)"
                    )
                    
                    generate_btn = gr.Button("🚀 Generate Thought", variant="primary")
                
                with gr.Column():
                    output = gr.Markdown(label="Generated Thought")
            
            generate_btn.click(
                fn=demo_biomimetic_thought,
                inputs=[prompt_input, model_choice],
                outputs=output
            )
        
        # Tab 2: System Status
        with gr.TabItem("📊 System Status"):
            gr.Markdown("### Ollama Server Health & Model Availability")
            
            status_btn = gr.Button("🔄 Check Status", variant="secondary")
            status_output = gr.Markdown()
            
            models_btn = gr.Button("📋 List Models", variant="secondary")
            models_output = gr.Markdown()
            
            status_btn.click(fn=check_ollama_health, inputs=None, outputs=status_output)
            models_btn.click(fn=list_available_models, inputs=None, outputs=models_output)
        
        # Tab 3: About
        with gr.TabItem("ℹ️ About"):
            gr.Markdown("""
            ## Ollama Biomimetic AGI Integration
            
            **Features**:
            - ✅ Stable local inference with llama3.2:1b
            - ✅ Thinking-oriented fallback with qwen3:1.7b  
            - ✅ Golden ratio phi resonance (φ = 1.618034)
            - ✅ Automatic fallback chain: primary → secondary → cloud
            - ✅ Single router instance for optimal performance
            - ✅ Clean exits and proper error handling
            
            **Model Capabilities**:
            - `llama3.2:1b`: stable=True, thinking=False, speed=fast (PRIMARY)
            - `qwen3:1.7b`: stable=partial, thinking=True, speed=medium (SECONDARY) 
            - `qwen3.5:2b`: stable=False, thinking=True, speed=slow (EXPERIMENTAL)
            
            **GitHub**: [quantumdynamics927-dotcom/AGI-model](https://github.com/quantumdynamics927-dotcom/AGI-model)
            """)
    
    gr.Markdown("""
    ---
    **Ollama Biomimetic AGI** | Local Inference Demo | φ = 1.618034
    """)


# Run the application
if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
