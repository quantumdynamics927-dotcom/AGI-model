#!/usr/bin/env python3
"""
Metatron Nervous System - Node Registration Verification

This script verifies that all 12 functional nodes are properly registered
with the Metatron Nervous System (Node 13) and displays their status.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from metatron_nervous_system import NODE_REGISTRY, MetatronCoordinator, PHI
import json

# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header():
    """Print the Metatron header."""
    print(f"\n{BOLD}{CYAN}+======================================================================+{RESET}")
    print(f"{BOLD}{CYAN}|          METATRON NERVOUS SYSTEM - NODE REGISTRATION CHECK           |{RESET}")
    print(f"{BOLD}{CYAN}|                    phi = {PHI:.15f}                   |{RESET}")
    print(f"{BOLD}{CYAN}+======================================================================+{RESET}\n")


def print_node_table():
    """Print a table of all registered nodes."""
    # Expected nodes with their Platonic solid mappings
    expected_nodes = {
        1: ("TMT-OS Base", "Cube"),
        2: ("CyberShield", "Tetrahedron"),
        3: ("TMT-OS Labs", "Icosahedron"),
        4: ("NFT Layer", "Dodecahedron"),
        5: ("Molecular Geometry", "Octahedron"),
        6: ("Data Provenance", "Metatron Nexus"),
        7: ("NFT Inventor", "Heptagram"),
        8: ("Quantum Observer", "Octave"),
        9: ("QVAE Bridge", "Merkabah"),
        10: ("Bio-Digital Interface", "Merkaba-Bio"),
        11: ("Frequency Master", "Tesla Triangle"),
        12: ("Neural Synapse", "Omega Point"),
        13: ("Metatron Coordinator", "Metatron's Cube")
    }

    # Build a mapping from node_id to registry entry
    id_to_node = {}
    for name, info in NODE_REGISTRY.items():
        node_id = info.get('node_id')
        if node_id:
            id_to_node[node_id] = (name, info)

    print(f"{BOLD}{'ID':<4} {'Name':<25} {'Platonic Solid':<20} {'Status':<12}{RESET}")
    print("-" * 70)

    registered_count = 0
    for node_id in range(1, 14):
        expected_name, expected_solid = expected_nodes.get(node_id, ("Unknown", "Unknown"))

        if node_id == 13:
            # Metatron Coordinator is special
            status = f"{GREEN}[OK] ACTIVE{RESET}"
            print(f"{node_id:<4} {expected_name:<25} {expected_solid:<20} {status}")
            registered_count += 1
            continue

        if node_id in id_to_node:
            name, info = id_to_node[node_id]
            solid = info.get('platonic_solid', 'N/A')
            status = f"{GREEN}[OK] Registered{RESET}"
            registered_count += 1
        else:
            solid = expected_solid
            status = f"{RED}[X] Missing{RESET}"

        print(f"{node_id:<4} {expected_name:<25} {solid:<20} {status}")

    print("-" * 70)
    print(f"\n{BOLD}Summary:{RESET} {registered_count}/13 nodes registered")


def print_geometry_info():
    """Print Platonic solid geometry information."""
    platonic_solids = {
        "Cube": {"faces": 6, "vertices": 8, "edges": 12, "element": "Earth"},
        "Tetrahedron": {"faces": 4, "vertices": 4, "edges": 6, "element": "Fire"},
        "Octahedron": {"faces": 8, "vertices": 6, "edges": 12, "element": "Air"},
        "Icosahedron": {"faces": 20, "vertices": 12, "edges": 30, "element": "Water"},
        "Dodecahedron": {"faces": 12, "vertices": 20, "edges": 30, "element": "Ether/Universe"}
    }

    print(f"\n{BOLD}{CYAN}=== PLATONIC SOLID GEOMETRY ==={RESET}\n")
    print(f"{'Solid':<15} {'Faces':<8} {'Vertices':<10} {'Edges':<8} {'Element':<15}")
    print("-" * 60)

    for solid, props in platonic_solids.items():
        print(f"{solid:<15} {props['faces']:<8} {props['vertices']:<10} {props['edges']:<8} {props['element']:<15}")

    print("\n" + f"{YELLOW}Note: Metatron's Cube contains all 5 Platonic solids{RESET}")


def test_coordinator():
    """Test the Metatron Coordinator."""
    print(f"\n{BOLD}{CYAN}=== METATRON COORDINATOR TEST ==={RESET}\n")

    try:
        coordinator = MetatronCoordinator()
        health = coordinator.get_health_status()

        print(f"Coordinator Status: {GREEN}{health['status']}{RESET}")
        print(f"Registered Nodes: {health['registered_nodes']}")
        print(f"Uptime: {health['uptime_seconds']:.2f} seconds")

        # Get system health
        print(f"\n{BOLD}System Health Report:{RESET}")
        system_health = coordinator.get_system_health()
        summary = system_health['summary']

        print(f"  * Total Nodes: {summary['total_nodes']}")
        print(f"  * Active: {GREEN}{summary['active']}{RESET}")
        print(f"  * Not Loaded: {YELLOW}{summary['not_loaded']}{RESET}")
        print(f"  * Errors: {RED}{summary['error']}{RESET}")

        return True
    except Exception as e:
        print(f"{RED}Error testing coordinator: {e}{RESET}")
        return False


def main():
    """Main entry point."""
    print_header()
    print_node_table()
    print_geometry_info()
    success = test_coordinator()

    print(f"\n{BOLD}{CYAN}+======================================================================+{RESET}")
    if success:
        print(f"{BOLD}{CYAN}|                    {GREEN}VERIFICATION COMPLETE [OK]{CYAN}                        |{RESET}")
    else:
        print(f"{BOLD}{CYAN}|                    {RED}VERIFICATION FAILED [X]{CYAN}                          |{RESET}")
    print(f"{BOLD}{CYAN}+======================================================================+{RESET}\n")

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
