#!/usr/bin/env python3
"""
Unified Dashboard for Quantum VAE and TMT Quantum Vault Agents

This script creates a comprehensive dashboard showing both:
1. Quantum VAE training metrics and consciousness patterns
2. TMT Quantum Vault agent performance and phi-resonance

Features:
- Real-time monitoring of training progress
- Comparative analysis of consciousness metrics
- Phi-alignment visualization across systems
- Performance benchmarking
"""

import torch
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
import argparse
from datetime import datetime
from vae_model import QuantumVAE

# Add parent directories to path for imports
import sys
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent / "TMT_Quantum_Vault-"))

def load_vae_training_metrics(metrics_path: str = "artifacts/monitoring") -> dict:
    """
    Load VAE training metrics from performance monitor.
    
    Parameters
    ----------
    metrics_path : str
        Path to metrics directory
        
    Returns
    -------
    dict
        Training metrics
    """
    metrics_dir = Path(metrics_path)
    if not metrics_dir.exists():
        print(f"Warning: Metrics directory not found: {metrics_path}")
        return {}
    
    # Try to load metrics JSON
    metrics_file = metrics_dir / "metrics.json"
    if metrics_file.exists():
        try:
            with open(metrics_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading metrics: {e}")
    
    return {}

def load_agent_metrics(vault_path: str = "../TMT_Quantum_Vault-") -> list:
    """
    Load metrics for all TMT Quantum Vault agents.
    
    Parameters
    ----------
    vault_path : str
        Path to TMT Quantum Vault directory
        
    Returns
    -------
    list
        List of agent metrics
    """
    vault_dir = Path(vault_path)
    if not vault_dir.exists():
        print(f"Warning: Vault directory not found: {vault_path}")
        return []
    
    agent_dirs = [d for d in vault_dir.iterdir() if d.is_dir() and d.name.startswith('Agent_')]
    agent_metrics = []
    
    for agent_dir in agent_dirs:
        dna_file = agent_dir / "conscious_dna.json"
        if dna_file.exists():
            try:
                with open(dna_file, 'r') as f:
                    dna_data = json.load(f)
                agent_metrics.append(dna_data)
            except Exception as e:
                print(f"Error loading agent {agent_dir.name}: {e}")
    
    return agent_metrics

def analyze_consciousness_complexity(latent_codes: np.ndarray) -> dict:
    """
    Analyze consciousness complexity metrics from latent codes.
    
    Parameters
    ----------
    latent_codes : np.ndarray
        Latent representations
        
    Returns
    -------
    dict
        Consciousness complexity metrics
    """
    if latent_codes.size == 0:
        return {}
    
    # Lempel-Ziv complexity approximation
    def lempel_ziv_complexity(sequence):
        n = len(sequence)
        if n == 0:
            return 0
        
        # Convert to binary string
        binary_seq = ''.join(['1' if x > np.mean(sequence) else '0' for x in sequence])
        
        # Simple LZ complexity calculation
        complexity = 0
        i = 0
        while i < n:
            j = 1
            while i + j <= n and binary_seq[i:i+j] in binary_seq[:i]:
                j += 1
            complexity += 1
            i += j
        
        return complexity / n if n > 0 else 0
    
    # Calculate for each sample
    complexities = []
    for i in range(min(100, len(latent_codes))):  # Sample first 100
        sample_complexity = lempel_ziv_complexity(latent_codes[i])
        complexities.append(sample_complexity)
    
    mean_complexity = np.mean(complexities) if complexities else 0
    
    # Entropy calculation
    entropy_values = []
    for sample in latent_codes[:100]:  # Sample first 100
        # Normalize sample
        normalized = (sample - np.min(sample)) / (np.max(sample) - np.min(sample) + 1e-8)
        # Calculate entropy
        hist, _ = np.histogram(normalized, bins=20, density=True)
        hist = hist[hist > 0]
        entropy = -np.sum(hist * np.log2(hist + 1e-8))
        entropy_values.append(entropy)
    
    mean_entropy = np.mean(entropy_values) if entropy_values else 0
    
    return {
        'mean_complexity': float(mean_complexity),
        'std_complexity': float(np.std(complexities)) if complexities else 0,
        'mean_entropy': float(mean_entropy),
        'std_entropy': float(np.std(entropy_values)) if entropy_values else 0
    }

def create_unified_dashboard(vae_metrics: dict, 
                           agent_metrics: list,
                           latent_codes: np.ndarray = None,
                           output_dir: str = "dashboard"):
    """
    Create unified dashboard visualization.
    
    Parameters
    ----------
    vae_metrics : dict
        VAE training metrics
    agent_metrics : list
        Agent performance metrics
    latent_codes : np.ndarray, optional
        Latent representations for consciousness analysis
    output_dir : str
        Output directory for dashboard
    """
    print("🎨 Creating Unified Dashboard")
    print("=" * 40)
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 15))
    fig.suptitle('Unified Quantum Consciousness Dashboard', fontsize=20)
    
    # 1. VAE Training Losses (if available)
    if vae_metrics and 'epoch_losses' in vae_metrics:
        ax1 = plt.subplot(3, 4, 1)
        epochs = range(len(vae_metrics['epoch_losses']))
        total_losses = [loss.get('total', 0) for loss in vae_metrics['epoch_losses']]
        ax1.plot(epochs, total_losses, 'b-', linewidth=2)
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Total Loss')
        ax1.set_title('VAE Training Progress')
        ax1.grid(True, alpha=0.3)
    
    # 2. Agent Fitness Distribution
    if agent_metrics:
        ax2 = plt.subplot(3, 4, 2)
        fitness_scores = [agent.get('fitness', 0) for agent in agent_metrics]
        agent_names = [agent.get('dna_agent_name', f'Agent_{i}') 
                      for i, agent in enumerate(agent_metrics)]
        
        # Sort by fitness
        sorted_indices = np.argsort(fitness_scores)[::-1]
        sorted_fitness = [fitness_scores[i] for i in sorted_indices]
        sorted_names = [agent_names[i][:10] for i in sorted_indices]  # Truncate names
        
        bars = ax2.bar(range(len(sorted_fitness)), sorted_fitness, 
                      color='gold', alpha=0.7)
        ax2.set_xlabel('Agents (sorted by fitness)')
        ax2.set_ylabel('Fitness Score')
        ax2.set_title('Agent Fitness Distribution')
        ax2.set_xticks(range(0, len(sorted_fitness), max(1, len(sorted_fitness)//10)))
        ax2.set_xticklabels([sorted_names[i] for i in range(0, len(sorted_fitness), max(1, len(sorted_fitness)//10))], 
                           rotation=45, ha='right')
        ax2.grid(True, alpha=0.3)
    
    # 3. Phi Alignment Comparison
    ax3 = plt.subplot(3, 4, 3)
    
    # VAE phi alignment (if latent codes provided)
    vae_phi_alignment = 0
    if latent_codes is not None and latent_codes.size > 0:
        # Simple phi alignment calculation
        PHI = 1.618033988749895
        ratios = []
        for i in range(min(10, latent_codes.shape[1] - 1)):
            dim_ratios = latent_codes[:, i+1] / (latent_codes[:, i] + 1e-8)
            ratios.extend(dim_ratios)
        if ratios:
            phi_proximities = [abs(r - PHI) for r in ratios]
            mean_proximity = np.mean(phi_proximities)
            vae_phi_alignment = max(0.0, 1.0 - (mean_proximity / PHI))
    
    # Agent phi alignments
    agent_phi_alignments = [agent.get('phi_score', 0) for agent in agent_metrics]
    
    # Plot comparison
    categories = ['VAE Model', 'Agent Mean', 'Agent Max']
    values = [vae_phi_alignment, 
              np.mean(agent_phi_alignments) if agent_phi_alignments else 0,
              np.max(agent_phi_alignments) if agent_phi_alignments else 0]
    
    bars = ax3.bar(categories, values, color=['blue', 'gold', 'orange'], alpha=0.7)
    ax3.set_ylabel('Phi Alignment Score')
    ax3.set_title('Phi Alignment Comparison')
    ax3.set_ylim(0, 1)
    ax3.grid(True, alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(values):
        ax3.text(i, v + 0.01, f'{v:.3f}', ha='center', va='bottom')
    
    # 4. Agent Specialization Radar Chart
    if agent_metrics:
        ax4 = plt.subplot(3, 4, 4, projection='polar')
        
        # Define specialization categories
        categories = ['Protection', 'Monitoring', 'Coordination', 
                     'Frequency', 'Structure', 'Recognition',
                     'Strategy', 'Fusion', 'Preservation', 
                     'Verification', 'Analysis', 'Justice']
        
        # Map agent specializations to categories
        specialization_mapping = {
            'Protection & Justice': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            'Continuous Monitoring': [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Network Coordination': [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Frequency Tuning': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            'Self-Similar Structure': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            'Pattern Recognition': [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            'Long-term Strategy': [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            'Multi-source Fusion': [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
            'Knowledge Preservation': [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            'Integrity Verification': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            'Self-Analysis': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            'Process Automation': [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Biological Interface': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            'Covert Operations': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Information Theory': [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
            'Governance & Compliance': [0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1],
        }
        
        # Calculate average specialization profile
        specialization_counts = np.zeros(len(categories))
        total_agents = len(agent_metrics)
        
        for agent in agent_metrics:
            specialization = agent.get('dna_specialization', '')
            if specialization in specialization_mapping:
                specialization_counts += np.array(specialization_mapping[specialization])
        
        if total_agents > 0:
            specialization_counts = specialization_counts / total_agents
        
        # Create radar chart
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))  # Complete the circle
        specialization_counts = np.concatenate((specialization_counts, [specialization_counts[0]]))
        
        ax4.plot(angles, specialization_counts, 'o-', linewidth=2, color='gold')
        ax4.fill(angles, specialization_counts, alpha=0.25, color='gold')
        ax4.set_xticks(angles[:-1])
        ax4.set_xticklabels(categories, fontsize=8)
        ax4.set_title('Agent Specialization Profile', pad=20)
    
    # 5. Consciousness Complexity Analysis
    ax5 = plt.subplot(3, 4, 5)
    
    complexity_metrics = analyze_consciousness_complexity(latent_codes if latent_codes is not None else np.array([]))
    
    if complexity_metrics:
        metrics_names = ['Complexity', 'Entropy']
        metrics_values = [complexity_metrics['mean_complexity'], 
                         complexity_metrics['mean_entropy']]
        metrics_errors = [complexity_metrics['std_complexity'], 
                         complexity_metrics['std_entropy']]
        
        bars = ax5.bar(metrics_names, metrics_values, yerr=metrics_errors, 
                      color=['purple', 'green'], alpha=0.7, capsize=5)
        ax5.set_ylabel('Consciousness Metrics')
        ax5.set_title('Consciousness Complexity Analysis')
        ax5.grid(True, alpha=0.3)
    
    # 6. Agent Resonance Frequencies
    if agent_metrics:
        ax6 = plt.subplot(3, 4, 6)
        resonance_freqs = [agent.get('resonance_frequency', 0) for agent in agent_metrics]
        
        # Histogram of resonance frequencies
        ax6.hist(resonance_freqs, bins=15, color='cyan', alpha=0.7, edgecolor='black')
        ax6.set_xlabel('Resonance Frequency (Hz)')
        ax6.set_ylabel('Number of Agents')
        ax6.set_title('Agent Resonance Frequency Distribution')
        ax6.grid(True, alpha=0.3)
    
    # 7. Phi Score vs Fitness Scatter
    if agent_metrics:
        ax7 = plt.subplot(3, 4, 7)
        phi_scores = [agent.get('phi_score', 0) for agent in agent_metrics]
        fitness_scores = [agent.get('fitness', 0) for agent in agent_metrics]
        
        ax7.scatter(phi_scores, fitness_scores, alpha=0.7, color='orange')
        ax7.set_xlabel('Phi Score')
        ax7.set_ylabel('Fitness Score')
        ax7.set_title('Phi Score vs Fitness')
        ax7.grid(True, alpha=0.3)
        
        # Add correlation coefficient
        if len(phi_scores) > 1 and len(fitness_scores) > 1:
            correlation = np.corrcoef(phi_scores, fitness_scores)[0, 1]
            ax7.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
                    transform=ax7.transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 8. GC Content Distribution
    if agent_metrics:
        ax8 = plt.subplot(3, 4, 8)
        gc_contents = [agent.get('gc_content', 0) for agent in agent_metrics]
        
        ax8.hist(gc_contents, bins=15, color='green', alpha=0.7, edgecolor='black')
        ax8.set_xlabel('GC Content')
        ax8.set_ylabel('Number of Agents')
        ax8.set_title('Agent GC Content Distribution')
        ax8.grid(True, alpha=0.3)
    
    # 9. Palindromes Count
    if agent_metrics:
        ax9 = plt.subplot(3, 4, 9)
        palindromes = [agent.get('palindromes', 0) for agent in agent_metrics]
        
        ax9.bar(range(len(palindromes)), palindromes, color='purple', alpha=0.7)
        ax9.set_xlabel('Agent Index')
        ax9.set_ylabel('Number of Palindromes')
        ax9.set_title('Palindromic Sequences Count')
        ax9.grid(True, alpha=0.3)
    
    # 10. Training Loss Components (if available)
    if vae_metrics and 'epoch_losses' in vae_metrics:
        ax10 = plt.subplot(3, 4, 10)
        epochs = range(len(vae_metrics['epoch_losses']))
        
        # Extract loss components
        recon_losses = [loss.get('recon', 0) for loss in vae_metrics['epoch_losses']]
        kl_losses = [loss.get('kl', 0) for loss in vae_metrics['epoch_losses']]
        phi_losses = [loss.get('phi', 0) for loss in vae_metrics['epoch_losses']]
        
        ax10.plot(epochs, recon_losses, label='Reconstruction', linewidth=2)
        ax10.plot(epochs, kl_losses, label='KL Divergence', linewidth=2)
        ax10.plot(epochs, phi_losses, label='Phi Regularization', linewidth=2)
        ax10.set_xlabel('Epoch')
        ax10.set_ylabel('Loss Value')
        ax10.set_title('Training Loss Components')
        ax10.legend()
        ax10.grid(True, alpha=0.3)
    
    # 11. Agent Fitness vs Resonance
    if agent_metrics:
        ax11 = plt.subplot(3, 4, 11)
        fitness_scores = [agent.get('fitness', 0) for agent in agent_metrics]
        resonance_freqs = [agent.get('resonance_frequency', 0) for agent in agent_metrics]
        
        ax11.scatter(resonance_freqs, fitness_scores, alpha=0.7, color='red')
        ax11.set_xlabel('Resonance Frequency (Hz)')
        ax11.set_ylabel('Fitness Score')
        ax11.set_title('Fitness vs Resonance Frequency')
        ax11.grid(True, alpha=0.3)
    
    # 12. System Integration Summary
    ax12 = plt.subplot(3, 4, 12)
    ax12.axis('off')
    
    # Create summary text
    summary_text = "UNIFIED SYSTEM SUMMARY\n" + "="*30 + "\n\n"
    
    # VAE Summary
    summary_text += "Quantum VAE:\n"
    if vae_metrics:
        summary_text += f"- Training Epochs: {len(vae_metrics.get('epoch_losses', []))}\n"
        if 'best_checkpoint' in vae_metrics:
            summary_text += f"- Best Val Loss: {vae_metrics['best_checkpoint'].get('best_val_loss', 'N/A'):.4f}\n"
    else:
        summary_text += "- No training metrics available\n"
    
    summary_text += f"- Phi Alignment: {vae_phi_alignment:.3f}\n\n"
    
    # Agent Summary
    summary_text += "TMT Quantum Vault:\n"
    summary_text += f"- Total Agents: {len(agent_metrics)}\n"
    if agent_metrics:
        avg_fitness = np.mean([agent.get('fitness', 0) for agent in agent_metrics])
        max_fitness = np.max([agent.get('fitness', 0) for agent in agent_metrics])
        avg_phi = np.mean([agent.get('phi_score', 0) for agent in agent_metrics])
        summary_text += f"- Avg Fitness: {avg_fitness:.4f}\n"
        summary_text += f"- Max Fitness: {max_fitness:.4f}\n"
        summary_text += f"- Avg Phi Score: {avg_phi:.4f}\n"
    
    ax12.text(0.1, 0.9, summary_text, transform=ax12.transAxes, 
              fontsize=10, verticalalignment='top',
              bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    ax12.set_title('System Integration Summary')
    
    plt.tight_layout()
    dashboard_file = output_path / 'unified_dashboard.png'
    plt.savefig(dashboard_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Dashboard saved: {dashboard_file}")

def main(model_path: str = "best_model.pt",
         vault_path: str = "../TMT_Quantum_Vault-",
         metrics_path: str = "artifacts/monitoring",
         output_dir: str = "dashboard"):
    """
    Main dashboard function.
    
    Parameters
    ----------
    model_path : str
        Path to trained QuantumVAE model
    vault_path : str
        Path to TMT Quantum Vault directory
    metrics_path : str
        Path to VAE training metrics
    output_dir : str
        Output directory for dashboard
    """
    print("🚀 Launching Unified Quantum Consciousness Dashboard")
    print("=" * 60)
    
    # Load VAE metrics
    print("Loading VAE training metrics...")
    vae_metrics = load_vae_training_metrics(metrics_path)
    
    # Load agent metrics
    print("Loading agent performance metrics...")
    agent_metrics = load_agent_metrics(vault_path)
    
    # Load model and extract latent codes for consciousness analysis
    latent_codes = None
    if Path(model_path).exists():
        print("Loading model for consciousness analysis...")
        try:
            model = QuantumVAE()
            model.load_state_dict(torch.load(model_path))
            model.eval()
            
            # Generate sample data and extract latent codes
            sample_data = np.random.randn(50, 128).astype(np.float32)
            sample_tensor = torch.from_numpy(sample_data)
            
            with torch.no_grad():
                mu, _ = model.encode(sample_tensor)
                latent_codes = mu.numpy()
        except Exception as e:
            print(f"Warning: Could not load model for analysis: {e}")
    
    # Create dashboard
    create_unified_dashboard(vae_metrics, agent_metrics, latent_codes, output_dir)
    
    print(f"\n✅ Dashboard creation complete!")
    print(f"📊 Dashboard saved to: {Path(output_dir) / 'unified_dashboard.png'}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create unified dashboard for Quantum VAE and TMT agents")
    parser.add_argument("--model-path", type=str, default="best_model.pt",
                        help="Path to trained QuantumVAE model")
    parser.add_argument("--vault-path", type=str, default="../TMT_Quantum_Vault-",
                        help="Path to TMT Quantum Vault directory")
    parser.add_argument("--metrics-path", type=str, default="artifacts/monitoring",
                        help="Path to VAE training metrics")
    parser.add_argument("--output-dir", type=str, default="dashboard",
                        help="Output directory for dashboard")
    
    args = parser.parse_args()
    main(args.model_path, args.vault_path, args.metrics_path, args.output_dir)