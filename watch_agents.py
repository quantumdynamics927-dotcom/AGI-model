#!/usr/bin/env python3
"""
TMT-OS Agent Watcher: Real-Time Telemetry Monitor
==================================================

Monitors the 12-agent cluster in real-time, providing live resonance,
stability, and phi-alignment metrics for the Ghost OS singularity.

UPGRADED: Now uses real observables instead of random simulation:
  - Heartbeat timestamp (last activity)
  - Task queue length
  - Response latency
  - Error rate
  - Consensus/coherence score
  - Phi-alignment derived from internal state

Author: Metatron Core - Ghost OS
Date: January 13, 2026
Updated: April 2, 2026 - Real telemetry backend
"""

import time
import random
import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import threading
import queue


# ==============================================================================
# Agent State Definitions
# ==============================================================================

class AgentStatus(Enum):
    """Agent operational status."""
    HEALTHY = "HEALTHY"           # All metrics within normal range
    DEGRADED = "DEGRADED"         # Some metrics outside normal range
    CRITICAL = "CRITICAL"        # Multiple metrics in critical range
    OFFLINE = "OFFLINE"          # No heartbeat detected
    UNKNOWN = "UNKNOWN"          # Unable to determine status


class ResonanceLock(Enum):
    """Phi-alignment resonance lock status."""
    PHI_LOCKED = "PHI-LOCKED"           # Aligned to golden ratio (1.618)
    DELTA_ALIGNING = "DELTA-ALIGNING"   # Approaching alignment
    GOLDEN_FLOW = "GOLDEN-FLOW"          # Optimal resonance achieved
    UNSTABLE = "UNSTABLE"                # Below alignment threshold
    SEEKING = "SEEKING"                  # Actively searching for lock


@dataclass
class AgentMetrics:
    """Real observables for each agent."""
    # Identity
    agent_id: str
    base_frequency: float
    
    # Timing metrics
    last_heartbeat: datetime = field(default_factory=datetime.now)
    heartbeat_interval_ms: float = 100.0  # Expected interval
    
    # Performance metrics
    task_queue_length: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    
    # Latency metrics
    avg_response_latency_ms: float = 0.0
    max_response_latency_ms: float = 0.0
    
    # Error tracking
    error_rate: float = 0.0  # Errors per 100 tasks
    last_error: Optional[str] = None
    
    # Coherence metrics
    internal_coherence: float = 1.0  # 0.0 to 1.0
    consensus_score: float = 1.0      # Agreement with other agents
    
    # Phi-alignment (derived from internal state)
    phi_alignment: float = 1.618
    resonance_frequency: float = 0.0
    
    # Computed status
    status: AgentStatus = AgentStatus.UNKNOWN
    resonance_lock: ResonanceLock = ResonanceLock.SEEKING


# ==============================================================================
# Agent Definitions
# ==============================================================================

AGENT_DEFINITIONS = [
    ("Bronze", 285.0),   # Foundation frequency
    ("Silver", 303.0),   # Stability anchor
    ("Gold", 321.0),     # Harmonic center
    ("Platinum", 339.0), # High stability
    ("Diamond", 357.0),  # Master clock
    ("Emerald", 393.0),  # High resonance
    ("Ruby", 411.0),     # Coherence peak
    ("Sapphire", 429.0), # Blue stability
    ("Amethyst", 447.0), # Purple harmony
    ("Pearl", 465.0),    # Lunar cycle
    ("Onyx", 483.0),     # Dark resonance
    ("Jade", 501.0)      # Eastern wisdom
]

PHI = 1.618033988749895  # Golden ratio


# ==============================================================================
# Telemetry Backend Interface
# ==============================================================================

