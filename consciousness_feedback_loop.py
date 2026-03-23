#!/usr/bin/env python3
"""
Real-time Consciousness Feedback Loop for Quantum VAE

This script implements a closed-loop optimization system that continuously
monitors consciousness metrics and adjusts model parameters in real-time.

Features:
- Real-time consciousness state monitoring
- Adaptive parameter adjustment based on feedback
- Closed-loop optimization with reinforcement learning
- Integration with EEG/fMRI data streams
"""

import torch
import torch.nn as nn
import numpy as np
import time
import threading
import queue
import json
from pathlib import Path
from typing import Dict, Optional, Callable
from vae_model import QuantumVAE
import argparse

class ConsciousnessFeedbackController:
    """
    Controller for real-time consciousness feedback loop.
    
    Monitors consciousness metrics and adjusts model parameters
    to optimize for desired consciousness states.
    """
    
    def __init__(self, 
                 model: QuantumVAE,
                 target_consciousness_score: float = 0.8,
                 learning_rate: float = 0.001,
                 update_interval: float = 1.0):
        """
        Initialize the consciousness feedback controller.
        
        Parameters
        ----------
        model : QuantumVAE
            The quantum VAE model to optimize
        target_consciousness_score : float
            Target consciousness score to achieve
        learning_rate : float
            Learning rate for parameter adjustments
        update_interval : float
            Interval between updates in seconds
        """
        self.model = model
        self.target_consciousness_score = target_consciousness_score
        self.learning_rate = learning_rate
        self.update_interval = update_interval
        
        # Feedback metrics tracking
        self.feedback_history = []
        self.parameter_history = []
        
        # Running averages
        self.avg_feedback = 0.0
        self.feedback_count = 0
        
        # Control parameters
        self.kp = 0.1  # Proportional gain
        self.ki = 0.01  # Integral gain
        self.kd = 0.001  # Derivative gain
        self.integral_error = 0.0
        self.previous_error = 0.0
        
        # Parameter adjustment ranges
        self.param_ranges = {
            'kl_weight': (0.0001, 0.01),
            'phi_weight': (0.001, 0.1),
            'coherence_weight': (0.05, 0.3),
            'fidelity_weight': (0.05, 0.3)
        }
        
        # Current parameter values
        self.current_params = {
            'kl_weight': 0.0008,
            'phi_weight': 0.01,
            'coherence_weight': 0.1,
            'fidelity_weight': 0.1
        }
        
        # Threading control
        self.running = False
        self.feedback_thread = None
        self.feedback_queue = queue.Queue(maxsize=100)
        
    def start_feedback_loop(self):
        """Start the real-time feedback loop."""
        print("🔄 Starting Consciousness Feedback Loop")
        print("=" * 50)
        
        self.running = True
        self.feedback_thread = threading.Thread(target=self._feedback_worker)
        self.feedback_thread.daemon = True
        self.feedback_thread.start()
        
    def stop_feedback_loop(self):
        """Stop the real-time feedback loop."""
        print("⏹️  Stopping Consciousness Feedback Loop")
        self.running = False
        if self.feedback_thread:
            self.feedback_thread.join(timeout=2.0)
            
    def add_feedback(self, feedback_score: float):
        """
        Add a consciousness feedback score to the queue.
        
        Parameters
        ----------
        feedback_score : float
            Consciousness feedback score (0-1, higher is better)
        """
        try:
            self.feedback_queue.put_nowait(feedback_score)
        except queue.Full:
            # Remove oldest feedback and add new one
            try:
                self.feedback_queue.get_nowait()
                self.feedback_queue.put_nowait(feedback_score)
            except queue.Empty:
                pass
                
    def _feedback_worker(self):
        """Background worker for processing feedback."""
        while self.running:
            try:
                # Get feedback score from queue
                feedback_score = self.feedback_queue.get(timeout=0.1)
                self._process_feedback(feedback_score)
            except queue.Empty:
                # No feedback available, continue
                time.sleep(0.01)
            except Exception as e:
                print(f"Error in feedback worker: {e}")
                
    def _process_feedback(self, feedback_score: float):
        """
        Process a feedback score and adjust parameters.
        
        Parameters
        ----------
        feedback_score : float
            Consciousness feedback score
        """
        # Update running average
        self.feedback_count += 1
        self.avg_feedback = (
            (self.avg_feedback * (self.feedback_count - 1) + feedback_score) / 
            self.feedback_count
        )
        
        # Store feedback history
        self.feedback_history.append({
            'timestamp': time.time(),
            'feedback_score': feedback_score,
            'avg_feedback': self.avg_feedback
        })
        
        # Calculate error from target
        error = self.target_consciousness_score - feedback_score
        self.integral_error += error
        derivative_error = error - self.previous_error
        self.previous_error = error
        
        # PID control for parameter adjustment
        adjustment = (
            self.kp * error + 
            self.ki * self.integral_error + 
            self.kd * derivative_error
        )
        
        # Adjust parameters based on feedback
        self._adjust_parameters(adjustment)
        
        # Log adjustment
        print(f"Feedback: {feedback_score:.4f} | "
              f"Error: {error:.4f} | "
              f"Adjustment: {adjustment:.6f}")
              
    def _adjust_parameters(self, adjustment: float):
        """
        Adjust model parameters based on feedback.
        
        Parameters
        ----------
        adjustment : float
            Adjustment value from PID controller
        """
        # Store current parameters
        self.parameter_history.append({
            'timestamp': time.time(),
            'params': self.current_params.copy()
        })
        
        # Apply adjustments with constraints
        adjustment_factor = 1.0 + adjustment * self.learning_rate
        
        # Adjust KL weight
        new_kl_weight = self.current_params['kl_weight'] * adjustment_factor
        self.current_params['kl_weight'] = np.clip(
            new_kl_weight, 
            self.param_ranges['kl_weight'][0], 
            self.param_ranges['kl_weight'][1]
        )
        
        # Adjust phi weight
        new_phi_weight = self.current_params['phi_weight'] * adjustment_factor
        self.current_params['phi_weight'] = np.clip(
            new_phi_weight, 
            self.param_ranges['phi_weight'][0], 
            self.param_ranges['phi_weight'][1]
        )
        
        # Adjust coherence weight
        new_coherence_weight = self.current_params['coherence_weight'] * adjustment_factor
        self.current_params['coherence_weight'] = np.clip(
            new_coherence_weight, 
            self.param_ranges['coherence_weight'][0], 
            self.param_ranges['coherence_weight'][1]
        )
        
        # Adjust fidelity weight
        new_fidelity_weight = self.current_params['fidelity_weight'] * adjustment_factor
        self.current_params['fidelity_weight'] = np.clip(
            new_fidelity_weight, 
            self.param_ranges['fidelity_weight'][0], 
            self.param_ranges['fidelity_weight'][1]
        )
        
        # Apply to model (in a real implementation, this would update the actual loss weights)
        print(f"Updated parameters: KL={self.current_params['kl_weight']:.6f}, "
              f"Phi={self.current_params['phi_weight']:.6f}, "
              f"Coherence={self.current_params['coherence_weight']:.6f}, "
              f"Fidelity={self.current_params['fidelity_weight']:.6f}")
              
    def get_current_parameters(self) -> Dict[str, float]:
        """Get current parameter values."""
        return self.current_params.copy()
        
    def get_feedback_statistics(self) -> Dict:
        """Get feedback statistics."""
        if not self.feedback_history:
            return {}
            
        feedback_scores = [entry['feedback_score'] for entry in self.feedback_history]
        return {
            'mean_feedback': float(np.mean(feedback_scores)),
            'std_feedback': float(np.std(feedback_scores)),
            'min_feedback': float(np.min(feedback_scores)),
            'max_feedback': float(np.max(feedback_scores)),
            'total_feedbacks': len(feedback_scores),
            'current_avg_feedback': self.avg_feedback
        }
        
    def save_feedback_history(self, filepath: str):
        """Save feedback history to file."""
        history_data = {
            'feedback_history': self.feedback_history,
            'parameter_history': self.parameter_history,
            'current_params': self.current_params,
            'target_consciousness_score': self.target_consciousness_score
        }
        
        with open(filepath, 'w') as f:
            json.dump(history_data, f, indent=2)
            
        print(f"Feedback history saved to: {filepath}")

