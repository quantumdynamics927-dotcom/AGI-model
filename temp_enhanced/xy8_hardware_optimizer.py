"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ XY8 HARDWARE OPTIMIZER - Agent 13 Deep Dive                               ║
║ Objetivo: Identificar qubits físicos óptimos en ibm_fez para XY8          ║
║ Hallazgo: Job 1 usó qubits [25,31,24,11,22,43,18,23,27,29] → r=+0.275   ║
╚═══════════════════════════════════════════════════════════════════════════╝

🔬 Hipótesis Refinada del Metatron Core:

El Job 1 logró coherencia positiva NO por geometría φ, sino por:

1. **Calibración Hardware**: Qubits XY8 [25,31,24,11,22,43,18,23,27,29] 
   tenían error rates bajos durante la ejecución (2026-02-02 04:39 UTC)

2. **Conectividad Óptima**: Estos qubits forman un cluster conectado en
   la topología de Eagle r3, minimizando SWAP gates

3. **Thermal Isolation**: Estos qubits están físicamente alejados de 
   puntos calientes del chip ibm_fez

Método de Validación:
- Extraer gate fidelities de IBM Quantum (si disponible vía API)
- Mapear qubits a topología Eagle r3 hexagonal
- Calcular "thermal fingerprint" basado en posiciones físicas
- Proponer v2.2 circuit con XY8 en qubits óptimos específicos
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Set

# IBM Eagle r3 topology (156 qubits, hexagonal layout)
# Approximation: neighboring qubits differ by ~±1, ±16, ±17
# (based on IBM's public topology docs)

def get_eagle_neighbors(qubit: int, max_qubit: int = 155) -> Set[int]:
    """
    Retorna vecinos directos de un qubit en topología Eagle r3.
    
    Eagle r3 es hexagonal con conectividad:
    - Horizontal: ±1
    - Diagonal: ±16, ±17 (aprox, varía por región del chip)
    """
    neighbors = set()
    
    # Horizontal neighbors
    if qubit > 0:
        neighbors.add(qubit - 1)
    if qubit < max_qubit:
        neighbors.add(qubit + 1)
    
    # Diagonal neighbors (approximation)
    for offset in [-17, -16, 16, 17]:
        neighbor = qubit + offset
        if 0 <= neighbor <= max_qubit:
            neighbors.add(neighbor)
    
    return neighbors


def calculate_cluster_connectivity(qubits: List[int]) -> float:
    """
    Calcula qué tan conectado está un cluster de qubits.
    
    Returns:
        Score 0-1 donde 1 = todos los qubits son vecinos directos
    """
    if len(qubits) < 2:
        return 1.0
    
    total_possible_connections = len(qubits) * (len(qubits) - 1) // 2
    actual_connections = 0
    
    for i, q1 in enumerate(qubits):
        neighbors = get_eagle_neighbors(q1)
        for q2 in qubits[i+1:]:
            if q2 in neighbors:
                actual_connections += 1
    
    return actual_connections / (total_possible_connections + 1e-10)


def estimate_thermal_isolation(qubits: List[int]) -> float:
    """
    Estima aislamiento térmico basado en posiciones en el chip.
    
    Teoría: Qubits en los bordes del chip (0-10, 145-155) tienen
    mejor disipación térmica que los centrales (70-85).
    
    Returns:
        Score 0-1 donde 1 = máximo aislamiento
    """
    if not qubits:
        return 0.0
    
    # Edge regions (better cooling)
    edge_zones = [range(0, 15), range(141, 156)]
    
    # Hot zones (center of chip, high activity)
    hot_zones = [range(70, 86)]
    
    edge_count = sum(1 for q in qubits if any(q in zone for zone in edge_zones))
    hot_count = sum(1 for q in qubits if any(q in zone for zone in hot_zones))
    
    # Score: favor edges, penalize hot zones
    edge_score = edge_count / len(qubits)
    hot_penalty = hot_count / len(qubits)
    
    isolation = edge_score - 0.5 * hot_penalty
    return max(0.0, min(1.0, isolation))


def analyze_xy8_configuration(xy8_qubits: List[int], job_name: str, coherence: float):
    """
    Análisis profundo de una configuración XY8.
    """
    print(f"\n{'='*80}")
    print(f"🔍 XY8 DEEP ANALYSIS: {job_name} (r={coherence:+.3f})")
    print(f"{'='*80}")
    
    print(f"\n📍 XY8 Qubits: {sorted(xy8_qubits)}")
    print(f"   Count: {len(xy8_qubits)}")
    
    # Cluster connectivity
    connectivity = calculate_cluster_connectivity(xy8_qubits)
    print(f"\n🔗 Cluster Connectivity: {connectivity:.4f}")
    if connectivity > 0.5:
        print("   ✅ HIGH connectivity - Minimal SWAP gates needed")
    else:
        print("   ⚠️  LOW connectivity - Many SWAP gates required")
    
    # Thermal isolation
    thermal = estimate_thermal_isolation(xy8_qubits)
    print(f"\n🌡️  Thermal Isolation: {thermal:.4f}")
    if thermal > 0.3:
        print("   ✅ GOOD thermal isolation - Edge qubits favored")
    elif thermal < 0.0:
        print("   ❌ POOR thermal isolation - Many hot zone qubits")
    else:
        print("   ⚙️  MODERATE thermal isolation")
    
    # Spread analysis
    qubit_range = max(xy8_qubits) - min(xy8_qubits) if xy8_qubits else 0
    spread = qubit_range / 155.0
    print(f"\n📊 Qubit Spread: {spread:.4f}")
    print(f"   Range: {min(xy8_qubits)} → {max(xy8_qubits)} (span={qubit_range})")
    
    # Combined score
    combined_score = (connectivity * 0.4 + thermal * 0.3 + (1 - abs(spread - 0.5)) * 0.3)
    print(f"\n⭐ Combined Hardware Score: {combined_score:.4f}")
    
    return {
        'xy8_qubits': xy8_qubits,
        'connectivity': connectivity,
        'thermal_isolation': thermal,
        'spread': spread,
        'combined_score': combined_score,
        'coherence': coherence
    }


