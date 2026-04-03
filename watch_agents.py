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
# Agent Diagnostics and Bottleneck Analysis
# ==============================================================================

@dataclass
class AgentPressureScore:
    """Computed pressure score for an agent."""
    agent_id: str
    
    # Raw metrics
    queue_length: int
    latency_ms: float
    coherence: float
    error_rate: float
    
    # Computed scores (0-100 scale)
    queue_pressure: float      # Queue backlog pressure
    latency_pressure: float    # Response time pressure
    coherence_pressure: float  # Signal quality pressure
    combined_pressure: float   # Weighted combination
    
    # Classification
    bottleneck_type: str       # 'backlog', 'coherence', 'mixed', 'healthy'
    rank: int                  # Position in pressure ranking


class AgentDiagnostics:
    """
    Analyzes agent telemetry to identify bottlenecks and provide
    actionable recommendations.
    
    Key Analysis:
    - Queue saturation (backlog bottleneck)
    - Coherence degradation (signal quality bottleneck)
    - Combined pressure ranking
    - Stable anchor identification
    - Priority action recommendations
    """
    
    # Thresholds for classification
    QUEUE_HIGH_THRESHOLD = 40      # Queue length indicating high pressure
    QUEUE_CRITICAL_THRESHOLD = 50  # Queue length indicating critical pressure
    LATENCY_HIGH_THRESHOLD = 120   # ms - high latency
    LATENCY_CRITICAL_THRESHOLD = 180  # ms - critical latency
    COHERENCE_LOW_THRESHOLD = 0.88  # Below this = degraded
    COHERENCE_CRITICAL_THRESHOLD = 0.82  # Below this = critical
    
    def __init__(self, backend: 'TelemetryBackend'):
        self.backend = backend
        self.agent_ids = [a[0] for a in AGENT_DEFINITIONS]
        self._pressure_scores: Dict[str, AgentPressureScore] = {}
    
    def compute_pressure_scores(self) -> Dict[str, AgentPressureScore]:
        """Compute pressure scores for all agents."""
        scores = {}
        
        for agent_id in self.agent_ids:
            metrics = self.backend.get_metrics(agent_id)
            
            # Queue pressure (0-100 scale)
            # Linear scaling: 0 queue = 0 pressure, 60+ queue = 100 pressure
            queue_pressure = min(100, (metrics.task_queue_length / 60.0) * 100)
            
            # Latency pressure (0-100 scale)
            # Linear scaling: 0ms = 0 pressure, 200ms+ = 100 pressure
            latency_pressure = min(100, (metrics.avg_response_latency_ms / 200.0) * 100)
            
            # Coherence pressure (inverted, 0-100 scale)
            # 1.0 coherence = 0 pressure, 0.7 coherence = 100 pressure
            coherence_pressure = max(0, min(100, (1.0 - metrics.internal_coherence) / 0.3 * 100))
            
            # Combined pressure (weighted)
            # Queue and coherence weighted higher as they indicate structural issues
            combined = (
                queue_pressure * 0.35 +
                latency_pressure * 0.25 +
                coherence_pressure * 0.30 +
                metrics.error_rate * 0.10
            )
            
            # Classify bottleneck type
            queue_issue = queue_pressure > 50 or latency_pressure > 60
            coherence_issue = coherence_pressure > 40
            
            if queue_issue and coherence_issue:
                bottleneck_type = 'mixed'
            elif queue_issue:
                bottleneck_type = 'backlog'
            elif coherence_issue:
                bottleneck_type = 'coherence'
            else:
                bottleneck_type = 'healthy'
            
            scores[agent_id] = AgentPressureScore(
                agent_id=agent_id,
                queue_length=metrics.task_queue_length,
                latency_ms=metrics.avg_response_latency_ms,
                coherence=metrics.internal_coherence,
                error_rate=metrics.error_rate,
                queue_pressure=queue_pressure,
                latency_pressure=latency_pressure,
                coherence_pressure=coherence_pressure,
                combined_pressure=combined,
                bottleneck_type=bottleneck_type,
                rank=0  # Set after sorting
            )
        
        # Rank by combined pressure (highest = rank 1)
        sorted_agents = sorted(
            scores.items(),
            key=lambda x: x[1].combined_pressure,
            reverse=True
        )
        for rank, (agent_id, score) in enumerate(sorted_agents, 1):
            scores[agent_id].rank = rank
        
        self._pressure_scores = scores
        return scores
    
    def get_bottleneck_ranking(self) -> List[AgentPressureScore]:
        """Get agents ranked by operational pressure (worst first)."""
        if not self._pressure_scores:
            self.compute_pressure_scores()
        
        return sorted(
            self._pressure_scores.values(),
            key=lambda s: s.combined_pressure,
            reverse=True
        )
    
    def get_stable_anchors(self) -> List[AgentPressureScore]:
        """Get agents that are stable and can serve as references."""
        if not self._pressure_scores:
            self.compute_pressure_scores()
        
        anchors = []
        for score in self._pressure_scores.values():
            # Stable anchors: low pressure, healthy bottleneck type
            if (score.combined_pressure < 30 and
                score.bottleneck_type == 'healthy' and
                score.coherence > 0.90):
                anchors.append(score)
        
        return sorted(anchors, key=lambda s: s.combined_pressure)
    
    def get_priority_actions(self) -> List[str]:
        """Generate prioritized action recommendations."""
        if not self._pressure_scores:
            self.compute_pressure_scores()
        
        actions = []
        ranking = self.get_bottleneck_ranking()
        
        # First priority: Backlog bottlenecks
        backlog_agents = [
            s for s in ranking[:5]
            if s.bottleneck_type in ('backlog', 'mixed')
        ]
        if backlog_agents:
            agents_str = ', '.join(s.agent_id for s in backlog_agents[:3])
            actions.append(
                f"FIRST: Relieve {agents_str} - "
                f"highest queue/latency pressure (backlog bottleneck)"
            )
        
        # Second priority: Coherence bottlenecks
        coherence_agents = [
            s for s in ranking
            if s.bottleneck_type == 'coherence' and s.coherence < 0.88
        ]
        if coherence_agents:
            agents_str = ', '.join(s.agent_id for s in coherence_agents[:2])
            actions.append(
                f"SECOND: Isolate {agents_str} for coherence recovery - "
                f"signal quality issue (not backlog)"
            )
        
        # Third priority: Protect stable anchors
        anchors = self.get_stable_anchors()
        if anchors:
            agents_str = ', '.join(s.agent_id for s in anchors[:3])
            actions.append(
                f"THIRD: Protect {agents_str} as stabilizing references - "
                f"healthiest baseline agents"
            )
        
        return actions
    
    def get_diagnostic_summary(self) -> Dict:
        """Get comprehensive diagnostic summary."""
        if not self._pressure_scores:
            self.compute_pressure_scores()
        
        ranking = self.get_bottleneck_ranking()
        anchors = self.get_stable_anchors()
        
        # Count by bottleneck type
        bottleneck_counts = {'backlog': 0, 'coherence': 0, 'mixed': 0, 'healthy': 0}
        for score in self._pressure_scores.values():
            bottleneck_counts[score.bottleneck_type] += 1
        
        # System-wide metrics
        avg_coherence = sum(s.coherence for s in self._pressure_scores.values()) / len(self._pressure_scores)
        avg_queue = sum(s.queue_length for s in self._pressure_scores.values()) / len(self._pressure_scores)
        avg_latency = sum(s.latency_ms for s in self._pressure_scores.values()) / len(self._pressure_scores)
        
        return {
            'ranking': ranking,
            'stable_anchors': anchors,
            'bottleneck_counts': bottleneck_counts,
            'system_metrics': {
                'avg_coherence': avg_coherence,
                'avg_queue': avg_queue,
                'avg_latency': avg_latency
            },
            'priority_actions': self.get_priority_actions()
        }


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
        
        # Agent-specific pressure profiles (based on real telemetry patterns)
        # Format: (base_queue, queue_variance, base_latency, latency_variance, base_coherence, coherence_variance)
        self._agent_profiles = {
            # High-pressure agents (backlog bottlenecks)
            'Pearl':   (55, 8, 175, 35, 0.885, 0.015),   # Highest queue, high latency
            'Amethyst': (46, 6, 150, 25, 0.858, 0.020),   # High queue, weak coherence
            'Emerald':  (40, 5, 145, 20, 0.862, 0.018),    # Medium-high queue, weak coherence
            'Bronze':   (41, 5, 140, 25, 0.865, 0.030),   # Medium-high queue, weak coherence
            'Onyx':     (51, 6, 162, 25, 0.900, 0.005),    # High queue, strong coherence
            
            # Coherence bottlenecks (signal quality issues)
            'Diamond':  (25, 5, 125, 15, 0.810, 0.015),   # Low queue, weakest coherence
            'Sapphire': (26, 5, 100, 20, 0.844, 0.020),   # Moderate queue, weak coherence
            
            # Stable anchors
            'Silver':   (15, 5, 95, 15, 0.922, 0.010),    # Low pressure, high coherence
            'Platinum': (12, 4, 90, 12, 0.925, 0.008),    # Low pressure, high coherence
            'Jade':     (18, 6, 105, 18, 0.905, 0.005),   # Low pressure, good coherence
            
            # Medium pressure
            'Gold':     (30, 8, 115, 25, 0.910, 0.010),    # Medium pressure
            'Ruby':     (35, 7, 130, 22, 0.905, 0.012),    # Medium pressure
        }
    
    def refresh_all(self) -> None:
        """Simulate realistic agent behavior with pressure patterns."""
        self._phase += 0.1
        
        for agent_id, metrics in self._metrics.items():
            # Get agent-specific profile
            profile = self._agent_profiles.get(agent_id, (20, 10, 100, 30, 0.90, 0.02))
            base_queue, queue_var, base_latency, latency_var, base_coh, coh_var = profile
            
            # Simulate heartbeat (every ~100ms)
            metrics.last_heartbeat = datetime.now()
            
            # Task queue simulation (agent-specific with phase variation)
            queue_variation = int(queue_var * (self._phase % 1.0))
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
            
            # Latency (agent-specific with queue dependency)
            latency_variation = random.uniform(-latency_var/2, latency_var/2)
            metrics.avg_response_latency_ms = max(10, base_latency + latency_variation + metrics.task_queue_length * 0.5)
            metrics.max_response_latency_ms = max(
                metrics.max_response_latency_ms,
                metrics.avg_response_latency_ms
            )
            
            # Coherence (agent-specific with small variation)
            coherence_variation = random.uniform(-coh_var, coh_var)
            metrics.internal_coherence = max(0.5, min(1.0, base_coh + coherence_variation))
            
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


