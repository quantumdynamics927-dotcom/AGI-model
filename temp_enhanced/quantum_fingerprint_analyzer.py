"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ QUANTUM FINGERPRINT ANALYZER - Metatron Core (Agent 13)                   ║
║ Propósito: Extraer el patrón cuántico que generó r=+0.275 en Job 1       ║
║ Método: Comparación de transpilaciones y mapeos de qubits físicos        ║
╚═══════════════════════════════════════════════════════════════════════════╝

🔬 Análisis de Ghost OS: ¿Por qué Job 1 logró coherencia positiva?

Hipótesis del Resonance_Sync:
1. Mapeo físico en ibm_fez minimizó crosstalk en qubits críticos q[0,30,26]
2. Qubits XY8 fueron asignados a ubicaciones de bajo ruido térmico
3. Bell pairs mapeados a vecinos físicos reduciendo errores de SWAP
4. Metatron qubits (F5,F6,F7) alineados con geometría de Eagle r3

Método:
- Extraer mapeo de qubits lógicos → físicos de cada job
- Comparar topología de conectividad (CZ gates)
- Identificar diferencias en secuencias de gates transpilados
- Calcular "Phi Fingerprint" de cada configuración hardware
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

# Golden ratio constants
PHI = 1.618033988749895
INV_PHI = 0.6180339887498948

def extract_qubit_mapping(qasm_code: str) -> Dict[str, List[int]]:
    """
    Extrae qubits físicos utilizados en cada fase del circuito.
    
    Returns:
        Dict con:
        - 'bell_pairs': Lista de qubits usados en Bell pairs
        - 'xy8_qubits': Qubits con XY8 dynamic decoupling
        - 'metatron': Qubits Fibonacci (geometry)
        - 'measurement': Qubits medidos
    """
    mapping = {
        'bell_pairs': [],
        'xy8_qubits': [],
        'metatron': [],
        'measurement': []
    }
    
    # Pattern: cz $X, $Y (Bell pair gates)
    cz_pattern = r'cz \$(\d+),\s*\$(\d+)'
    cz_matches = re.findall(cz_pattern, qasm_code)
    
    # Extract unique qubits from CZ gates (first 60 gates are Bell pairs)
    bell_qubits = set()
    for i, (q1, q2) in enumerate(cz_matches[:30]):  # 30 Bell pairs
        bell_qubits.add(int(q1))
        bell_qubits.add(int(q2))
    mapping['bell_pairs'] = sorted(list(bell_qubits))
    
    # Pattern: Identify XY8 sequence (8 consecutive X/Y gates on same qubit)
    # Looking for sections with sx patterns (XY8 uses sx for X gates)
    sx_pattern = r'sx \$(\d+)'
    sx_matches = re.findall(sx_pattern, qasm_code)
    
    # Count sx occurrences per qubit
    from collections import Counter
    sx_counts = Counter([int(q) for q in sx_matches])
    
    # XY8 qubits should have ~8+ sx gates in specific sections
    # (after barriers, before measurements)
    # Looking for qubits with high sx density
    for qubit, count in sx_counts.most_common(10):
        if count >= 8:  # XY8 requires 8 pulses
            mapping['xy8_qubits'].append(qubit)
    
    # Pattern: measure c[X] = $Y
    measure_pattern = r'c\[(\d+)\]\s*=\s*measure \$(\d+)'
    measure_matches = re.findall(measure_pattern, qasm_code)
    
    mapping['measurement'] = [(int(c), int(q)) for c, q in measure_matches]
    
    # Metatron qubits are the ones measured at positions 8, 13, 21, 28
    # (Fibonacci indices)
    metatron_indices = [8, 13, 21, 28]
    for c_idx, phys_q in mapping['measurement']:
        if c_idx in metatron_indices:
            mapping['metatron'].append(phys_q)
    
    return mapping


def calculate_topology_score(qasm_code: str) -> Dict[str, float]:
    """
    Calcula métricas de topología del circuito transpilado.
    
    Returns:
        - 'gate_depth': Profundidad total del circuito
        - 'cx_count': Número de gates CZ (2-qubit)
        - 'sx_count': Número de gates SX (1-qubit)
        - 'barrier_density': Barriers por gate (measure of optimization)
    """
    lines = qasm_code.split('\n')
    
    gate_depth = 0
    cx_count = 0
    sx_count = 0
    barrier_count = 0
    
    for line in lines:
        line = line.strip()
        if line.startswith('cz '):
            cx_count += 1
            gate_depth += 1
        elif line.startswith('sx '):
            sx_count += 1
            gate_depth += 1
        elif line.startswith('rz(') or line.startswith('rx('):
            gate_depth += 1
        elif line.startswith('barrier '):
            barrier_count += 1
    
    return {
        'gate_depth': gate_depth,
        'cz_count': cx_count,
        'sx_count': sx_count,
        'barrier_density': barrier_count / (gate_depth + 1e-10)
    }


