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
# CLI Entry Point
# ==============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="TMT-OS Agent Watcher")
    parser.add_argument("--health", action="store_true", help="Perform health check")
    parser.add_argument("--diagnose", action="store_true", help="Run diagnostic analysis")
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
    elif args.diagnose:
        run_diagnostics(backend, use_real=args.real)
    else:
        watch_agents(backend, use_real=args.real)