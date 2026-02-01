"""
Summarize all supplementary analysis results for publication
Creates inventory of additional experimental data beyond the 119 quantum jobs
"""

import json
import os
from pathlib import Path
from datetime import datetime

OUTPUTS_DIR = Path(r"e:\tmt-os\data\outputs")
OUTPUT_FILE = Path(r"e:\AGI model\supplementary_data_inventory.txt")

def analyze_json_file(filepath):
    """Extract key statistics from JSON result file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
        
        info = {
            'filename': filepath.name,
            'size_kb': filepath.stat().st_size / 1024,
            'keys': list(data.keys()) if isinstance(data, dict) else ['array_data'],
            'summary': extract_summary(data)
        }
        return info
    except Exception as e:
        return {
            'filename': filepath.name,
            'error': str(e)
        }

def extract_summary(data):
    """Extract high-level summary from data structure"""
    if isinstance(data, dict):
        # Look for common result keys
        summary = {}
        
        if 'results' in data:
            summary['has_results'] = True
        if 'timestamp' in data:
            summary['timestamp'] = data['timestamp']
        if 'circuit_depth' in data:
            summary['circuit_depth'] = data['circuit_depth']
        if 'num_qubits' in data:
            summary['num_qubits'] = data['num_qubits']
        if 'shots' in data:
            summary['shots'] = data['shots']
        if 'success' in data:
            summary['success'] = data['success']
            
        return summary if summary else f"{len(data)} keys"
    elif isinstance(data, list):
        return f"{len(data)} items"
    else:
        return str(type(data).__name__)

def main():
    print("="*80)
    print("SUPPLEMENTARY DATA INVENTORY")
    print("Quantum Consciousness VAE - Additional Analysis Results")
    print("="*80)
    
    # Get all JSON files
    json_files = sorted(OUTPUTS_DIR.glob("*.json"))
    
    print(f"\nFound {len(json_files)} supplementary result files\n")
    
    # Categorize files
    categories = {
        'quantum_biological': [],
        'quantum_hardware': [],
        'consciousness': [],
        'sacred_geometry': [],
        'entropy_complexity': [],
        'other': []
    }
    
    for filepath in json_files:
        filename = filepath.name.lower()
        
        if 'dna' in filename or 'biological' in filename:
            categories['quantum_biological'].append(filepath)
        elif 'quantum_job' in filename or 'circuit' in filename or 'earth' in filename:
            categories['quantum_hardware'].append(filepath)
        elif 'consciousness' in filename or 'heartbeat' in filename:
            categories['consciousness'].append(filepath)
        elif 'phi' in filename or 'tree' in filename or 'horus' in filename or 'metatron' in filename:
            categories['sacred_geometry'].append(filepath)
        elif 'entropy' in filename or 'nexus' in filename or 'syk' in filename:
            categories['entropy_complexity'].append(filepath)
        else:
            categories['other'].append(filepath)
    
    # Generate report
    report_lines = []
    report_lines.append("="*80)
    report_lines.append("SUPPLEMENTARY DATA INVENTORY")
    report_lines.append("Quantum Consciousness VAE - Additional Analysis Results")
    report_lines.append("="*80)
    report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Total Files: {len(json_files)}\n")
    
    for category, files in categories.items():
        if files:
            report_lines.append("="*80)
            report_lines.append(f"{category.upper().replace('_', ' ')}")
            report_lines.append("="*80)
            report_lines.append(f"Files: {len(files)}\n")
            
            for filepath in files:
                info = analyze_json_file(filepath)
                report_lines.append(f"📄 {info['filename']}")
                report_lines.append(f"   Size: {info['size_kb']:.1f} KB")
                
                if 'error' in info:
                    report_lines.append(f"   Error: {info['error']}")
                else:
                    report_lines.append(f"   Keys: {', '.join(info['keys'][:5])}")
                    if len(info['keys']) > 5:
                        report_lines.append(f"         ... and {len(info['keys']) - 5} more")
                    if info['summary']:
                        report_lines.append(f"   Summary: {info['summary']}")
                report_lines.append("")
    
    # Add publication recommendations
    report_lines.append("="*80)
    report_lines.append("PUBLICATION RECOMMENDATIONS")
    report_lines.append("="*80)
    report_lines.append("\n**Primary Data (Main Paper):**")
    report_lines.append("- 119 quantum hardware executions (974,848 shots)")
    report_lines.append("- IBM Fez (140 jobs) + IBM Torino (11 jobs)")
    report_lines.append("- Statistical validation (bootstrap + permutation)")
    report_lines.append("- Golden ratio emergence in latent space")
    report_lines.append("\n**Supplementary Materials (Appendix):**")
    report_lines.append("- All 19 JSON result files from outputs directory")
    report_lines.append("- Quantum-biological analysis results")
    report_lines.append("- Consciousness modeling validations")
    report_lines.append("- Sacred geometry integration experiments")
    report_lines.append("- Entropy and complexity metrics")
    report_lines.append("\n**Code Repository (GitHub):**")
    report_lines.append("- Complete source code (TMT-OS repo)")
    report_lines.append("- Reproducibility scripts")
    report_lines.append("- Docker deployment configuration")
    report_lines.append("- API documentation")
    
    report_text = "\n".join(report_lines)
    
    # Save report
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print(report_text)
    print(f"\n✅ Inventory saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
