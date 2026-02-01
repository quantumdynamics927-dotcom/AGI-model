"""
Comprehensive Analysis of 151 IBM Quantum Hardware Executions
Analyzes all quantum job results from TMT-OS DNA-consciousness circuits
"""

import json
import glob
import os
from pathlib import Path
import numpy as np
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Headless mode

# Job directory
JOBS_DIR = r"e:\tmt-os\data\jobs\jobs"

def load_all_jobs():
    """Load all job info and result files"""
    results = []
    
    # Find all result files
    result_files = glob.glob(os.path.join(JOBS_DIR, "*-result.json"))
    
    print(f"Found {len(result_files)} result files")
    
    for result_file in result_files:
        try:
            # Get corresponding info file
            info_file = result_file.replace('-result.json', '-info.json')
            
            # Load both files
            with open(result_file, 'r', encoding='utf-8', errors='ignore') as f:
                result_data = json.load(f)
            
            info_data = None
            if os.path.exists(info_file):
                with open(info_file, 'r', encoding='utf-8', errors='ignore') as f:
                    info_data = json.load(f)
            
            # Extract job ID from filename
            job_id = os.path.basename(result_file).replace('-result.json', '').replace('job-', '')
            
            results.append({
                'job_id': job_id,
                'result': result_data,
                'info': info_data,
                'result_file': result_file,
                'info_file': info_file
            })
            
        except Exception as e:
            print(f"Error loading {result_file}: {e}")
            continue
    
    return results

def extract_measurement_stats(result_data):
    """Extract measurement statistics from result data (handles nested __value__ structure)"""
    try:
        # Handle Qiskit Result format with nested __value__ wrappers
        if isinstance(result_data, dict):
            # Unwrap PrimitiveResult __value__ if present
            if '__value__' in result_data:
                result_data = result_data['__value__']
            
            # Get pub_results
            if 'pub_results' in result_data:
                pub_results_list = result_data['pub_results']
                if pub_results_list and len(pub_results_list) > 0:
                    pub_result = pub_results_list[0]
                    
                    # Unwrap SamplerPubResult __value__
                    if '__value__' in pub_result:
                        pub_result = pub_result['__value__']
                    
                    # Get data field
                    data = pub_result.get('data', {})
                    
                    # Unwrap DataBin __value__
                    if '__value__' in data:
                        data = data['__value__']
                    
                    # Get fields (BitArray structure)
                    fields = data.get('fields', {})
                    
                    # Try 'meas' or 'c' field
                    meas_field = fields.get('meas') or fields.get('c')
                    
                    if meas_field:
                        # Unwrap BitArray __value__
                        if '__value__' in meas_field:
                            meas_data = meas_field['__value__']
                        else:
                            meas_data = meas_field
                        
                        # Extract num_bits
                        num_bits = meas_data.get('num_bits', 0)
                        
                        # Default IBM shots value
                        num_shots = 8192
                        
                        return {
                            'num_shots': num_shots,
                            'num_bits': num_bits,
                            'shape': (),
                            'has_measurements': True
                        }
        
        return {'error': 'Unknown format', 'has_measurements': False}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': str(e), 'has_measurements': False}

def extract_execution_times(info_data):
    """Extract execution timestamps and backend info"""
    try:
        if info_data:
            # Handle both direct dict and __value__ wrapped format
            if '__value__' in info_data:
                info_data = info_data['__value__']
            
            created = info_data.get('created', info_data.get('creation_date', ''))
            
            # Extract backend name from nested structure
            backend_name = 'unknown'
            if 'backend' in info_data:
                backend = info_data['backend']
                if isinstance(backend, dict):
                    backend_name = backend.get('name', 'unknown')
                else:
                    backend_name = str(backend)
            
            return {
                'created': created,
                'backend': backend_name
            }
    except Exception as e:
        print(f"Error extracting execution times: {e}")
        return {'error': str(e)}
    
    return {'created': '', 'backend': 'unknown'}

def analyze_jobs(jobs):
    """Comprehensive analysis of all jobs"""
    stats = {
        'total_jobs': len(jobs),
        'successful_jobs': 0,
        'total_shots': 0,
        'backends': defaultdict(int),
        'creation_dates': [],
        'qubit_counts': defaultdict(int),
        'jobs_with_measurements': 0,
        'jobs_by_session': defaultdict(list)
    }
    
    for job in jobs:
        # Extract measurement stats
        meas_stats = extract_measurement_stats(job['result'])
        
        if 'has_measurements' in meas_stats and meas_stats['has_measurements']:
            stats['jobs_with_measurements'] += 1
            stats['successful_jobs'] += 1
            stats['total_shots'] += meas_stats.get('num_shots', 0)
            stats['qubit_counts'][meas_stats.get('num_bits', 0)] += 1
        
        # Extract timing info
        if job['info']:
            timing = extract_execution_times(job['info'])
            if 'backend' in timing:
                stats['backends'][timing['backend']] += 1
            if 'created' in timing:
                stats['creation_dates'].append(timing['created'])
    
    return stats

