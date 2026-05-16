"""
Scientific Python Ecosystem for Quantum AGI Research
Hugging Face Gradio Space

An interactive demonstration of NumPy, Pandas, SciPy, Matplotlib, 
Scikit-learn, Qiskit, and Numba for quantum consciousness research.
"""

import gradio as gr
import numpy as np
import pandas as pd
from scipy import optimize, integrate, stats
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from io import BytesIO
from PIL import Image
import time

# Try optional imports
try:
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import classification_report, accuracy_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from qiskit import QuantumCircuit, Aer, execute
    import qiskit
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False

try:
    from numba import jit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

# Constants
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
PHI_INV = 1 / PHI


def numpy_demo():
    """Demonstrate NumPy operations for quantum research."""
    results = []
    
    # Golden ratio constants
    results.append(f"**Golden Ratio (φ):** {PHI:.10f}")
    results.append(f"**Golden Ratio Inverse (φ⁻¹):** {PHI_INV:.10f}")
    
    # Latent vector (like VAE)
    np.random.seed(42)
    latent_dim = 32
    latent_vector = np.random.randn(4, latent_dim)
    results.append(f"\n**Latent vector shape:** {latent_vector.shape}")
    
    # Density matrix (quantum state)
    psi = np.random.randn(4) + 1j * np.random.randn(4)
    psi = psi / np.linalg.norm(psi)
    density_matrix = np.outer(psi, np.conj(psi))
    results.append(f"**Density matrix shape:** {density_matrix.shape}")
    results.append(f"**Trace:** {np.trace(density_matrix):.10f}")
    results.append(f"**Is Hermitian:** {np.allclose(density_matrix, density_matrix.T.conj())}")
    
    # Phi-harmonic sequence
    phi_harmonic = np.array([PHI ** n for n in range(-3, 4)])
    results.append(f"\n**Phi-harmonic sequence:** `{phi_harmonic.round(4)}`")
    
    return "\n".join(results)


def pandas_demo():
    """Demonstrate Pandas DataFrame for time-series metrics."""
    np.random.seed(42)
    dates = pd.date_range(start='2026-01-01', periods=10, freq='D')
    
    df = pd.DataFrame({
        'timestamp': dates.strftime('%Y-%m-%d'),
        'metric_a': np.random.uniform(0.5, 0.7, 10),
        'metric_b': np.random.uniform(0.3, 0.9, 10),
        'metric_c': np.random.uniform(0.1, 0.5, 10),
        'metric_d': np.random.uniform(0.8, 1.0, 10),
    })
    
    stats_df = df.describe().round(4)
    
    return df.round(4), stats_df


def scipy_demo():
    """Demonstrate SciPy optimization and statistics."""
    results = []
    
    # Optimization: Demonstrate minimizer finding known constant
    def phi_loss(x):
        return (x - PHI_INV) ** 2
    
    result = optimize.minimize_scalar(phi_loss, bounds=(0.5, 0.7), method='bounded')
    results.append("### SciPy Optimization Demo")
    results.append(f"**Minimizer target:** φ⁻¹ = {PHI_INV:.10f}")
    results.append(f"**Recovered value:** {result.x:.10f}")
    results.append(f"**Residual error:** {abs(result.x - PHI_INV):.2e} ✓ Optimizer verified")
    
    # Integration: Domain integral of sampled density function
    def sample_density(x):
        """Sample density function centered at φ⁻¹ for demonstration."""
        return np.exp(-((x - PHI_INV) ** 2) / 0.1)
    
    integral, error = integrate.quad(sample_density, 0, 1)
    results.append(f"\n### Integration Demo")
    results.append(f"**Domain integral of sampled density:** {integral:.6f} ± {error:.2e}")
    
    # Statistics: Normality test on sample distribution
    sample = np.random.normal(loc=PHI_INV, scale=0.1, size=100)
    stat, p_value = stats.normaltest(sample)
    results.append(f"\n### Statistical Validation")
    results.append(f"**Normality test on 100-sample draw:**")
    results.append(f"- Statistic: {stat:.4f}")
    results.append(f"- p-value: {p_value:.4f}")
    results.append(f"- Result: {'Gaussian-compatible (p > 0.05) ✓' if p_value > 0.05 else 'Non-Gaussian (p ≤ 0.05)'}")
    
    # Binomial distribution (102 qubits)
    binom = stats.binom(n=102, p=0.5)
    results.append(f"\n### Binomial Model (n=102, p=0.5)")
    results.append(f"- Mean: {binom.mean():.2f}")
    results.append(f"- Std: {binom.std():.2f}")
    
    return "\n".join(results)


