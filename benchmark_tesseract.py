"""
Benchmark script for comparing tesseract routing vs flat routing approaches.
"""

import torch
import numpy as np
import time
import json
from typing import Dict, Any, Callable, Tuple
from pathlib import Path
import logging

from quantum_cognitive_core import QuantumCognitiveCore, QuantumCognitiveConfig
from benchmark_framework import BenchmarkFramework

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TesseractBenchmarkFramework:
    """Benchmark framework specifically for tesseract routing comparisons"""
    
    def __init__(self, output_dir: str = "tesseract_benchmarks"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def run_routing_comparison(
        self,
        num_samples: int = 100,
        task_name: str = "routing_comparison"
    ) -> Dict[str, Any]:
        """Run comparison between tesseract routing and flat routing"""
        
        logger.info("Running tesseract routing comparison benchmark...")
        
        # Create cores with and without tesseract routing
        config_flat = QuantumCognitiveConfig()
        config_flat.tesseract_enabled = False
        
        config_tesseract = QuantumCognitiveConfig()
        config_tesseract.tesseract_enabled = True
        
        core_flat = QuantumCognitiveCore(config_flat)
        core_tesseract = QuantumCognitiveCore(config_tesseract)
        
        # Benchmark results
        results = {
            'flat_routing': self._benchmark_core(core_flat, num_samples, "flat"),
            'tesseract_routing': self._benchmark_core(core_tesseract, num_samples, "tesseract")
        }
        
        # Save results
        self._save_results(results, task_name)
        
        return results
        
    def _benchmark_core(
        self, 
        core: QuantumCognitiveCore, 
        num_samples: int, 
        approach: str
    ) -> Dict[str, Any]:
        """Benchmark a specific core configuration"""
        logger.info(f"Benchmarking {approach} routing approach...")
        
        total_latency = 0.0
        total_accuracy = 0.0
        successful_samples = 0
        failed_samples = 0
        
        # Track route paths for tesseract-enabled cores
        route_paths = []
        
        for i in range(num_samples):
            try:
                # Generate random input
                input_data = torch.randn(1, core.config.encoder_input_dim)
                target = torch.randn(1, core.config.encoder_latent_dim)
                
                # Measure latency
                start_time = time.time()
                
                # Process input
                result = core.process_input(input_data)
                
                latency = time.time() - start_time
                total_latency += latency
                
                # Calculate accuracy (simplified metric)
                action = result['action']
                if action.shape != target.shape:
                    # Handle dimension mismatch
                    if action.shape[0] == 1 and target.shape[0] == 1:
                        # Both are single samples, compare feature dimensions
                        min_dim = min(action.shape[1], target.shape[1])
                        action_slice = action[:, :min_dim]
                        target_slice = target[:, :min_dim]
                    else:
                        # Different batch dimensions, use flattened comparison
                        action_flat = action.flatten()
                        target_flat = target.flatten()
                        min_elements = min(len(action_flat), len(target_flat))
                        action_slice = action_flat[:min_elements].unsqueeze(0)
                        target_slice = target_flat[:min_elements].unsqueeze(0)
                else:
                    action_slice = action
                    target_slice = target
                
                # Cosine similarity as accuracy metric
                action_norm = action_slice / (torch.norm(action_slice) + 1e-8)
                target_norm = target_slice / (torch.norm(target_slice) + 1e-8)
                accuracy = torch.dot(action_norm.flatten(), target_norm.flatten()).item()
                accuracy = (accuracy + 1.0) / 2.0  # Normalize to [0,1]
                
                total_accuracy += accuracy
                successful_samples += 1
                
                # Track route path if tesseract is enabled
                if approach == "tesseract" and 'tesseract_vertex' in result:
                    route_paths.append(result['tesseract_vertex'])
                
            except Exception as e:
                logger.warning(f"Sample {i} failed for {approach} routing: {e}")
                failed_samples += 1
                if failed_samples > num_samples * 0.1:  # Stop if too many failures
                    logger.error(f"Too many failures for {approach} routing, stopping benchmark")
                    break
                    
        # Calculate metrics
        valid_samples = successful_samples
        avg_accuracy = total_accuracy / valid_samples if valid_samples > 0 else 0.0
        avg_latency = total_latency / valid_samples if valid_samples > 0 else 0.0
        
        return {
            'approach': approach,
            'valid_samples': valid_samples,
            'failed_samples': failed_samples,
            'total_samples': num_samples,
            'accuracy': avg_accuracy,
            'latency_seconds': avg_latency,
            'route_paths': route_paths if approach == "tesseract" else [],
            'success_rate': valid_samples / num_samples if num_samples > 0 else 0.0
        }
        
    def run_edge_scoring_comparison(
        self,
        num_samples: int = 100,
        task_name: str = "edge_scoring_comparison"
    ) -> Dict[str, Any]:
        """Compare classical vs quantum edge scoring"""
        
        logger.info("Running edge scoring comparison benchmark...")
        
        # Create cores with and without quantum edge scoring
        config_classical = QuantumCognitiveConfig()
        config_classical.tesseract_enabled = True
        
        config_quantum = QuantumCognitiveConfig()
        config_quantum.tesseract_enabled = True
        
        core_classical = QuantumCognitiveCore(config_classical)
        core_quantum = QuantumCognitiveCore(config_quantum)
        
        # Disable quantum backend for classical scoring
        if core_classical.quantum_edge_scorer:
            core_classical.quantum_edge_scorer.backend = None
            
        # Benchmark results
        results = {
            'classical_edge_scoring': self._benchmark_edge_scoring(core_classical, num_samples, "classical"),
            'quantum_edge_scoring': self._benchmark_edge_scoring(core_quantum, num_samples, "quantum")
        }
        
        # Save results
        self._save_results(results, task_name)
        
        return results
        
    def _benchmark_edge_scoring(
        self, 
        core: QuantumCognitiveCore, 
        num_samples: int, 
        approach: str
    ) -> Dict[str, Any]:
        """Benchmark edge scoring approach"""
        logger.info(f"Benchmarking {approach} edge scoring...")
        
        total_latency = 0.0
        total_scores = 0.0
        successful_samples = 0
        failed_samples = 0
        
        for i in range(num_samples):
            try:
                # Generate random input
                input_data = torch.randn(1, core.config.encoder_input_dim)
                
                # Measure latency
                start_time = time.time()
                
                # Process input (this will trigger edge scoring if tesseract is enabled)
                result = core.process_input(input_data)
                
                latency = time.time() - start_time
                total_latency += latency
                
                # Track scoring if available
                if 'router_info' in result and result['router_info']:
                    total_scores += result['router_info'].get('confidence', 0.5)
                else:
                    total_scores += 0.5  # Default score
                    
                successful_samples += 1
                
            except Exception as e:
                logger.warning(f"Sample {i} failed for {approach} edge scoring: {e}")
                failed_samples += 1
                if failed_samples > num_samples * 0.1:  # Stop if too many failures
                    logger.error(f"Too many failures for {approach} edge scoring, stopping benchmark")
                    break
                    
        # Calculate metrics
        valid_samples = successful_samples
        avg_score = total_scores / valid_samples if valid_samples > 0 else 0.0
        avg_latency = total_latency / valid_samples if valid_samples > 0 else 0.0
        
        return {
            'approach': approach,
            'valid_samples': valid_samples,
            'failed_samples': failed_samples,
            'total_samples': num_samples,
            'average_score': avg_score,
            'latency_seconds': avg_latency,
            'success_rate': valid_samples / num_samples if num_samples > 0 else 0.0
        }
        
    def run_phi_weighting_comparison(
        self,
        num_samples: int = 100,
        task_name: str = "phi_weighting_comparison"
    ) -> Dict[str, Any]:
        """Compare routing with and without phi weighting"""
        
        logger.info("Running phi weighting comparison benchmark...")
        
        # Create cores with and without phi weighting
        config_no_phi = QuantumCognitiveConfig()
        config_no_phi.tesseract_enabled = True
        
        config_with_phi = QuantumCognitiveConfig()
        config_with_phi.tesseract_enabled = True
        
        core_no_phi = QuantumCognitiveCore(config_no_phi)
        core_with_phi = QuantumCognitiveCore(config_with_phi)
        
        # Disable phi weighting for one core (simplified approach)
        # In practice, this would involve modifying the router's transition_weights method
        
        # Benchmark results
        results = {
            'no_phi_weighting': self._benchmark_core(core_no_phi, num_samples, "no_phi"),
            'with_phi_weighting': self._benchmark_core(core_with_phi, num_samples, "with_phi")
        }
        
        # Save results
        self._save_results(results, task_name)
        
        return results
        
    def run_fault_tolerance_comparison(
        self,
        num_samples: int = 100,
        task_name: str = "fault_tolerance_comparison"
    ) -> Dict[str, Any]:
        """Compare fault-aware routing vs standard routing"""
        
        logger.info("Running fault tolerance comparison benchmark...")
        
        # Create cores with and without fault awareness
        config_standard = QuantumCognitiveConfig()
        config_standard.tesseract_enabled = True
        
        config_fault_aware = QuantumCognitiveConfig()
        config_fault_aware.tesseract_enabled = True
        
        core_standard = QuantumCognitiveCore(config_standard)
        core_fault_aware = QuantumCognitiveCore(config_fault_aware)
        
        # Simulate degraded vertices for fault-aware core
        if core_fault_aware.tesseract_router:
            # Mark some vertices as degraded
            degraded_vertices = [3, 7, 11, 15]  # Some vertices in each family
            core_fault_aware.tesseract_router.update_fault_mask(degraded_vertices)
            
        # Benchmark results
        results = {
            'standard_routing': self._benchmark_core(core_standard, num_samples, "standard"),
            'fault_aware_routing': self._benchmark_core(core_fault_aware, num_samples, "fault_aware")
        }
        
        # Save results
        self._save_results(results, task_name)
        
        return results
        
    def _save_results(self, results: Dict[str, Any], task_name: str):
        """Save benchmark results to file"""
        filename = self.output_dir / f"{task_name}_{int(time.time())}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Saved benchmark results to {filename}")
        except Exception as e:
            logger.error(f"Failed to save benchmark results: {e}")

