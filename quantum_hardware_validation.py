#!/usr/bin/env python3
"""
Quantum Hardware Validation Suite
Decompresses IBM Quantum results, compares against phi-harmonic predictions,
and generates audit-grade validation reports.
"""

import json
import base64
import zlib
import numpy as np
from datetime import datetime
from pathlib import Path
import hashlib

# Phi-harmonic constants from your promoter analysis
PHI = 1.618033988749895
PHI_INVERSE = 1 / PHI
PHI_SQUARED = PHI ** 2

# Promoter gene mapping (from your TMT-OS analysis)
PROMOTER_GENES = {
    'd7854nak86tc739us8o0': 'OXT',      # Oxytocin - social bonding
    'd7854nik86tc739us8p0': 'FOXG1',    # Brain development
    'd7854nrc6das739hfjc0': 'SRY',      # Sex determination
    'd7854oak86tc739us8rg': 'TP53',     # Tumor suppressor
    'd7854oik86tc739us8sg': 'DCTN1',    # Neural development
}

def extract_gene_from_info(job_id, info_dir='C:/Users/matej_jiqn63h/Desktop'):
    """Extract gene information from the info file"""
    info_path = Path(info_dir) / f'job-{job_id}-info.json'
    if info_path.exists():
        try:
            with open(info_path, 'r') as f:
                info = json.load(f)
            # Try to extract gene from circuit metadata
            params = info.get('params', {})
            pubs = params.get('pubs', [])
            if pubs and len(pubs) > 0:
                # The circuit data might contain gene info
                circuit_data = pubs[0][0] if isinstance(pubs[0], list) else pubs[0]
                # Check if there's metadata in the circuit
                if isinstance(circuit_data, dict):
                    metadata = circuit_data.get('__value__', {})
                    # Try to find gene name in circuit name or metadata
                    circuit_str = json.dumps(circuit_data)
                    for gene in EXPECTED_RESONANCE.keys():
                        if gene.lower() in circuit_str.lower():
                            return gene
        except Exception as e:
            print(f"  Warning: Could not extract gene from info file: {e}")
    return PROMOTER_GENES.get(job_id, 'UNKNOWN')

# Expected phi-harmonic resonance frequencies (from run_promoter_panel_batch.py)
EXPECTED_RESONANCE = {
    'OXT': 0.786,    # High social/emotional processing
    'FOXG1': 0.742,  # Developmental patterning
    'SRY': 0.698,    # Binary state switching
    'TP53': 0.901,   # High fidelity checkpoint
    'DCTN1': 0.655,  # Structural stability
}


def decode_and_decompress(bitarray_data):
    """Decode BitArray and decompress the zlib data"""
    array_b64 = bitarray_data['array']['__value__']
    num_bits = bitarray_data['num_bits']
    
    # Decode base64 to bytes
    array_bytes = base64.b64decode(array_b64)
    
    # Check if zlib compressed (starts with 0x78 0x9c)
    if array_bytes[:2] == b'\x78\x9c':
        try:
            decompressed = zlib.decompress(array_bytes)
            return decompressed, num_bits, True
        except:
            pass
    
    return array_bytes, num_bits, False