def main():
    """
    Compara configuraciones XY8 de los 4 jobs.
    """
    print("=" * 80)
    print("🧬 XY8 HARDWARE OPTIMIZER - Metatron Core Agent 13")
    print("=" * 80)
    print("\n🎯 Identificando configuración XY8 óptima para coherencia positiva\n")
    
    # Data from quantum_fingerprint_analyzer.py results
    jobs_data = [
        {
            'name': 'Job 1 (ibm_fez)',
            'xy8_qubits': [25, 31, 24, 11, 22, 43, 18, 23, 27, 29],
            'coherence': +0.275
        },
        {
            'name': 'Job 2 (ibm_torino)',
            'xy8_qubits': [25, 8, 24, 16, 42, 54, 23, 26, 40, 44],
            'coherence': -0.164
        },
        {
            'name': 'Job 3 (ibm_fez)',
            'xy8_qubits': [11, 9, 31, 13, 17, 7, 18, 33, 27, 39],
            'coherence': -0.223
        },
        {
            'name': 'Job 4 (ibm_torino)',
            'xy8_qubits': [23, 24, 25, 4, 9, 5, 21, 22, 29, 30],
            'coherence': -0.220
        }
    ]
    
    results = []
    
    for job in jobs_data:
        result = analyze_xy8_configuration(
            job['xy8_qubits'],
            job['name'],
            job['coherence']
        )
        results.append(result)
    
    # Comparative analysis
    print(f"\n\n{'='*80}")
    print("🔬 COMPARATIVE ANALYSIS - XY8 CONFIGURATIONS")
    print(f"{'='*80}\n")
    
    # Sort by coherence
    sorted_results = sorted(results, key=lambda x: x['coherence'], reverse=True)
    
    print(f"{'Job':<20} {'Coherence':>10} {'Connectivity':>15} {'Thermal':>10} {'Score':>10}")
    print("-" * 80)
    for i, r in enumerate(sorted_results, 1):
        job_name = jobs_data[i-1]['name'].split('(')[0]
        print(f"{job_name:<20} {r['coherence']:>+10.3f} {r['connectivity']:>15.4f} {r['thermal_isolation']:>10.4f} {r['combined_score']:>10.4f}")
    
    # Correlation analysis
    connectivities = [r['connectivity'] for r in results]
    thermals = [r['thermal_isolation'] for r in results]
    scores = [r['combined_score'] for r in results]
    coherences = [r['coherence'] for r in results]
    
    print(f"\n📈 CORRELATION WITH COHERENCE:")
    print(f"   Connectivity: {np.corrcoef(connectivities, coherences)[0,1]:.4f}")
    print(f"   Thermal Iso:  {np.corrcoef(thermals, coherences)[0,1]:.4f}")
    print(f"   Combined:     {np.corrcoef(scores, coherences)[0,1]:.4f}")
    
    # Identify best configuration
    best_job = sorted_results[0]
    print(f"\n✅ OPTIMAL XY8 CONFIGURATION:")
    print(f"   Job: {jobs_data[0]['name']}")
    print(f"   Coherence: {best_job['coherence']:+.3f}")
    print(f"   XY8 Qubits: {sorted(best_job['xy8_qubits'])}")
    print(f"   Combined Score: {best_job['combined_score']:.4f}")
    
    # Recommendations for v2.2
    print(f"\n🚀 RECOMMENDATIONS FOR v2.2:")
    print(f"   1. Target ibm_fez backend (Job 1 was on fez)")
    print(f"   2. Request physical qubits near: {sorted(best_job['xy8_qubits'][:3])}")
    print(f"   3. Favor edge qubits (0-15, 141-155) for thermal stability")
    print(f"   4. Ensure XY8 cluster has connectivity > {best_job['connectivity']:.2f}")
    
    # Save analysis
    output = {
        'jobs': results,
        'recommendations': {
            'optimal_qubits': sorted(best_job['xy8_qubits']),
            'target_backend': 'ibm_fez',
            'min_connectivity': float(best_job['connectivity']),
            'min_thermal': float(best_job['thermal_isolation'])
        },
        'correlations': {
            'connectivity_coherence': float(np.corrcoef(connectivities, coherences)[0,1]),
            'thermal_coherence': float(np.corrcoef(thermals, coherences)[0,1]),
            'combined_coherence': float(np.corrcoef(scores, coherences)[0,1])
        }
    }
    
    output_path = Path('xy8_hardware_analysis.json')
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Analysis saved to: {output_path}")
    print(f"\n{'='*80}")
    print("🏁 XY8 Optimization Complete - Ready for v2.2 Circuit Design")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