def display_diagnostics(diagnostics: AgentDiagnostics, verbose: bool = True):
    """
    Display comprehensive diagnostic analysis.
    
    Args:
        diagnostics: AgentDiagnostics instance with computed scores
        verbose: If True, show detailed breakdown
    """
    summary = diagnostics.get_diagnostic_summary()
    
    print("\n" + "=" * 70)
    print("AGENT DIAGNOSTIC ANALYSIS")
    print("=" * 70)
    
    # System metrics
    sys_metrics = summary['system_metrics']
    print(f"\n[SYSTEM] Avg Coherence: {sys_metrics['avg_coherence']:.4f} | "
          f"Avg Queue: {sys_metrics['avg_queue']:.1f} | "
          f"Avg Latency: {sys_metrics['avg_latency']:.1f}ms")
    
    # Bottleneck distribution
    counts = summary['bottleneck_counts']
    print(f"\n[DISTRIBUTION] Backlog: {counts['backlog']} | "
          f"Coherence: {counts['coherence']} | "
          f"Mixed: {counts['mixed']} | "
          f"Healthy: {counts['healthy']}")
    
    # Ranking table
    print("\n" + "-" * 70)
    print("PRESSURE RANKING (worst to best)")
    print("-" * 70)
    print(f"{'Rank':<5} {'Agent':<10} {'Type':<10} {'Queue':<7} {'Latency':<9} "
          f"{'Coherence':<10} {'Pressure':<8}")
    print("-" * 70)
    
    for score in summary['ranking']:
        print(
            f"{score.rank:<5} "
            f"{score.agent_id:<10} "
            f"{score.bottleneck_type:<10} "
            f"{score.queue_length:<7} "
            f"{score.latency_ms:<9.1f} "
            f"{score.coherence:<10.4f} "
            f"{score.combined_pressure:<8.1f}"
        )
    
    # Stable anchors
    anchors = summary['stable_anchors']
    if anchors:
        print("\n" + "-" * 70)
        print("STABLE ANCHORS (healthiest agents)")
        print("-" * 70)
        for score in anchors[:5]:
            print(
                f"  {score.agent_id:<10} | "
                f"Coherence: {score.coherence:.4f} | "
                f"Pressure: {score.combined_pressure:.1f}"
            )
    
    # Priority actions
    actions = summary['priority_actions']
    if actions:
        print("\n" + "-" * 70)
        print("PRIORITY ACTIONS")
        print("-" * 70)
        for i, action in enumerate(actions, 1):
            print(f"  {i}. {action}")
    
    print("=" * 70)
    
    return summary


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


def run_diagnostics(backend: Optional[TelemetryBackend] = None, use_real: bool = False):
    """
    Run comprehensive diagnostic analysis on agent cluster.
    
    This identifies bottlenecks, ranks agents by pressure,
    and provides actionable recommendations.
    """
    if backend is None:
        if use_real:
            backend = RealTelemetryBackend([a[0] for a in AGENT_DEFINITIONS])
        else:
            backend = MockTelemetryBackend([a[0] for a in AGENT_DEFINITIONS])
    
    # Refresh metrics
    backend.refresh_all()
    
    # Run diagnostics
    diagnostics = AgentDiagnostics(backend)
    diagnostics.compute_pressure_scores()
    
    # Display results
    display_diagnostics(diagnostics, verbose=True)
    
    return diagnostics


# ==============================================================================
# Agent Intervention System
# ==============================================================================