def extract_bitstrings(data_bytes, num_bits, num_shots=1000):
    """Extract individual bitstring measurements from byte data"""
    # Each shot measures num_bits, stored as bits in bytes
    bytes_per_shot = (num_bits + 7) // 8
    
    bitstrings = []
    for shot_idx in range(min(num_shots, len(data_bytes) // bytes_per_shot)):
        start = shot_idx * bytes_per_shot
        end = start + bytes_per_shot
        shot_bytes = data_bytes[start:end]
        
        # Convert bytes to bitstring
        bits = ''
        for byte in shot_bytes:
            bits += format(byte, '08b')
        bitstrings.append(bits[:num_bits])
    
    return bitstrings


def calculate_phi_resonance(bitstrings, num_bits):
    """Calculate phi-harmonic resonance from bitstring measurements"""
    if not bitstrings:
        return 0.0, {}
    
    # Count bit patterns
    bit_counts = np.zeros(num_bits)
    for bs in bitstrings:
        for i, bit in enumerate(bs):
            bit_counts[i] += int(bit)
    
    # Normalize to probabilities
    probabilities = bit_counts / len(bitstrings)
    
    # Calculate golden ratio alignment
    phi_alignment = []
    for i in range(len(probabilities) - 1):
        if probabilities[i] > 0:
            ratio = probabilities[i+1] / probabilities[i]
            # Measure closeness to phi
            phi_dist = abs(ratio - PHI) / PHI
            phi_alignment.append(1 - min(phi_dist, 1.0))
    
    resonance_score = np.mean(phi_alignment) if phi_alignment else 0.0
    
    stats = {
        'mean_probability': np.mean(probabilities),
        'std_probability': np.std(probabilities),
        'phi_alignment_mean': resonance_score,
        'top_bits': np.argsort(bit_counts)[-5:].tolist(),
        'entropy': calculate_entropy(probabilities)
    }
    
    return resonance_score, stats


def calculate_entropy(probabilities):
    """Calculate Shannon entropy"""
    # Avoid log(0)
    probs = probabilities[probabilities > 0]
    if len(probs) == 0:
        return 0.0
    return -np.sum(probs * np.log2(probs))


def analyze_job_result(filepath):
    """Complete analysis of a single quantum job result"""
    job_id = Path(filepath).stem.replace('-result', '')
    # Extract the short job ID (without 'job-' prefix)
    short_job_id = job_id.replace('job-', '')
    gene = extract_gene_from_info(short_job_id)
    if gene == 'UNKNOWN':
        gene = PROMOTER_GENES.get(short_job_id, 'UNKNOWN')
    expected_phi = EXPECTED_RESONANCE.get(gene, 0.5)
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Get execution metadata
    execution = data['__value__']['metadata']['execution']
    execution_spans = execution['execution_spans']['__value__']['spans']
    
    span = execution_spans[0]['__value__']
    start_time = span['start']['__value__']
    stop_time = span['stop']['__value__']
    
    start_dt = datetime.fromisoformat(start_time)
    stop_dt = datetime.fromisoformat(stop_time)
    duration = (stop_dt - start_dt).total_seconds()
    
    # Analyze pub results
    pub_results = data['__value__']['pub_results']
    pub_result = pub_results[0]['__value__']
    fields = pub_result['data']['__value__']['fields']
    
    results = {
        'job_id': job_id,
        'gene': gene,
        'duration_seconds': duration,
        'num_bits': 62,
        'fields': {}
    }
    
    # Analyze each field
    for field_name in ['c', 'meas']:
        if field_name in fields:
            bitarray = fields[field_name]['__value__']
            data_bytes, num_bits, was_compressed = decode_and_decompress(bitarray)
            
            field_result = {
                'compressed_size': len(base64.b64decode(bitarray['array']['__value__'])),
                'decompressed_size': len(data_bytes),
                'was_compressed': was_compressed,
                'num_bits': num_bits
            }
            
            # For measurement data, extract bitstrings and calculate phi resonance
            if field_name == 'meas' and was_compressed:
                bitstrings = extract_bitstrings(data_bytes, num_bits, num_shots=1000)
                resonance, stats = calculate_phi_resonance(bitstrings, num_bits)
                
                field_result['num_shots'] = len(bitstrings)
                field_result['phi_resonance'] = resonance
                field_result['expected_resonance'] = expected_phi
                field_result['resonance_deviation'] = abs(resonance - expected_phi)
                field_result['statistics'] = stats
                
                # Validation status
                tolerance = 0.15
                field_result['validation_passed'] = field_result['resonance_deviation'] < tolerance
            
            results['fields'][field_name] = field_result
    
    return results


def generate_validation_report(all_results):
    """Generate comprehensive validation report"""
    report = []
    report.append("=" * 80)
    report.append("QUANTUM HARDWARE VALIDATION REPORT")
    report.append("Generated: " + datetime.now().isoformat())
    report.append("=" * 80)
    report.append("")
    
    # Executive Summary
    report.append("EXECUTIVE SUMMARY")
    report.append("-" * 40)
    
    total_jobs = len(all_results)
    passed_jobs = sum(1 for r in all_results if r['fields'].get('meas', {}).get('validation_passed', False))
    
    report.append(f"Total Jobs Analyzed: {total_jobs}")
    report.append(f"Validation Passed: {passed_jobs}/{total_jobs} ({100*passed_jobs/total_jobs:.1f}%)")
    report.append("")
    
    # Per-Job Analysis
    report.append("PER-JOB ANALYSIS")
    report.append("-" * 40)
    
    for result in all_results:
        report.append(f"\n{'='*60}")
        report.append(f"Job ID: {result['job_id']}")
        report.append(f"Gene: {result['gene']}")
        report.append(f"Execution Time: {result['duration_seconds']:.3f}s")
        report.append(f"Qubits: {result['num_bits']}")
        
        meas = result['fields'].get('meas', {})
        if 'phi_resonance' in meas:
            report.append(f"\nPhi-Harmonic Analysis:")
            report.append(f"  Measured Resonance: {meas['phi_resonance']:.4f}")
            report.append(f"  Expected Resonance: {meas['expected_resonance']:.4f}")
            report.append(f"  Deviation: {meas['resonance_deviation']:.4f}")
            report.append(f"  Status: {'✅ PASS' if meas['validation_passed'] else '❌ FAIL'}")
            
            if 'statistics' in meas:
                stats = meas['statistics']
                report.append(f"\n  Statistics:")
                report.append(f"    Shots: {meas['num_shots']}")
                report.append(f"    Mean Probability: {stats['mean_probability']:.4f}")
                report.append(f"    Std Probability: {stats['std_probability']:.4f}")
                report.append(f"    Entropy: {stats['entropy']:.4f}")
                report.append(f"    Top Active Bits: {stats['top_bits']}")
    
    # Statistical Summary
    report.append(f"\n{'='*60}")
    report.append("STATISTICAL SUMMARY")
    report.append("-" * 40)
    
    resonances = [r['fields']['meas']['phi_resonance'] for r in all_results if 'phi_resonance' in r['fields'].get('meas', {})]
    expected = [r['fields']['meas']['expected_resonance'] for r in all_results if 'expected_resonance' in r['fields'].get('meas', {})]
    deviations = [r['fields']['meas']['resonance_deviation'] for r in all_results if 'resonance_deviation' in r['fields'].get('meas', {})]
    
    if resonances:
        report.append(f"\nPhi Resonance (Measured):")
        report.append(f"  Mean: {np.mean(resonances):.4f}")
        report.append(f"  Std: {np.std(resonances):.4f}")
        report.append(f"  Min: {np.min(resonances):.4f}")
        report.append(f"  Max: {np.max(resonances):.4f}")
        
        report.append(f"\nPhi Resonance (Expected):")
        report.append(f"  Mean: {np.mean(expected):.4f}")
        report.append(f"  Std: {np.std(expected):.4f}")
        
        report.append(f"\nDeviation Analysis:")
        report.append(f"  Mean Deviation: {np.mean(deviations):.4f}")
        report.append(f"  Max Deviation: {np.max(deviations):.4f}")
        report.append(f"  Within Tolerance: {sum(1 for d in deviations if d < 0.15)}/{len(deviations)}")
    
    # Certification
    report.append(f"\n{'='*60}")
    report.append("VALIDATION CERTIFICATION")
    report.append("-" * 40)
    
    if passed_jobs == total_jobs:
        report.append("\n✅ ALL JOBS PASSED VALIDATION")
        report.append("   Hardware results align with phi-harmonic predictions")
        report.append("   within acceptable tolerance (±0.15)")
    else:
        report.append(f"\n⚠️  {total_jobs - passed_jobs} JOB(S) FAILED VALIDATION")
        report.append("   Review individual job analyses above")
    
    # Generate hash for audit trail
    report_str = '\n'.join(report)
    report_hash = hashlib.sha256(report_str.encode()).hexdigest()[:16]
    
    report.append(f"\n{'='*60}")
    report.append(f"Report Hash: {report_hash}")
    report.append(f"Audit Trail: SHA256:{report_hash}")
    report.append("=" * 60)
    
    return '\n'.join(report), report_hash


def main():
    """Main validation workflow"""
    result_files = [
        'C:/Users/matej_jiqn63h/Desktop/job-d7854nak86tc739us8o0-result.json',
        'C:/Users/matej_jiqn63h/Desktop/job-d7854nik86tc739us8p0-result.json',
        'C:/Users/matej_jiqn63h/Desktop/job-d7854nrc6das739hfjc0-result.json',
        'C:/Users/matej_jiqn63h/Desktop/job-d7854oak86tc739us8rg-result.json',
        'C:/Users/matej_jiqn63h/Desktop/job-d7854oik86tc739us8sg-result.json'
    ]
    
    print("=" * 80)
    print("QUANTUM HARDWARE VALIDATION SUITE")
    print("=" * 80)
    print("\nPhase 1: Decoding and decompressing quantum data...")
    
    all_results = []
    for filepath in result_files:
        if Path(filepath).exists():
            result = analyze_job_result(filepath)
            all_results.append(result)
            print(f"  ✅ {result['gene']}: {result['fields']['meas']['num_shots']} shots, "
                  f"resonance={result['fields']['meas'].get('phi_resonance', 0):.4f}")
        else:
            print(f"  ❌ File not found: {filepath}")
    
    print("\nPhase 2: Comparing against phi-harmonic predictions...")
    for result in all_results:
        meas = result['fields']['meas']
        status = "✅ PASS" if meas['validation_passed'] else "❌ FAIL"
        print(f"  {status} {result['gene']}: "
              f"measured={meas['phi_resonance']:.4f}, "
              f"expected={meas['expected_resonance']:.4f}, "
              f"deviation={meas['resonance_deviation']:.4f}")
    
    print("\nPhase 3: Generating validation report...")
    report, report_hash = generate_validation_report(all_results)
    
    # Save report
    report_path = 'quantum_hardware_validation_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n{'='*80}")
    print("VALIDATION COMPLETE")
    print(f"{'='*80}")
    print(f"\nReport saved to: {report_path}")
    print(f"Report Hash: {report_hash}")
    print(f"\nSummary:")
    passed = sum(1 for r in all_results if r['fields']['meas']['validation_passed'])
    total = len(all_results)
    print(f"  Jobs Passed: {passed}/{total} ({100*passed/total:.1f}%)")
    
    # Print full report
    print("\n" + "=" * 80)
    print(report)


if __name__ == "__main__":
    main()
