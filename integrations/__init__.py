"""
Integrations module for AGI-model.

This module contains adapters for external systems and services.
"""

from .cybershield_adapter import ingest_scan_file, ingest_scan_payload

__all__ = ['ingest_scan_file', 'ingest_scan_payload']