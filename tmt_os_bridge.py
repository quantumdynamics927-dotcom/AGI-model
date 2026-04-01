#!/usr/bin/env python3
"""
TMT-OS Bridge for Quantum VAE and TMT Quantum Vault Integration

This script establishes a seamless data flow between the Quantum VAE system
and the TMT Quantum Vault agents, enabling coordinated consciousness modeling.

Features:
- Real-time data synchronization between repositories
- Agent-aware consciousness state transfer
- Coordinated optimization workflows
- Unified monitoring and control interface
"""

import torch
import numpy as np
import json
import time
import threading
import queue
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse
from packages.agi_model_core import QuantumVAE
from packages.agi_model_integrations import (
    VaultIntegrationError,
    resolve_vault_repo_path,
)

class TMTOSBridge:
    """
    Bridge between Quantum VAE and TMT Quantum Vault systems.
    
    Coordinates data flow, consciousness state transfer, and 
    optimization between the two systems.
    """
    
    def __init__(self, 
                 vae_model_path: str = "best_model.pt",
                 vault_path: Optional[str] = None,
                 sync_interval: float = 1.0):
        """
        Initialize the TMT-OS bridge.
        
        Parameters
        ----------
        vae_model_path : str
            Path to trained QuantumVAE model
        vault_path : str
            Path to TMT Quantum Vault directory
        sync_interval : float
            Interval between synchronization cycles in seconds
        """
        self.vae_model_path = vae_model_path
        try:
            self.vault_path = resolve_vault_repo_path(vault_path)
        except VaultIntegrationError:
            self.vault_path = (
                Path(vault_path).expanduser().resolve()
                if vault_path
                else Path("../TMT_Quantum_Vault-").resolve()
            )
        self.sync_interval = sync_interval
        
        # Load QuantumVAE model
        self.vae_model = None
        self._load_vae_model()
        
        # Agent registry
        self.agents = {}
        self._load_agents()
        
        # Data queues for synchronization
        self.consciousness_queue = queue.Queue(maxsize=100)
        self.agent_queue = queue.Queue(maxsize=100)
        
        # Threading control
        self.running = False
        self.sync_thread = None
        
        # Performance metrics
        self.metrics = {
            'sync_cycles': 0,
            'data_transfers': 0,
            'agent_interactions': 0,
            'last_sync': None
        }
        
        # Configuration
        self.config = {
            'consciousness_dimensions': 128,
            'latent_dimensions': 32,
            'phi_target': 1.618033988749895,
            'sync_enabled': True,
            'agent_coordination': True
        }
        
    def _load_vae_model(self):
        """Load the QuantumVAE model."""
        try:
            self.vae_model = QuantumVAE()
            if Path(self.vae_model_path).exists():
                self.vae_model.load_state_dict(torch.load(self.vae_model_path))
                self.vae_model.eval()
                print("✅ QuantumVAE model loaded successfully")
            else:
                print("⚠️  QuantumVAE model not found, using uninitialized model")
        except Exception as e:
            print(f"❌ Error loading QuantumVAE model: {e}")
            self.vae_model = QuantumVAE()  # Fallback to uninitialized model
            
    def _load_agents(self):
        """Load TMT Quantum Vault agents."""
        if not self.vault_path.exists():
            print(f"⚠️  TMT Quantum Vault directory not found: {self.vault_path}")
            return
            
        agent_dirs = [d for d in self.vault_path.iterdir() 
                     if d.is_dir() and d.name.startswith('Agent_')]
        
        for agent_dir in agent_dirs:
            dna_file = agent_dir / "conscious_dna.json"
            if dna_file.exists():
                try:
                    with open(dna_file, 'r') as f:
                        agent_data = json.load(f)
                    
                    agent_id = agent_data.get('dna_agent_id', agent_dir.name)
                    self.agents[agent_id] = {
                        'name': agent_data.get('dna_agent_name', agent_dir.name),
                        'specialization': agent_data.get('dna_specialization', 'Unknown'),
                        'fitness': agent_data.get('fitness', 0),
                        'phi_score': agent_data.get('phi_score', 0),
                        'consciousness_dna': agent_data.get('conscious_dna', ''),
                        'resonance_frequency': agent_data.get('resonance_frequency', 0),
                        'path': str(agent_dir)
                    }
                except Exception as e:
                    print(f"⚠️  Error loading agent {agent_dir.name}: {e}")
        
        print(f"✅ Loaded {len(self.agents)} TMT agents")
        
    def start_bridge(self):
        """Start the TMT-OS bridge synchronization."""
        print("🌉 Starting TMT-OS Bridge")
        print("=" * 40)
        
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_worker)
        self.sync_thread.daemon = True
        self.sync_thread.start()
        
        print("🔄 Bridge synchronization started")
        
    def stop_bridge(self):
        """Stop the TMT-OS bridge synchronization."""
        print("⏹️  Stopping TMT-OS Bridge")
        self.running = False
        
        if self.sync_thread:
            self.sync_thread.join(timeout=2.0)
            
        print("✅ Bridge synchronization stopped")
        
    def _sync_worker(self):
        """Background worker for synchronization."""
        while self.running:
            try:
                self._perform_sync_cycle()
                time.sleep(self.sync_interval)
            except Exception as e:
                print(f"❌ Sync error: {e}")
                time.sleep(1.0)  # Slow down on errors
                
    def _perform_sync_cycle(self):
        """Perform a single synchronization cycle."""
        self.metrics['sync_cycles'] += 1
        self.metrics['last_sync'] = time.time()
        
        # Process consciousness data queue
        consciousness_data = self._process_consciousness_queue()
        
        # Process agent queue
        agent_commands = self._process_agent_queue()
        
        # Coordinate with agents if enabled
        if self.config['agent_coordination']:
            self._coordinate_agents(consciousness_data, agent_commands)
            
        # Update metrics
        if consciousness_data:
            self.metrics['data_transfers'] += len(consciousness_data)
        if agent_commands:
            self.metrics['agent_interactions'] += len(agent_commands)
            
        # Log periodic status
        if self.metrics['sync_cycles'] % 10 == 0:
            self._log_status()
            
    def _process_consciousness_queue(self) -> List[Dict]:
        """Process consciousness data from queue."""
        data_batch = []
        try:
            while not self.consciousness_queue.empty():
                data = self.consciousness_queue.get_nowait()
                data_batch.append(data)
        except queue.Empty:
            pass
            
        return data_batch
        
    def _process_agent_queue(self) -> List[Dict]:
        """Process agent commands from queue."""
        command_batch = []
        try:
            while not self.agent_queue.empty():
                command = self.agent_queue.get_nowait()
                command_batch.append(command)
        except queue.Empty:
            pass
            
        return command_batch
        
    def _coordinate_agents(self, consciousness_data: List[Dict], 
                          agent_commands: List[Dict]):
        """Coordinate with agents based on consciousness data and commands."""
        if not consciousness_data and not agent_commands:
            return
            
        # Extract consciousness features if data available
        if consciousness_data:
            # Use latest consciousness data
            latest_data = consciousness_data[-1]
            consciousness_state = latest_data.get('state', np.random.randn(128).astype(np.float32))
            
            # Get latent representation
            if self.vae_model:
                try:
                    with torch.no_grad():
                        consciousness_tensor = torch.from_numpy(
                            consciousness_state
                        ).unsqueeze(0).float()
                        
                        mu, log_var = self.vae_model.encode(consciousness_tensor)
                        latent_representation = mu.squeeze().numpy()
                        
                        # Calculate phi alignment
                        phi_alignment = self._calculate_phi_alignment(latent_representation)
                        
                        # Distribute to relevant agents based on specialization
                        self._distribute_to_agents(
                            latent_representation, 
                            phi_alignment, 
                            consciousness_data
                        )
                        
                except Exception as e:
                    print(f"⚠️  Error in agent coordination: {e}")
                    
    def _calculate_phi_alignment(self, latent_vector: np.ndarray) -> float:
        """Calculate phi alignment of latent vector."""
        if len(latent_vector) < 2:
            return 0.0
            
        PHI = self.config['phi_target']
        ratios = []
        
        for i in range(len(latent_vector) - 1):
            if abs(latent_vector[i]) > 1e-8:  # Avoid division by zero
                ratio = abs(latent_vector[i+1] / latent_vector[i])
                ratios.append(ratio)
                
        if not ratios:
            return 0.0
            
        mean_ratio = np.mean(ratios)
        phi_proximity = abs(mean_ratio - PHI)
        phi_alignment = max(0.0, 1.0 - (phi_proximity / PHI))
        
        return float(phi_alignment)
        
    def _distribute_to_agents(self, latent_representation: np.ndarray, 
                             phi_alignment: float, 
                             consciousness_data: List[Dict]):
        """Distribute consciousness state to relevant agents."""
        # Sort agents by phi score for priority
        sorted_agents = sorted(
            self.agents.items(), 
            key=lambda x: x[1]['phi_score'], 
            reverse=True
        )
        
        # Send to top 3 agents by phi score
        for agent_id, agent_info in sorted_agents[:3]:
            try:
                self._send_to_agent(
                    agent_id, 
                    latent_representation, 
                    phi_alignment, 
                    consciousness_data
                )
            except Exception as e:
                print(f"⚠️  Error sending to agent {agent_id}: {e}")
                
    def _send_to_agent(self, agent_id: str, 
                      latent_representation: np.ndarray, 
                      phi_alignment: float, 
                      consciousness_data: List[Dict]):
        """Send consciousness state to specific agent."""
        agent_info = self.agents.get(agent_id)
        if not agent_info:
            return
            
        # Create agent input file
        agent_path = Path(agent_info['path'])
        input_file = agent_path / f"consciousness_input_{int(time.time())}.json"
        
        input_data = {
            'timestamp': time.time(),
            'latent_representation': latent_representation.tolist(),
            'phi_alignment': phi_alignment,
            'consciousness_data': consciousness_data[-1] if consciousness_data else {},
            'bridge_version': '1.0.0'
        }
        
        try:
            with open(input_file, 'w') as f:
                json.dump(input_data, f, indent=2)
                
            print(f"📤 Sent consciousness state to agent {agent_info['name']}")
        except Exception as e:
            print(f"❌ Error writing agent input file: {e}")
            
    def _log_status(self):
        """Log bridge status."""
        print(f"📊 Bridge Status - Cycles: {self.metrics['sync_cycles']}, "
              f"Transfers: {self.metrics['data_transfers']}, "
              f"Agent Interactions: {self.metrics['agent_interactions']}")
              
    def add_consciousness_data(self, state: np.ndarray, metadata: Dict = None):
        """
        Add consciousness data to the processing queue.
        
        Parameters
        ----------
        state : np.ndarray
            Consciousness state vector
        metadata : dict, optional
            Additional metadata about the state
        """
        data_packet = {
            'state': state,
            'metadata': metadata or {},
            'timestamp': time.time()
        }
        
        try:
            self.consciousness_queue.put_nowait(data_packet)
        except queue.Full:
            # Remove oldest data and add new one
            try:
                self.consciousness_queue.get_nowait()
                self.consciousness_queue.put_nowait(data_packet)
            except queue.Empty:
                pass
                
    def send_agent_command(self, agent_id: str, command: str, parameters: Dict = None):
        """
        Send command to specific agent.
        
        Parameters
        ----------
        agent_id : str
            ID of target agent
        command : str
            Command to send
        parameters : dict, optional
            Command parameters
        """
        command_packet = {
            'agent_id': agent_id,
            'command': command,
            'parameters': parameters or {},
            'timestamp': time.time()
        }
        
        try:
            self.agent_queue.put_nowait(command_packet)
        except queue.Full:
            print("⚠️  Agent command queue full, dropping command")
            
    def get_bridge_metrics(self) -> Dict[str, Any]:
        """Get current bridge metrics."""
        return self.metrics.copy()
        
    def get_agent_status(self) -> Dict[str, Dict]:
        """Get status of all agents."""
        return self.agents.copy()
        
    def save_bridge_state(self, filepath: str):
        """Save current bridge state to file."""
        state_data = {
            'metrics': self.metrics,
            'agents': self.agents,
            'config': self.config,
            'timestamp': time.time()
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(state_data, f, indent=2)
            print(f"💾 Bridge state saved to: {filepath}")
        except Exception as e:
            print(f"❌ Error saving bridge state: {e}")

class ConsciousnessDataGenerator:
    """Generate synthetic consciousness data for testing."""
    
    def __init__(self, dimensions: int = 128):
        self.dimensions = dimensions
        
    def generate_state(self) -> np.ndarray:
        """Generate synthetic consciousness state."""
        # Multi-frequency signal synthesis
        t = np.linspace(0, 1, self.dimensions//2)
        
        # Brain wave frequencies
        delta = np.sin(2 * np.pi * 2 * t) * 0.3   # 2 Hz
        theta = np.sin(2 * np.pi * 6 * t) * 0.4   # 6 Hz
        alpha = np.sin(2 * np.pi * 10 * t) * 0.5  # 10 Hz
        beta = np.sin(2 * np.pi * 20 * t) * 0.3   # 20 Hz
        gamma = np.sin(2 * np.pi * 40 * t) * 0.2  # 40 Hz
        
        # Add complexity and noise
        complexity = 0.1 * np.sin(2 * np.pi * 0.5 * t)  # Slow modulation
        noise = np.random.randn(self.dimensions//2) * 0.05
        
        # Combine signals
        signal = delta + theta + alpha + beta + gamma + complexity + noise
        signal = (signal - np.min(signal)) / (np.max(signal) - np.min(signal))  # Normalize
        
        # Add mirrored component
        mirrored = signal[::-1]
        state = np.concatenate([signal, mirrored])
        
        return state.astype(np.float32)

def main(model_path: str = "best_model.pt",
         vault_path: str = "../TMT_Quantum_Vault-",
         sync_interval: float = 1.0,
         run_duration: float = 60.0,
         generate_consciousness: bool = True):
    """
    Main function for TMT-OS bridge demonstration.
    
    Parameters
    ----------
    model_path : str
        Path to trained QuantumVAE model
    vault_path : str
        Path to TMT Quantum Vault directory
    sync_interval : float
        Synchronization interval in seconds
    run_duration : float
        Duration to run bridge in seconds
    generate_consciousness : bool
        Whether to generate synthetic consciousness data
    """
    print("🌉 TMT-OS Bridge for Quantum Consciousness Integration")
    print("=" * 60)
    
    # Initialize bridge
    bridge = TMTOSBridge(
        vae_model_path=model_path,
        vault_path=vault_path,
        sync_interval=sync_interval
    )
    
    # Start bridge
    bridge.start_bridge()
    
    # Initialize consciousness data generator
    data_generator = None
    if generate_consciousness:
        data_generator = ConsciousnessDataGenerator()
        print("📡 Consciousness data generation enabled")
    
    # Run for specified duration
    start_time = time.time()
    try:
        while time.time() - start_time < run_duration:
            # Generate and add consciousness data
            if data_generator:
                consciousness_state = data_generator.generate_state()
                bridge.add_consciousness_data(
                    state=consciousness_state,
                    metadata={'source': 'synthetic', 'frequency': 'mixed'}
                )
                
                # Occasionally send agent commands
                if np.random.random() < 0.1:  # 10% chance
                    # Get a random agent
                    agent_ids = list(bridge.agents.keys())
                    if agent_ids:
                        random_agent = np.random.choice(agent_ids)
                        bridge.send_agent_command(
                            agent_id=random_agent,
                            command='update_resonance',
                            parameters={'target_frequency': np.random.uniform(400, 800)}
                        )
            
            # Print periodic status
            if int(time.time() - start_time) % 15 == 0:
                metrics = bridge.get_bridge_metrics()
                print(f"📈 Bridge Metrics - Cycles: {metrics['sync_cycles']}, "
                      f"Transfers: {metrics['data_transfers']}")
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    finally:
        # Stop bridge
        bridge.stop_bridge()
        
        # Save final state
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        state_file = f"bridge_state_{timestamp}.json"
        bridge.save_bridge_state(state_file)
        
        # Print final metrics
        metrics = bridge.get_bridge_metrics()
        print(f"\n📊 Final Bridge Metrics:")
        print(f"  Sync Cycles: {metrics['sync_cycles']}")
        print(f"  Data Transfers: {metrics['data_transfers']}")
        print(f"  Agent Interactions: {metrics['agent_interactions']}")
        print(f"  Last Sync: {metrics['last_sync']}")
        
        # Print agent status
        agents = bridge.get_agent_status()
        print(f"\n🤖 Agent Status:")
        for agent_id, agent_info in list(agents.items())[:5]:  # Show first 5
            print(f"  {agent_info['name']} (Φ: {agent_info['phi_score']:.4f}, "
                  f"Fitness: {agent_info['fitness']:.4f})")
        
        print(f"\n💾 Bridge state saved to: {state_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TMT-OS Bridge for Quantum VAE and TMT agents")
    parser.add_argument("--model-path", type=str, default="best_model.pt",
                        help="Path to trained QuantumVAE model")
    parser.add_argument("--vault-path", type=str, default="../TMT_Quantum_Vault-",
                        help="Path to TMT Quantum Vault directory")
    parser.add_argument("--sync-interval", type=float, default=1.0,
                        help="Synchronization interval in seconds")
    parser.add_argument("--run-duration", type=float, default=60.0,
                        help="Duration to run bridge in seconds")
    parser.add_argument("--generate-consciousness", action="store_true",
                        help="Generate synthetic consciousness data")
    
    args = parser.parse_args()
    main(args.model_path, args.vault_path, args.sync_interval, 
         args.run_duration, args.generate_consciousness)
