"""
Tests for Planning Mode - AGI Agent Planning System

This module tests the planning mode functionality:
1. Planning report generation
2. UTC timestamp generation
3. Report serialization
4. Agent coordination
5. Goal and strategy management
"""
import unittest
import sys
import os
import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from agi_scripts.planning_mode import (
        PlanningReport,
        utc_timestamp,
        write_planning_report,
    )
    PLANNING_MODE_AVAILABLE = True
except ImportError:
    PLANNING_MODE_AVAILABLE = False


@unittest.skipIf(not PLANNING_MODE_AVAILABLE, "planning_mode module not available")
class TestUTCTimestamp(unittest.TestCase):
    """Tests for utc_timestamp function."""

    def test_timestamp_format(self):
        """Test that timestamp is in ISO format."""
        timestamp = utc_timestamp()
        self.assertIsInstance(timestamp, str)
        
        # Should be parseable as ISO format
        try:
            datetime.fromisoformat(timestamp)
        except ValueError:
            self.fail("Timestamp is not in valid ISO format")
        
        print("TestUTCTimestamp: test_timestamp_format PASSED")

    def test_timestamp_is_utc(self):
        """Test that timestamp includes UTC timezone info."""
        timestamp = utc_timestamp()
        # Should contain timezone indicator
        self.assertIn('+00:00', timestamp)
        print("TestUTCTimestamp: test_timestamp_is_utc PASSED")

    def test_timestamp_monotonic(self):
        """Test that timestamps are monotonically increasing."""
        ts1 = utc_timestamp()
        # Small delay to ensure different timestamps
        import time
        time.sleep(0.01)
        ts2 = utc_timestamp()
        
        # Second timestamp should be greater or equal
        self.assertGreaterEqual(ts2, ts1)
        print("TestUTCTimestamp: test_timestamp_monotonic PASSED")


@unittest.skipIf(not PLANNING_MODE_AVAILABLE, "planning_mode module not available")
class TestPlanningReport(unittest.TestCase):
    """Tests for PlanningReport dataclass."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.sample_report = PlanningReport(
            agent="test_agent",
            objective="Test objective for planning report",
            generated_at=utc_timestamp(),
            planning_mode=True,
            current_state={
                "status": "active",
                "progress": 0.5,
                "resources": ["resource1", "resource2"],
            },
            goals=[
                "Goal 1: Complete task A",
                "Goal 2: Achieve outcome B",
                "Goal 3: Optimize metric C",
            ],
            strategies=[
                {
                    "name": "Strategy 1",
                    "description": "First approach",
                    "priority": 1,
                },
                {
                    "name": "Strategy 2",
                    "description": "Alternative approach",
                    "priority": 2,
                },
            ],
            evaluation_metrics=[
                "Accuracy",
                "Efficiency",
                "Consciousness alignment",
            ],
            coordination={
                "nodes": ["node1", "node2"],
                "communication_protocol": "quantum_entanglement",
            },
            risks=[
                "Risk 1: Resource depletion",
                "Risk 2: Decoherence",
            ],
            next_actions=[
                "Action 1: Initialize subsystem",
                "Action 2: Run diagnostics",
            ],
        )

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_report_initialization(self):
        """Test that PlanningReport initializes with all fields."""
        self.assertEqual(self.sample_report.agent, "test_agent")
        self.assertIn("objective", self.sample_report.objective)
        self.assertTrue(self.sample_report.planning_mode)
        print("TestPlanningReport: test_report_initialization PASSED")

    def test_report_to_dict(self):
        """Test that report can be converted to dictionary."""
        report_dict = self.sample_report.to_dict()
        
        self.assertIsInstance(report_dict, dict)
        self.assertEqual(report_dict['agent'], 'test_agent')
        self.assertEqual(len(report_dict['goals']), 3)
        self.assertEqual(len(report_dict['strategies']), 2)
        self.assertIn('coordination', report_dict)
        print("TestPlanningReport: test_report_to_dict PASSED")

    def test_report_serialization(self):
        """Test that report can be serialized to JSON."""
        report_dict = self.sample_report.to_dict()
        
        # Should be JSON serializable
        try:
            json_str = json.dumps(report_dict, indent=2)
            self.assertIsInstance(json_str, str)
            
            # Should be deserializable
            loaded_dict = json.loads(json_str)
            self.assertEqual(loaded_dict['agent'], 'test_agent')
        except (TypeError, json.JSONDecodeError) as e:
            self.fail(f"Failed to serialize/deserialize report: {e}")
        
        print("TestPlanningReport: test_report_serialization PASSED")

    def test_report_structure_completeness(self):
        """Test that report contains all required fields."""
        report_dict = self.sample_report.to_dict()
        
        required_fields = [
            'agent', 'objective', 'generated_at', 'planning_mode',
            'current_state', 'goals', 'strategies', 'evaluation_metrics',
            'coordination', 'risks', 'next_actions',
        ]
        
        for field in required_fields:
            self.assertIn(field, report_dict, f"Missing required field: {field}")
        
        print("TestPlanningReport: test_report_structure_completeness PASSED")


@unittest.skipIf(not PLANNING_MODE_AVAILABLE, "planning_mode module not available")
class TestWritePlanningReport(unittest.TestCase):
    """Tests for write_planning_report function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.sample_report = PlanningReport(
            agent="test_agent",
            objective="Test objective",
            generated_at=utc_timestamp(),
            planning_mode=True,
            current_state={"status": "test"},
            goals=["test goal"],
            strategies=[{"name": "test strategy"}],
            evaluation_metrics=["test metric"],
            coordination={"nodes": []},
            risks=[],
            next_actions=["test action"],
        )

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_write_report_creates_file(self):
        """Test that write_planning_report creates a file."""
        output_path = write_planning_report(
            output_dir=Path(self.temp_dir),
            prefix="test",
            report=self.sample_report,
        )
        
        self.assertTrue(output_path.exists())
        self.assertEqual(output_path.parent, Path(self.temp_dir))
        self.assertTrue(output_path.name.startswith("test_planning_report_"))
        self.assertTrue(output_path.name.endswith(".json"))
        print("TestWritePlanningReport: test_write_report_creates_file PASSED")

    def test_write_report_content(self):
        """Test that written report contains correct content."""
        output_path = write_planning_report(
            output_dir=Path(self.temp_dir),
            prefix="test",
            report=self.sample_report,
        )
        
        with open(output_path, 'r') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(loaded_data['agent'], 'test_agent')
        self.assertEqual(loaded_data['objective'], 'Test objective')
        print("TestWritePlanningReport: test_write_report_content PASSED")

    def test_write_report_creates_directories(self):
        """Test that write_planning_report creates parent directories."""
        nested_dir = Path(self.temp_dir) / "subdir1" / "subdir2"
        
        output_path = write_planning_report(
            output_dir=nested_dir,
            prefix="test",
            report=self.sample_report,
        )
        
        self.assertTrue(nested_dir.exists())
        self.assertTrue(output_path.exists())
        print("TestWritePlanningReport: test_write_report_creates_directories PASSED")

    def test_write_report_timestamp_in_filename(self):
        """Test that filename contains timestamp."""
        output_path = write_planning_report(
            output_dir=Path(self.temp_dir),
            prefix="test",
            report=self.sample_report,
        )
        
        # Filename should contain timestamp pattern YYYYMMDD_HHMMSS
        import re
        pattern = r'\d{8}_\d{6}'
        self.assertTrue(re.search(pattern, output_path.name))
        print("TestWritePlanningReport: test_write_report_timestamp_in_filename PASSED")


if __name__ == '__main__':
    unittest.main(verbosity=2)
