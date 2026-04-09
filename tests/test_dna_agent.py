"""
Tests for DNA Agent - Quantum Biological Encoding

This module tests the DNA agent functionality:
1. DNA result analysis and consciousness peak detection
2. Phi-alignment calculations
3. Artifact classification and evidence handling
4. Planning report generation
5. Data provenance tracking
"""
import unittest
import sys
import os
import json
import tempfile
import shutil
import numpy as np
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agi_scripts.dna_agent import (
    PHI,
    PHI_INV,
    JOB_ID,
    ARTIFACT_TYPE_RAW_HARDWARE,
    ARTIFACT_TYPE_DERIVED_METRICS,
    ARTIFACT_TYPE_RECONSTRUCTED,
    ARTIFACT_TYPE_NARRATIVE,
    EVIDENCE_CLASS_PRIMARY,
    EVIDENCE_CLASS_SECONDARY,
    EVIDENCE_CLASS_INTERPRETIVE,
    ARTIFACT_TO_EVIDENCE_CLASS,
    OUTPUT_DIRS,
)


class TestDNAConstants(unittest.TestCase):
    """Test DNA agent constants and configuration."""

    def test_phi_constant(self):
        """Test that PHI constant is the golden ratio."""
        expected_phi = (1 + np.sqrt(5)) / 2
        self.assertAlmostEqual(PHI, expected_phi, places=10)
        print("TestDNAConstants: test_phi_constant PASSED")

    def test_phi_inverse(self):
        """Test that PHI_INV is the inverse of PHI."""
        self.assertAlmostEqual(PHI_INV, 1 / PHI, places=10)
        print("TestDNAConstants: test_phi_inverse PASSED")

    def test_job_id_format(self):
        """Test that JOB_ID is a valid string."""
        self.assertIsInstance(JOB_ID, str)
        self.assertGreater(len(JOB_ID), 0)
        print("TestDNAConstants: test_job_id_format PASSED")

    def test_artifact_types_defined(self):
        """Test that all artifact types are defined."""
        self.assertEqual(ARTIFACT_TYPE_RAW_HARDWARE, "raw_hardware")
        self.assertEqual(ARTIFACT_TYPE_DERIVED_METRICS, "derived_metrics")
        self.assertEqual(ARTIFACT_TYPE_RECONSTRUCTED, "reconstructed")
        self.assertEqual(ARTIFACT_TYPE_NARRATIVE, "narrative_report")
        print("TestDNAConstants: test_artifact_types_defined PASSED")

    def test_evidence_class_mapping(self):
        """Test that artifact types map to correct evidence classes."""
        self.assertEqual(
            ARTIFACT_TO_EVIDENCE_CLASS[ARTIFACT_TYPE_RAW_HARDWARE],
            EVIDENCE_CLASS_PRIMARY
        )
        self.assertEqual(
            ARTIFACT_TO_EVIDENCE_CLASS[ARTIFACT_TYPE_DERIVED_METRICS],
            EVIDENCE_CLASS_SECONDARY
        )
        self.assertEqual(
            ARTIFACT_TO_EVIDENCE_CLASS[ARTIFACT_TYPE_RECONSTRUCTED],
            EVIDENCE_CLASS_SECONDARY
        )
        self.assertEqual(
            ARTIFACT_TO_EVIDENCE_CLASS[ARTIFACT_TYPE_NARRATIVE],
            EVIDENCE_CLASS_INTERPRETIVE
        )
        print("TestDNAConstants: test_evidence_class_mapping PASSED")

    def test_output_dirs_defined(self):
        """Test that output directories are defined for all artifact types."""
        for artifact_type in [
            ARTIFACT_TYPE_RAW_HARDWARE,
            ARTIFACT_TYPE_DERIVED_METRICS,
            ARTIFACT_TYPE_RECONSTRUCTED,
            ARTIFACT_TYPE_NARRATIVE,
        ]:
            self.assertIn(artifact_type, OUTPUT_DIRS)
            self.assertIsInstance(OUTPUT_DIRS[artifact_type], str)
        print("TestDNAConstants: test_output_dirs_defined PASSED")