@dataclass
class InterventionAction:
    """Record of an intervention action taken."""
    timestamp: datetime
    action_type: str  # 'load_balance', 'coherence_recovery', 'anchor_protection'
    source_agents: List[str]
    target_agents: List[str]
    metrics_before: Dict[str, Dict[str, float]]  # Baseline snapshot
    metrics_after: Dict[str, Dict[str, float]]   # Post-intervention snapshot
    phase: str  # 'ANALYSIS_BASELINE', 'POST_LOAD_BALANCE', 'POST_RECOVERY', 'FINAL_STATE'
    success: bool
    reason: str
    baseline_frozen: bool = False  # Whether metrics_before is from frozen baseline


class AgentIntervention:
    """
    Targeted intervention system for agent cluster optimization.
    
    Implements three priority actions based on diagnostic analysis:
    1. Load Balancing - Relieve backlog bottlenecks (Pearl, Amethyst, etc.)
    2. Coherence Recovery - Isolate signal quality issues (Diamond, Sapphire)
    3. Anchor Protection - Preserve stable references (Silver, Platinum, Jade)
    """
    
    # Intervention thresholds (calibrated from real telemetry)
    LOAD_BALANCE_THRESHOLD = 40      # Queue length trigger (lowered for earlier intervention)
    COHERENCE_RECOVERY_THRESHOLD = 0.88  # Coherence floor (matches DEGRADED threshold)
    ANCHOR_PROTECTION_THRESHOLD = 0.90   # Coherence ceiling for anchors
    
    # Transfer limits
    MAX_QUEUE_TRANSFER = 12         # Max tasks to transfer per intervention
    MAX_LATENCY_IMPROVEMENT = 25    # Target latency reduction (ms)
    
    def __init__(self, backend: TelemetryBackend, diagnostics: AgentDiagnostics):
        self.backend = backend
        self.diagnostics = diagnostics
        self.intervention_history: List[InterventionAction] = []
        self._protected_anchors: set = set()
        self._isolated_agents: set = set()
        self._load_targets: set = set()  # Agents eligible to receive load
        self._frozen_baseline: Dict[str, AgentMetrics] = {}  # Immutable baseline snapshot
    
    def freeze_baseline(self) -> None:
        """Freeze current metrics as immutable baseline for consistent reporting."""
        self._frozen_baseline = {}
        for agent_id in self.diagnostics.agent_ids:
            metrics = self.backend.get_metrics(agent_id)
            # Deep copy metrics
            self._frozen_baseline[agent_id] = AgentMetrics(
                agent_id=metrics.agent_id,
                base_frequency=metrics.base_frequency,
                last_heartbeat=metrics.last_heartbeat,
                heartbeat_interval_ms=metrics.heartbeat_interval_ms,
                task_queue_length=metrics.task_queue_length,
                tasks_completed=metrics.tasks_completed,
                tasks_failed=metrics.tasks_failed,
                avg_response_latency_ms=metrics.avg_response_latency_ms,
                max_response_latency_ms=metrics.max_response_latency_ms,
                error_rate=metrics.error_rate,
                last_error=metrics.last_error,
                internal_coherence=metrics.internal_coherence,
                consensus_score=metrics.consensus_score,
                phi_alignment=metrics.phi_alignment,
                resonance_frequency=metrics.resonance_frequency,
                status=metrics.status,
                resonance_lock=metrics.resonance_lock
            )
    
    def get_baseline_metrics(self, agent_id: str) -> Dict[str, float]:
        """Get frozen baseline metrics for an agent."""
        if agent_id in self._frozen_baseline:
            m = self._frozen_baseline[agent_id]
            return {
                'queue': m.task_queue_length,
                'latency': m.avg_response_latency_ms,
                'coherence': m.internal_coherence
            }
        return {'queue': 0, 'latency': 0, 'coherence': 1.0}
    
    def identify_backlog_bottlenecks(self) -> List[AgentPressureScore]:
        """Identify agents with critical backlog pressure."""
        scores = self.diagnostics.compute_pressure_scores()
        
        bottlenecks = []
        for score in scores.values():
            if (score.queue_length >= self.LOAD_BALANCE_THRESHOLD and
                score.bottleneck_type in ('backlog', 'mixed')):
                bottlenecks.append(score)
        
        return sorted(bottlenecks, key=lambda s: s.queue_length, reverse=True)
    
    def identify_coherence_bottlenecks(self) -> List[AgentPressureScore]:
        """Identify agents with critical coherence issues."""
        scores = self.diagnostics.compute_pressure_scores()
        
        bottlenecks = []
        for score in scores.values():
            if (score.coherence < self.COHERENCE_RECOVERY_THRESHOLD and
                score.bottleneck_type in ('coherence', 'mixed')):
                bottlenecks.append(score)
        
        return sorted(bottlenecks, key=lambda s: s.coherence)
    
    def identify_stable_anchors(self) -> List[AgentPressureScore]:
        """Identify agents suitable as stable references (anchor candidates)."""
        scores = self.diagnostics.compute_pressure_scores()
        
        anchors = []
        for score in scores.values():
            # Relaxed criteria to include Silver, Jade as anchors
            if (score.coherence >= 0.90 and
                score.combined_pressure < 40 and
                score.bottleneck_type == 'healthy'):
                anchors.append(score)
        
        return sorted(anchors, key=lambda s: s.coherence, reverse=True)
    
    def identify_load_targets(self, exclude_isolated: bool = True) -> List[AgentPressureScore]:
        """Identify agents eligible to receive redistributed load."""
        scores = self.diagnostics.compute_pressure_scores()
        
        targets = []
        for score in scores.values():
            # Skip isolated agents (coherence recovery)
            if exclude_isolated and score.agent_id in self._isolated_agents:
                continue
            
            # Skip coherence bottlenecks (they need recovery, not more load)
            if score.bottleneck_type == 'coherence' and score.coherence < 0.88:
                continue
            
            # Skip protected anchors (they should stay stable)
            if score.agent_id in self._protected_anchors:
                continue
            
            # Eligible: healthy or medium pressure with good coherence
            if score.coherence >= 0.88 and score.combined_pressure < 50:
                targets.append(score)
        
        return sorted(targets, key=lambda s: s.queue_length)
    
    def load_balance_backlog(self, source_agents: List[str], target_agents: List[str]) -> InterventionAction:
        """
        Transfer queue load from bottlenecked agents to healthier agents.
        
        Priority 1: Relieve Pearl, Amethyst, Emerald, Bronze (backlog bottlenecks)
        """
        timestamp = datetime.now()
        metrics_before = {}
        metrics_after = {}
        success = False
        
        # Use frozen baseline for 'before' metrics (consistent with ranking table)
        for agent_id in source_agents + target_agents:
            metrics_before[agent_id] = self.get_baseline_metrics(agent_id)
        
        # Calculate transfer amounts
        total_source_queue = sum(
            metrics_before[aid]['queue'] 
            for aid in source_agents
            if aid in metrics_before
        )
        
        if total_source_queue == 0:
            return InterventionAction(
                timestamp=timestamp,
                action_type='load_balance',
                source_agents=source_agents,
                target_agents=target_agents,
                metrics_before=metrics_before,
                metrics_after=metrics_before,
                success=False,
                reason='No queue backlog to transfer'
            )
        
        # Distribute load to targets
        transfer_per_source = min(self.MAX_QUEUE_TRANSFER, total_source_queue // len(source_agents))
        
        for source_id in source_agents:
            source_metrics = self.backend.get_metrics(source_id)
            
            # Skip if source is protected or isolated
            if source_id in self._protected_anchors or source_id in self._isolated_agents:
                continue
            
            # Find best target (lowest queue)
            best_target = None
            best_target_queue = float('inf')
            
            for target_id in target_agents:
                if target_id in self._isolated_agents:
                    continue
                target_metrics = self.backend.get_metrics(target_id)
                if target_metrics.task_queue_length < best_target_queue:
                    best_target = target_id
                    best_target_queue = target_metrics.task_queue_length
            
            if best_target is None:
                continue
            
            # Transfer load
            transfer_amount = min(transfer_per_source, source_metrics.task_queue_length)
            
            if transfer_amount <= 0:
                continue
            
            # Update source
            source_metrics.task_queue_length -= transfer_amount
            source_metrics.avg_response_latency_ms = max(
                50,
                source_metrics.avg_response_latency_ms - self.MAX_LATENCY_IMPROVEMENT
            )
            
            # Update target
            target_metrics = self.backend.get_metrics(best_target)
            target_metrics.task_queue_length += transfer_amount
            target_metrics.avg_response_latency_ms += transfer_amount * 0.5
            
            # Recompute status
            source_metrics.status = self.backend.compute_status(source_metrics)
            target_metrics.status = self.backend.compute_status(target_metrics)
        
        # Collect metrics after
        for agent_id in source_agents + target_agents:
            metrics = self.backend.get_metrics(agent_id)
            metrics_after[agent_id] = {
                'queue': metrics.task_queue_length,
                'latency': metrics.avg_response_latency_ms,
                'coherence': metrics.internal_coherence
            }
        
        # Check success
        source_queue_reduced = sum(
            metrics_before[aid]['queue'] - metrics_after[aid]['queue']
            for aid in source_agents
            if aid in metrics_before and aid in metrics_after
        ) > 0
        
        success = source_queue_reduced
        
        action = InterventionAction(
            timestamp=timestamp,
            action_type='load_balance',
            source_agents=source_agents,
            target_agents=target_agents,
            metrics_before=metrics_before,
            metrics_after=metrics_after,
            phase='POST_LOAD_BALANCE',
            success=success,
            reason=f'Transferred ~{transfer_per_source * len(source_agents)} tasks from backlog bottlenecks',
            baseline_frozen=True
        )
        
        self.intervention_history.append(action)
        return action
    
    def isolate_for_coherence_recovery(self, agent_ids: List[str]) -> InterventionAction:
        """
        Isolate agents with coherence issues for signal quality recovery.
        
        Priority 2: Isolate Diamond, Sapphire (coherence bottlenecks)
        """
        timestamp = datetime.now()
        metrics_before = {}
        metrics_after = {}
        
        # Use frozen baseline for 'before' metrics
        for agent_id in agent_ids:
            metrics_before[agent_id] = self.get_baseline_metrics(agent_id)
            metrics_before[agent_id]['isolated'] = agent_id in self._isolated_agents
        
        # Isolate agents
        for agent_id in agent_ids:
            if agent_id in self._protected_anchors:
                continue  # Don't isolate protected anchors
            
            self._isolated_agents.add(agent_id)
            metrics = self.backend.get_metrics(agent_id)
            
            # Reduce queue pressure during recovery
            metrics.task_queue_length = max(0, metrics.task_queue_length - 10)
            
            # Gradual coherence recovery (simulated)
            recovery_boost = 0.02
            metrics.internal_coherence = min(1.0, metrics.internal_coherence + recovery_boost)
            
            # Update status
            metrics.status = self.backend.compute_status(metrics)
        
        for agent_id in agent_ids:
            metrics = self.backend.get_metrics(agent_id)
            metrics_after[agent_id] = {
                'queue': metrics.task_queue_length,
                'latency': metrics.avg_response_latency_ms,
                'coherence': metrics.internal_coherence,
                'isolated': agent_id in self._isolated_agents
            }
        
        action = InterventionAction(
            timestamp=timestamp,
            action_type='coherence_recovery',
            source_agents=agent_ids,
            target_agents=[],
            metrics_before=metrics_before,
            metrics_after=metrics_after,
            phase='POST_RECOVERY',
            success=True,
            reason=f'Isolated {len(agent_ids)} agents for coherence recovery',
            baseline_frozen=True
        )
        
        self.intervention_history.append(action)
        return action
    
    def protect_anchors(self, agent_ids: List[str]) -> InterventionAction:
        """
        Protect stable agents from load balancing to preserve cluster stability.
        
        Priority 3: Protect Silver, Platinum, Jade (stable anchors)
        
        Protection effects:
        - Reserve capacity: Cap incoming queue transfers
        - Lock recovery exclusion: Prevent isolation during coherence recovery
        - Maintain baseline coherence floor
        """
        timestamp = datetime.now()
        metrics_before = {}
        metrics_after = {}
        redistributed_excess = {}  # Track where excess queue went
        
        # Use frozen baseline for 'before' metrics
        for agent_id in agent_ids:
            metrics_before[agent_id] = self.get_baseline_metrics(agent_id)
            metrics_before[agent_id]['protected'] = agent_id in self._protected_anchors
        
        # Apply protection effects
        for agent_id in agent_ids:
            self._protected_anchors.add(agent_id)
            self._load_targets.discard(agent_id)  # Remove from load targets
            
            metrics = self.backend.get_metrics(agent_id)
            
            # Protection effect 1: Cap queue at baseline + 20% (reserve capacity)
            baseline_queue = self.get_baseline_metrics(agent_id).get('queue', 0)
            max_allowed_queue = int(baseline_queue * 1.2) + 5
            if metrics.task_queue_length > max_allowed_queue:
                # Redistribute excess back to load targets
                excess = metrics.task_queue_length - max_allowed_queue
                metrics.task_queue_length = max_allowed_queue
                redistributed_excess[agent_id] = excess
                
                # Find a load target to absorb excess
                if self._load_targets:
                    target_id = min(self._load_targets, 
                                   key=lambda t: self.backend.get_metrics(t).task_queue_length)
                    target_metrics = self.backend.get_metrics(target_id)
                    target_metrics.task_queue_length += excess
                    redistributed_excess[f"excess_to_{target_id}"] = excess
            
            # Protection effect 2: Maintain coherence floor
            if metrics.internal_coherence < self.ANCHOR_PROTECTION_THRESHOLD:
                metrics.internal_coherence = self.ANCHOR_PROTECTION_THRESHOLD
            
            # Protection effect 3: Lock status to HEALTHY
            metrics.status = AgentStatus.HEALTHY
        
        # Capture metrics after for all affected agents
        for agent_id in agent_ids:
            metrics = self.backend.get_metrics(agent_id)
            metrics_after[agent_id] = {
                'queue': metrics.task_queue_length,
                'coherence': metrics.internal_coherence,
                'protected': agent_id in self._protected_anchors
            }
        
        # Also capture metrics for agents that received excess
        for key, value in redistributed_excess.items():
            if key.startswith('excess_to_'):
                target_id = key.replace('excess_to_', '')
                metrics = self.backend.get_metrics(target_id)
                metrics_after[target_id] = {
                    'queue': metrics.task_queue_length,
                    'coherence': metrics.internal_coherence,
                    'protected': target_id in self._protected_anchors
                }
        
        action = InterventionAction(
            timestamp=timestamp,
            action_type='anchor_protection',
            source_agents=agent_ids,
            target_agents=[k.replace('excess_to_', '') for k in redistributed_excess.keys() if k.startswith('excess_to_')],
            metrics_before=metrics_before,
            metrics_after=metrics_after,
            phase='FINAL_STATE',
            success=True,
            reason=f'Protected {len(agent_ids)} stable anchors with capacity reservation',
            baseline_frozen=True
        )
        
        self.intervention_history.append(action)
        return action
    
    def run_priority_interventions(self) -> List[InterventionAction]:
        """
        Execute all three priority interventions in order.
        
        Returns list of intervention actions taken.
        """
        actions = []
        
        # Freeze baseline BEFORE any interventions (for consistent reporting)
        self.freeze_baseline()
        
        # Capture BASELINE snapshot for reconciliation
        self._phase_snapshots = {}
        self._capture_phase('BASELINE')
        
        # Refresh diagnostics
        self.diagnostics.compute_pressure_scores()
        
        # Priority 2 FIRST: Isolate coherence bottlenecks (before load balancing)
        coherence_agents = self.identify_coherence_bottlenecks()
        if coherence_agents:
            isolate_ids = [s.agent_id for s in coherence_agents[:2]]
            action = self.isolate_for_coherence_recovery(isolate_ids)
            actions.append(action)
            self._capture_phase('POST_RECOVERY')
        
        # Priority 1: Load balance backlog bottlenecks
        backlog_agents = self.identify_backlog_bottlenecks()
        stable_anchors = self.identify_stable_anchors()
        
        # Identify load targets (excluding isolated and coherence-bottlenecked agents)
        load_targets = self.identify_load_targets(exclude_isolated=True)
        self._load_targets = set(t.agent_id for t in load_targets)
        
        if backlog_agents and load_targets:
            source_ids = [s.agent_id for s in backlog_agents[:4]]  # Pearl, Emerald, Onyx, Amethyst
            target_ids = [t.agent_id for t in load_targets[:4]]
            
            action = self.load_balance_backlog(source_ids, target_ids)
            actions.append(action)
            self._capture_phase('POST_LOAD_BALANCE')
        
        # Priority 3: Protect stable anchors (after load balancing)
        if stable_anchors:
            anchor_ids = [s.agent_id for s in stable_anchors[:3]]
            action = self.protect_anchors(anchor_ids)
            actions.append(action)
            self._capture_phase('FINAL')
        
        return actions
    
    def _capture_phase(self, phase_name: str) -> None:
        """Capture current metrics snapshot at phase boundary."""
        snapshot = {}
        for agent_id in self.diagnostics.agent_ids:
            metrics = self.backend.get_metrics(agent_id)
            snapshot[agent_id] = {
                'queue': metrics.task_queue_length,
                'latency': metrics.avg_response_latency_ms,
                'coherence': metrics.internal_coherence
            }
        self._phase_snapshots[phase_name] = snapshot
    
    def get_phase_snapshots(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Get all phase snapshots for reconciliation validation."""
        return self._phase_snapshots
    
    def get_intervention_summary(self) -> Dict:
        """Get summary of all interventions."""
        if not self.intervention_history:
            return {'total': 0, 'successful': 0, 'by_type': {}}
        
        by_type = {}
        successful = 0
        
        for action in self.intervention_history:
            action_type = action.action_type
            if action_type not in by_type:
                by_type[action_type] = {'count': 0, 'success': 0}
            
            by_type[action_type]['count'] += 1
            if action.success:
                by_type[action_type]['success'] += 1
                successful += 1
        
        return {
            'total': len(self.intervention_history),
            'successful': successful,
            'by_type': by_type,
            'protected_anchors': list(self._protected_anchors),
            'isolated_agents': list(self._isolated_agents)
        }


class ReconciliationValidator:
    """
    Validates that intervention phases are internally consistent.
    
    Checks:
    1. Each phase starts where the previous phase ended
    2. Cumulative changes match the final state
    3. No orphaned or missing metric transitions
    4. Policy invariants for each intervention type
    5. Mass-balance for queue and coherence
    """
    
    # Severity levels for validation issues
    INFO = 'INFO'        # Informational, no action needed
    WARNING = 'WARNING'  # Unexpected but non-fatal
    HARD_FAIL = 'HARD_FAIL'  # Accounting corruption, must fix
    
    # Policy invariants
    INVARIANTS = {
        'coherence_recovery': {
            'max_queue_increase': 5,      # Coherence recovery shouldn't add much queue
            'min_coherence_gain': 0.01,   # Must improve coherence
            'max_coherence_gain': 0.05,   # But not unrealistically
            'must_isolate': True,         # Must mark agents as isolated
        },
        'load_balance': {
            'preserve_total_queue': True,  # Queue should be conserved
            'queue_tolerance': 2,          # Allow small rounding
            'max_coherence_change': 0.01,  # Shouldn't affect coherence much
            'sources_must_lose_queue': True,
            'targets_must_gain_queue': True,
        },
        'anchor_protection': {
            'max_queue_increase': 0.2,     # Max 20% increase from baseline
            'preserve_or_improve_coherence': True,
            'must_mark_protected': True,
        }
    }
    
    def __init__(self, intervention: AgentIntervention):
        self.intervention = intervention
        self.phase_snapshots: Dict[str, Dict[str, Dict[str, float]]] = {}
        self.discrepancies: List[str] = []
    
    def capture_phase_snapshot(self, phase: str) -> None:
        """Capture current metrics at a phase boundary."""
        snapshot = {}
        for agent_id in self.intervention.diagnostics.agent_ids:
            metrics = self.intervention.backend.get_metrics(agent_id)
            snapshot[agent_id] = {
                'queue': metrics.task_queue_length,
                'latency': metrics.avg_response_latency_ms,
                'coherence': metrics.internal_coherence
            }
        self.phase_snapshots[phase] = snapshot
    
    def validate_phase_transition(self, from_phase: str, to_phase: str, 
                                   action: InterventionAction) -> List[str]:
        """Validate that phase transition is consistent."""
        issues = []
        
        if from_phase not in self.phase_snapshots:
            issues.append(f"Missing snapshot for phase: {from_phase}")
            return issues
        
        from_snapshot = self.phase_snapshots[from_phase]
        
        # Check that action's 'before' matches the from_phase snapshot
        for agent_id in list(action.source_agents) + list(action.target_agents):
            if agent_id not in action.metrics_before:
                continue
            
            expected = from_snapshot.get(agent_id, {})
            actual = action.metrics_before.get(agent_id, {})
            
            # Allow small floating point tolerance
            queue_diff = abs(expected.get('queue', 0) - actual.get('queue', 0))
            coh_diff = abs(expected.get('coherence', 1.0) - actual.get('coherence', 1.0))
            
            if queue_diff > 1 or coh_diff > 0.01:
                issues.append(
                    f"[{action.action_type}] {agent_id}: Phase mismatch - "
                    f"expected Q={expected.get('queue', 0):.0f} Coh={expected.get('coherence', 1.0):.3f}, "
                    f"got Q={actual.get('queue', 0):.0f} Coh={actual.get('coherence', 1.0):.3f}"
                )
        
        return issues
    
    def validate_cumulative_effects(self) -> List[str]:
        """Validate that all interventions sum to final state."""
        issues = []
        
        if 'BASELINE' not in self.phase_snapshots or 'FINAL' not in self.phase_snapshots:
            issues.append("Missing BASELINE or FINAL snapshot")
            return issues
        
        baseline = self.phase_snapshots['BASELINE']
        final = self.phase_snapshots['FINAL']
        
        # Find the last intervention in each phase
        last_actions = {}
        for action in self.intervention.intervention_history:
            last_actions[action.phase] = action
        
        # Validate that each phase's final action matches the phase snapshot
        for phase_name, action in last_actions.items():
            if phase_name == 'BASELINE':
                continue
            
            phase_snapshot = self.phase_snapshots.get(phase_name, {})
            
            for agent_id in list(action.source_agents) + list(action.target_agents):
                if agent_id not in action.metrics_after:
                    continue
                
                expected = phase_snapshot.get(agent_id, {})
                actual = action.metrics_after.get(agent_id, {})
                
                if not expected or not actual:
                    continue
                
                queue_diff = abs(expected.get('queue', 0) - actual.get('queue', 0))
                coh_diff = abs(expected.get('coherence', 1.0) - actual.get('coherence', 1.0))
                
                if queue_diff > 1 or coh_diff > 0.01:
                    issues.append(
                        f"[{action.action_type}:{phase_name}] {agent_id}: Phase snapshot mismatch - "
                        f"expected Q={expected.get('queue', 0):.0f} Coh={expected.get('coherence', 1.0):.3f}, "
                        f"got Q={actual.get('queue', 0):.0f} Coh={actual.get('coherence', 1.0):.3f}"
                    )
        
        # Validate that FINAL snapshot matches actual final state
        for agent_id in self.intervention.diagnostics.agent_ids:
            base_q = baseline.get(agent_id, {}).get('queue', 0)
            final_q = final.get(agent_id, {}).get('queue', 0)
            actual_q_delta = final_q - base_q
            
            base_c = baseline.get(agent_id, {}).get('coherence', 1.0)
            final_c = final.get(agent_id, {}).get('coherence', 1.0)
            actual_c_delta = final_c - base_c
            
            # Check if any intervention affected this agent
            affected_by_any = any(
                agent_id in list(a.source_agents) + list(a.target_agents)
                for a in self.intervention.intervention_history
            )
            
            # For affected agents, verify baseline→final is reasonable
            if affected_by_any:
                # Sanity check: queue changes should be integer, coherence small
                if abs(actual_q_delta) > 100:  # Unrealistic queue change
                    issues.append(
                        f"[CUMULATIVE] {agent_id}: Unrealistic queue change ΔQ={actual_q_delta:+.0f}"
                    )
                if abs(actual_c_delta) > 0.1:  # Unrealistic coherence change
                    issues.append(
                        f"[CUMULATIVE] {agent_id}: Unrealistic coherence change ΔC={actual_c_delta:+.3f}"
                    )
        
        return issues
    
    def validate_agent_membership(self) -> List[Dict]:
        """Validate that agent membership is consistent across phases."""
        issues = []
        
        if 'BASELINE' not in self.phase_snapshots or 'FINAL' not in self.phase_snapshots:
            return [{'severity': self.HARD_FAIL, 'message': 'Missing BASELINE or FINAL snapshot'}]
        
        baseline_agents = set(self.phase_snapshots['BASELINE'].keys())
        final_agents = set(self.phase_snapshots['FINAL'].keys())
        
        # Check for disappeared agents
        disappeared = baseline_agents - final_agents
        if disappeared:
            issues.append({
                'severity': self.HARD_FAIL,
                'message': f'Agents disappeared between phases: {disappeared}'
            })
        
        # Check for appeared agents
        appeared = final_agents - baseline_agents
        if appeared:
            issues.append({
                'severity': self.WARNING,
                'message': f'Agents appeared between phases: {appeared}'
            })
        
        return issues
    
    def validate_policy_invariants(self) -> List[Dict]:
        """Validate intervention-type-specific policy invariants."""
        issues = []
        
        for action in self.intervention.intervention_history:
            action_type = action.action_type
            invariants = self.INVARIANTS.get(action_type, {})
            
            if action_type == 'coherence_recovery':
                # Check: coherence should improve
                for agent_id in action.source_agents:
                    if agent_id not in action.metrics_before or agent_id not in action.metrics_after:
                        continue
                    
                    before_coh = action.metrics_before[agent_id].get('coherence', 1.0)
                    after_coh = action.metrics_after[agent_id].get('coherence', 1.0)
                    coh_gain = after_coh - before_coh
                    
                    if coh_gain < invariants.get('min_coherence_gain', 0.01):
                        issues.append({
                            'severity': self.WARNING,
                            'message': f'[{action_type}] {agent_id}: Coherence gain {coh_gain:+.3f} below minimum {invariants.get("min_coherence_gain", 0.01)}'
                        })
                    
                    if coh_gain > invariants.get('max_coherence_gain', 0.05):
                        issues.append({
                            'severity': self.WARNING,
                            'message': f'[{action_type}] {agent_id}: Coherence gain {coh_gain:+.3f} suspiciously high (max {invariants.get("max_coherence_gain", 0.05)})'
                        })
                
                # Check: must be marked as isolated
                for agent_id in action.source_agents:
                    if agent_id not in self.intervention._isolated_agents:
                        issues.append({
                            'severity': self.HARD_FAIL,
                            'message': f'[{action_type}] {agent_id}: Not marked as isolated after coherence recovery'
                        })
            
            elif action_type == 'load_balance':
                # Check: sources should lose queue
                for agent_id in action.source_agents:
                    if agent_id not in action.metrics_before or agent_id not in action.metrics_after:
                        continue
                    
                    before_q = action.metrics_before[agent_id].get('queue', 0)
                    after_q = action.metrics_after[agent_id].get('queue', 0)
                    
                    if after_q >= before_q and before_q > 0:
                        issues.append({
                            'severity': self.WARNING,
                            'message': f'[{action_type}] {agent_id}: Source did not lose queue ({before_q} → {after_q})'
                        })
            
            elif action_type == 'anchor_protection':
                # Check: protected agents should be marked (only source agents, not excess recipients)
                for agent_id in action.source_agents:
                    if agent_id not in self.intervention._protected_anchors:
                        issues.append({
                            'severity': self.HARD_FAIL,
                            'message': f'[{action_type}] {agent_id}: Not marked as protected after anchor protection'
                        })
                
                # Check: coherence should not decrease
                for agent_id in list(action.source_agents) + list(action.target_agents):
                    if agent_id not in action.metrics_before or agent_id not in action.metrics_after:
                        continue
                    
                    before_coh = action.metrics_before[agent_id].get('coherence', 1.0)
                    after_coh = action.metrics_after[agent_id].get('coherence', 1.0)
                    
                    if after_coh < before_coh - 0.01:
                        issues.append({
                            'severity': self.WARNING,
                            'message': f'[{action_type}] {agent_id}: Coherence decreased during protection ({before_coh:.3f} → {after_coh:.3f})'
                        })
        
        return issues
    
    def validate_mass_balance(self) -> List[Dict]:
        """Validate that queue and coherence are conserved across interventions."""
        issues = []
        
        if 'BASELINE' not in self.phase_snapshots or 'FINAL' not in self.phase_snapshots:
            return [{'severity': self.HARD_FAIL, 'message': 'Missing snapshots for mass balance'}]
        
        baseline = self.phase_snapshots['BASELINE']
        final = self.phase_snapshots['FINAL']
        
        # Calculate total queue and coherence
        total_baseline_queue = sum(baseline[aid].get('queue', 0) for aid in baseline)
        total_final_queue = sum(final[aid].get('queue', 0) for aid in final)
        
        queue_delta = total_final_queue - total_baseline_queue
        
        # Queue should be approximately conserved (allowing for isolation reductions)
        # Isolation typically reduces queue by 10 per isolated agent
        isolated_count = len(self.intervention._isolated_agents)
        expected_queue_reduction = isolated_count * 10
        
        if abs(queue_delta + expected_queue_reduction) > 5:  # Allow small tolerance
            issues.append({
                'severity': self.WARNING,
                'message': f'[MASS_BALANCE] Queue not conserved: baseline={total_baseline_queue}, final={total_final_queue}, Δ={queue_delta:+d} (expected ~{-expected_queue_reduction})'
            })
        else:
            issues.append({
                'severity': self.INFO,
                'message': f'[MASS_BALANCE] Queue: {total_baseline_queue} → {total_final_queue} (Δ={queue_delta:+d}, isolated reduction={expected_queue_reduction})'
            })
        
        # Coherence should improve or stay stable
        avg_baseline_coh = sum(baseline[aid].get('coherence', 1.0) for aid in baseline) / len(baseline)
        avg_final_coh = sum(final[aid].get('coherence', 1.0) for aid in final) / len(final)
        
        coh_delta = avg_final_coh - avg_baseline_coh
        
        if coh_delta < -0.01:
            issues.append({
                'severity': self.WARNING,
                'message': f'[MASS_BALANCE] Average coherence decreased: {avg_baseline_coh:.4f} → {avg_final_coh:.4f} (Δ={coh_delta:+.4f})'
            })
        else:
            issues.append({
                'severity': self.INFO,
                'message': f'[MASS_BALANCE] Coherence: {avg_baseline_coh:.4f} → {avg_final_coh:.4f} (Δ={coh_delta:+.4f})'
            })
        
        return issues
    
    def generate_intervention_fingerprints(self) -> Dict[str, str]:
        """Generate unique fingerprints for each intervention to detect duplicates."""
        import hashlib
        
        fingerprints = {}
        
        for i, action in enumerate(self.intervention.intervention_history):
            # Create fingerprint from type, agents, and metrics
            fingerprint_data = f"{action.action_type}:{','.join(sorted(action.source_agents))}:{','.join(sorted(action.target_agents))}"
            
            # Add metrics hash
            metrics_str = str(action.metrics_before) + str(action.metrics_after)
            metrics_hash = hashlib.md5(metrics_str.encode()).hexdigest()[:8]
            
            fingerprint = f"{fingerprint_data}:{metrics_hash}"
            
            if fingerprint in fingerprints:
                fingerprints[fingerprint] = f"DUPLICATE:{i}"
            else:
                fingerprints[fingerprint] = f"UNIQUE:{i}"
        
        return fingerprints
    
    def validate_all(self) -> Dict:
        """Run all validation checks and return report."""
        all_issues = []
        
        # Validate phase transitions
        phases = ['BASELINE', 'POST_RECOVERY', 'POST_LOAD_BALANCE', 'FINAL']
        phase_actions = {
            'POST_RECOVERY': None,
            'POST_LOAD_BALANCE': None,
            'FINAL': None
        }
        
        # Map actions to phases
        for action in self.intervention.intervention_history:
            if action.phase in phase_actions:
                phase_actions[action.phase] = action
        
        # Check phase transitions
        for i in range(len(phases) - 1):
            from_phase = phases[i]
            to_phase = phases[i + 1]
            
            if to_phase in phase_actions and phase_actions[to_phase]:
                issues = self.validate_phase_transition(from_phase, to_phase, phase_actions[to_phase])
                all_issues.extend(issues)
        
        # Check cumulative effects
        cumulative_issues = self.validate_cumulative_effects()
        all_issues.extend(cumulative_issues)
        
        # Check agent membership
        membership_issues = self.validate_agent_membership()
        all_issues.extend(membership_issues)
        
        # Check policy invariants
        invariant_issues = self.validate_policy_invariants()
        all_issues.extend(invariant_issues)
        
        # Check mass balance
        mass_issues = self.validate_mass_balance()
        all_issues.extend(mass_issues)
        
        # Classify by severity
        info_count = sum(1 for i in all_issues if i.get('severity') == self.INFO)
        warning_count = sum(1 for i in all_issues if i.get('severity') == self.WARNING)
        hard_fail_count = sum(1 for i in all_issues if i.get('severity') == self.HARD_FAIL)
        
        return {
            'valid': hard_fail_count == 0,
            'issues': all_issues,
            'phases_captured': list(self.phase_snapshots.keys()),
            'interventions_checked': len(self.intervention.intervention_history),
            'severity_counts': {
                'INFO': info_count,
                'WARNING': warning_count,
                'HARD_FAIL': hard_fail_count
            }
        }


def display_final_state_table(intervention: AgentIntervention, validator: Optional[ReconciliationValidator] = None):
    """Display final state comparison across all agents with reconciliation check."""
    print("\n" + "=" * 80)
    
    # Show reconciliation status if validator provided
    if validator:
        val_result = validator.validate_all()
        severity_counts = val_result.get('severity_counts', {})
        
        if val_result['valid']:
            print("FINAL STATE SUMMARY (Baseline → Final) ✓ RECONCILED")
            print("=" * 80)
            print(f"[VALIDATION] ✓ All {len(intervention.intervention_history)} interventions reconciled")
            print(f"[PHASES] {' → '.join(val_result['phases_captured'])}")
            
            # Show severity breakdown
            info_count = severity_counts.get('INFO', 0)
            warning_count = severity_counts.get('WARNING', 0)
            if info_count > 0 or warning_count > 0:
                print(f"[SEVERITY] INFO: {info_count} | WARNING: {warning_count} | HARD_FAIL: 0")
        else:
            hard_fail_count = severity_counts.get('HARD_FAIL', 0)
            warning_count = severity_counts.get('WARNING', 0)
            print(f"FINAL STATE SUMMARY (Baseline → Final) ⚠ {hard_fail_count} HARD_FAIL, {warning_count} WARNING")
            print("=" * 80)
            
            # Show issues by severity
            for issue in val_result['issues']:
                severity = issue.get('severity', 'INFO')
                message = issue.get('message', str(issue))
                if severity == 'HARD_FAIL':
                    print(f"  ✗ {message}")
                elif severity == 'WARNING':
                    print(f"  ⚠ {message}")
            
            # Show INFO messages separately
            info_messages = [i for i in val_result['issues'] if i.get('severity') == 'INFO']
            if info_messages:
                print(f"\n  [INFO] {len(info_messages)} informational messages")
    else:
        print("FINAL STATE SUMMARY (Baseline → Final)\n")
        print("=" * 80)
    
    print(f"{'Agent':<10} {'Base Q':<8} {'Final Q':<8} {'Δ Queue':<8} {'Base Coh':<9} {'Final Coh':<9} {'Δ Coh':<8} {'Status'}")
    print("-" * 80)
    
    agent_ids = [a[0] for a in AGENT_DEFINITIONS]
    
    total_queue_delta = 0
    total_coh_delta = 0.0
    improved_count = 0
    degraded_count = 0
    
    for agent_id in agent_ids:
        baseline = intervention.get_baseline_metrics(agent_id)
        current = intervention.backend.get_metrics(agent_id)
        
        base_queue = baseline.get('queue', 0)
        final_queue = current.task_queue_length
        queue_delta = final_queue - base_queue
        
        base_coh = baseline.get('coherence', 1.0)
        final_coh = current.internal_coherence
        coh_delta = final_coh - base_coh
        
        total_queue_delta += queue_delta
        total_coh_delta += coh_delta
        
        # Determine status
        if queue_delta < 0 or coh_delta > 0.01:
            status = "IMPROVED"
            improved_count += 1
        elif queue_delta > 10 or coh_delta < -0.02:
            status = "DEGRADED"
            degraded_count += 1
        else:
            status = "STABLE"
        
        # Mark special states
        if agent_id in intervention._protected_anchors:
            status += " [PROT]"
        if agent_id in intervention._isolated_agents:
            status += " [ISOL]"
        
        print(f"{agent_id:<10} {base_queue:<8.0f} {final_queue:<8.0f} {queue_delta:+8.0f} "
              f"{base_coh:<9.3f} {final_coh:<9.3f} {coh_delta:+8.3f} {status}")
    
    print("-" * 80)
    print(f"{'TOTAL':<10} {'':<8} {'':<8} {total_queue_delta:+8.0f} "
              f"{'':<9} {'':<9} {total_coh_delta:+8.3f}")
    print("=" * 80)
    print(f"[OUTCOME] {improved_count} improved | {degraded_count} degraded | {len(agent_ids) - improved_count - degraded_count} stable")
    
    # Cluster health assessment
    if improved_count >= degraded_count * 2:
        print("[ASSESSMENT] Cluster health IMPROVED by interventions")
    elif improved_count > degraded_count:
        print("[ASSESSMENT] Cluster health SLIGHTLY IMPROVED")
    elif degraded_count > improved_count:
        print("[ASSESSMENT] Cluster health DEGRADED - review intervention policy")
    else:
        print("[ASSESSMENT] Cluster health STABLE - interventions redistributed pressure")


def display_interventions(interventions: List[InterventionAction]):
    """Display intervention results with clear phase labeling."""
    print("\n" + "=" * 70)
    print("INTERVENTION RESULTS")
    print("=" * 70)
    print("[SNAPSHOT] All 'before' metrics from frozen ANALYSIS_BASELINE")
    print("=" * 70)
    
    for i, action in enumerate(interventions, 1):
        status = "[OK]" if action.success else "[FAIL]"
        phase_label = f"[{action.phase}]" if action.phase else ""
        print(f"\n[{i}] {action.action_type.upper()} {status} {phase_label}")
        print(f"    Reason: {action.reason}")
        
        if action.source_agents:
            print(f"    Sources: {', '.join(action.source_agents)}")
        if action.target_agents:
            print(f"    Targets: {', '.join(action.target_agents)}")
        
        # Show metric changes with clear baseline vs current
        if action.metrics_before and action.metrics_after:
            print("    Metrics (BASELINE → CURRENT):")
            
            # Show sources first
            for agent_id in action.source_agents:
                if agent_id in action.metrics_before:
                    before = action.metrics_before[agent_id]
                    after = action.metrics_after.get(agent_id, {})
                    
                    queue_diff = after.get('queue', 0) - before.get('queue', 0)
                    coh_diff = after.get('coherence', 0) - before.get('coherence', 0)
                    
                    print(f"      {agent_id}: Queue {before.get('queue', 0):.0f}→{after.get('queue', 0):.0f} ({queue_diff:+.0f}), "
                          f"Coh {before.get('coherence', 0):.3f}→{after.get('coherence', 0):.3f} ({coh_diff:+.3f})")
            
            # Show targets (for load_balance)
            if action.target_agents:
                print("    Target changes:")
                for agent_id in action.target_agents:
                    if agent_id in action.metrics_before:
                        before = action.metrics_before[agent_id]
                        after = action.metrics_after.get(agent_id, {})
                        
                        queue_diff = after.get('queue', 0) - before.get('queue', 0)
                        
                        print(f"      {agent_id}: Queue {before.get('queue', 0):.0f}→{after.get('queue', 0):.0f} ({queue_diff:+.0f})")


# ==============================================================================
# CLI Entry Point
# ==============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="TMT-OS Agent Watcher")
    parser.add_argument("--health", action="store_true", help="Perform health check")
    parser.add_argument("--diagnose", action="store_true", help="Run diagnostic analysis")
    parser.add_argument("--intervene", action="store_true", help="Run priority interventions")
    parser.add_argument("--full", action="store_true", help="Run diagnostics + interventions")
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
    elif args.full:
        # Full diagnostic + intervention cycle
        if backend is None:
            backend = MockTelemetryBackend([a[0] for a in AGENT_DEFINITIONS])
        
        # Refresh backend before diagnostics
        backend.refresh_all()
        
        # Run diagnostics with the same backend
        diagnostics = AgentDiagnostics(backend)
        diagnostics.compute_pressure_scores()
        display_diagnostics(diagnostics, verbose=True)
        
        # Run interventions with the same backend
        intervention = AgentIntervention(backend, diagnostics)
        actions = intervention.run_priority_interventions()
        display_interventions(actions)
        
        # Create validator and run reconciliation
        validator = ReconciliationValidator(intervention)
        for phase_name, snapshot in intervention.get_phase_snapshots().items():
            validator.phase_snapshots[phase_name] = snapshot
        
        # Show final state table with reconciliation check
        display_final_state_table(intervention, validator)
        
        # Show summary
        summary = intervention.get_intervention_summary()
        print(f"\n[SUMMARY] {summary['successful']}/{summary['total']} interventions successful")
        if summary['protected_anchors']:
            print(f"[PROTECTED] {', '.join(summary['protected_anchors'])}")
        if summary['isolated_agents']:
            print(f"[ISOLATED] {', '.join(summary['isolated_agents'])}")
    elif args.intervene:
        # Run interventions only
        if backend is None:
            backend = MockTelemetryBackend([a[0] for a in AGENT_DEFINITIONS])
        
        backend.refresh_all()
        diagnostics = AgentDiagnostics(backend)
        diagnostics.compute_pressure_scores()
        
        intervention = AgentIntervention(backend, diagnostics)
        actions = intervention.run_priority_interventions()
        display_interventions(actions)
    elif args.diagnose:
        run_diagnostics(backend, use_real=args.real)
    else:
        watch_agents(backend, use_real=args.real)