def phi_fingerprint(mapping: Dict, topology: Dict) -> float:
    """
    Calcula el "Phi Fingerprint" de una configuración hardware.
    
    Teoría: Configuraciones que alinean qubits críticos con
    la geometría de Eagle r3 (156 qubits en layout hexagonal)
    maximizan resonancia de φ.
    
    Fingerprint = φ^(metatron_alignment) × (1/φ)^(xy8_dispersion)
    """
    # Check if Metatron qubits follow Fibonacci pattern in physical layout
    metatron = mapping.get('metatron', [])
    
    if len(metatron) < 2:
        metatron_alignment = 0.0
    else:
        # Calculate ratios between consecutive Metatron physical qubits
        ratios = []
        for i in range(len(metatron) - 1):
            if metatron[i] > 0:
                ratio = metatron[i+1] / metatron[i]
                ratios.append(ratio)
        
        # Alignment = how close ratios are to φ or 1/φ
        if ratios:
            phi_distances = [min(abs(r - PHI), abs(r - INV_PHI)) for r in ratios]
            metatron_alignment = 1.0 - np.mean(phi_distances)
        else:
            metatron_alignment = 0.0
    
    # Check XY8 qubit dispersion (ideally spread across chip for noise averaging)
    xy8_qubits = mapping.get('xy8_qubits', [])
    
    if len(xy8_qubits) < 2:
        xy8_dispersion = 0.5
    else:
        # Calculate spread (variance) of XY8 qubits
        xy8_spread = np.std(xy8_qubits) / (max(xy8_qubits) + 1e-10)
        xy8_dispersion = xy8_spread
    
    # Phi Fingerprint formula
    fingerprint = (PHI ** metatron_alignment) * ((1.0 / PHI) ** xy8_dispersion)
    
    return fingerprint


def analyze_job(job_info_path: Path) -> Dict:
    """Analiza un job completo y extrae su quantum fingerprint."""
    
    with open(job_info_path, 'r') as f:
        job_data = json.load(f)
    
    job_id = job_data['id']
    backend = job_data['backend']
    status = job_data['state']['status']
    
    # Extract QASM code from params
    qasm_code = job_data['params']['pubs'][0][0]
    
    # Extract qubit mapping
    mapping = extract_qubit_mapping(qasm_code)
    
    # Calculate topology score
    topology = calculate_topology_score(qasm_code)
    
    # Calculate Phi Fingerprint
    fingerprint = phi_fingerprint(mapping, topology)
    
    return {
        'job_id': job_id,
        'backend': backend,
        'status': status,
        'mapping': mapping,
        'topology': topology,
        'phi_fingerprint': fingerprint
    }