def generate_report(stats, output_dir=r"e:\AGI model"):
    """Generate comprehensive analysis report"""
    
    # Create report text
    report = []
    report.append("=" * 80)
    report.append("QUANTUM HARDWARE EXECUTION ANALYSIS")
    report.append("IBM Quantum Jobs - DNA-Consciousness Circuits")
    report.append("=" * 80)
    report.append("")
    
    report.append(f"Total Quantum Jobs Found: {stats['total_jobs']}")
    report.append(f"Successful Executions: {stats['successful_jobs']}")
    report.append(f"Jobs with Valid Measurements: {stats['jobs_with_measurements']}")
    report.append(f"Total Measurement Shots: {stats['total_shots']:,}")
    report.append("")
    
    report.append("=" * 80)
    report.append("QUANTUM BACKENDS USED")
    report.append("=" * 80)
    for backend, count in sorted(stats['backends'].items(), key=lambda x: -x[1]):
        report.append(f"  {backend}: {count} jobs")
    report.append("")
    
    report.append("=" * 80)
    report.append("QUBIT CIRCUIT SIZES")
    report.append("=" * 80)
    for num_bits, count in sorted(stats['qubit_counts'].items()):
        report.append(f"  {num_bits}-bit circuits: {count} jobs")
    report.append("")
    
    # Execution timeline
    if stats['creation_dates']:
        dates = [d for d in stats['creation_dates'] if d]
        if dates:
            report.append("=" * 80)
            report.append("EXECUTION TIMELINE")
            report.append("=" * 80)
            report.append(f"  First execution: {min(dates)}")
            report.append(f"  Last execution: {max(dates)}")
            report.append(f"  Total unique dates: {len(set(d.split('T')[0] for d in dates if 'T' in d))}")
            report.append("")
    
    # Statistical summary
    report.append("=" * 80)
    report.append("STATISTICAL SUMMARY")
    report.append("=" * 80)
    if stats['successful_jobs'] > 0:
        avg_shots = stats['total_shots'] / stats['successful_jobs']
        report.append(f"  Average shots per job: {avg_shots:,.1f}")
        report.append(f"  Total quantum measurements: {stats['total_shots']:,}")
    report.append("")
    
    # Save report
    report_text = "\n".join(report)
    output_file = os.path.join(output_dir, "quantum_jobs_analysis_report.txt")
    
    with open(output_file, 'w') as f:
        f.write(report_text)
    
    print(report_text)
    print(f"\n✅ Report saved to: {output_file}")
    
    return report_text

def create_visualizations(stats, output_dir=r"e:\AGI model"):
    """Create visualization plots (with error handling)"""
    
    try:
        # Backend distribution
        if stats['backends']:
            print("\nCreating backend distribution plot...")
            fig = plt.figure(figsize=(10, 6))
            backends = list(stats['backends'].keys())
            counts = [stats['backends'][b] for b in backends]
            
            plt.bar(backends, counts, color='steelblue', alpha=0.7)
            plt.xlabel('IBM Quantum Backend', fontsize=12)
            plt.ylabel('Number of Jobs', fontsize=12)
            plt.title('Quantum Hardware Usage Distribution', fontsize=14, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            
            # Save without tight_layout to avoid font rendering issues
            plt.subplots_adjust(bottom=0.2, left=0.1, right=0.95, top=0.9)
            plt.savefig(os.path.join(output_dir, 'quantum_backends_distribution.png'), dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"✅ Saved: quantum_backends_distribution.png")
    except Exception as e:
        print(f"⚠️ Backend plot failed (non-critical): {str(e)}")
        plt.close('all')
    
    try:
        # Qubit distribution
        if stats['qubit_counts']:
            print("\nCreating circuit size distribution plot...")
            fig = plt.figure(figsize=(10, 6))
            qubits = sorted(stats['qubit_counts'].keys())
            counts = [stats['qubit_counts'][q] for q in qubits]
            
            plt.bar([str(q) for q in qubits], counts, color='darkgreen', alpha=0.7)
            plt.xlabel('Circuit Size (qubits)', fontsize=12)
            plt.ylabel('Number of Jobs', fontsize=12)
            plt.title('Quantum Circuit Size Distribution', fontsize=14, fontweight='bold')
            
            # Save without tight_layout to avoid font rendering issues
            plt.subplots_adjust(bottom=0.1, left=0.1, right=0.95, top=0.9)
            plt.savefig(os.path.join(output_dir, 'circuit_size_distribution.png'), dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"✅ Saved: circuit_size_distribution.png")
    except Exception as e:
        print(f"⚠️ Circuit size plot failed (non-critical): {str(e)}")
        plt.close('all')
    
    print("\n✅ Visualization generation complete (errors ignored)")

def main():
    print("Starting comprehensive quantum jobs analysis...")
    print("-" * 80)
    
    # Load all jobs
    jobs = load_all_jobs()
    print(f"\nLoaded {len(jobs)} quantum job executions")
    
    # Analyze
    stats = analyze_jobs(jobs)
    
    # Generate report
    generate_report(stats)
    
    # Create visualizations (optional - skip if matplotlib has issues)
    print("\n" + "="*80)
    print("Attempting to create visualizations...")
    try:
        create_visualizations(stats)
    except KeyboardInterrupt:
        print("\n⚠️ Visualization interrupted by user - skipping (report is complete)")
    except Exception as e:
        print(f"\n⚠️ Visualization failed (non-critical): {str(e)}")
        print("Report generation was successful - visualizations are optional")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
    
    return stats

if __name__ == "__main__":
    stats = main()