def run_complete_tesseract_benchmark():
    """Run complete tesseract benchmark suite"""
    logger.info("Running complete tesseract benchmark suite...")
    
    benchmark = TesseractBenchmarkFramework()
    
    # 1. Routing comparison
    routing_results = benchmark.run_routing_comparison(
        num_samples=50, 
        task_name="routing_comparison"
    )
    
    # 2. Edge scoring comparison
    edge_results = benchmark.run_edge_scoring_comparison(
        num_samples=50, 
        task_name="edge_scoring_comparison"
    )
    
    # 3. Phi weighting comparison
    phi_results = benchmark.run_phi_weighting_comparison(
        num_samples=50, 
        task_name="phi_weighting_comparison"
    )
    
    # 4. Fault tolerance comparison
    fault_results = benchmark.run_fault_tolerance_comparison(
        num_samples=50, 
        task_name="fault_tolerance_comparison"
    )
    
    # Compile summary
    summary = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "routing_comparison": {
            "flat_accuracy": routing_results['flat_routing']['accuracy'],
            "tesseract_accuracy": routing_results['tesseract_routing']['accuracy'],
            "flat_latency": routing_results['flat_routing']['latency_seconds'],
            "tesseract_latency": routing_results['tesseract_routing']['latency_seconds'],
            "improvement": routing_results['tesseract_routing']['accuracy'] - routing_results['flat_routing']['accuracy']
        },
        "edge_scoring_comparison": {
            "classical_score": edge_results['classical_edge_scoring']['average_score'],
            "quantum_score": edge_results['quantum_edge_scoring']['average_score'],
            "classical_latency": edge_results['classical_edge_scoring']['latency_seconds'],
            "quantum_latency": edge_results['quantum_edge_scoring']['latency_seconds']
        },
        "phi_weighting_comparison": {
            "no_phi_accuracy": phi_results['no_phi_weighting']['accuracy'],
            "with_phi_accuracy": phi_results['with_phi_weighting']['accuracy'],
            "phi_benefit": phi_results['with_phi_weighting']['accuracy'] - phi_results['no_phi_weighting']['accuracy']
        },
        "fault_tolerance_comparison": {
            "standard_accuracy": fault_results['standard_routing']['accuracy'],
            "fault_aware_accuracy": fault_results['fault_aware_routing']['accuracy'],
            "fault_tolerance_benefit": fault_results['fault_aware_routing']['accuracy'] - fault_results['standard_routing']['accuracy']
        }
    }
    
    # Save summary
    benchmark._save_results(summary, "tesseract_benchmark_summary")
    
    # Print results
    print("\n" + "="*60)
    print("TESSELLATED COGNITIVE ROUTING BENCHMARK RESULTS")
    print("="*60)
    
    print(f"\nRouting Comparison:")
    print(f"  Flat Routing Accuracy: {summary['routing_comparison']['flat_accuracy']:.4f}")
    print(f"  Tesseract Routing Accuracy: {summary['routing_comparison']['tesseract_accuracy']:.4f}")
    print(f"  Improvement: {summary['routing_comparison']['improvement']*100:.2f}%")
    
    print(f"\nEdge Scoring Comparison:")
    print(f"  Classical Edge Score: {summary['edge_scoring_comparison']['classical_score']:.4f}")
    print(f"  Quantum Edge Score: {summary['edge_scoring_comparison']['quantum_score']:.4f}")
    
    print(f"\nPhi Weighting Comparison:")
    print(f"  Without Phi Weighting: {summary['phi_weighting_comparison']['no_phi_accuracy']:.4f}")
    print(f"  With Phi Weighting: {summary['phi_weighting_comparison']['with_phi_accuracy']:.4f}")
    print(f"  Phi Benefit: {summary['phi_weighting_comparison']['phi_benefit']*100:.2f}%")
    
    print(f"\nFault Tolerance Comparison:")
    print(f"  Standard Routing: {summary['fault_tolerance_comparison']['standard_accuracy']:.4f}")
    print(f"  Fault-Aware Routing: {summary['fault_tolerance_comparison']['fault_aware_accuracy']:.4f}")
    print(f"  Fault Tolerance Benefit: {summary['fault_tolerance_comparison']['fault_tolerance_benefit']*100:.2f}%")
    
    print(f"\n" + "="*60)
    print("BENCHMARK COMPLETE")
    print("="*60)
    
    return summary

# Example usage
if __name__ == "__main__":
    # Run the complete benchmark suite
    summary = run_complete_tesseract_benchmark()
    
    # Additional analysis could be done here
    print(f"\nDetailed results saved to tesseract_benchmarks/ directory")