def matplotlib_demo():
    """Generate visualization plots."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 1. Phi-harmonic sequence
    phi_powers = np.arange(-5, 6)
    phi_values = PHI ** phi_powers
    axes[0, 0].semilogy(phi_powers, phi_values, 'o-', linewidth=2, markersize=8, color='purple')
    axes[0, 0].axhline(y=1, color='gray', linestyle='--', alpha=0.5)
    axes[0, 0].axhline(y=PHI_INV, color='red', linestyle='--', alpha=0.7, label=f'φ⁻¹ = {PHI_INV:.3f}')
    axes[0, 0].set_title('Phi-Harmonic Sequence', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Power of φ')
    axes[0, 0].set_ylabel('Value (log scale)')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Training metrics
    epochs = np.arange(1, 11)
    metric_a = 0.6 + 0.1 * np.sin(epochs * 0.5)
    metric_b = 0.5 + 0.3 * np.exp(-epochs * 0.1)
    axes[0, 1].plot(epochs, metric_a, 'b-o', label='Metric A', linewidth=2)
    axes[0, 1].plot(epochs, metric_b, 'r-s', label='Metric B', linewidth=2)
    axes[0, 1].axhline(y=PHI_INV, color='blue', linestyle='--', alpha=0.5)
    axes[0, 1].set_title('Training Metrics Over Epochs', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Training Epoch')
    axes[0, 1].set_ylabel('Metric Value')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Quantum state probability
    qubit_states = np.arange(102)
    probabilities = np.exp(-((qubit_states - 51) ** 2) / 500)
    probabilities /= probabilities.sum()
    axes[1, 0].bar(qubit_states, probabilities, color='green', alpha=0.6)
    axes[1, 0].set_title('Quantum State Probability (102 Qubits)', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Qubit Index')
    axes[1, 0].set_ylabel('Probability')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Latent space projection
    np.random.seed(42)
    latent_2d = np.random.randn(100, 2) * PHI_INV
    colors = np.random.rand(100)
    scatter = axes[1, 1].scatter(latent_2d[:, 0], latent_2d[:, 1], c=colors, cmap='viridis', alpha=0.6)
    axes[1, 1].axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    axes[1, 1].axvline(x=0, color='gray', linestyle='-', alpha=0.3)
    axes[1, 1].set_title('Latent Space Projection', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('Dimension 1')
    axes[1, 1].set_ylabel('Dimension 2')
    plt.colorbar(scatter, ax=axes[1, 1], label='Sample Score')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Convert to image
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return Image.open(buf)


def sklearn_demo(n_samples, n_features, test_size):
    """Demonstrate scikit-learn classification."""
    if not SKLEARN_AVAILABLE:
        return "Scikit-learn not installed. Install with: pip install scikit-learn"
    
    results = []
    
    # Generate synthetic data
    np.random.seed(42)
    X = np.random.randn(n_samples, n_features) * PHI_INV
    X += np.sin(np.arange(n_features) * PHI)
    
    # Create classification labels based on sum of features
    sample_scores = np.sum(X, axis=1)
    y = np.digitize(sample_scores, bins=[-10, 10])
    
    results.append(f"**Dataset shape:** {X.shape}")
    results.append(f"**Class distribution:** {np.bincount(y)}")
    
    # Split and scale
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train classifier
    clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    clf.fit(X_train_scaled, y_train)
    
    y_pred = clf.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    results.append(f"\n**Accuracy:** {accuracy:.4f}")
    
    # Cross-validation
    cv_scores = cross_val_score(clf, X_train_scaled, y_train, cv=5)
    results.append(f"**CV scores:** {cv_scores.round(4)}")
    results.append(f"**Mean CV accuracy:** {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    
    # Feature importance
    importances = clf.feature_importances_
    top_indices = np.argsort(importances)[-10:][::-1]
    results.append(f"\n**Top 10 important features:** {top_indices}")
    
    return "\n".join(results)


def qiskit_demo(n_qubits, shots):
    """Demonstrate Qiskit quantum circuit."""
    if not QISKIT_AVAILABLE:
        return "Qiskit not installed. Install with: pip install qiskit", None
    
    results = []
    results.append(f"**Qiskit version:** {qiskit.__version__}")
    
    # Create circuit
    qc = QuantumCircuit(n_qubits, n_qubits)
    
    # Hadamard gates
    for q in range(n_qubits):
        qc.h(q)
    
    # Phi-harmonic rotations
    for q in range(n_qubits):
        angle = PHI_INV * np.pi * (q + 1) / n_qubits
        qc.rz(angle, q)
    
    # Entanglement
    for q in range(0, n_qubits - 1, 2):
        qc.cx(q, q + 1)
    
    # Measurement
    qc.measure(range(n_qubits), range(n_qubits))
    
    # Circuit diagram
    circuit_str = str(qc.draw(output='text'))
    
    # Simulate
    simulator = Aer.get_backend('qasm_simulator')
    job = execute(qc, simulator, shots=shots)
    result = job.result()
    counts = result.get_counts(qc)
    
    results.append(f"\n**Circuit:** {n_qubits} qubits, depth {qc.depth()}")
    results.append(f"\n**Measurement results ({shots} shots):**")
    
    for state, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        results.append(f"  |{state}⟩: {count} shots ({count/shots*100:.2f}%)")
    
    # Entanglement entropy
    total = sum(counts.values())
    probs = np.array(list(counts.values())) / total
    entropy = -np.sum(probs * np.log2(probs + 1e-10))
    results.append(f"\n**Entanglement entropy:** {entropy:.4f} bits")
    
    return "\n".join(results), circuit_str


def numba_demo(n_states, n_steps):
    """Demonstrate Numba JIT acceleration."""
    results = []
    
    if not NUMBA_AVAILABLE:
        results.append("Numba not installed. Install with: pip install numba")
        results.append("\nShowing pure Python benchmark only...")
        
        # Pure Python only
        def quantum_evolution_python(states, steps, phi):
            result = np.zeros(steps)
            for i in range(steps):
                for j in range(len(states)):
                    states[j] = np.sin(phi * states[j] + i * 0.01)
                result[i] = np.sum(states ** 2)
            return result
        
        initial_states = np.random.randn(n_states) * PHI_INV
        
        start = time.time()
        _ = quantum_evolution_python(initial_states.copy(), n_steps, PHI)
        time_python = time.time() - start
        
        results.append(f"\n**Pure Python time:** {time_python:.4f} seconds")
        results.append(f"**Numba:** Not available")
        
        return "\n".join(results)
    
    # Pure Python version
    def quantum_evolution_python(states, steps, phi):
        result = np.zeros(steps)
        for i in range(steps):
            for j in range(len(states)):
                states[j] = np.sin(phi * states[j] + i * 0.01)
            result[i] = np.sum(states ** 2)
        return result
    
    # Numba JIT version
    @jit(nopython=True, parallel=True)
    def quantum_evolution_numba(states, steps, phi):
        result = np.zeros(steps)
        for i in range(steps):
            for j in range(len(states)):
                states[j] = np.sin(phi * states[j] + i * 0.01)
            result[i] = np.sum(states ** 2)
        return result
    
    initial_states = np.random.randn(n_states) * PHI_INV
    
    # Warm up JIT
    _ = quantum_evolution_numba(initial_states.copy(), 10, PHI)
    
    # Benchmark Python
    start = time.time()
    result_python = quantum_evolution_python(initial_states.copy(), n_steps, PHI)
    time_python = time.time() - start
    
    # Benchmark Numba
    start = time.time()
    result_numba = quantum_evolution_numba(initial_states.copy(), n_steps, PHI)
    time_numba = time.time() - start
    
    results.append(f"**Quantum state evolution:** {n_steps} steps, {n_states} states")
    results.append(f"\n**Pure Python time:** {time_python:.4f} seconds")
    results.append(f"**Numba JIT time:** {time_numba:.4f} seconds")
    results.append(f"**Speedup:** {time_python / time_numba:.2f}x")
    results.append(f"**Results match:** {np.allclose(result_python, result_numba)}")
    results.append(f"\n**Final state energy:** {result_numba[-1]:.6f}")
    
    return "\n".join(results)


def dna_quantum_demo(dna_sequence, encoding_scheme):
    """Demonstrate DNA-to-quantum encoding."""
    results = []
    results.append(f"**DNA Sequence:** `{dna_sequence}`")
    results.append(f"**Length:** {len(dna_sequence)} bp")
    results.append(f"**Encoding Scheme:** {encoding_scheme}")
    
    # DNA base-to-gate mapping
    gate_map = {
        'base_to_gate': {'A': 'H', 'T': 'X', 'G': 'RZ(π/4)', 'C': 'RY(π/4)'},
        'codon': {'ATG': 'H', 'TAA': 'X', 'GGG': 'RZ', 'CCC': 'RY'},
        'watson_crick': {'AT': 'Bell', 'GC': 'Phase', 'TA': 'Bell', 'CG': 'Phase'}
    }
    
    mapping = gate_map.get(encoding_scheme, gate_map['base_to_gate'])
    results.append(f"\n**Gate Mapping:** `{mapping}`")
    
    # Calculate circuit properties
    n_qubits = len(dna_sequence)
    depth = n_qubits + len(dna_sequence) // 2
    total_gates = n_qubits * 2
    
    results.append(f"\n**Circuit Properties:**")
    results.append(f"- Qubits: {n_qubits}")
    results.append(f"- Depth: {depth}")
    results.append(f"- Total Gates: {total_gates}")
    
    # Generate OpenQASM snippet
    qasm_lines = [
        "OPENQASM 2.0;",
        'include "qelib1.inc";',
        f"qreg q[{n_qubits}];",
        f"creg c[{n_qubits}];"
    ]
    
    for i, base in enumerate(dna_sequence[:8]):  # Show first 8 bases
        if encoding_scheme == 'base_to_gate':
            if base == 'A':
                qasm_lines.append(f"h q[{i}];")
            elif base == 'T':
                qasm_lines.append(f"x q[{i}];")
            elif base == 'G':
                qasm_lines.append(f"rz(pi/4) q[{i}];")
            elif base == 'C':
                qasm_lines.append(f"ry(pi/4) q[{i}];")
    
    qasm_lines.append(f"measure q -> c;")
    
    results.append(f"\n**OpenQASM Preview:**")
    results.append("```")
    for line in qasm_lines[:12]:
        results.append(line)
    if len(qasm_lines) > 12:
        results.append("...")
    results.append("```")
    
    return "\n".join(results)


# Create Gradio interface
with gr.Blocks(title="Scientific Python for Quantum AGI Research", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # Scientific Python Ecosystem for Quantum AGI Research
    
    Interactive demonstration of NumPy, Pandas, SciPy, Matplotlib, Scikit-learn, Qiskit, and Numba
    for quantum consciousness research and AGI development.
    
    **Golden Ratio (φ):** 1.6180339887... | **φ⁻¹:** 0.6180339887...
    """)
    
    with gr.Tabs():
        # Tab 1: NumPy
        with gr.Tab("NumPy - Numerical Computing"):
            gr.Markdown("""
            ### NumPy: Foundation of Scientific Python
            
            N-dimensional arrays, linear algebra, and golden ratio calculations for quantum research.
            """)
            numpy_btn = gr.Button("Run NumPy Demo", variant="primary")
            numpy_output = gr.Markdown()
            numpy_btn.click(numpy_demo, outputs=numpy_output)
        
        # Tab 2: Pandas
        with gr.Tab("Pandas - Data Analysis"):
            gr.Markdown("""
            ### Pandas: Time-Series Metrics DataFrame
            
            Data manipulation and statistical aggregations for numerical analysis.
            """)
            pandas_btn = gr.Button("Run Pandas Demo", variant="primary")
            pandas_output = gr.DataFrame()
            pandas_stats = gr.DataFrame()
            pandas_btn.click(pandas_demo, outputs=[pandas_output, pandas_stats])
        
        # Tab 3: SciPy
        with gr.Tab("SciPy - Scientific Algorithms"):
            gr.Markdown("""
            ### SciPy: Optimization & Statistics
            
            Minimization, integration, and statistical tests for quantum state analysis.
            """)
            scipy_btn = gr.Button("Run SciPy Demo", variant="primary")
            scipy_output = gr.Markdown()
            scipy_btn.click(scipy_demo, outputs=scipy_output)
        
        # Tab 4: Matplotlib
        with gr.Tab("Matplotlib - Visualization"):
            gr.Markdown("""
            ### Matplotlib: Quantum State Visualization
            
            Publication-quality plots for phi-harmonic sequences and training metrics.
            """)
            matplotlib_btn = gr.Button("Generate Plots", variant="primary")
            matplotlib_output = gr.Image(type="pil")
            matplotlib_btn.click(matplotlib_demo, outputs=matplotlib_output)
        
        # Tab 5: Scikit-learn
        with gr.Tab("Scikit-learn - Machine Learning"):
            gr.Markdown("""
            ### Scikit-learn: Sample Classification
            
            Random Forest classifier for numerical feature data.
            """)
            with gr.Row():
                sklearn_samples = gr.Slider(100, 1000, value=500, step=100, label="Samples")
                sklearn_features = gr.Slider(10, 128, value=102, step=1, label="Features (Qubits)")
                sklearn_test = gr.Slider(0.1, 0.4, value=0.2, step=0.05, label="Test Size")
            sklearn_btn = gr.Button("Train Classifier", variant="primary")
            sklearn_output = gr.Markdown()
            sklearn_btn.click(sklearn_demo, inputs=[sklearn_samples, sklearn_features, sklearn_test], outputs=sklearn_output)
        
        # Tab 6: Qiskit
        with gr.Tab("Qiskit - Quantum Computing"):
            gr.Markdown("""
            ### Qiskit: DNA Quantum Circuit Simulation
            
            Quantum circuit design with phi-harmonic rotations and entanglement.
            """)
            with gr.Row():
                qiskit_qubits = gr.Slider(2, 16, value=8, step=1, label="Qubits")
                qiskit_shots = gr.Slider(256, 4096, value=1024, step=256, label="Shots")
            qiskit_btn = gr.Button("Run Quantum Circuit", variant="primary")
            qiskit_output = gr.Markdown()
            qiskit_circuit = gr.Code(language="python", label="Circuit Diagram")
            qiskit_btn.click(qiskit_demo, inputs=[qiskit_qubits, qiskit_shots], outputs=[qiskit_output, qiskit_circuit])
        
        # Tab 7: Numba
        with gr.Tab("Numba - Performance"):
            gr.Markdown("""
            ### Numba: JIT Compilation for Quantum Simulations
            
            Accelerate numerical loops with near-C performance.
            """)
            with gr.Row():
                numba_states = gr.Slider(10, 512, value=102, step=1, label="States (Qubits)")
                numba_steps = gr.Slider(100, 5000, value=1000, step=100, label="Evolution Steps")
            numba_btn = gr.Button("Run Benchmark", variant="primary")
            numba_output = gr.Markdown()
            numba_btn.click(numba_demo, inputs=[numba_states, numba_steps], outputs=numba_output)
        
        # Tab 8: DNA Quantum
        with gr.Tab("DNA Quantum Circuits"):
            gr.Markdown("""
            ### DNA-to-Quantum Circuit Encoding
            
            Encode DNA sequences into quantum circuits with phi-harmonic gates.
            """)
            dna_input = gr.Textbox(value="ATGCATGC", label="DNA Sequence", placeholder="Enter DNA sequence (A, T, G, C)")
            dna_scheme = gr.Dropdown(
                choices=["base_to_gate", "codon", "watson_crick"],
                value="base_to_gate",
                label="Encoding Scheme"
            )
            dna_btn = gr.Button("Encode DNA", variant="primary")
            dna_output = gr.Markdown()
            dna_btn.click(dna_quantum_demo, inputs=[dna_input, dna_scheme], outputs=dna_output)
    
    gr.Markdown("""
    ---
    ### Library Coverage in AGI-Model
    
    | Library | Usage | Status |
    |---------|-------|--------|
    | **NumPy** | Quantum state arrays, phi-harmonic calculations | Core |
    | **Pandas** | Consciousness metrics, time-series | Limited |
    | **SciPy** | Optimization, statistics, integration | Limited |
    | **Matplotlib** | Visualization (latent space, training) | Extensive |
    | **PyTorch** | QuantumVAE, neural networks | Core |
    | **Scikit-learn** | Classification, preprocessing | Limited |
    | **Qiskit** | IBM Quantum hardware integration | Active |
    | **Numba** | Performance optimization | Optional |
    
    **Repository:** [AGI-model](https://github.com/quantumdynamics927-dotcom/AGI-model)
    """)


if __name__ == "__main__":
    demo.launch()