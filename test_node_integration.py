#!/usr/bin/env python3
"""
Integration test script for Metatron Nervous System nodes.
Tests that all nodes can be imported and initialized successfully.
"""

import sys
import os

# Add paths for node imports
sys.path.append('TMT-OS')
sys.path.append('TMT-OS-Labs')
sys.path.append('data_provenance')

def test_node_initialization():
    """Test that all implemented nodes can be initialized."""
    results = {}

    try:
        # Test Node 1
        from node1_base_os import Node1BaseOS
        node1 = Node1BaseOS()
        results['node1'] = node1.get_health_status()['status']
        print(f"✓ Node 1 (Base OS): {results['node1']}")
    except Exception as e:
        results['node1'] = f"FAILED: {e}"
        print(f"✗ Node 1 (Base OS): {results['node1']}")

    try:
        # Test Node 2
        from node2_cybershield import Node2CyberShield
        node2 = Node2CyberShield()
        results['node2'] = node2.get_health_status()['status']
        print(f"✓ Node 2 (CyberShield): {results['node2']}")
    except Exception as e:
        results['node2'] = f"FAILED: {e}"
        print(f"✗ Node 2 (CyberShield): {results['node2']}")

    try:
        # Test Node 3
        from node3_experimental_labs import Node3ExperimentalLabs
        node3 = Node3ExperimentalLabs()
        results['node3'] = node3.get_health_status()['status']
        print(f"✓ Node 3 (Experimental Labs): {results['node3']}")
    except Exception as e:
        results['node3'] = f"FAILED: {e}"
        print(f"✗ Node 3 (Experimental Labs): {results['node3']}")

    try:
        # Test Node 4
        from node4_nft_layer import Node4NFTLayer
        node4 = Node4NFTLayer()
        results['node4'] = node4.get_health_status()['status']
        print(f"✓ Node 4 (NFT Layer): {results['node4']}")
    except Exception as e:
        results['node4'] = f"FAILED: {e}"
        print(f"✗ Node 4 (NFT Layer): {results['node4']}")

    try:
        # Test Node 6
        from node6_audit_trails import Node6AuditTrails
        node6 = Node6AuditTrails()
        results['node6'] = node6.get_health_status()['status']
        print(f"✓ Node 6 (Data Provenance): {results['node6']}")
    except Exception as e:
        results['node6'] = f"FAILED: {e}"
        print(f"✗ Node 6 (Data Provenance): {results['node6']}")

    # Check if all nodes are healthy
    all_healthy = all('FAILED' not in status for status in results.values())

    print(f"\nIntegration Test Result: {'PASSED' if all_healthy else 'FAILED'}")
    print(f"Healthy nodes: {sum(1 for s in results.values() if 'FAILED' not in s)}/{len(results)}")

    return results

if __name__ == '__main__':
    print("=== Metatron Nervous System Integration Test ===")
    test_node_initialization()
    print("=== Test Complete ===")