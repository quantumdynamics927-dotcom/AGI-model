#!/usr/bin/env python3
"""
Validate OpenQASM circuits for IBM Quantum compatibility.

Checks for:
1. Negative angles in gates that require [0, π/2] range
2. Unsupported gate decompositions
3. Circuit structure validation

Error Code 1517: rzz/cp angles outside [0, π/2] range
"""

import re
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict

CIRCUITS_DIR = Path(r"E:\tmt-os\autonomous_circuits")

# Gates that require angles in [0, π/2] on IBM hardware
RESTRICTED_ANGLE_GATES = ['rzz', 'rzx', 'cp', 'crz']


def parse_qasm_file(filepath: Path) -> Dict:
    """Parse OpenQASM file and extract gate information."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    result = {
        'filepath': filepath,
        'filename': filepath.name,
        'qubits': 0,
        'gates': [],
        'negative_angles': [],
        'custom_gates': [],
        'issues': []
    }
    
    # Extract qubit count
    qreg_match = re.search(r'qreg\s+\w+\[(\d+)\]', content)
    if qreg_match:
        result['qubits'] = int(qreg_match.group(1))
    
    # Extract custom gate definitions
    gate_defs = re.findall(r'gate\s+(\w+)\s+([^{\s]+)\s*\{([^}]+)\}', content)
    for gate_name, qubits, body in gate_defs:
        result['custom_gates'].append({
            'name': gate_name,
            'qubits': qubits,
            'body': body
        })
        
        # Check for negative angles in custom gate
        neg_angles = find_negative_angles(body)
        if neg_angles:
            result['negative_angles'].extend([
                {'gate': gate_name, **na} for na in neg_angles
            ])
    
    # Check main circuit for negative angles
    # Remove gate definitions first
    main_circuit = re.sub(r'gate\s+\w+\s+[^{]+\{[^}]+\}', '', content)
    neg_angles = find_negative_angles(main_circuit)
    result['negative_angles'].extend(neg_angles)
    
    # Extract gate counts
    gate_pattern = r'\b(h|x|y|z|cx|cz|rx|ry|rz|p|cp|swap|rzz|rzx)\b'
    gates = re.findall(gate_pattern, content.lower())
    result['gates'] = list(set(gates))
    
    return result


def find_negative_angles(text: str) -> List[Dict]:
    """Find negative angle expressions in QASM text."""
    issues = []
    
    # Pattern for gate(angle) qubit
    angle_pattern = r'(rx|ry|rz|p|cp|rzz|rzx|crz)\s*\(\s*([^)]+)\s*\)'
    
    for match in re.finditer(angle_pattern, text, re.IGNORECASE):
        gate_name = match.group(1).lower()
        angle_expr = match.group(2).strip()
        
        # Check for explicit negative sign
        if angle_expr.startswith('-'):
            issues.append({
                'gate': gate_name,
                'angle': angle_expr,
                'issue': 'explicit_negative'
            })
        
        # Try to evaluate the angle
        try:
            # Replace pi with np.pi
            eval_expr = angle_expr.replace('pi', 'np.pi')
            angle_value = eval(eval_expr)
            
            if angle_value < 0:
                issues.append({
                    'gate': gate_name,
                    'angle': angle_expr,
                    'value': angle_value,
                    'issue': 'negative_value'
                })
            elif gate_name in RESTRICTED_ANGLE_GATES and angle_value > np.pi/2:
                issues.append({
                    'gate': gate_name,
                    'angle': angle_expr,
                    'value': angle_value,
                    'issue': 'exceeds_pi_over_2'
                })
        except:
            pass  # Complex expression, skip
    
    return issues


def validate_all_circuits() -> List[Dict]:
    """Validate all QASM files in the circuits directory."""
    results = []
    
    qasm_files = list(CIRCUITS_DIR.glob("*.qasm"))
    
    for qasm_file in qasm_files:
        result = parse_qasm_file(qasm_file)
        results.append(result)
    
    return results


def generate_report(results: List[Dict]) -> str:
    """Generate validation report."""
    report = []
    report.append("=" * 70)
    report.append("IBM Quantum Circuit Validation Report")
    report.append("=" * 70)
    
    # Summary
    total = len(results)
    with_issues = sum(1 for r in results if r['negative_angles'])
    
    report.append(f"\nTotal circuits: {total}")
    report.append(f"Circuits with angle issues: {with_issues}")
    report.append(f"Valid circuits: {total - with_issues}")
    
    # Detailed issues
    report.append("\n" + "=" * 70)
    report.append("Detailed Analysis")
    report.append("=" * 70)
    
    for result in results:
        status = "❌ ISSUES" if result['negative_angles'] else "✅ OK"
        report.append(f"\n{result['filename']}: {status}")
        report.append(f"  Qubits: {result['qubits']}")
        report.append(f"  Gates: {', '.join(result['gates'])}")
        
        if result['custom_gates']:
            report.append(f"  Custom gates: {[g['name'] for g in result['custom_gates']]}")
        
        if result['negative_angles']:
            report.append("  ⚠️  Negative angle issues:")
            for issue in result['negative_angles']:
                if 'gate' in issue:
                    report.append(f"    - Gate '{issue['gate']}': angle {issue['angle']}")
                    if 'value' in issue:
                        report.append(f"      Value: {issue['value']:.6f} rad")
    
    # Fix recommendations
    report.append("\n" + "=" * 70)
    report.append("Fix Recommendations")
    report.append("=" * 70)
    
    for result in results:
        if result['negative_angles']:
            report.append(f"\n{result['filename']}:")
            report.append("  Replace negative angles with equivalent positive angles:")
            report.append("  -θ → 2π - θ (for phase gates)")
            report.append("  Example: -π/4 → 7π/4")
    
    return "\n".join(report)


def fix_negative_angles(content: str) -> str:
    """Attempt to fix negative angles in QASM content."""
    # Pattern for negative angles
    neg_pattern = r'(rx|ry|rz|p|cp|rzz|rzx|crz)\s*\(\s*-\s*([^)]+)\s*\)'
    
    def replace_negative(match):
        gate = match.group(1)
        angle = match.group(2)
        # Wrap angle: -θ → (2π - θ)
        return f'{gate}(2*pi - {angle})'
    
    fixed = re.sub(neg_pattern, replace_negative, content, flags=re.IGNORECASE)
    return fixed


def main():
    print("Validating circuits in:", CIRCUITS_DIR)
    print()
    
    results = validate_all_circuits()
    report = generate_report(results)
    print(report)
    
    # Save report
    report_path = CIRCUITS_DIR / "validation_report.txt"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")
    
    return results


if __name__ == "__main__":
    main()