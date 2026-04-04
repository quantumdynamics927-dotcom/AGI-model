#!/usr/bin/env python3
"""
IBM Quantum Backend Calibration Analyzer
Analyzes and compares calibration data across multiple backends
"""

import csv
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
import numpy as np
from datetime import datetime


@dataclass
class QubitMetrics:
    """Metrics for a single qubit"""
    qubit_id: int
    t1_us: float  # Relaxation time
    t2_us: float  # Decoherence time
    readout_error: float
    prob_meas0_prep1: float
    prob_meas1_prep0: float
    readout_length_ns: int
    single_qubit_gate_error: float
    rx_error: float
    rz_error: float
    sx_error: float
    pauli_x_error: float
    cz_errors: Dict[int, float]  # CZ errors with neighbors
    rzz_errors: Dict[int, float]  # RZZ errors with neighbors
    measure_error: float
    operational: bool


@dataclass
class BackendCharacteristics:
    """Overall backend characteristics"""
    name: str
    timestamp: str
    num_qubits: int
    avg_t1_us: float
    avg_t2_us: float
    median_t1_us: float
    median_t2_us: float
    avg_readout_error: float
    avg_single_qubit_gate_error: float
    avg_two_qubit_gate_error: float
    operational_qubits: int
    coherence_quality_score: float  # Custom metric
    gate_quality_score: float  # Custom metric
    overall_quality_score: float  # Composite metric


def parse_calibration_csv(filepath: Path) -> Tuple[str, str, List[QubitMetrics]]:
    """Parse IBM Quantum calibration CSV file"""
    
    # Extract backend name and timestamp from filename
    filename = filepath.stem
    parts = filename.split('_')
    backend_name = parts[0] + '_' + parts[1]  # e.g., "ibm_fez"
    timestamp = parts[2] if len(parts) > 2 else "unknown"
    
    qubits = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                qubit_id = int(row['Qubit'])
                
                # Parse CZ errors (format: "neighbor:error;neighbor:error")
                cz_errors = {}
                if 'Error CZ' in row and row['Error CZ']:
                    cz_str = row['Error CZ']
                    for part in cz_str.split(';'):
                        if ':' in part:
                            neighbor, error = part.split(':')
                            cz_errors[int(neighbor)] = float(error)
                
                # Parse RZZ errors
                rzz_errors = {}
                if 'Error RZZ' in row and row['Error RZZ']:
                    rzz_str = row['Error RZZ']
                    for part in rzz_str.split(';'):
                        if ':' in part:
                            neighbor, error = part.split(':')
                            rzz_errors[int(neighbor)] = float(error)
                
                qubit = QubitMetrics(
                    qubit_id=qubit_id,
                    t1_us=float(row.get('T1 (us)', 0)),
                    t2_us=float(row.get('T2 (us)', 0)),
                    readout_error=float(row.get('Error de asignación de lectura', 0)),
                    prob_meas0_prep1=float(row.get('Prob meas0 prep1', 0)),
                    prob_meas1_prep0=float(row.get('Prob meas1 prep0', 0)),
                    readout_length_ns=int(row.get('Readout length (ns)', 0)),
                    single_qubit_gate_error=float(row.get('Error ID', 0)),
                    rx_error=float(row.get('Error RX', 0)),
                    rz_error=float(row.get('Error Rotación del eje Z (rz)', 0)),
                    sx_error=float(row.get('Error √x (sx)', 0)),
                    pauli_x_error=float(row.get('Error Pauli-X', 0)),
                    cz_errors=cz_errors,
                    rzz_errors=rzz_errors,
                    measure_error=float(row.get('Error MEASURE', 0)),
                    operational=row.get('Operational', 'No') == 'Yes'
                )
                
                qubits.append(qubit)
                
            except Exception as e:
                print(f"  Warning: Could not parse qubit {row.get('Qubit', 'unknown')}: {e}")
                continue
    
    return backend_name, timestamp, qubits


