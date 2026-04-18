"""
Tesseract Governance Module

Tracks and logs tesseract-based cognitive routing for benchmarking and debugging.
Records transition paths, confidence metrics, and system health.
"""

import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class RouteStep:
    """Single step in a cognitive routing path"""
    timestamp: float
    vertex_id: int
    vertex_name: str
    confidence: float
    latency_ms: float
    transition_score: Optional[float] = None
    quantum_score: Optional[float] = None
    error: Optional[str] = None

@dataclass
class RouteSession:
    """Complete routing session with all steps"""
    session_id: str
    start_time: float
    end_time: float
    route_path: List[RouteStep]
    total_latency_ms: float
    success: bool
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TesseractGovernance:
    """Governance system for tesseract-based cognitive routing"""
    
    def __init__(self, log_dir: str = "route_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.current_session: Optional[RouteSession] = None
        self.route_history: List[RouteSession] = []
        
    def start_route_session(self, session_id: Optional[str] = None) -> str:
        """
        Start a new routing session.
        
        Args:
            session_id: Optional custom session ID
            
        Returns:
            Session ID
        """
        if session_id is None:
            session_id = f"route_{int(time.time() * 1000)}"
            
        self.current_session = RouteSession(
            session_id=session_id,
            start_time=time.time(),
            end_time=0.0,
            route_path=[],
            total_latency_ms=0.0,
            success=True,
            error=None,
            metadata={}
        )
        
        logger.info(f"Started route session: {session_id}")
        return session_id
        
    def log_route_step(self, step: RouteStep):
        """
        Log a single step in the current routing session.
        
        Args:
            step: Route step to log
        """
        if self.current_session is None:
            logger.warning("No active route session, step not logged")
            return
            
        self.current_session.route_path.append(step)
        self.current_session.total_latency_ms += step.latency_ms
        
        logger.debug(f"Logged route step: {step.vertex_id} ({step.vertex_name})")
        
    def end_route_session(self, success: bool = True, error: Optional[str] = None):
        """
        End the current routing session.
        
        Args:
            success: Whether the session completed successfully
            error: Error message if session failed
        """
        if self.current_session is None:
            logger.warning("No active route session to end")
            return
            
        self.current_session.end_time = time.time()
        self.current_session.success = success
        self.current_session.error = error
        
        # Add to history
        self.route_history.append(self.current_session)
        
        # Save to file
        self._save_session(self.current_session)
        
        logger.info(f"Ended route session: {self.current_session.session_id} "
                   f"(success: {success}, steps: {len(self.current_session.route_path)})")
        
        # Clear current session
        self.current_session = None
        
    def _save_session(self, session: RouteSession):
        """Save route session to file"""
        try:
            filename = self.log_dir / f"{session.session_id}.json"
            session_dict = asdict(session)
            
            # Convert numpy types if present
            self._convert_numpy_types(session_dict)
            
            with open(filename, 'w') as f:
                json.dump(session_dict, f, indent=2)
                
            logger.debug(f"Saved route session to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save route session: {e}")
            
    def _convert_numpy_types(self, obj):
        """Recursively convert numpy types to native Python types"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if hasattr(value, 'item'):  # numpy scalar
                    obj[key] = value.item()
                else:
                    self._convert_numpy_types(value)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if hasattr(item, 'item'):  # numpy scalar
                    obj[i] = item.item()
                else:
                    self._convert_numpy_types(item)
                    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about route sessions"""
        if not self.route_history:
            return {"message": "No route sessions recorded"}
            
        total_sessions = len(self.route_history)
        successful_sessions = sum(1 for s in self.route_history if s.success)
        failed_sessions = total_sessions - successful_sessions
        
        # Calculate average path length for successful sessions
        successful_paths = [s for s in self.route_history if s.success]
        if successful_paths:
            avg_path_length = sum(len(s.route_path) for s in successful_paths) / len(successful_paths)
        else:
            avg_path_length = 0
            
        # Calculate average latency
        if successful_paths:
            avg_latency = sum(s.total_latency_ms for s in successful_paths) / len(successful_paths)
        else:
            avg_latency = 0
            
        return {
            "total_sessions": total_sessions,
            "successful_sessions": successful_sessions,
            "failed_sessions": failed_sessions,
            "success_rate": successful_sessions / total_sessions if total_sessions > 0 else 0,
            "average_path_length": avg_path_length,
            "average_latency_ms": avg_latency
        }
        
    def get_recent_sessions(self, count: int = 10) -> List[RouteSession]:
        """Get most recent route sessions"""
        return self.route_history[-count:] if self.route_history else []
        
    def analyze_routing_patterns(self) -> Dict[str, Any]:
        """Analyze common routing patterns and vertex usage"""
        if not self.route_history:
            return {"message": "No route sessions recorded"}
            
        # Count vertex visits
        vertex_visits = {}
        transition_counts = {}
        
        for session in self.route_history:
            if not session.success:
                continue
                
            previous_vertex = None
            for step in session.route_path:
                # Count vertex visits
                vertex_visits[step.vertex_id] = vertex_visits.get(step.vertex_id, 0) + 1
                
                # Count transitions
                if previous_vertex is not None:
                    transition = (previous_vertex, step.vertex_id)
                    transition_counts[transition] = transition_counts.get(transition, 0) + 1
                    
                previous_vertex = step.vertex_id
                
        # Find most visited vertices
        most_visited = sorted(vertex_visits.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Find most common transitions
        most_common_transitions = sorted(transition_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "vertex_visits": vertex_visits,
            "transition_counts": transition_counts,
            "most_visited_vertices": most_visited,
            "most_common_transitions": most_common_transitions
        }
        
    def export_benchmark_data(self, filename: str = "routing_benchmark.json"):
        """Export data for benchmarking analysis"""
        benchmark_data = {
            "sessions": [asdict(session) for session in self.route_history],
            "statistics": self.get_session_stats(),
            "patterns": self.analyze_routing_patterns()
        }
        
        # Convert numpy types
        self._convert_numpy_types(benchmark_data)
        
        # Save to file
        filepath = self.log_dir / filename
        with open(filepath, 'w') as f:
            json.dump(benchmark_data, f, indent=2)
            
        logger.info(f"Exported benchmark data to {filepath}")
        return str(filepath)

# Example usage
if __name__ == "__main__":
    # Create governance system
    governance = TesseractGovernance()
    
    # Start session
    session_id = governance.start_route_session("test_route_001")
    
    # Log some route steps
    import random
    for i in range(5):
        step = RouteStep(
            timestamp=time.time(),
            vertex_id=i,
            vertex_name=f"Vertex_{i}",
            confidence=random.random(),
            latency_ms=random.uniform(10, 100),
            transition_score=random.random(),
            quantum_score=random.random()
        )
        governance.log_route_step(step)
        
    # End session
    governance.end_route_session(success=True)
    
    # Show statistics
    stats = governance.get_session_stats()
    print(f"Session statistics: {stats}")
    
    # Show patterns
    patterns = governance.analyze_routing_patterns()
    print(f"Routing patterns: {patterns}")