"""
Wing Occlusion Package

Geometric occlusion transforms inspired by butterfly wing interference patterns.
"""

from .geometry import (
    generate_fibonacci_spiral,
    compute_distance_to_spirals,
    occlude_points,
    recover_points,
    compute_recovery_error,
    PHI,
)

from .metrics import (
    compute_reconstruction_mae,
    compute_hidden_fraction,
    compute_distance_preservation,
    compute_structural_preservation,
    compute_runtime_metrics,
)

from .models import (
    WingInterferenceEncoder,
    ConsciousnessLatentEncoder,
    train_autoencoder,
    compute_wing_consciousness_metrics,
)

__version__ = '1.0.0'
__all__ = [
    # Geometry
    'generate_fibonacci_spiral',
    'compute_distance_to_spirals',
    'occlude_points',
    'recover_points',
    'compute_recovery_error',
    'PHI',
    
    # Metrics
    'compute_reconstruction_mae',
    'compute_hidden_fraction',
    'compute_distance_preservation',
    'compute_structural_preservation',
    'compute_runtime_metrics',
    
    # Models
    'WingInterferenceEncoder',
    'ConsciousnessLatentEncoder',
    'train_autoencoder',
    'compute_wing_consciousness_metrics',
]
