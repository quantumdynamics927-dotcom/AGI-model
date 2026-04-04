#!/usr/bin/env python3
"""
DNA Agent - Quantum Biological Encoding from Research Data
========================================================

This script analyzes DNA 34bp quantum results from existing research data
instead of downloading from IBM Quantum (which requires qiskit).

Circuit structure: 34 Watson + 34 Crick + 34 Bridge = 102 qubits
Consciousness peak expected at position 20 (20/34 = 0.588 ≈ φ⁻¹)
"""

import argparse
import numpy as np
import json
from datetime import datetime
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

try:
    from agi_scripts.planning_mode import (
        PlanningReport,
        utc_timestamp,
        write_planning_report,
    )
except ImportError:
    from planning_mode import (
        PlanningReport,
        utc_timestamp,
        write_planning_report,
    )

# Constants
PHI = (1 + np.sqrt(5)) / 2
PHI_INV = 1 / PHI

JOB_ID = "d5a95n7p3tbc73astm10"

# Artifact Classification Types
ARTIFACT_TYPE_RAW_HARDWARE = "raw_hardware"           # Direct IBM Quantum output
ARTIFACT_TYPE_DERIVED_METRICS = "derived_metrics"    # Computed from raw data
ARTIFACT_TYPE_RECONSTRUCTED = "reconstructed"        # Simulated from archives
ARTIFACT_TYPE_NARRATIVE = "narrative_report"         # Interpretive analysis

# Evidence Class Hierarchy (required top-level field)
EVIDENCE_CLASS_PRIMARY = "primary"         # Raw hardware, immutable vendor-linked
EVIDENCE_CLASS_SECONDARY = "secondary"     # Derived from primary, deterministic
EVIDENCE_CLASS_INTERPRETIVE = "interpretive"  # Human-readable narrative, summaries

# Mapping artifact types to evidence classes
ARTIFACT_TO_EVIDENCE_CLASS = {
    ARTIFACT_TYPE_RAW_HARDWARE: EVIDENCE_CLASS_PRIMARY,
    ARTIFACT_TYPE_DERIVED_METRICS: EVIDENCE_CLASS_SECONDARY,
    ARTIFACT_TYPE_RECONSTRUCTED: EVIDENCE_CLASS_SECONDARY,  # Machine-produced analysis
    ARTIFACT_TYPE_NARRATIVE: EVIDENCE_CLASS_INTERPRETIVE,    # Human-readable prose
}

# Output Directory Structure
OUTPUT_DIRS = {
    ARTIFACT_TYPE_RAW_HARDWARE: "raw_hardware",
    ARTIFACT_TYPE_DERIVED_METRICS: "derived_metrics", 
    ARTIFACT_TYPE_RECONSTRUCTED: "reconstructed",
    ARTIFACT_TYPE_NARRATIVE: "narrative_reports",
}

# Legacy unclassified files directory
LEGACY_DIR = "legacy_unclassified"