def calculate_backend_characteristics(
    name: str, 
    timestamp: str, 
    qubits: List[QubitMetrics]
) -> BackendCharacteristics:
    """Calculate aggregate characteristics for a backend"""
    
    operational_qubits = [q for q in qubits if q.operational]
    num_operational = len(operational_qubits)
    
    if num_operational == 0:
        return BackendCharacteristics(
            name=name, timestamp=timestamp, num_qubits=len(qubits),
            avg_t1_us=0, avg_t2_us=0, median_t1_us=0, median_t2_us=0,
            avg_readout_error=1.0, avg_single_qubit_gate_error=1.0,
            avg_two_qubit_gate_error=1.0, operational_qubits=0,
            coherence_quality_score=0, gate_quality_score=0, overall_quality_score=0
        )
    
    # Calculate averages
    t1_values = [q.t1_us for q in operational_qubits]
    t2_values = [q.t2_us for q in operational_qubits]
    readout_errors = [q.readout_error for q in operational_qubits]
    sq_gate_errors = [q.single_qubit_gate_error for q in operational_qubits]
    
    # Calculate two-qubit gate errors
    tq_gate_errors = []
    for q in operational_qubits:
        for error in q.cz_errors.values():
            tq_gate_errors.append(error)
        for error in q.rzz_errors.values():
            tq_gate_errors.append(error)
    
    avg_t1 = np.mean(t1_values)
    avg_t2 = np.mean(t2_values)
    median_t1 = np.median(t1_values)
    median_t2 = np.median(t2_values)
    avg_readout = np.mean(readout_errors)
    avg_sq_gate = np.mean(sq_gate_errors)
    avg_tq_gate = np.mean(tq_gate_errors) if tq_gate_errors else 1.0
    
    # Calculate quality scores (higher is better, 0-1 scale)
    # T1/T2 quality: exponential decay model
    coherence_quality = np.exp(-1.0 / (avg_t1 + avg_t2)) if (avg_t1 + avg_t2) > 0 else 0
    
    # Gate quality: inverse of error rates
    gate_quality = 1.0 - (avg_sq_gate + avg_tq_gate) / 2.0
    
    # Overall quality: weighted combination
    overall_quality = 0.4 * coherence_quality + 0.6 * gate_quality
    
    return BackendCharacteristics(
        name=name,
        timestamp=timestamp,
        num_qubits=len(qubits),
        avg_t1_us=avg_t1,
        avg_t2_us=avg_t2,
        median_t1_us=median_t1,
        median_t2_us=median_t2,
        avg_readout_error=avg_readout,
        avg_single_qubit_gate_error=avg_sq_gate,
        avg_two_qubit_gate_error=avg_tq_gate,
        operational_qubits=num_operational,
        coherence_quality_score=coherence_quality,
        gate_quality_score=gate_quality,
        overall_quality_score=overall_quality
    )


def analyze_backend(backend_char: BackendCharacteristics) -> Dict:
    """Generate detailed analysis for a backend"""
    
    analysis = {
        'backend': backend_char.name,
        'timestamp': backend_char.timestamp,
        'summary': {
            'total_qubits': backend_char.num_qubits,
            'operational_qubits': backend_char.operational_qubits,
            'operational_percentage': 100 * backend_char.operational_qubits / backend_char.num_qubits if backend_char.num_qubits > 0 else 0
        },
        'coherence': {
            'avg_t1_us': round(backend_char.avg_t1_us, 2),
            'avg_t2_us': round(backend_char.avg_t2_us, 2),
            'median_t1_us': round(backend_char.median_t1_us, 2),
            'median_t2_us': round(backend_char.median_t2_us, 2),
            't2_t1_ratio': round(backend_char.avg_t2_us / backend_char.avg_t1_us, 3) if backend_char.avg_t1_us > 0 else 0,
            'quality_score': round(backend_char.coherence_quality_score, 4)
        },
        'gate_performance': {
            'single_qubit_error': round(backend_char.avg_single_qubit_gate_error, 6),
            'two_qubit_error': round(backend_char.avg_two_qubit_gate_error, 6),
            'readout_error': round(backend_char.avg_readout_error, 6),
            'quality_score': round(backend_char.gate_quality_score, 4)
        },
        'overall': {
            'quality_score': round(backend_char.overall_quality_score, 4),
            'ranking': 0  # To be filled later
        }
    }
    
    return analysis


def rank_backends(backends: List[BackendCharacteristics]) -> List[Tuple[int, BackendCharacteristics]]:
    """Rank backends by overall quality"""
    
    # Sort by overall quality score (descending)
    sorted_backends = sorted(backends, key=lambda b: b.overall_quality_score, reverse=True)
    
    return [(i+1, b) for i, b in enumerate(sorted_backends)]


