import unittest
import os
import sys
import numpy as np

# Add project root to the path to allow direct import of 'molecular_geometry'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from molecular_geometry.node5_spatial_intelligence import Node5SpatialIntelligence
except ImportError as e:
     raise ImportError(
        "Could not import Node5SpatialIntelligence. "
        "Ensure 'molecular_geometry/node5_spatial_intelligence.py' exists and the test is run from the project root."
    ) from e

class TestNode5SpatialIntelligence(unittest.TestCase):
    """Unit tests for the Node5SpatialIntelligence class."""

    @classmethod
    def setUpClass(cls):
        """Set up for all tests. Create a node instance."""
        cls.node5 = Node5SpatialIntelligence()
        cls.viz_output_path = 'test_molecular_visualization.png'

    def tearDown(self):
        """Clean up generated files after each test run."""
        if os.path.exists(self.viz_output_path):
            os.remove(self.viz_output_path)

    def test_initialization(self):
        """Test that the node initializes with correct default attributes."""
        self.assertEqual(self.node5.NODE_ID, 5)
        self.assertEqual(self.node5.NODE_NAME, "Molecular Geometry")
        self.assertEqual(self.node5.PLATONIC_SOLID, "Octahedron")
        self.assertEqual(self.node5.status, "active")
        print("TestNode5: test_initialization PASSED")

    def test_analyze_structure_water(self):
        """Test structure analysis with a known water molecule."""
        symbols = ['O', 'H', 'H']
        # Standard water molecule coordinates
        coords = np.array([
            [0.0, 0.0, 0.0],
            [0.757, 0.586, 0.0],
            [-0.757, 0.586, 0.0]
        ])
        
        analysis = self.node5.analyze_structure(symbols, coords)
        
        self.assertEqual(analysis['num_atoms'], 3)
        self.assertAlmostEqual(analysis['total_mass'], 15.999 + 2 * 1.008, places=3)
        # For this H2O with O at origin, COM will be slightly shifted in Y.
        self.assertAlmostEqual(analysis['center_of_mass'][0], 0.0, places=3)
        self.assertAlmostEqual(analysis['center_of_mass'][1], 0.065, places=3)
        self.assertAlmostEqual(analysis['center_of_mass'][2], 0.0, places=3)
        self.assertAlmostEqual(analysis['radius_of_gyration'], 0.65, places=2)
        print("TestNode5: test_analyze_structure_water PASSED")

    def test_recognize_patterns(self):
        """Test pattern recognition for linear, planar, and non-planar geometries."""
        # 1. Planar molecule (e.g., a simplified benzene ring)
        planar_coords = np.array([
            [1, 0, 0.01], [-1, 0, -0.01], [0, 1, 0.02], [0, -1, -0.02]
        ])
        self.assertTrue(self.node5.recognize_patterns(planar_coords)['is_planar'], "Should detect planar molecule.")

        # 2. Linear molecule (e.g., CO2)
        linear_coords = np.array([
            [0, 0, 0], [1.16, 0.01, 0.01], [-1.16, -0.01, -0.01]
        ])
        self.assertTrue(self.node5.recognize_patterns(linear_coords)['is_linear'], "Should detect linear molecule.")

        # 3. Non-planar molecule (e.g., methane)
        non_planar_coords = np.array([
            [0.0, 0.0, 0.0],
            [0.6, 0.6, 0.6], [-0.6, -0.6, 0.6],
            [-0.6, 0.6, -0.6], [0.6, -0.6, -0.6]
        ])
        patterns = self.node5.recognize_patterns(non_planar_coords)
        self.assertFalse(patterns['is_linear'], "Methane should not be linear.")
        self.assertFalse(patterns['is_planar'], "Methane should not be planar.")
        print("TestNode5: test_recognize_patterns PASSED")

    def test_generate_3d_visualization(self):
        """Test that the 3D visualization is created successfully on disk."""
        symbols = ['C', 'H', 'H', 'H', 'H']
        coords = np.random.rand(5, 3) * 2 # Random coordinates for testing
        
        saved_path = self.node5.generate_3d_visualization(symbols, coords, self.viz_output_path)
        
        self.assertTrue(os.path.exists(self.viz_output_path), "Visualization image file should be created.")
        self.assertEqual(os.path.abspath(self.viz_output_path), saved_path, "Returned path should be absolute.")
        self.assertGreater(os.path.getsize(self.viz_output_path), 1000, "Image file should not be empty.")
        print("TestNode5: test_generate_3d_visualization PASSED")

    def test_input_validation_for_analysis(self):
        """Test that the analysis function correctly rejects invalid input."""
        # Test case 1: Mismatched lengths of symbols and coordinates
        with self.assertRaisesRegex(ValueError, "Length of symbols list must match"):
            self.node5.analyze_structure(['C'], np.zeros((2, 3)))
        
        # Test case 2: Incorrect coordinate shape (should be Nx3)
        with self.assertRaisesRegex(ValueError, "Coordinates must be a NumPy array of shape"):
            self.node5.analyze_structure(['C'], np.zeros((1, 4)))
        
        # Test case 3: Not a numpy array
        with self.assertRaisesRegex(ValueError, "Coordinates must be a NumPy array of shape"):
            self.node5.analyze_structure(['C'], [[0,0,0]])
        print("TestNode5: test_input_validation_for_analysis PASSED")

if __name__ == '__main__':
    print("Running tests for Node 5: Molecular Geometry...")
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNode5SpatialIntelligence))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.failures or result.errors:
        print("Node 5 tests failed.")
        sys.exit(1)
    print("All tests for Node 5 passed successfully.")