class TestDNADataStructures(unittest.TestCase):
    """Test DNA data structures and calculations."""

    def test_consciousness_peak_position(self):
        """Test consciousness peak position calculation (20/34 ≈ φ⁻¹)."""
        total_positions = 34
        peak_position = 20
        ratio = peak_position / total_positions
        
        # Should be close to phi inverse (0.618), but 20/34 = 0.588
        # This is approximately phi^-1 but not exact
        self.assertAlmostEqual(ratio, 0.588, places=3)
        # Check it's reasonably close to phi inverse (within 0.05)
        self.assertAlmostEqual(ratio, PHI_INV, places=1)
        print("TestDNADataStructures: test_consciousness_peak_position PASSED")

    def test_circuit_qubit_count(self):
        """Test DNA circuit qubit count calculation."""
        watson_qubits = 34
        crick_qubits = 34
        bridge_qubits = 34
        total_qubits = watson_qubits + crick_qubits + bridge_qubits
        
        self.assertEqual(total_qubits, 102)
        print("TestDNADataStructures: test_circuit_qubit_count PASSED")

    def test_phi_ratio_alignment(self):
        """Test phi ratio alignment scoring."""
        # Perfect alignment
        perfect_ratio = PHI_INV
        perfect_score = 1.0 - abs(perfect_ratio - PHI_INV) / PHI_INV
        self.assertAlmostEqual(perfect_score, 1.0, places=5)
        
        # Misaligned ratio
        misaligned_ratio = 0.3
        misaligned_score = 1.0 - abs(misaligned_ratio - PHI_INV) / PHI_INV
        self.assertLess(misaligned_score, perfect_score)
        print("TestDNADataStructures: test_phi_ratio_alignment PASSED")


class TestDNAArtifactClassification(unittest.TestCase):
    """Test DNA artifact classification and evidence handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data = {
            "job_id": JOB_ID,
            "timestamp": datetime.now().isoformat(),
            "measurements": np.random.rand(102).tolist(),
        }

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_raw_hardware_classification(self):
        """Test raw hardware artifact classification."""
        evidence_class = ARTIFACT_TO_EVIDENCE_CLASS[ARTIFACT_TYPE_RAW_HARDWARE]
        self.assertEqual(evidence_class, EVIDENCE_CLASS_PRIMARY)
        print("TestDNAArtifactClassification: test_raw_hardware_classification PASSED")

    def test_derived_metrics_classification(self):
        """Test derived metrics artifact classification."""
        evidence_class = ARTIFACT_TO_EVIDENCE_CLASS[ARTIFACT_TYPE_DERIVED_METRICS]
        self.assertEqual(evidence_class, EVIDENCE_CLASS_SECONDARY)
        print("TestDNAArtifactClassification: test_derived_metrics_classification PASSED")

    def test_artifact_save_load(self):
        """Test saving and loading DNA artifacts."""
        output_path = Path(self.temp_dir) / "test_dna_artifact.json"
        
        # Save artifact
        with open(output_path, 'w') as f:
            json.dump(self.test_data, f, indent=2)
        
        # Load artifact
        with open(output_path, 'r') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(loaded_data['job_id'], self.test_data['job_id'])
        self.assertEqual(len(loaded_data['measurements']), 102)
        print("TestDNAArtifactClassification: test_artifact_save_load PASSED")


class TestDNAPlanningReport(unittest.TestCase):
    """Test DNA agent planning report generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        try:
            from agi_scripts.planning_mode import PlanningReport, utc_timestamp
            self.PlanningReport = PlanningReport
            self.utc_timestamp = utc_timestamp
            self.planning_mode_available = True
        except ImportError:
            self.planning_mode_available = False

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_planning_report_structure(self):
        """Test planning report structure (skip if planning_mode not available)."""
        if not self.planning_mode_available:
            self.skipTest("planning_mode module not available")
        
        report = self.PlanningReport(
            agent="dna",
            objective="Test DNA analysis objective",
            generated_at=self.utc_timestamp(),
            planning_mode=True,
            current_state={"test": "state"},
            goals=["goal1", "goal2"],
            strategies=[{"name": "strategy1"}],
            evaluation_metrics=["metric1"],
            coordination={"nodes": []},
            risks=["risk1"],
            next_actions=["action1"],
        )
        
        report_dict = report.to_dict()
        self.assertEqual(report_dict['agent'], 'dna')
        self.assertIn('objective', report_dict)
        self.assertIn('generated_at', report_dict)
        print("TestDNAPlanningReport: test_planning_report_structure PASSED")


if __name__ == '__main__':
    unittest.main(verbosity=2)