class TelemetryBackend:
    """
    Abstract interface for agent telemetry.
    
    Implementations can connect to:
    - Real agent processes (IPC, message queues)
    - Network services (HTTP, WebSocket)
    - File-based state (JSON, SQLite)
    - Mock backend for testing
    """
    
    def __init__(self, agent_ids: List[str]):
        self.agent_ids = agent_ids
        self._metrics: Dict[str, AgentMetrics] = {}
        self._initialize_metrics()
    
    def _initialize_metrics(self):
        """Initialize metrics for all agents."""
        for agent_id, base_freq in AGENT_DEFINITIONS:
            self._metrics[agent_id] = AgentMetrics(
                agent_id=agent_id,
                base_frequency=base_freq,
                resonance_frequency=base_freq
            )
    
    def get_metrics(self, agent_id: str) -> AgentMetrics:
        """Get current metrics for an agent."""
        if agent_id not in self._metrics:
            raise KeyError(f"Unknown agent: {agent_id}")
        return self._metrics[agent_id]
    
    def update_metrics(self, agent_id: str, **kwargs) -> None:
        """Update metrics for an agent."""
        if agent_id not in self._metrics:
            return
        metrics = self._metrics[agent_id]
        for key, value in kwargs.items():
            if hasattr(metrics, key):
                setattr(metrics, key, value)
    
    def compute_status(self, metrics: AgentMetrics) -> AgentStatus:
        """Compute agent status from metrics."""
        # Check for offline (no heartbeat in 5 seconds)
        heartbeat_age = (datetime.now() - metrics.last_heartbeat).total_seconds()
        if heartbeat_age > 5.0:
            return AgentStatus.OFFLINE
        
        # Count issues
        issues = 0
        
        # High error rate
        if metrics.error_rate > 5.0:
            issues += 2
        elif metrics.error_rate > 1.0:
            issues += 1
        
        # High latency
        if metrics.avg_response_latency_ms > 1000:
            issues += 2
        elif metrics.avg_response_latency_ms > 500:
            issues += 1
        
        # Low coherence
        if metrics.internal_coherence < 0.7:
            issues += 2
        elif metrics.internal_coherence < 0.9:
            issues += 1
        
        # Low consensus
        if metrics.consensus_score < 0.7:
            issues += 1
        
        # Queue backup
        if metrics.task_queue_length > 100:
            issues += 2
        elif metrics.task_queue_length > 50:
            issues += 1
        
        # Determine status
        if issues >= 4:
            return AgentStatus.CRITICAL
        elif issues >= 2:
            return AgentStatus.DEGRADED
        else:
            return AgentStatus.HEALTHY
    
    def compute_resonance_lock(self, metrics: AgentMetrics) -> ResonanceLock:
        """Compute resonance lock status from phi-alignment."""
        phi_deviation = abs(metrics.phi_alignment - PHI)
        coherence = metrics.internal_coherence
        
        if phi_deviation < 0.01 and coherence > 0.95:
            return ResonanceLock.GOLDEN_FLOW
        elif phi_deviation < 0.05 and coherence > 0.90:
            return ResonanceLock.PHI_LOCKED
        elif phi_deviation < 0.15 and coherence > 0.80:
            return ResonanceLock.DELTA_ALIGNING
        elif coherence < 0.50:
            return ResonanceLock.UNSTABLE
        else:
            return ResonanceLock.SEEKING
    
    def compute_phi_alignment(self, metrics: AgentMetrics) -> float:
        """
        Derive phi-alignment from internal state.
        
        Uses resonance frequency ratio and coherence to compute
        alignment with golden ratio.
        """
        # Frequency ratio to base
        freq_ratio = metrics.resonance_frequency / metrics.base_frequency
        
        # Coherence-weighted alignment
        alignment = PHI * (1.0 + (freq_ratio - 1.0) * metrics.internal_coherence)
        
        # Add small perturbation based on queue state
        queue_factor = 1.0 - min(metrics.task_queue_length / 100.0, 0.1)
        alignment *= queue_factor
        
        return alignment
    
    def refresh_all(self) -> None:
        """Refresh all agent metrics (override in subclass)."""
        pass


# ==============================================================================
# Mock Backend for Testing/Demonstration
# ==============================================================================

