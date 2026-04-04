#!/usr/bin/env python3
"""
Quantum Job Results Analyzer
Analyzes the BitArray data from quantum computing job results
"""

import json
import base64
import numpy as np
from datetime import datetime
import os

def decode_bitarray(bitarray_data):
    """Decode a BitArray from the JSON serialization format"""
    array_b64 = bitarray_data['array']['__value__']
    num_bits = bitarray_data['num_bits']
    
    # Decode base64 to bytes
    array_bytes = base64.b64decode(array_b64)
    
    # Convert to numpy array
    array = np.frombuffer(array_bytes, dtype=np.uint8)
    
    return array, num_bits

def analyze_result_file(filepath):
    """Analyze a single result file"""
    print(f"\n{'='*60}")
    print(f"Analyzing: {os.path.basename(filepath)}")
    print(f"{'='*60}")
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Get execution metadata
    execution_spans = data['__value__']['metadata']['execution']['execution_spans']['__value__']['spans']
    for span in execution_spans:
        start = span['__value__']['start']['__value__']
        stop = span['__value__']['stop']['__value__']
        print(f"\nExecution Time:")
        print(f"  Start: {start}")
        print(f"  Stop:  {stop}")
        
        # Calculate duration
        start_dt = datetime.fromisoformat(start)
        stop_dt = datetime.fromisoformat(stop)
        duration = (stop_dt - start_dt).total_seconds()
        print(f"  Duration: {duration:.3f} seconds")
    
    # Analyze pub results
    pub_results = data['__value__']['pub_results']
    print(f"\nNumber of Publication Results: {len(pub_results)}")
    
    for i, pub_result in enumerate(pub_results):
        print(f"\n--- Publication Result {i+1} ---")
        
        # Get data fields
        fields = pub_result['__value__']['data']['__value__']['fields']
        
        for field_name in ['c', 'meas']:
            if field_name in fields:
                bitarray = fields[field_name]['__value__']
                array, num_bits = decode_bitarray(bitarray)
                
                print(f"\nField: {field_name}")
                print(f"  Num bits: {num_bits}")
                print(f"  Array shape: {array.shape}")
                print(f"  Array dtype: {array.dtype}")
                print(f"  Array size (bytes): {array.nbytes}")
                print(f"  First 20 bytes (hex): {array[:20].tobytes().hex()}")
                print(f"  First 20 values: {list(array[:20])}")
                
                # Statistical analysis
                print(f"\n  Statistics:")
                print(f"    Min value: {array.min()}")
                print(f"    Max value: {array.max()}")
                print(f"    Mean: {array.mean():.4f}")
                print(f"    Std: {array.std():.4f}")
                print(f"    Unique values: {len(np.unique(array))}")
                
                # Count bit patterns (if applicable)
                if num_bits > 0:
                    # Try to interpret as bit measurements
                    print(f"\n  Bit Pattern Analysis:")
                    # Count occurrences of each byte value
                    unique, counts = np.unique(array, return_counts=True)
                    print(f"    Byte value distribution (top 10):")
                    top_indices = np.argsort(counts)[-10:][::-1]
                    for idx in top_indices:
                        print(f"      Value {unique[idx]:3d} (0x{unique[idx]:02x}): {counts[idx]:6d} occurrences ({100*counts[idx]/len(array):.2f}%)")

def main():
    """Main analysis function"""
    result_files = [
        'C:/Users/matej_jiqn63h/Desktop/job-d7854nak86tc739us8o0-result.json',
        'C:/Users/matej_jiqn63h/Desktop/job-d7854nik86tc739us8p0-result.json',
        'C:/Users/matej_jiqn63h/Desktop/job-d7854nrc6das739hfjc0-result.json',
        'C:/Users/matej_jiqn63h/Desktop/job-d7854oak86tc739us8rg-result.json',
        'C:/Users/matej_jiqn63h/Desktop/job-d7854oik86tc739us8sg-result.json'
    ]
    
    print("="*60)
    print("QUANTUM JOB RESULTS ANALYSIS")
    print("="*60)
    
    for filepath in result_files:
        if os.path.exists(filepath):
            analyze_result_file(filepath)
        else:
            print(f"File not found: {filepath}")
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