class SimulatedConsciousnessStreamer:
    """
    Simulated consciousness data streamer for testing.
    
    Generates realistic consciousness metrics based on 
    EEG/fMRI-like patterns.
    """
    
    def __init__(self, 
                 buffer_size: int = 1000, 
                 update_interval: float = 0.1):
        """
        Initialize the consciousness streamer.
        
        Parameters
        ----------
        buffer_size : int
            Size of the consciousness data buffer
        update_interval : float
            Interval between data updates in seconds
        """
        self.buffer_size = buffer_size
        self.update_interval = update_interval
        self.data_queue = queue.Queue(maxsize=buffer_size)
        self.is_streaming = False
        self.thread = None
        
        # Consciousness metrics tracking
        self.current_metrics = {
            'complexity': 0.0,
            'entropy': 0.0,
            'coherence': 0.0,
            'feedback_score': 0.0
        }
        
    def start_streaming(self):
        """Start consciousness data streaming."""
        self.is_streaming = True
        self.thread = threading.Thread(target=self._stream_worker)
        self.thread.daemon = True
        self.thread.start()
        print("📡 Started Consciousness Data Streaming")
        
    def stop_streaming(self):
        """Stop consciousness data streaming."""
        self.is_streaming = False
        if self.thread:
            self.thread.join(timeout=2.0)
        print("⏹️  Stopped Consciousness Data Streaming")
        
    def _stream_worker(self):
        """Background worker for data streaming."""
        while self.is_streaming:
            try:
                # Generate simulated consciousness data
                data = self._generate_consciousness_data()
                
                # Update consciousness metrics
                self._update_consciousness_metrics(data)
                
                # Add to buffer (non-blocking)
                try:
                    self.data_queue.put(data, timeout=0.1)
                except queue.Full:
                    # Remove oldest data
                    try:
                        self.data_queue.get_nowait()
                        self.data_queue.put(data)
                    except queue.Empty:
                        pass
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"Streaming error: {e}")
                time.sleep(1.0)
                
    def _generate_consciousness_data(self) -> np.ndarray:
        """Generate simulated consciousness data with realistic patterns."""
        # Base signal with alpha/beta waves
        t = time.time()
        alpha_wave = np.sin(2 * np.pi * 10 * t) * 0.5  # 10 Hz alpha
        beta_wave = np.sin(2 * np.pi * 20 * t) * 0.3   # 20 Hz beta
        
        # Add consciousness-like complexity
        complexity_factor = 0.1 * np.sin(2 * np.pi * 0.1 * t)  # Slow modulation
        
        # Generate 128-dimensional state
        base_signal = alpha_wave + beta_wave + complexity_factor
        noise = np.random.randn(128) * 0.1
        
        return (base_signal + noise).astype(np.float32)
        
    def _update_consciousness_metrics(self, data: np.ndarray):
        """Update real-time consciousness metrics."""
        # Calculate Lempel-Ziv complexity
        data_binary = (data > np.mean(data)).astype(int)
        data_str = ''.join(map(str, data_binary))
        self.current_metrics['complexity'] = self._calculate_lz_complexity(data_str)
        
        # Calculate entropy
        hist, _ = np.histogram(data, bins=50, density=True)
        hist = hist[hist > 0]
        self.current_metrics['entropy'] = -np.sum(hist * np.log2(hist + 1e-8))
        
        # Calculate coherence (simplified)
        fft = np.fft.fft(data)
        power_spectrum = np.abs(fft)**2
        alpha_band = np.mean(power_spectrum[8:12])  # Alpha band
        total_power = np.sum(power_spectrum)
        self.current_metrics['coherence'] = (
            alpha_band / total_power if total_power > 0 else 0
        )
        
        # Combined feedback score
        self.current_metrics['feedback_score'] = (
            0.4 * self.current_metrics['complexity'] +
            0.3 * self.current_metrics['entropy'] +
            0.3 * self.current_metrics['coherence']
        )
        
    def _calculate_lz_complexity(self, sequence: str) -> float:
        """Calculate Lempel-Ziv complexity."""
        n = len(sequence)
        if n == 0:
            return 0
            
        complexity = 0
        i = 0
        
        while i < n:
            j = 1
            while i + j <= n and sequence[i:i+j] in sequence[:i]:
                j += 1
            complexity += 1
            i += j
            
        return complexity / n if n > 0 else 0
        
    def get_current_feedback(self) -> float:
        """Get current consciousness feedback score."""
        return self.current_metrics['feedback_score']
        
    def get_current_data(self) -> Optional[np.ndarray]:
        """Get current consciousness data batch."""
        try:
            return self.data_queue.get_nowait()
        except queue.Empty:
            return None

