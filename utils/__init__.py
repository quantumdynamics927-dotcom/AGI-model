"""
Utility modules for AGI MODEL project

Contains:
- golden_ratio_callback: Golden ratio optimization and tracking
- performance_monitor: Comprehensive training metrics monitoring
"""

from .golden_ratio_callback import GoldenRatioCallback, phi_regularization_loss
from .performance_monitor import PerformanceMonitor

__all__ = [
    'GoldenRatioCallback',
    'phi_regularization_loss',
    'PerformanceMonitor'
]
