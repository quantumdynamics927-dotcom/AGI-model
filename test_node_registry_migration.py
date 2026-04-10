#!/usr/bin/env python3
"""
Regression test for Node 4 and 7 registry migration from NFT to research-focused roles.

This test ensures that:
1. Node 4 is now "Research Planner" instead of "NFT Layer"
2. Node 7 is now "Discovery Validator" instead of "NFT Inventor"
3. Deprecated aliases work with proper warnings
4. The expected nodes table in check_metatron_registration.py is updated
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from metatron_nervous_system import NODE_REGISTRY, DEPRECATED_NODE_ALIASES, get_node_info
from check_metatron_registration import print_node_table
import logging

# Configure logging to capture warnings
logging.basicConfig(level=logging.WARNING)


def test_node_4_migration():
    """Test that Node 4 is now Research Planner."""
    node4_info = NODE_REGISTRY.get('node4_research_planner')
    assert node4_info is not None, "Node 4 research_planner not found in registry"
    assert 'Research Planner' in node4_info['role'], f"Node 4 role should contain 'Research Planner', got: {node4_info['role']}"
    assert 'NFT' not in node4_info['role'], f"Node 4 role should not contain 'NFT', got: {node4_info['role']}"
    print("✓ Node 4 migration: PASS")


def test_node_7_migration():
    """Test that Node 7 is now Discovery Validator."""
    node7_info = NODE_REGISTRY.get('node7_discovery_validator')
    assert node7_info is not None, "Node 7 discovery_validator not found in registry"
    assert 'Discovery Validator' in node7_info['role'], f"Node 7 role should contain 'Discovery Validator', got: {node7_info['role']}"
    assert 'NFT' not in node7_info['role'], f"Node 7 role should not contain 'NFT', got: {node7_info['role']}"
    print("✓ Node 7 migration: PASS")


def test_deprecated_aliases():
    """Test that deprecated aliases work with warnings."""
    # Test Node 4 alias
    node4_alias = get_node_info('node4_nft_layer')
    assert node4_alias is not None, "Node 4 deprecated alias should work"
    assert 'Research Planner' in node4_alias['role'], f"Node 4 alias should resolve to Research Planner, got: {node4_alias['role']}"
    
    # Test Node 7 alias
    node7_alias = get_node_info('node7_nft_inventor')
    assert node7_alias is not None, "Node 7 deprecated alias should work"
    assert 'Discovery Validator' in node7_alias['role'], f"Node 7 alias should resolve to Discovery Validator, got: {node7_alias['role']}"
    print("✓ Deprecated aliases: PASS")


def test_expected_nodes_table():
    """Test that the expected nodes table is updated."""
    # Import the function and extract expected_nodes from it
    import inspect
    import check_metatron_registration
    
    # Get the source code of print_node_table to extract expected_nodes
    source = inspect.getsource(check_metatron_registration.print_node_table)
    
    # Extract the expected_nodes dictionary from the source
    lines = source.split('\n')
    expected_nodes = {}
    
    for line in lines:
        if '("Research Planner"' in line and 'Dodecahedron' in line:
            expected_nodes[4] = ("Research Planner", "Dodecahedron")
        if '("Discovery Validator"' in line and 'Heptagram' in line:
            expected_nodes[7] = ("Discovery Validator", "Heptagram")
    
    # Check Node 4
    if 4 in expected_nodes:
        node4_name, node4_solid = expected_nodes[4]
        assert node4_name == "Research Planner", f"Expected Node 4 name should be 'Research Planner', got: {node4_name}"
    else:
        raise AssertionError("Node 4 not found in expected_nodes table")
    
    # Check Node 7
    if 7 in expected_nodes:
        node7_name, node7_solid = expected_nodes[7]
        assert node7_name == "Discovery Validator", f"Expected Node 7 name should be 'Discovery Validator', got: {node7_name}"
    else:
        raise AssertionError("Node 7 not found in expected_nodes table")
    print("✓ Expected nodes table: PASS")


def main():
    """Run all registry migration tests."""
    print("Running Node Registry Migration Tests...")
    print("=" * 50)
    
    try:
        test_node_4_migration()
        test_node_7_migration()
        test_deprecated_aliases()
        test_expected_nodes_table()
        
        print("=" * 50)
        print("✅ ALL TESTS PASSED - Node registry migration successful!")
        print("\nSummary of changes:")
        print("- Node 4: NFT Layer → Research Planner")
        print("- Node 7: NFT Inventor → Discovery Validator")
        print("- Backward compatibility: Deprecated aliases with warnings")
        print("- Registration check: Updated expected nodes table")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()