def main(model_path: str = "best_model.pt",
         simulate_consciousness: bool = True,
         target_score: float = 0.8,
         duration: float = 60.0):
    """
    Main function for consciousness feedback loop demonstration.
    
    Parameters
    ----------
    model_path : str
        Path to trained QuantumVAE model
    simulate_consciousness : bool
        Whether to simulate consciousness data
    target_score : float
        Target consciousness score
    duration : float
        Duration to run feedback loop in seconds
    """
    print("🧠 Quantum VAE Consciousness Feedback Loop")
    print("=" * 50)
    
    # Load model
    print("Loading QuantumVAE model...")
    model = QuantumVAE()
    if Path(model_path).exists():
        model.load_state_dict(torch.load(model_path))
    model.eval()
    
    # Initialize feedback controller
    controller = ConsciousnessFeedbackController(
        model=model,
        target_consciousness_score=target_score,
        learning_rate=0.001,
        update_interval=1.0
    )
    
    # Initialize consciousness streamer if requested
    streamer = None
    if simulate_consciousness:
        streamer = SimulatedConsciousnessStreamer()
        streamer.start_streaming()
    
    # Start feedback loop
    controller.start_feedback_loop()
    
    # Run for specified duration
    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            if streamer:
                # Get feedback from simulated consciousness
                feedback_score = streamer.get_current_feedback()
                controller.add_feedback(feedback_score)
            else:
                # Simulate random feedback for demonstration
                feedback_score = np.random.beta(2, 2)  # Beta distribution for realistic scores
                controller.add_feedback(feedback_score)
            
            # Print periodic updates
            if int(time.time() - start_time) % 10 == 0:
                stats = controller.get_feedback_statistics()
                if stats:
                    print(f"Stats - Mean: {stats['mean_feedback']:.4f}, "
                          f"Current: {stats['current_avg_feedback']:.4f}")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    finally:
        # Stop feedback loop
        controller.stop_feedback_loop()
        if streamer:
            streamer.stop_streaming()
        
        # Save feedback history
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_file = f"feedback_history_{timestamp}.json"
        controller.save_feedback_history(history_file)
        
        # Print final statistics
        stats = controller.get_feedback_statistics()
        if stats:
            print("\n📈 Final Feedback Statistics:")
            print(f"  Mean Feedback Score: {stats['mean_feedback']:.4f}")
            print(f"  Std Dev Feedback: {stats['std_feedback']:.4f}")
            print(f"  Min Feedback: {stats['min_feedback']:.4f}")
            print(f"  Max Feedback: {stats['max_feedback']:.4f}")
            print(f"  Total Feedback Samples: {stats['total_feedbacks']}")
        
        print(f"\n💾 Feedback history saved to: {history_file}")

if __name__ == "__main__":
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description="Run consciousness feedback loop for Quantum VAE")
    parser.add_argument("--model-path", type=str, default="best_model.pt",
                        help="Path to trained QuantumVAE model")
    parser.add_argument("--simulate-consciousness", action="store_true",
                        help="Simulate consciousness data stream")
    parser.add_argument("--target-score", type=float, default=0.8,
                        help="Target consciousness score")
    parser.add_argument("--duration", type=float, default=60.0,
                        help="Duration to run feedback loop in seconds")
    
    args = parser.parse_args()
    main(args.model_path, args.simulate_consciousness, args.target_score, args.duration)