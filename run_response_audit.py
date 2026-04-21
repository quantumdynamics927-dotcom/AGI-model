#!/usr/bin/env python3
"""
Run Response Path Audit

Script to run the controlled ablation study for quantum/tesseract routing.
This implements the three-condition experiment:
- C0: classical_baseline
- C1: tesseract_classical
- C2: tesseract_quantum

Usage:
    python run_response_audit.py [--config CONFIG] [--prompts N] [--repeats N]
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

from response_path_audit import ResponsePathAuditor


def main():
    parser = argparse.ArgumentParser(
        description="Run Response Path Audit and Ablation Study"
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='response_audit_results',
        help='Directory for audit results (default: response_audit_results)'
    )
    parser.add_argument(
        '--model-id',
        type=str,
        default='quantum_vae_v1',
        help='Model identifier for logging'
    )
    parser.add_argument(
        '--temperature',
        type=float,
        default=0.7,
        help='Generation temperature (keep constant across conditions)'
    )
    parser.add_argument(
        '--num-prompts',
        type=int,
        default=50,
        help='Number of prompts to use (default: 50, use all)'
    )
    parser.add_argument(
        '--num-repeats',
        type=int,
        default=3,
        help='Number of repeated runs per prompt per config (default: 3)'
    )
    parser.add_argument(
        '--configs',
        type=str,
        nargs='+',
        default=['C0', 'C1', 'C2'],
        choices=['C0', 'C1', 'C2'],
        help='Configurations to run (default: all)'
    )
    parser.add_argument(
        '--prompt-classes',
        type=str,
        nargs='+',
        default=None,
        choices=['ambiguous', 'tool_use', 'fault_tolerance', 'memory_governance', 'factual_control'],
        help='Specific prompt classes to test (default: all)'
    )
    parser.add_argument(
        '--seeds',
        type=int,
        nargs='+',
        default=[42, 123, 456, 789, 1024],
        help='Random seeds for reproducibility (default: 42, 123, 456, 789, 1024)'
    )
    parser.add_argument(
        '--skip-existing',
        action='store_true',
        help='Skip if results already exist'
    )
    
    args = parser.parse_args()
    
    # Check if results already exist
    output_dir = Path(args.output_dir)
    if args.skip_existing and output_dir.exists():
        results_file = output_dir / "audit_summary.json"
        if results_file.exists():
            print(f"Results already exist at {output_dir}")
            print("Use --force to overwrite")
            return 0
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Save run configuration
    run_config = {
        'timestamp': datetime.now().isoformat(),
        'model_id': args.model_id,
        'temperature': args.temperature,
        'num_prompts': args.num_prompts,
        'num_repeats': args.num_repeats,
        'configs': args.configs,
        'prompt_classes': args.prompt_classes,
        'seeds': args.seeds
    }
    
    with open(output_dir / "run_config.json", 'w') as f:
        json.dump(run_config, f, indent=2)
    
    print("=" * 80)
    print("RESPONSE PATH AUDIT - CONTROLLED ABLATION STUDY")
    print("=" * 80)
    print()
    print(f"Model: {args.model_id}")
    print(f"Temperature: {args.temperature}")
    print(f"Configurations: {', '.join(args.configs)}")
    print(f"Repeats per prompt: {args.num_repeats}")
    print(f"Seeds: {args.seeds}")
    print()
    
    # Create auditor
    auditor = ResponsePathAuditor(
        output_dir=args.output_dir,
        model_id=args.model_id,
        temperature=args.temperature,
        seeds=args.seeds
    )
    
    # Filter prompts by class if specified
    prompt_ids = None
    if args.prompt_classes:
        prompt_ids = [
            p.prompt_id for p in auditor.prompts
            if p.prompt_class in args.prompt_classes
        ]
    
    # Limit number of prompts
    if prompt_ids is None:
        prompt_ids = [p.prompt_id for p in auditor.prompts[:args.num_prompts]]
    else:
        prompt_ids = prompt_ids[:args.num_prompts]
    
    print(f"Total prompts: {len(prompt_ids)}")
    print(f"Prompt classes: {set(p.prompt_class for p in auditor.prompts if p.prompt_id in prompt_ids)}")
    print()
    
    # Run audit
    print("Starting audit...")
    print("-" * 80)
    
    summary = auditor.run_audit(
        prompt_ids=prompt_ids,
        configs=args.configs,
        num_repeats=args.num_repeats
    )
    
    # Generate report
    print()
    print("-" * 80)
    print("Generating report...")
    report = auditor.generate_report()
    
    # Save report
    report_file = output_dir / "audit_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print()
    print("=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)
    print()
    print(f"Results saved to: {output_dir}")
    print(f"Report saved to: {report_file}")
    print()
    
    # Print summary
    print("SUMMARY")
    print("-" * 40)
    for config_id in args.configs:
        if config_id in summary['by_config']:
            stats = summary['by_config'][config_id]
            print(f"\n{config_id}:")
            print(f"  Mean Judge Score: {stats['mean_judge_score']:.4f} ± {stats['std_judge_score']:.4f}")
            print(f"  Task Success Rate: {stats['task_success_rate']:.2%}")
            print(f"  Mean Route Length: {stats['mean_route_length']:.2f}")
            print(f"  Mean Latency: {stats['mean_latency_ms']:.2f} ms")
    
    print()
    print("PAIRWISE COMPARISONS")
    print("-" * 40)
    for comp_name, comp_data in summary['pairwise_comparisons'].items():
        print(f"\n{comp_name}:")
        print(f"  Judge Score Diff: {comp_data['judge_score_diff']:+.4f}")
        print(f"  Route Length Diff: {comp_data['route_length_diff']:+.2f}")
        print(f"  Success Rate Diff: {comp_data['success_rate_diff']:+.2%}")
    
    print()
    print("=" * 80)
    
    # Analyze route differences
    print("\nROUTE DIVERGENCE ANALYSIS")
    print("-" * 40)
    route_analysis = auditor.analyze_route_differences()
    print(f"Total divergences: {len(route_analysis['route_divergences'])}")
    
    if route_analysis['route_divergences']:
        print("\nSample divergences:")
        for div in route_analysis['route_divergences'][:3]:
            print(f"  Prompt {div['prompt_id']} ({div['config_comparison']}):")
            print(f"    Divergence at step {div['divergence_point']}")
            print(f"    Judge Score Diff: {div['judge_score_diff']:+.4f}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())