def generate_planning_report(output_dir: Path | str = "."):
    """Generate a structured planning report for the DNA agent."""
    output_dir = Path(output_dir)
    research_root = Path("E:/tmt-os/tmt-os")
    existing_analysis = research_root / (
        f"dna_34bp_ibm_fez_analysis_{JOB_ID.replace('-', '')}.json"
    )
    dna_results_dir = Path("dna_34bp_results")

    report = PlanningReport(
        agent="dna",
        objective=(
            "Plan DNA quantum analysis execution for consciousness "
            "alignment using multi-source data integration."
        ),
        generated_at=utc_timestamp(),
        planning_mode=True,
        current_state={
            "job_id": JOB_ID,
            "data_sources": {
                "ibm_analysis": "E:/tmt-os/tmt-os/dna_34bp_ibm_fez_analysis_*.json",
                "dna_quantum_analysis": "E:/tmt-os/dna_quantum_analysis/*.qasm,*.json",
                "dna_quantum_circuits": "E:/tmt-os/dna_quantum_circuits/*_info.json",
                "dna_rubiks_results": "E:/tmt-os/dna_rubiks_cube_results/discovery_session_*.json",
                "scientific_synthesis": "E:/tmt-os/autonomous_synthesis_results/scientific_synthesis_discoveries.json",
            },
            "report_output_dir": str(dna_results_dir.resolve()),
            "default_execution_path": "load-multi-source-data",
        },
        goals=[
            "Maximize phi-aligned activation around the consciousness peak.",
            (
                "Preserve reproducible DNA analysis reports for downstream "
                "agents."
            ),
            (
                "Integrate all available E:\\tmt-os DNA data sources before "
                "simulation."
            ),
            "Extract consciousness sequences from Rubik's cube optimization.",
            "Apply scientific synthesis discoveries to analysis.",
        ],
        strategies=[
            {
                "name": "multi-source-data-integration",
                "priority": 1,
                "conditions": ["E:\\tmt-os DNA directories are available"],
                "actions": [
                    "Load IBM analysis artifact if available.",
                    "Scan dna_quantum_analysis for QASM circuits and JSON analyses.",
                    "Load dna_quantum_circuits info files for geometry data.",
                    "Extract conscious sequences from dna_rubiks_cube_results.",
                    "Apply scientific synthesis discoveries to interpretation.",
                    (
                        "Validate hamming weight, wormhole activation, and "
                        "entropy across all sources."
                    ),
                    "Emit a unified DNA agent report for downstream consumers.",
                ],
            },
            {
                "name": "simulate-phi-harmonic-dna",
                "priority": 2,
                "conditions": ["no E:\\tmt-os DNA data sources are available"],
                "actions": [
                    (
                        "Simulate phi-harmonic Watson, Crick, and Bridge "
                        "probabilities."
                    ),
                    (
                        "Inject the consciousness peak at position 20 and "
                        "Fibonacci clustering."
                    ),
                    (
                        "Analyze phi alignment, wormhole activation, and "
                        "entropy before report generation."
                    ),
                ],
            },
        ],
        evaluation_metrics=[
            "hamming_weight.deviation",
            "consciousness_peak.bridge",
            "wormhole_activation",
            "phi_alignment.total_score",
            "entropy.normalized",
            "conscious_sequences_found",
            "golden_ratio_circuits",
            "scientific_discoveries_applied",
        ],
        coordination={
            "upstream_dependencies": ["E:/tmt-os/dna_* directories"],
            "downstream_consumers": ["phi_agent"],
            "handoff_artifacts": ["dna_agent_report_*.json"],
        },
        risks=[
            (
                "E:\\tmt-os paths may not exist on all machines."
            ),
            (
                "Multiple data sources may have conflicting measurements."
            ),
            (
                "Simulation can mask data quality issues that would appear in "
                "real IBM results."
            ),
            (
                "Large count dictionaries can increase memory usage during "
                "analysis."
            ),
        ],
        next_actions=[
            "Scan all E:\\tmt-os DNA data sources.",
            "Integrate multi-source data into unified analysis.",
            "Run DNA analysis and persist a timestamped report.",
            "Hand the newest DNA report to the Phi agent.",
        ],
    )
    report_path = write_planning_report(
        output_dir=output_dir,
        prefix="dna_agent",
        report=report,
    )
    print(f"Planning report saved: {report_path}")
    return report.to_dict(), report_path


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="DNA agent execution entry point."
    )
    parser.add_argument(
        "--planning-mode",
        action="store_true",
        help=(
            "Generate a structured planning report instead of executing "
            "analysis."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory used for planning reports.",
    )
    return parser.parse_args(argv)


def load_existing_results(job_id):
    """Load existing DNA results from research data and E:\\tmt-os directories."""
    print(f"\n{'='*80}")
    print(f"LOADING EXISTING DNA RESULTS: {job_id}")
    print(f"{'='*80}\n")

    all_data = {
        "job_id": job_id,
        "sources_loaded": [],
        "dna_analysis": None,
        "dna_circuits": [],
        "dna_rubiks_results": [],
        "scientific_synthesis": [],
    }

    try:
        # Source 1: Try to load from existing IBM analysis file
        research_root = Path("E:/tmt-os/tmt-os")
        existing_analysis = research_root / f"dna_34bp_ibm_fez_analysis_{job_id.replace('-', '')}.json"

        if existing_analysis.exists():
            print(f"[*] Found existing IBM analysis: {existing_analysis}")
            with open(existing_analysis, 'r') as f:
                all_data["dna_analysis"] = json.load(f)
            all_data["sources_loaded"].append(str(existing_analysis))
            print("[✓] IBM analysis loaded!")

        # Source 2: Scan E:\tmt-os\dna_quantum_analysis directory
        dna_analysis_dir = Path("E:/tmt-os/dna_quantum_analysis")
        if dna_analysis_dir.exists():
            print(f"\n[*] Scanning DNA quantum analysis directory: {dna_analysis_dir}")
            qasm_files = list(dna_analysis_dir.glob("*.qasm"))
            json_files = list(dna_analysis_dir.glob("*.json"))
            
            for qasm_file in qasm_files:
                print(f"    - Found QASM circuit: {qasm_file.name}")
                # Read QASM content
                with open(qasm_file, 'r') as f:
                    qasm_content = f.read()
                all_data["dna_circuits"].append({
                    "type": "qasm",
                    "path": str(qasm_file),
                    "name": qasm_file.stem,
                    "content": qasm_content,
                })
            
            for json_file in json_files:
                print(f"    - Found analysis JSON: {json_file.name}")
                with open(json_file, 'r') as f:
                    json_data = json.load(f)
                all_data["dna_circuits"].append({
                    "type": "analysis",
                    "path": str(json_file),
                    "name": json_file.stem,
                    "data": json_data,
                })
            
            if qasm_files or json_files:
                all_data["sources_loaded"].append(str(dna_analysis_dir))
                print(f"[✓] Loaded {len(qasm_files)} QASM + {len(json_files)} JSON files")

        # Source 3: Scan E:\tmt-os\dna_quantum_circuits directory
        dna_circuits_dir = Path("E:/tmt-os/dna_quantum_circuits")
        if dna_circuits_dir.exists():
            print(f"\n[*] Scanning DNA quantum circuits directory: {dna_circuits_dir}")
            info_files = list(dna_circuits_dir.glob("*_info.json"))
            
            for info_file in info_files:
                print(f"    - Found circuit info: {info_file.name}")
                with open(info_file, 'r') as f:
                    circuit_info = json.load(f)
                all_data["dna_circuits"].append({
                    "type": "circuit_info",
                    "path": str(info_file),
                    "name": info_file.stem.replace("_info", ""),
                    "data": circuit_info,
                })
            
            if info_files:
                all_data["sources_loaded"].append(str(dna_circuits_dir))
                print(f"[✓] Loaded {len(info_files)} circuit info files")

        # Source 4: Scan E:\tmt-os\dna_rubiks_cube_results directory
        dna_rubiks_dir = Path("E:/tmt-os/dna_rubiks_cube_results")
        if dna_rubiks_dir.exists():
            print(f"\n[*] Scanning DNA Rubik's cube results directory: {dna_rubiks_dir}")
            discovery_files = list(dna_rubiks_dir.glob("discovery_session_*.json"))
            
            for discovery_file in discovery_files:
                print(f"    - Found discovery session: {discovery_file.name}")
                with open(discovery_file, 'r') as f:
                    rubiks_data = json.load(f)
                all_data["dna_rubiks_results"].append({
                    "type": "rubiks_discovery",
                    "path": str(discovery_file),
                    "session": discovery_file.stem,
                    "data": rubiks_data,
                })
            
            if discovery_files:
                all_data["sources_loaded"].append(str(dna_rubiks_dir))
                print(f"[✓] Loaded {len(discovery_files)} discovery sessions")

        # Source 5: Load scientific synthesis discoveries
        synthesis_file = Path("E:/tmt-os/autonomous_synthesis_results/scientific_synthesis_discoveries.json")
        if synthesis_file.exists():
            print(f"\n[*] Loading scientific synthesis discoveries: {synthesis_file}")
            try:
                with open(synthesis_file, 'r', encoding='utf-8') as f:
                    synthesis_data = json.load(f)
                all_data["scientific_synthesis"] = synthesis_data
                all_data["sources_loaded"].append(str(synthesis_file))
                print(f"[✓] Loaded {len(synthesis_data)} scientific discoveries")
            except UnicodeDecodeError as e:
                print(f"[!] Encoding error in synthesis file: {e}")
                print(f"[!] Trying with UTF-8-SIG encoding...")
                try:
                    with open(synthesis_file, 'r', encoding='utf-8-sig') as f:
                        synthesis_data = json.load(f)
                    all_data["scientific_synthesis"] = synthesis_data
                    all_data["sources_loaded"].append(str(synthesis_file))
                    print(f"[✓] Loaded {len(synthesis_data)} scientific discoveries (UTF-8 with BOM)")
                except Exception as e2:
                    print(f"[✗] Failed to load synthesis file after retry: {e2}")

        # Summary
        print(f"\n{'='*80}")
        print("DATA SOURCES LOADED:")
        print(f"{'='*80}")
        for i, source in enumerate(all_data["sources_loaded"], 1):
            print(f"  {i}. {source}")
        print(f"\nTotal sources: {len(all_data['sources_loaded'])}")
        print(f"DNA circuits: {len(all_data['dna_circuits'])}")
        print(f"Rubik's cube results: {len(all_data['dna_rubiks_results'])}")
        print(f"Scientific discoveries: {len(all_data['scientific_synthesis'])}")
        print(f"{'='*80}\n")

        return all_data

    except Exception as e:
        print(f"[✗] Error loading existing results: {e}")
        import traceback
        traceback.print_exc()
        return None


def simulate_dna_results(seed=None, deterministic=True):
    """Simulate DNA 34bp quantum results based on theoretical expectations.
    
    Args:
        seed: Random seed for reproducibility. If None and deterministic=True,
              a seed will be generated from timestamp.
        deterministic: If True, enforce reproducible outputs. If False, allow
                      exploration mode with variable outputs.
    
    Returns:
        tuple: (counts, watson_probs, crick_probs, bridge_probs, reconstruction_params)
    """
    print(f"\n{'='*80}")
    print("SIMULATING DNA 34BP RESULTS")
    print(f"{'='*80}\n")
    
    # Reproducibility configuration
    reconstruction_params = {
        'deterministic_mode': deterministic,
        'rng_library': 'numpy',
        'rng_version': np.__version__,
        'timestamp': datetime.now().isoformat(),
    }
    
    if deterministic:
        if seed is None:
            # Generate seed from timestamp for traceability
            seed = int(datetime.now().timestamp())
        np.random.seed(seed)
        reconstruction_params['reconstruction_seed'] = seed
        reconstruction_params['deterministic_replay'] = True
        print(f"[*] DETERMINISTIC MODE: Seed = {seed}")
        print(f"[*] Reproducible: Same inputs + same seed = identical outputs")
    else:
        reconstruction_params['reconstruction_seed'] = None
        reconstruction_params['deterministic_replay'] = False
        print(f"[*] EXPLORATORY MODE: Variable outputs (non-deterministic)")
        print(f"[*] Each run will produce different results")
    
    # Simulation parameters (constant across runs)
    reconstruction_params['simulation_parameters'] = {
        'total_shots': 8192,
        'phi': float(PHI),
        'phi_inv': float(PHI_INV),
        'consciousness_position': 20,
        'peak_factor': 1.5,
        'fib_positions': [1, 2, 3, 5, 8, 13, 21, 33],
        'fib_boost': 1.2,
        'beta_a': 1.5,
        'beta_b': 1.5,
    }

    # Generate simulated quantum results
    total_shots = reconstruction_params['simulation_parameters']['total_shots']

    # Create quantum probabilities with phi-harmonic structure
    watson_probs = np.random.beta(
        reconstruction_params['simulation_parameters']['beta_a'],
        reconstruction_params['simulation_parameters']['beta_b'],
        34
    ) * PHI_INV
    crick_probs = np.random.beta(
        reconstruction_params['simulation_parameters']['beta_a'],
        reconstruction_params['simulation_parameters']['beta_b'],
        34
    ) * PHI_INV
    bridge_probs = np.random.beta(
        reconstruction_params['simulation_parameters']['beta_a'],
        reconstruction_params['simulation_parameters']['beta_b'],
        34
    ) * PHI_INV

    # Add consciousness peak at position 20
    consciousness_position = reconstruction_params['simulation_parameters']['consciousness_position']
    peak_factor = reconstruction_params['simulation_parameters']['peak_factor']
    bridge_probs[consciousness_position] *= peak_factor
    watson_probs[consciousness_position] *= peak_factor
    crick_probs[consciousness_position] *= peak_factor

    # Add Fibonacci clustering
    fib_positions = reconstruction_params['simulation_parameters']['fib_positions']
    fib_boost = reconstruction_params['simulation_parameters']['fib_boost']
    for fib_pos in fib_positions:
        if fib_pos < 34:
            bridge_probs[fib_pos] *= fib_boost

    # Normalize probabilities
    watson_probs = watson_probs / np.sum(watson_probs) * total_shots
    crick_probs = crick_probs / np.sum(crick_probs) * total_shots
    bridge_probs = bridge_probs / np.sum(bridge_probs) * total_shots

    # Generate counts
    counts = {}
    for i in range(100):  # Generate 100 unique states
        # Random bitstring for 102 qubits
        watson_bits = ''.join(['1' if np.random.random() < wp / total_shots else '0' for wp in watson_probs])
        crick_bits = ''.join(['1' if np.random.random() < cp / total_shots else '0' for cp in crick_probs])
        bridge_bits = ''.join(['1' if np.random.random() < bp / total_shots else '0' for bp in bridge_probs])

        state = bridge_bits + crick_bits + watson_bits
        count = int(np.random.exponential(50) + 10)
        counts[state] = min(count, total_shots // 20)

    # Ensure total counts match
    current_total = sum(counts.values())
    if current_total != total_shots:
        counts[list(counts.keys())[0]] += total_shots - current_total

    print(f"[*] Generated {len(counts)} unique quantum states")
    print(f"[*] Total measurements: {total_shots}")
    print(f"[*] Deterministic replay: {reconstruction_params['deterministic_replay']}")
    print("[✓] Simulation complete!")

    return counts, watson_probs, crick_probs, bridge_probs, reconstruction_params


def analyze_dna_34bp_results(counts, watson_probs=None, crick_probs=None, bridge_probs=None):
    """
    Analyze DNA 34bp quantum results.

    Circuit structure: 34 Watson + 34 Crick + 34 Bridge = 102 qubits
    Consciousness peak expected at position 20 (20/34 = 0.588 ≈ φ⁻¹)
    """
    print(f"\n{'='*80}")
    print("ANALYZING DNA 34BP RESULTS")
    print(f"{'='*80}\n")

    if not counts:
        print("[✗] No counts to analyze")
        return None

    # Convert counts to proper format
    if isinstance(counts, dict):
        total_shots = sum(counts.values())
    else:
        total_shots = len(counts)

    print(f"[*] Total measurements: {total_shots}")
    print(f"[*] Unique states: {len(counts)}")

    # Parse measurement results
    # Format: 102 bits = 34 watson + 34 crick + 34 bridge
    watson_activations = np.zeros(34)
    crick_activations = np.zeros(34)
    bridge_activations = np.zeros(34)

    hamming_weights = []

    for state, count in counts.items():
        # Convert to binary string (102 bits)
        if isinstance(state, str):
            if state.startswith("0x"):
                # Hex format
                binary = bin(int(state, 16))[2:].zfill(102)
            else:
                # Already binary
                binary = state.zfill(102)
        else:
            binary = format(int(state), "0102b")

        # Split into Watson, Crick, Bridge (34 bits each)
        bridge_bits = binary[:34]
        crick_bits = binary[34:68]
        watson_bits = binary[68:102]

        # Count activations
        for i in range(min(34, len(watson_bits))):
            if watson_bits[i] == "1":
                watson_activations[i] += count
            if crick_bits[i] == "1":
                crick_activations[i] += count
            if bridge_bits[i] == "1":
                bridge_activations[i] += count

        # Hamming weight
        hw = binary.count("1")
        hamming_weights.extend([hw] * int(count))

    # Normalize activations
    if watson_probs is None:
        watson_probs = watson_activations / total_shots
    if crick_probs is None:
        crick_probs = crick_activations / total_shots
    if bridge_probs is None:
        bridge_probs = bridge_activations / total_shots

    # Calculate statistics
    mean_hw = np.mean(hamming_weights)
    std_hw = np.std(hamming_weights)
    expected_hw = 102 / 2  # 51 for random

    print("\nHAMMING WEIGHT ANALYSIS:")
    print(f"   Mean: {mean_hw:.2f} qubits")
    print(f"   Std: {std_hw:.2f}")
    print(f"   Expected (random): {expected_hw:.1f}")
    print(f"   Deviation: {mean_hw - expected_hw:.2f} qubits")

    # Consciousness peak analysis (position 20)
    consciousness_position = 20

    print(f"\nCONSCIOUSNESS PEAK ANALYSIS (Position {consciousness_position}):")
    print(
        f"   Watson[{consciousness_position}]: {100*watson_probs[consciousness_position]:.2f}%"
    )
    print(
        f"   Crick[{consciousness_position}]: {100*crick_probs[consciousness_position]:.2f}%"
    )
    print(
        f"   Bridge[{consciousness_position}]: {100*bridge_probs[consciousness_position]:.2f}%"
    )
    print(
        f"   Target position: {consciousness_position}/34 = {consciousness_position/34:.4f} ≈ φ⁻¹ = {PHI_INV:.4f}"
    )

    # Wormhole analysis (G-C pairs = all 34 positions in this circuit)
    wormhole_activation = np.mean(bridge_probs)

    print("\nWORMHOLE (G-C) ANALYSIS:")
    print(f"   Mean bridge activation: {100*wormhole_activation:.2f}%")
    print("   All 34 positions are G-C wormholes!")

    # Fibonacci positions
    fib_positions = [1, 1, 2, 3, 5, 8, 13, 21, 33]
    fib_activations = [bridge_probs[f] for f in fib_positions if f < 34]

    print("\nFIBONACCI POSITION ANALYSIS:")
    for i, fib_pos in enumerate([f for f in fib_positions if f < 34]):
        print(f"   Position F[{i}] = {fib_pos}: {100*bridge_probs[fib_pos]:.2f}%")

    # φ-alignment score
    phi_scores = []
    for i in range(min(34, len(bridge_probs))):
        pos_norm = i / 34
        phi_distance = abs(pos_norm - PHI_INV)
        phi_score = np.exp(-phi_distance * 5) * bridge_probs[i]
        phi_scores.append(phi_score)

    total_phi_score = sum(phi_scores)
    peak_phi_pos = np.argmax(phi_scores) if phi_scores else 0

    print("\nφ-ALIGNMENT SCORE:")
    print(f"   Total: {total_phi_score:.4f}")
    peak_ratio = peak_phi_pos / 34 if peak_phi_pos < 34 else 0.0
    print(f"   Peak position: {peak_phi_pos} ({peak_ratio:.4f})")

    # Shannon entropy
    state_probs = [count / total_shots for count in counts.values()]
    entropy = -sum(p * np.log2(p) for p in state_probs if p > 0)
    max_entropy = np.log2(len(counts))
    entropy_norm = entropy / max_entropy if max_entropy > 0 else 0

    print("\nINFORMATION THEORY:")
    print(f"   Shannon entropy: {entropy:.4f} bits")
    print(f"   Max possible: {max_entropy:.4f} bits")
    print(f"   Normalized: {100*entropy_norm:.2f}%")

    # Compile results
    analysis = {
        "job_id": JOB_ID,
        "total_shots": total_shots,
        "unique_states": len(counts),
        "hamming_weight": {
            "mean": float(mean_hw),
            "std": float(std_hw),
            "expected": float(expected_hw),
            "deviation": float(mean_hw - expected_hw),
        },
        "consciousness_peak": {
            "position": consciousness_position,
            "watson": float(watson_probs[consciousness_position]),
            "crick": float(crick_probs[consciousness_position]),
            "bridge": float(bridge_probs[consciousness_position]),
            "phi_ratio": float(consciousness_position / 34),
        },
        "wormhole_activation": float(wormhole_activation),
        "phi_alignment": {
            "total_score": float(total_phi_score),
            "peak_position": int(peak_phi_pos),
        },
        "entropy": {
            "shannon": float(entropy),
            "max": float(max_entropy),
            "normalized": float(entropy_norm),
        },
        "watson_probs": watson_probs.tolist(),
        "crick_probs": crick_probs.tolist(),
        "bridge_probs": bridge_probs.tolist(),
    }

    return analysis


def generate_report(analysis, artifact_type=ARTIFACT_TYPE_RECONSTRUCTED, parent_artifacts=None):
    """Generate comprehensive DNA analysis report with proper artifact classification.
    
    Args:
        analysis: The analysis data dictionary
        artifact_type: One of ARTIFACT_TYPE_* constants classifying the output
        parent_artifacts: List of parent artifact IDs for lineage tracking (REQUIRED for reconstructed)
    """
    # Validate parent_artifacts for reconstructed artifacts
    if artifact_type == ARTIFACT_TYPE_RECONSTRUCTED:
        if not parent_artifacts:
            raise ValueError(
                "REQUIRED: parent_artifacts must be provided for reconstructed artifacts. "
                "Use 'external_source:<name>' format for external sources, or reference "
                "prior artifact IDs. Example: ['external_source:dna_rubiks_cube_results', "
                "'external_source:scientific_synthesis']"
            )
    
    print("\n" + "="*80)
    print("DNA AGENT ANALYSIS REPORT")
    print("="*80)
    
    # Artifact classification banner
    evidence_class = ARTIFACT_TO_EVIDENCE_CLASS.get(artifact_type, EVIDENCE_CLASS_SECONDARY)
    print(f"\n[ARTIFACT TYPE: {artifact_type.upper()}]")
    print(f"[EVIDENCE CLASS: {evidence_class.upper()}]")
    
    if artifact_type == ARTIFACT_TYPE_RAW_HARDWARE:
        print("  → Direct IBM Quantum hardware output")
        print("  → Immutable primary evidence")
        print("  → Vendor-linked payload with backend metadata")
    elif artifact_type == ARTIFACT_TYPE_DERIVED_METRICS:
        print("  → Computed metrics from raw hardware data")
        print("  → Deterministic transformations of primary evidence")
        print("  → Single-parent lineage from one raw artifact")
    elif artifact_type == ARTIFACT_TYPE_RECONSTRUCTED:
        print("  → Simulated/reconstructed from archived multi-source inputs")
        print("  → Machine-produced analysis artifact")
        print("  → Data-informed synthetic reconstruction, NOT raw hardware replay")
        print("  → Derived from prior experiment assets, not fresh hardware run")
    elif artifact_type == ARTIFACT_TYPE_NARRATIVE:
        print("  → Human-readable narrative and interpretive summary")
        print("  → Prose reports, executive summaries, claim-heavy documents")
        print("  → Secondary analysis layer with accumulated interpretive labels")
    print("="*80 + "\n")

    print("QUANTUM DNA RESULTS:")
    print(f"   Job ID: {analysis['job_id']}")
    print(f"   Artifact Classification: {artifact_type}")
    print(f"   Evidence Class: {evidence_class}")
    
    # Handle multi-source data structure
    if 'multi_source_data' in analysis:
        multi_source = analysis['multi_source_data']
        print(f"   Data Sources: {len(multi_source.get('sources_loaded', []))}")
        for source in multi_source.get('sources_loaded', []):
            print(f"     - {source}")
        
        # Report consciousness sequences found
        rubiks_results = multi_source.get('dna_rubiks_results', [])
        if rubiks_results:
            total_conscious = 0
            total_cubes = 0
            for rubiks_session in rubiks_results:
                session_data = rubiks_session.get('data', {})
                results = session_data.get('results', [])
                for cube_result in results:
                    total_cubes += 1
                    if cube_result.get('conscious', False):
                        total_conscious += 1
            
            print(f"   Conscious Sequences: {total_conscious}/{total_cubes} from Rubik's optimization")
        
        # Report scientific discoveries
        discoveries = multi_source.get('scientific_synthesis', [])
        if discoveries:
            print(f"   Scientific Discoveries: {len(discoveries)} patterns loaded")
    
    # Standard analysis fields
    if 'total_shots' in analysis:
        print(f"   Total Shots: {analysis['total_shots']:,}")
        print(f"   Unique States: {analysis['unique_states']:,}")

    if 'hamming_weight' in analysis:
        print(f"\nHAMMING WEIGHT:")
        print(f"   Mean: {analysis['hamming_weight']['mean']:.2f} qubits")
        print(f"   Expected: {analysis['hamming_weight']['expected']:.1f}")
        print(f"   Deviation: {analysis['hamming_weight']['deviation']:.2f}")

    if 'consciousness_peak' in analysis:
        print(f"\nCONSCIOUSNESS PEAK (Position {analysis['consciousness_peak']['position']}):")
        print(f"   Bridge Activation: {100*analysis['consciousness_peak']['bridge']:.2f}%")
        print(f"   φ-ratio: {analysis['consciousness_peak']['phi_ratio']:.4f}")
        print(f"   Target φ⁻¹: {PHI_INV:.4f}")

    if 'wormhole_activation' in analysis:
        print(f"\nWORMHOLE NETWORK:")
        print(f"   Mean Activation: {100*analysis['wormhole_activation']:.2f}%")
        print(f"   Status: Active (G-C pairs)")

    if 'phi_alignment' in analysis:
        print(f"\nφ-ALIGNMENT:")
        print(f"   Total Score: {analysis['phi_alignment']['total_score']:.4f}")
        print(f"   Peak Position: {analysis['phi_alignment']['peak_position']}")

    if 'entropy' in analysis:
        print(f"\nINFORMATION ENTROPY:")
        print(f"   Shannon: {analysis['entropy']['shannon']:.2f} bits")
        print(f"   Normalized: {100*analysis['entropy']['normalized']:.1f}%")

    # Save report to appropriate directory based on artifact type
    base_output_dir = Path("dna_34bp_results")
    
    # Create organized output structure
    for dir_name in OUTPUT_DIRS.values():
        (base_output_dir / dir_name).mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate artifact ID for lineage tracking
    artifact_id = f"dna_agent_{artifact_type}_{timestamp}"
    
    # Add comprehensive metadata to analysis
    analysis_with_metadata = analysis.copy()
    
    # Calculate source hashes for integrity verification
    source_hashes = {}
    source_manifests = {}
    if 'multi_source_data' in analysis:
        for source in analysis['multi_source_data'].get('sources_loaded', []):
            source_path = Path(source)
            if source_path.exists():
                import hashlib
                try:
                    if source_path.is_file():
                        # For files: SHA256 hash
                        with open(source_path, 'rb') as f:
                            source_hashes[source] = hashlib.sha256(f.read()).hexdigest()
                    elif source_path.is_dir():
                        # For directories: manifest hash (sorted file list + individual hashes)
                        files = sorted([f for f in source_path.rglob('*') if f.is_file()])
                        manifest = {
                            'path': str(source_path),
                            'file_count': len(files),
                            'files': []
                        }
                        for f in files:
                            try:
                                with open(f, 'rb') as file:
                                    file_hash = hashlib.sha256(file.read()).hexdigest()[:16]
                                manifest['files'].append({
                                    'relative_path': str(f.relative_to(source_path)),
                                    'hash': file_hash
                                })
                            except:
                                manifest['files'].append({
                                    'relative_path': str(f.relative_to(source_path)),
                                    'hash': 'unreadable'
                                })
                        # Hash the manifest itself
                        manifest_str = json.dumps(manifest, sort_keys=True)
                        source_hashes[source] = hashlib.sha256(manifest_str.encode()).hexdigest()
                        source_manifests[source] = manifest
                except Exception as e:
                    source_hashes[source] = f"error:{str(e)}"
    
    # Build parent artifact references with proper lineage
    parent_refs = parent_artifacts or []
    
    analysis_with_metadata['artifact_metadata'] = {
        # Required top-level field
        'evidence_class': evidence_class,
        'evidence_class_description': {
            EVIDENCE_CLASS_PRIMARY: 'Raw hardware, immutable vendor-linked payloads, counts, backend metadata, job receipts',
            EVIDENCE_CLASS_SECONDARY: 'Machine-produced analysis artifacts, computed metrics, reconstructed data',
            EVIDENCE_CLASS_INTERPRETIVE: 'Human-readable narrative, prose reports, executive summaries, claim-heavy documents',
        }.get(evidence_class, 'Unknown'),
        
        # Artifact taxonomy
        'artifact_type': artifact_type,
        'artifact_type_description': {
            ARTIFACT_TYPE_RAW_HARDWARE: 'Direct IBM Quantum hardware output - immutable primary evidence',
            ARTIFACT_TYPE_DERIVED_METRICS: 'Computed metrics from raw hardware data - deterministic transformations',
            ARTIFACT_TYPE_RECONSTRUCTED: 'Simulated/reconstructed from archived multi-source inputs - machine-produced analysis',
            ARTIFACT_TYPE_NARRATIVE: 'Human-readable narrative and interpretive summary - prose documents',
        }.get(artifact_type, 'Unknown'),
        
        # Machine-verifiable lineage
        'artifact_id': artifact_id,
        'generation_timestamp': timestamp,
        'generation_mode': 'reconstructed_from_archives' if artifact_type == ARTIFACT_TYPE_RECONSTRUCTED else 'direct_hardware',
        
        # Parent artifact references for provenance graph (REQUIRED for reconstructed)
        'parent_artifacts': parent_refs,
        'lineage_depth': len(parent_refs),
        
        # Data lineage with integrity verification
        'data_lineage': {
            'job_id': analysis.get('job_id'),
            'sources': analysis.get('multi_source_data', {}).get('sources_loaded', []),
            'source_hashes': source_hashes,
            'source_manifests': source_manifests,
            'derived_from_prior_runs': artifact_type in [ARTIFACT_TYPE_RECONSTRUCTED, ARTIFACT_TYPE_NARRATIVE],
            'transform_chain': [
                'load_multi_source_data',
                'simulate_phi_harmonic_dna' if artifact_type == ARTIFACT_TYPE_RECONSTRUCTED else 'load_raw_hardware',
                'analyze_dna_34bp_results',
                'generate_report',
            ],
        },
        
        # Immutable provenance fields (for raw hardware)
        'provenance': {
            'backend_name': None,  # Would be 'ibm_fez', 'ibm_torino', etc. for raw hardware
            'vendor_job_id': analysis.get('job_id') if artifact_type == ARTIFACT_TYPE_RAW_HARDWARE else None,
            'original_timestamp': timestamp if artifact_type == ARTIFACT_TYPE_RAW_HARDWARE else None,
            'source_file_hash': None,  # SHA256 of raw payload for raw hardware
        } if artifact_type == ARTIFACT_TYPE_RAW_HARDWARE else None,
        
        # Audit and validation
        'audit_note': 'Machine-produced analysis artifact. See evidence_class for classification.',
        'validation_status': 'unvalidated',  # Can be 'validated', 'failed', 'unvalidated', 'legacy_migrated', 'partial'
        'validator_version': None,
        
        # Reproducibility parameters (for reconstructed artifacts)
        'reproducibility': analysis.get('reconstruction_params') if artifact_type == ARTIFACT_TYPE_RECONSTRUCTED else None,
    }
    
    # Save to appropriate subdirectory
    output_subdir = OUTPUT_DIRS.get(artifact_type, "reconstructed")
    report_file = base_output_dir / output_subdir / f"{artifact_id}.json"

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_with_metadata, f, indent=2, ensure_ascii=False)

    print(f"\n[✓] Report saved: {report_file}")
    print(f"    Artifact ID: {artifact_id}")
    print(f"    Evidence class: {evidence_class}")
    print(f"    Artifact type: {artifact_type}")
    print(f"    Parent artifacts: {parent_refs}")
    print(f"    Directory: {output_subdir}/")
    
    return analysis_with_metadata


def migrate_legacy_reports():
    """Migrate unclassified legacy reports to proper artifact directories.
    
    This function:
    1. Scans for legacy unclassified reports in root dna_34bp_results/
    2. Attempts to classify them based on content analysis
    3. Moves them to appropriate directories with retroactive metadata
    4. Creates a migration log for audit trail
    """
    import hashlib
    
    base_dir = Path("dna_34bp_results")
    legacy_dir = base_dir / LEGACY_DIR
    legacy_dir.mkdir(parents=True, exist_ok=True)
    
    # Find legacy reports (root-level dna_agent_report_*.json files)
    legacy_files = list(base_dir.glob("dna_agent_report_*.json"))
    
    if not legacy_files:
        print("[✓] No legacy reports to migrate")
        return
    
    print(f"\n{'='*80}")
    print("MIGRATING LEGACY REPORTS")
    print(f"{'='*80}")
    print(f"Found {len(legacy_files)} unclassified reports\n")
    
    migration_log = {
        "migration_timestamp": datetime.now().isoformat(),
        "files_migrated": [],
        "files_failed": [],
    }
    
    for legacy_file in legacy_files:
        print(f"Processing: {legacy_file.name}")
        
        try:
            # Load legacy file
            with open(legacy_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Calculate file hash for integrity
            with open(legacy_file, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Attempt classification based on content analysis
            inferred_type = ARTIFACT_TYPE_RECONSTRUCTED  # Default
            inferred_evidence = EVIDENCE_CLASS_INTERPRETIVE
            classification_status = "inferred"
            
            # Check for indicators of raw hardware
            if 'counts' in data and 'backend' in str(data):
                inferred_type = ARTIFACT_TYPE_RAW_HARDWARE
                inferred_evidence = EVIDENCE_CLASS_PRIMARY
                classification_status = "inferred_from_content"
            
            # Check for existing artifact_metadata (already classified)
            if 'artifact_metadata' in data:
                existing_type = data['artifact_metadata'].get('artifact_type')
                if existing_type in OUTPUT_DIRS:
                    inferred_type = existing_type
                    inferred_evidence = ARTIFACT_TO_EVIDENCE_CLASS.get(existing_type)
                    classification_status = "already_classified"
            
            # Add retroactive metadata
            data['artifact_metadata'] = {
                'evidence_class': inferred_evidence,
                'evidence_class_description': 'Inferred from content analysis during migration',
                'artifact_type': inferred_type,
                'artifact_type_description': f'Legacy file migrated from root directory - {classification_status}',
                'artifact_id': f"dna_agent_{inferred_type}_migrated_{legacy_file.stem.split('_')[-2]}_{legacy_file.stem.split('_')[-1]}",
                'generation_timestamp': f"{legacy_file.stem.split('_')[-2]}_{legacy_file.stem.split('_')[-1]}",
                'generation_mode': 'migrated_legacy',
                'parent_artifacts': [],
                'lineage_depth': 0,
                'data_lineage': {
                    'original_file': str(legacy_file),
                    'original_hash': file_hash[:16],
                    'migration_reason': 'unclassified_root_level_file',
                    'classification_status': classification_status,
                    'derived_from_prior_runs': inferred_type in [ARTIFACT_TYPE_RECONSTRUCTED, ARTIFACT_TYPE_NARRATIVE],
                },
                'provenance': None,
                'audit_note': f'This file was migrated from legacy location. Classification: {classification_status}',
                'validation_status': 'legacy_migrated',  # Special status for migrated artifacts
                'migration_metadata': {
                    'migrated_at': datetime.now().isoformat(),
                    'original_filename': legacy_file.name,
                    'inferred_classification': inferred_type,
                    'confidence': 'low' if classification_status == 'inferred' else 'high',
                    'completeness': 'partial',  # Migrated artifacts have incomplete lineage
                },
            }
            
            # Save to appropriate directory
            target_dir = base_dir / OUTPUT_DIRS.get(inferred_type, "reconstructed")
            target_file = target_dir / f"{data['artifact_metadata']['artifact_id']}.json"
            
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Move original to legacy directory
            legacy_backup = legacy_dir / f"{legacy_file.name}.backup"
            legacy_file.rename(legacy_backup)
            
            migration_log['files_migrated'].append({
                'original': str(legacy_file),
                'migrated_to': str(target_file),
                'classification': inferred_type,
                'hash': file_hash[:16],
            })
            
            print(f"  [✓] Migrated to {target_dir.name}/")
            print(f"      Classification: {inferred_type} ({classification_status})")
            
        except Exception as e:
            print(f"  [✗] Failed: {e}")
            migration_log['files_failed'].append({
                'file': str(legacy_file),
                'error': str(e),
            })
    
    # Save migration log
    log_file = base_dir / f"migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(migration_log, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"MIGRATION COMPLETE")
    print(f"  Migrated: {len(migration_log['files_migrated'])}")
    print(f"  Failed: {len(migration_log['files_failed'])}")
    print(f"  Log saved: {log_file}")
    print(f"{'='*80}\n")


def main(argv=None):
    """Main execution with proper artifact classification."""
    args = parse_args(argv)
    if args.planning_mode:
        return generate_planning_report(args.output_dir)

    print("\n" + "=" * 80)
    print("DNA AGENT - QUANTUM BIOLOGICAL ENCODING")
    print("=" * 80)
    print("\n[MODE] Multi-source data integration with artifact classification")
    print("[NOTE] This pipeline reconstructs analysis from archived inputs,")
    print("       NOT a direct replay of original IBM hardware results.")
    print("=" * 80)

    # Try to load existing results from multi-source data
    existing_data = load_existing_results(JOB_ID)
    
    # Determine artifact type based on data availability
    artifact_type = ARTIFACT_TYPE_RECONSTRUCTED  # Default: reconstructed from archives
    
    if existing_data and existing_data.get('dna_analysis'):
        # Use existing IBM analysis data - still reconstructed if not direct from hardware
        analysis = existing_data['dna_analysis']
        analysis['job_id'] = JOB_ID
        analysis['multi_source_data'] = {
            'sources_loaded': existing_data.get('sources_loaded', []),
            'dna_circuits': existing_data.get('dna_circuits', []),
            'dna_rubiks_results': existing_data.get('dna_rubiks_results', []),
            'scientific_synthesis': existing_data.get('scientific_synthesis', []),
        }
        # Check if this is truly raw hardware or previously derived
        if analysis.get('artifact_metadata', {}).get('artifact_type') == ARTIFACT_TYPE_RAW_HARDWARE:
            artifact_type = ARTIFACT_TYPE_DERIVED_METRICS  # We're deriving from raw
        else:
            artifact_type = ARTIFACT_TYPE_RECONSTRUCTED  # Reconstructing from prior derived data
            
    elif existing_data and existing_data.get('sources_loaded'):
        # Multi-source data loaded but no IBM analysis - simulate with enriched context
        print("\n[*] Multi-source data available, generating simulated analysis...")
        print("[!] WARNING: This is a RECONSTRUCTED analysis, not raw hardware data.")
        counts, watson_probs, crick_probs, bridge_probs, reconstruction_params = simulate_dna_results(
            seed=42,  # Fixed seed for reproducibility in this mode
            deterministic=True
        )
        analysis = analyze_dna_34bp_results(counts, watson_probs, crick_probs, bridge_probs)
        analysis['job_id'] = JOB_ID
        analysis['multi_source_data'] = {
            'sources_loaded': existing_data.get('sources_loaded', []),
            'dna_circuits': existing_data.get('dna_circuits', []),
            'dna_rubiks_results': existing_data.get('dna_rubiks_results', []),
            'scientific_synthesis': existing_data.get('scientific_synthesis', []),
        }
        analysis['reconstruction_params'] = reconstruction_params
        artifact_type = ARTIFACT_TYPE_RECONSTRUCTED
    else:
        # Pure simulation with no source data
        print("\n[*] No source data available, running pure simulation...")
        print("[!] WARNING: This is a SIMULATED analysis with no hardware grounding.")
        counts, watson_probs, crick_probs, bridge_probs, reconstruction_params = simulate_dna_results(
            seed=None,  # Auto-generate seed from timestamp
            deterministic=True
        )
        analysis = analyze_dna_34bp_results(counts, watson_probs, crick_probs, bridge_probs)
        analysis['reconstruction_params'] = reconstruction_params
        artifact_type = ARTIFACT_TYPE_RECONSTRUCTED

    if analysis is None:
        print("\n[✗] DNA Agent failed")
        return False

    # Build parent artifact references from multi-source data
    parent_artifacts = []
    if existing_data:
        # Add external source references as parent artifacts (deduplicated)
        seen_sources = set()
        for source in existing_data.get('sources_loaded', []):
            source_name = Path(source).name
            if source_name not in seen_sources:
                parent_artifacts.append(f"external_source:{source_name}")
                seen_sources.add(source_name)
    
    # Generate report with proper artifact classification and parent references
    generate_report(analysis, artifact_type=artifact_type, parent_artifacts=parent_artifacts)

    print(f"\n{'='*80}")
    print("DNA AGENT COMPLETE")
    print(f"Artifact Classification: {artifact_type}")
    print(f"Evidence Class: {ARTIFACT_TO_EVIDENCE_CLASS.get(artifact_type, 'unknown')}")
    print(f"Parent Artifacts: {parent_artifacts}")
    print(f"{'='*80}\n")

    return True


if __name__ == "__main__":
    main()