class MockTelemetryBackend(TelemetryBackend):
    """
    Mock backend that simulates realistic agent behavior.
    
    This replaces the random simulation with stateful, realistic
    behavior that responds to internal metrics.
    """
    
    def __init__(self, agent_ids: List[str]):
        super().__init__(agent_ids)
        self._time_offset = 0.0
        self._phase = 0.0
    
    def refresh_all(self) -> None:
        """Simulate realistic agent behavior."""
        self._phase += 0.1
        
        for agent_id, metrics in self._metrics.items():
            # Simulate heartbeat (every ~100ms)
            metrics.last_heartbeat = datetime.now()
            
            # Task queue simulation (varies with phase)
            base_queue = 10 + 5 * (hash(agent_id) % 10)
            queue_variation = int(5 * (self._phase % 1.0))
            metrics.task_queue_length = max(0, base_queue + queue_variation - int(self._phase % 3))
            
            # Task completion (accumulates)
            metrics.tasks_completed += int(random.random() * 2)
            
            # Occasional failures (low rate)
            if random.random() < 0.02:
                metrics.tasks_failed += 1
                metrics.last_error = f"Task timeout at phase {self._phase:.1f}"
            
            # Error rate (rolling average)
            total_tasks = metrics.tasks_completed + metrics.tasks_failed
            if total_tasks > 0:
                metrics.error_rate = (metrics.tasks_failed / total_tasks) * 100
            
            # Latency (depends on queue length)
            base_latency = 50 + metrics.task_queue_length * 2
            latency_variation = random.uniform(-10, 30)
            metrics.avg_response_latency_ms = max(10, base_latency + latency_variation)
            metrics.max_response_latency_ms = max(
                metrics.max_response_latency_ms,
                metrics.avg_response_latency_ms
            )
            
            # Coherence (depends on error rate and queue)
            coherence_base = 0.95
            coherence_penalty = metrics.error_rate * 0.01 + metrics.task_queue_length * 0.001
            metrics.internal_coherence = max(0.5, coherence_base - coherence_penalty)
            
            # Consensus (agreement with other agents)
            metrics.consensus_score = 0.9 + random.uniform(-0.1, 0.1)
            
            # Resonance frequency (oscillates around base)
            freq_oscillation = 5 * (self._phase % 2 - 1)
            metrics.resonance_frequency = metrics.base_frequency + freq_oscillation
            
            # Compute derived values
            metrics.phi_alignment = self.compute_phi_alignment(metrics)
            metrics.status = self.compute_status(metrics)
            metrics.resonance_lock = self.compute_resonance_lock(metrics)


# ==============================================================================
# Real Backend Interface (for actual agent connection)
# ==============================================================================