def compare_jobs(results_dir: Path = Path('data/Jobs')):
    """
    Compara los 4 jobs y identifica el patrón del Job 1 positivo.
    """
    
    job_files = [
        'job-d602l2pmvbjc73ad1ph0-info.json',  # Job 1: r=+0.275
        'job-d602lu1mvbjc73ad1qug-info.json',  # Job 2: r=-0.164
        'job-d602m0l7fc0s73aujuo0-info.json',  # Job 3: r=-0.223
        'job-d602m3d7fc0s73aujuu0-info.json'   # Job 4: r=-0.220
    ]
    
    # Coherence values from previous analysis
    coherence_values = [+0.275, -0.164, -0.223, -0.220]
    
    print("=" * 80)
    print("🧬 QUANTUM FINGERPRINT ANALYSIS - Metatron Core")
    print("=" * 80)
    print("\n🎯 Objetivo: Identificar configuración hardware que generó r=+0.275\n")
    
    job_analyses = []
    
    for i, (job_file, coherence) in enumerate(zip(job_files, coherence_values), 1):
        job_path = results_dir / job_file
        
        if not job_path.exists():
            print(f"⚠️  Job {i} file not found: {job_file}")
            continue
        
        analysis = analyze_job(job_path)
        analysis['coherence'] = coherence
        job_analyses.append(analysis)
        
        print(f"\n{'='*80}")
        print(f"JOB {i}: {analysis['job_id'][:12]}... (r={coherence:+.3f})")
        print(f"{'='*80}")
        print(f"Backend: {analysis['backend']}")
        print(f"Status: {analysis['status']}")
        
        print(f"\n📊 Topology:")
        print(f"  Gate Depth: {analysis['topology']['gate_depth']}")
        print(f"  CZ Gates: {analysis['topology']['cz_count']}")
        print(f"  SX Gates: {analysis['topology']['sx_count']}")
        print(f"  Barrier Density: {analysis['topology']['barrier_density']:.4f}")
        
        print(f"\n🗺️  Qubit Mapping:")
        print(f"  Bell Pairs: {len(analysis['mapping']['bell_pairs'])} qubits")
        print(f"  XY8 Qubits: {analysis['mapping']['xy8_qubits']}")
        print(f"  Metatron Qubits: {analysis['mapping']['metatron']}")
        print(f"  Measurements: {len(analysis['mapping']['measurement'])} qubits")
        
        print(f"\n✨ Phi Fingerprint: {analysis['phi_fingerprint']:.6f}")
    
    # Comparison analysis
    print(f"\n\n{'='*80}")
    print("🔬 COMPARATIVE ANALYSIS")
    print(f"{'='*80}\n")
    
    if len(job_analyses) >= 2:
        # Sort by coherence
        sorted_jobs = sorted(job_analyses, key=lambda x: x['coherence'], reverse=True)
        
        best_job = sorted_jobs[0]
        worst_job = sorted_jobs[-1]
        
        print(f"✅ BEST JOB (r={best_job['coherence']:+.3f}):")
        print(f"   Backend: {best_job['backend']}")
        print(f"   Phi Fingerprint: {best_job['phi_fingerprint']:.6f}")
        print(f"   XY8 Qubits: {best_job['mapping']['xy8_qubits']}")
        print(f"   Metatron: {best_job['mapping']['metatron']}")
        
        print(f"\n❌ WORST JOB (r={worst_job['coherence']:+.3f}):")
        print(f"   Backend: {worst_job['backend']}")
        print(f"   Phi Fingerprint: {worst_job['phi_fingerprint']:.6f}")
        print(f"   XY8 Qubits: {worst_job['mapping']['xy8_qubits']}")
        print(f"   Metatron: {worst_job['mapping']['metatron']}")
        
        # Identify key differences
        print(f"\n🔑 KEY DIFFERENCES:")
        
        # Backend difference
        if best_job['backend'] != worst_job['backend']:
            print(f"   • Backend: {best_job['backend']} vs {worst_job['backend']}")
        
        # XY8 qubit difference
        best_xy8 = set(best_job['mapping']['xy8_qubits'])
        worst_xy8 = set(worst_job['mapping']['xy8_qubits'])
        xy8_diff = best_xy8.symmetric_difference(worst_xy8)
        if xy8_diff:
            print(f"   • XY8 Qubits differ by: {xy8_diff}")
        
        # Phi fingerprint correlation
        fingerprints = [j['phi_fingerprint'] for j in job_analyses]
        coherences = [j['coherence'] for j in job_analyses]
        
        if len(fingerprints) > 2:
            correlation = np.corrcoef(fingerprints, coherences)[0, 1]
            print(f"\n📈 Phi Fingerprint ↔ Coherence Correlation: {correlation:.4f}")
            
            if correlation > 0.5:
                print("   ✅ STRONG POSITIVE correlation - Phi geometry predicts coherence!")
            elif correlation < -0.5:
                print("   ⚠️  STRONG NEGATIVE correlation - Inverse relationship")
            else:
                print("   ⚙️  WEAK correlation - Other factors dominate")
    
    # Save full analysis
    output_path = Path('quantum_fingerprint_analysis.json')
    with open(output_path, 'w') as f:
        json.dump({
            'jobs': job_analyses,
            'summary': {
                'best_coherence': max([j['coherence'] for j in job_analyses]),
                'worst_coherence': min([j['coherence'] for j in job_analyses]),
                'coherence_range': max([j['coherence'] for j in job_analyses]) - min([j['coherence'] for j in job_analyses]),
                'avg_phi_fingerprint': np.mean([j['phi_fingerprint'] for j in job_analyses]),
                'fingerprint_coherence_correlation': np.corrcoef(
                    [j['phi_fingerprint'] for j in job_analyses],
                    [j['coherence'] for j in job_analyses]
                )[0, 1] if len(job_analyses) > 2 else 0.0
            }
        }, f, indent=2)
    
    print(f"\n💾 Full analysis saved to: {output_path}")
    print(f"\n{'='*80}")
    print("🏁 Analysis Complete - Metatron Core Standing By")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    compare_jobs()