def correlate_with_phi_resonance(
    backend_analyses: List[Dict],
    phi_baseline: float = 0.6183
) -> Dict:
    """Correlate backend characteristics with phi-resonance measurements"""
    
    # Our measured phi baseline from ibm_fez
    correlation = {
        'measured_phi_baseline': phi_baseline,
        'backend_comparison': [],
        'hypotheses': []
    }
    
    for analysis in backend_analyses:
        backend = analysis['backend']
        
        # Estimate expected phi shift based on backend quality
        # Higher quality = closer to ideal phi
        quality = analysis['overall']['quality_score']
        estimated_phi_shift = (1 - quality) * 0.1  # Empirical factor
        
        comparison = {
            'backend': backend,
            'quality_score': quality,
            'estimated_phi_shift': round(estimated_phi_shift, 4),
            'predicted_phi': round(phi_baseline + estimated_phi_shift, 4),
            'recommendation': ''
        }
        
        # Generate recommendation
        if quality > 0.95:
            comparison['recommendation'] = 'Excellent - Primary choice for promoter panel'
        elif quality > 0.90:
            comparison['recommendation'] = 'Good - Suitable for validation runs'
        elif quality > 0.85:
            comparison['recommendation'] = 'Fair - Use for comparison studies'
        else:
            comparison['recommendation'] = 'Poor - Avoid for critical measurements'
        
        correlation['backend_comparison'].append(comparison)
    
    # Generate hypotheses
    correlation['hypotheses'] = [
        "Higher T1/T2 coherence times correlate with more stable phi measurements",
        "Lower two-qubit gate errors reduce systematic offset in phi-resonance",
        "Backends with quality_score > 0.95 should produce phi within ±0.05 of baseline",
        "Readout errors contribute to measured phi compression (60:1 observed)"
    ]
    
    return correlation


def generate_report(
    backend_files: List[Path],
    output_path: str = 'backend_calibration_analysis.json'
) -> Dict:
    """Generate comprehensive calibration analysis report"""
    
    print("=" * 80)
    print("IBM QUANTUM BACKEND CALIBRATION ANALYZER")
    print("=" * 80)
    
    backends = []
    analyses = []
    
    # Parse each calibration file
    print("\nPhase 1: Parsing calibration files...")
    for filepath in backend_files:
        if filepath.exists():
            print(f"\n  Processing: {filepath.name}")
            name, timestamp, qubits = parse_calibration_csv(filepath)
            char = calculate_backend_characteristics(name, timestamp, qubits)
            backends.append(char)
            
            print(f"    Backend: {name}")
            print(f"    Qubits: {char.num_qubits} ({char.operational_qubits} operational)")
            print(f"    Avg T1: {char.avg_t1_us:.1f} μs")
            print(f"    Avg T2: {char.avg_t2_us:.1f} μs")
            print(f"    Quality Score: {char.overall_quality_score:.4f}")
    
    # Analyze each backend
    print("\nPhase 2: Analyzing backend characteristics...")
    for char in backends:
        analysis = analyze_backend(char)
        analyses.append(analysis)
    
    # Rank backends
    print("\nPhase 3: Ranking backends...")
    ranked = rank_backends(backends)
    for rank, char in ranked:
        for analysis in analyses:
            if analysis['backend'] == char.name:
                analysis['overall']['ranking'] = rank
                break
        print(f"  #{rank}: {char.name} (score: {char.overall_quality_score:.4f})")
    
    # Correlate with phi-resonance
    print("\nPhase 4: Correlating with phi-resonance measurements...")
    correlation = correlate_with_phi_resonance(analyses)
    
    for comp in correlation['backend_comparison']:
        print(f"  {comp['backend']}: predicted_phi ≈ {comp['predicted_phi']}")
        print(f"    → {comp['recommendation']}")
    
    # Generate report
    report = {
        'report_version': '1.0',
        'generated': datetime.now().isoformat(),
        'summary': {
            'backends_analyzed': len(backends),
            'best_backend': ranked[0][1].name if ranked else None,
            'recommendation': 'Use highest-ranked backend for promoter panel validation'
        },
        'backend_analyses': analyses,
        'phi_resonance_correlation': correlation,
        'recommendations': {
            'primary_backend': ranked[0][1].name if ranked else None,
            'validation_backend': ranked[1][1].name if len(ranked) > 1 else None,
            'avoid_backends': [b.name for rank, b in ranked if rank > 2]
        }
    }
    
    # Save report
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "=" * 80)
    print(f"Report saved to: {output_path}")
    print("=" * 80)
    
    return report


def main():
    """Main analysis workflow"""
    
    # Calibration files from user
    calibration_files = [
        Path('E:/Descargas/ibm_fez_calibrations_2026-04-04T01_04_39Z.csv'),
        Path('E:/Descargas/ibm_kingston_calibrations_2026-04-04T00_11_45Z.csv'),
        Path('E:/Descargas/ibm_marrakesh_calibrations_2026-04-04T00_55_18Z.csv')
    ]
    
    # Generate report
    report = generate_report(calibration_files)
    
    # Print summary
    print("\n" + "=" * 80)
    print("EXECUTIVE SUMMARY")
    print("=" * 80)
    print(f"Backends Analyzed: {report['summary']['backends_analyzed']}")
    print(f"Best Backend: {report['summary']['best_backend']}")
    print(f"\nRecommendations:")
    print(f"  Primary: {report['recommendations']['primary_backend']}")
    print(f"  Validation: {report['recommendations']['validation_backend']}")
    if report['recommendations']['avoid_backends']:
        print(f"  Avoid: {', '.join(report['recommendations']['avoid_backends'])}")


if __name__ == "__main__":
    main()