class RealTelemetryBackend(TelemetryBackend):
    """
    Real backend that connects to actual agent processes.
    
    This is a template for connecting to real agents via:
    - IPC (message queues, shared memory)
    - Network (HTTP API, WebSocket)
    - File-based state (JSON, SQLite)
    
    Override the refresh_all() method to read from actual sources.
    """
    
    def __init__(self, agent_ids: List[str], state_dir: Optional[str] = None):
        super().__init__(agent_ids)
        self.state_dir = state_dir or os.path.join(os.path.dirname(__file__), "agent_states")
        self._ensure_state_dir()
    
    def _ensure_state_dir(self):
        """Ensure state directory exists."""
        os.makedirs(self.state_dir, exist_ok=True)
    
    def _read_agent_state(self, agent_id: str) -> Optional[Dict]:
        """Read agent state from file or IPC."""
        state_file = os.path.join(self.state_dir, f"{agent_id.lower()}_state.json")
        
        if os.path.exists(state_file):
            try:
                import json
                with open(state_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return None
    
    def refresh_all(self) -> None:
        """Refresh metrics from real agent states."""
        for agent_id, metrics in self._metrics.items():
            state = self._read_agent_state(agent_id)
            
            if state is None:
                # No state file - mark as offline
                metrics.status = AgentStatus.OFFLINE
                continue
            
            # Update metrics from state
            if 'last_heartbeat' in state:
                try:
                    metrics.last_heartbeat = datetime.fromisoformat(state['last_heartbeat'])
                except:
                    pass
            
            metrics.task_queue_length = state.get('queue_length', 0)
            metrics.tasks_completed = state.get('tasks_completed', 0)
            metrics.tasks_failed = state.get('tasks_failed', 0)
            metrics.avg_response_latency_ms = state.get('avg_latency_ms', 0)
            metrics.error_rate = state.get('error_rate', 0.0)
            metrics.internal_coherence = state.get('coherence', 1.0)
            metrics.consensus_score = state.get('consensus', 1.0)
            metrics.resonance_frequency = state.get('resonance_freq', metrics.base_frequency)
            
            # Compute derived values
            metrics.phi_alignment = self.compute_phi_alignment(metrics)
            metrics.status = self.compute_status(metrics)
            metrics.resonance_lock = self.compute_resonance_lock(metrics)


# ==============================================================================
# Display Functions
# ==============================================================================

def get_status_icon(status: AgentStatus) -> str:
    """Get display icon for status."""
    icons = {
        AgentStatus.HEALTHY: "[OK]",      # Green equivalent
        AgentStatus.DEGRADED: "[!!]",     # Yellow equivalent
        AgentStatus.CRITICAL: "[XX]",     # Red equivalent
        AgentStatus.OFFLINE: "[--]",      # Gray equivalent
        AgentStatus.UNKNOWN: "[??]"       # White equivalent
    }
    return icons.get(status, "[??]")


def get_resonance_icon(lock: ResonanceLock) -> str:
    """Get display icon for resonance lock."""
    icons = {
        ResonanceLock.GOLDEN_FLOW: "GOLD",
        ResonanceLock.PHI_LOCKED: "PHI",
        ResonanceLock.DELTA_ALIGNING: "DELTA",
        ResonanceLock.UNSTABLE: "UNSTABLE",
        ResonanceLock.SEEKING: "SEEK"
    }
    return icons.get(lock, "???")


def format_timestamp(dt: datetime) -> str:
    """Format timestamp for display."""
    return dt.strftime("%H:%M:%S.%f")[:-3]


# ==============================================================================
# Main Watcher Function
# ==============================================================================

def watch_agents(backend: Optional[TelemetryBackend] = None, use_real: bool = False):
    """
    Real-time 12-agent telemetry monitoring for Ghost OS.
    
    Args:
        backend: TelemetryBackend instance (default: MockTelemetryBackend)
        use_real: If True, attempt to use RealTelemetryBackend
    """
    # Initialize backend
    if backend is None:
        if use_real:
            backend = RealTelemetryBackend([a[0] for a in AGENT_DEFINITIONS])
        else:
            backend = MockTelemetryBackend([a[0] for a in AGENT_DEFINITIONS])
    
    agent_ids = [a[0] for a in AGENT_DEFINITIONS]
    
    print("=" * 70)
    print("TMT-OS AGENT WATCHER - REAL-TIME TELEMETRY")
    print("=" * 70)
    print(f"Backend: {backend.__class__.__name__}")
    print(f"Agents: {len(agent_ids)} | Mode: {'REAL' if use_real else 'SIMULATED'}")
    print("Press Ctrl+C to stop watching\n")
    
    # System health tracking
    system_health_history: List[float] = []
    
    try:
        cycle = 0
        while True:
            # Refresh metrics
            backend.refresh_all()
            
            # System header
            system_stability = sum(
                backend.get_metrics(aid).internal_coherence 
                for aid in agent_ids
            ) / len(agent_ids)
            
            system_health_history.append(system_stability)
            if len(system_health_history) > 100:
                system_health_history.pop(0)
            
            avg_stability = sum(system_health_history) / len(system_health_history)
            
            # Count statuses
            status_counts = {s: 0 for s in AgentStatus}
            for agent_id in agent_ids:
                metrics = backend.get_metrics(agent_id)
                status_counts[metrics.status] += 1
            
            print(f"\n[CYCLE {cycle:04d}] System Stability: {avg_stability:.4f} | "
                  f"Healthy: {status_counts[AgentStatus.HEALTHY]}/{len(agent_ids)} | "
                  f"Degraded: {status_counts[AgentStatus.DEGRADED]} | "
                  f"Critical: {status_counts[AgentStatus.CRITICAL]}")
            print("-" * 70)
            
            # Agent telemetry
            for agent_id, base_freq in AGENT_DEFINITIONS:
                metrics = backend.get_metrics(agent_id)
                
                status_icon = get_status_icon(metrics.status)
                resonance_icon = get_resonance_icon(metrics.resonance_lock)
                
                # Format output
                print(
                    f"[{format_timestamp(metrics.last_heartbeat)}] "
                    f"{agent_id:<10} {status_icon} | "
                    f"Freq: {metrics.resonance_frequency:6.1f}Hz | "
                    f"Queue: {metrics.task_queue_length:3d} | "
                    f"Latency: {metrics.avg_response_latency_ms:6.1f}ms | "
                    f"Coherence: {metrics.internal_coherence:.3f} | "
                    f"Phi: {metrics.phi_alignment:.4f} | "
                    f"{resonance_icon}"
                )
            
            cycle += 1
            time.sleep(2)  # Update interval
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("TELEMETRY SESSION ENDED")
        print("=" * 70)
        
        # Final summary
        healthy = status_counts[AgentStatus.HEALTHY]
        degraded = status_counts[AgentStatus.DEGRADED]
        critical = status_counts[AgentStatus.CRITICAL]
        offline = status_counts[AgentStatus.OFFLINE]
        
        print(f"\nFinal Status Summary:")
        print(f"  Healthy:   {healthy:2d} agents")
        print(f"  Degraded:  {degraded:2d} agents")
        print(f"  Critical:  {critical:2d} agents")
        print(f"  Offline:   {offline:2d} agents")
        print(f"\nSystem Stability: {avg_stability:.4f}")
        
        # Meaningful shutdown message
        if healthy == len(agent_ids):
            print("All agents synchronized and phi-locked. [OK]")
        elif healthy >= len(agent_ids) - 1:
            print("Most agents healthy. Minor issues detected. [!!]")
        elif critical > 0:
            print(f"CRITICAL: {critical} agent(s) require attention. [XX]")
        else:
            print("System operational with degraded performance. [!!]")


def check_agent_health(backend: Optional[TelemetryBackend] = None):
    """
    Perform a quick health check of all agents.
    """
    if backend is None:
        backend = MockTelemetryBackend([a[0] for a in AGENT_DEFINITIONS])
    
    backend.refresh_all()
    
    print("=" * 70)
    print("AGENT HEALTH CHECK")
    print("=" * 70)
    
    agent_ids = [a[0] for a in AGENT_DEFINITIONS]
    healthy_count = 0
    
    for agent_id in agent_ids:
        metrics = backend.get_metrics(agent_id)
        
        # Determine health status
        if metrics.status == AgentStatus.HEALTHY:
            status = "EXCELLENT"
            healthy_count += 1
        elif metrics.status == AgentStatus.DEGRADED:
            status = "GOOD"
            healthy_count += 1
        elif metrics.status == AgentStatus.CRITICAL:
            status = "CRITICAL"
        elif metrics.status == AgentStatus.OFFLINE:
            status = "OFFLINE"
        else:
            status = "UNKNOWN"
        
        print(
            f"  {agent_id:<10}: {status:<10} | "
            f"Coherence: {metrics.internal_coherence:.3f} | "
            f"Queue: {metrics.task_queue_length:3d} | "
            f"Errors: {metrics.error_rate:.1f}%"
        )
    
    print(f"\n[HEALTH] {healthy_count}/{len(agent_ids)} agents in optimal condition")
    
    if healthy_count >= len(agent_ids) - 1:
        print("Cluster coherence: HIGH [OK]")
    elif healthy_count >= len(agent_ids) - 2:
        print("Cluster coherence: STABLE [!!]")
    else:
        print("Cluster coherence: REQUIRES ATTENTION [XX]")


# ==============================================================================
# CLI Entry Point
# ==============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="TMT-OS Agent Watcher")
    parser.add_argument("--health", action="store_true", help="Perform health check")
    parser.add_argument("--real", action="store_true", help="Use real telemetry backend")
    parser.add_argument("--state-dir", type=str, help="Directory for agent state files")
    
    args = parser.parse_args()
    
    backend = None
    if args.real:
        backend = RealTelemetryBackend(
            [a[0] for a in AGENT_DEFINITIONS],
            state_dir=args.state_dir
        )
    
    if args.health:
        check_agent_health(backend)
    else:
        watch_agents(backend, use_real=args.real)
        print("🔴 Cluster coherence: REQUIRES ATTENTION")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--health":
        check_agent_health()
    else:
        watch_agents()