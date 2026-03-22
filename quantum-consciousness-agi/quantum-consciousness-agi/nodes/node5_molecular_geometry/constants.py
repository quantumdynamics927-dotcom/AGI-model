"""Physical and mathematical constants for molecular geometry calculations.

This module provides atomic data, physical constants, and sacred geometry
ratios used throughout the molecular geometry analysis pipeline.
"""
from typing import Dict
import math

# Golden ratio and related sacred geometry constants
PHI = (1 + math.sqrt(5)) / 2  # 1.618033988749895
PHI_SQUARED = PHI ** 2
PHI_INVERSE = 1 / PHI
SQRT_PHI = math.sqrt(PHI)

# Fibonacci-related angles (degrees)
GOLDEN_ANGLE = 360 / (PHI ** 2)  # ~137.5 degrees - phyllotaxis angle
FIBONACCI_ANGLE = 360 * PHI_INVERSE  # ~222.5 degrees

# Physical constants
BOHR_TO_ANGSTROM = 0.529177210903
ANGSTROM_TO_BOHR = 1 / BOHR_TO_ANGSTROM
KCAL_TO_KJ = 4.184
HARTREE_TO_KCAL = 627.5094740631

# Atomic masses (AMU) - most common isotopes
ATOMIC_MASSES: Dict[str, float] = {
    'H': 1.00794, 'He': 4.002602, 'Li': 6.941, 'Be': 9.012182,
    'B': 10.811, 'C': 12.0107, 'N': 14.0067, 'O': 15.9994,
    'F': 18.9984032, 'Ne': 20.1797, 'Na': 22.98976928, 'Mg': 24.305,
    'Al': 26.9815386, 'Si': 28.0855, 'P': 30.973762, 'S': 32.065,
    'Cl': 35.453, 'Ar': 39.948, 'K': 39.0983, 'Ca': 40.078,
    'Sc': 44.955912, 'Ti': 47.867, 'V': 50.9415, 'Cr': 51.9961,
    'Mn': 54.938045, 'Fe': 55.845, 'Co': 58.933195, 'Ni': 58.6934,
    'Cu': 63.546, 'Zn': 65.38, 'Ga': 69.723, 'Ge': 72.64,
    'As': 74.9216, 'Se': 78.96, 'Br': 79.904, 'Kr': 83.798,
    'Rb': 85.4678, 'Sr': 87.62, 'Y': 88.90585, 'Zr': 91.224,
    'Nb': 92.90638, 'Mo': 95.96, 'Tc': 98.0, 'Ru': 101.07,
    'Rh': 102.9055, 'Pd': 106.42, 'Ag': 107.8682, 'Cd': 112.411,
    'In': 114.818, 'Sn': 118.71, 'Sb': 121.76, 'Te': 127.6,
    'I': 126.90447, 'Xe': 131.293, 'Cs': 132.9054519, 'Ba': 137.327,
    'La': 138.90547, 'Ce': 140.116, 'Pr': 140.90765, 'Nd': 144.242,
    'Pm': 145.0, 'Sm': 150.36, 'Eu': 151.964, 'Gd': 157.25,
    'Tb': 158.92535, 'Dy': 162.5, 'Ho': 164.93032, 'Er': 167.259,
    'Tm': 168.93421, 'Yb': 173.054, 'Lu': 174.9668, 'Hf': 178.49,
    'Ta': 180.94788, 'W': 183.84, 'Re': 186.207, 'Os': 190.23,
    'Ir': 192.217, 'Pt': 195.084, 'Au': 196.966569, 'Hg': 200.59,
    'Tl': 204.3833, 'Pb': 207.2, 'Bi': 208.9804, 'Po': 209.0,
    'At': 210.0, 'Rn': 222.0, 'Fr': 223.0, 'Ra': 226.0,
    'Ac': 227.0, 'Th': 232.03806, 'Pa': 231.03588, 'U': 238.02891,
}

# Van der Waals radii (Angstroms) - Bondi radii
VDW_RADII: Dict[str, float] = {
    'H': 1.20, 'He': 1.40, 'Li': 1.82, 'Be': 1.53, 'B': 1.92,
    'C': 1.70, 'N': 1.55, 'O': 1.52, 'F': 1.47, 'Ne': 1.54,
    'Na': 2.27, 'Mg': 1.73, 'Al': 1.84, 'Si': 2.10, 'P': 1.80,
    'S': 1.80, 'Cl': 1.75, 'Ar': 1.88, 'K': 2.75, 'Ca': 2.31,
    'Ni': 1.63, 'Cu': 1.40, 'Zn': 1.39, 'Ga': 1.87, 'Ge': 2.11,
    'As': 1.85, 'Se': 1.90, 'Br': 1.85, 'Kr': 2.02, 'Rb': 3.03,
    'Sr': 2.49, 'Pd': 1.63, 'Ag': 1.72, 'Cd': 1.58, 'In': 1.93,
    'Sn': 2.17, 'Sb': 2.06, 'Te': 2.06, 'I': 1.98, 'Xe': 2.16,
    'Cs': 3.43, 'Ba': 2.68, 'Pt': 1.75, 'Au': 1.66, 'Hg': 1.55,
    'Tl': 1.96, 'Pb': 2.02, 'Bi': 2.07, 'Po': 1.97, 'At': 2.02,
    'Rn': 2.20, 'Fr': 3.48, 'Ra': 2.83, 'U': 1.86,
}

# Covalent radii (Angstroms) - for bond detection
COVALENT_RADII: Dict[str, float] = {
    'H': 0.31, 'He': 0.28, 'Li': 1.28, 'Be': 0.96, 'B': 0.84,
    'C': 0.76, 'N': 0.71, 'O': 0.66, 'F': 0.57, 'Ne': 0.58,
    'Na': 1.66, 'Mg': 1.41, 'Al': 1.21, 'Si': 1.11, 'P': 1.07,
    'S': 1.05, 'Cl': 1.02, 'Ar': 1.06, 'K': 2.03, 'Ca': 1.76,
    'Sc': 1.70, 'Ti': 1.60, 'V': 1.53, 'Cr': 1.39, 'Mn': 1.39,
    'Fe': 1.32, 'Co': 1.26, 'Ni': 1.24, 'Cu': 1.32, 'Zn': 1.22,
    'Ga': 1.22, 'Ge': 1.20, 'As': 1.19, 'Se': 1.20, 'Br': 1.20,
    'Kr': 1.16, 'Rb': 2.20, 'Sr': 1.95, 'Y': 1.90, 'Zr': 1.75,
    'Nb': 1.64, 'Mo': 1.54, 'Tc': 1.47, 'Ru': 1.46, 'Rh': 1.42,
    'Pd': 1.39, 'Ag': 1.45, 'Cd': 1.44, 'In': 1.42, 'Sn': 1.39,
    'Sb': 1.39, 'Te': 1.38, 'I': 1.39, 'Xe': 1.40, 'Cs': 2.44,
    'Ba': 2.15, 'La': 2.07, 'Ce': 2.04, 'Pr': 2.03, 'Nd': 2.01,
    'Pm': 1.99, 'Sm': 1.98, 'Eu': 1.98, 'Gd': 1.96, 'Tb': 1.94,
    'Dy': 1.92, 'Ho': 1.92, 'Er': 1.89, 'Tm': 1.90, 'Yb': 1.87,
    'Lu': 1.87, 'Hf': 1.75, 'Ta': 1.70, 'W': 1.62, 'Re': 1.51,
    'Os': 1.44, 'Ir': 1.41, 'Pt': 1.36, 'Au': 1.36, 'Hg': 1.32,
    'Tl': 1.45, 'Pb': 1.46, 'Bi': 1.48, 'Po': 1.40, 'At': 1.50,
    'Rn': 1.50, 'Fr': 2.60, 'Ra': 2.21, 'Ac': 2.15, 'Th': 2.06,
    'Pa': 2.00, 'U': 1.96, 'Np': 1.90, 'Pu': 1.87, 'Am': 1.80,
}

# Atomic numbers
ATOMIC_NUMBERS: Dict[str, int] = {
    'H': 1, 'He': 2, 'Li': 3, 'Be': 4, 'B': 5, 'C': 6, 'N': 7,
    'O': 8, 'F': 9, 'Ne': 10, 'Na': 11, 'Mg': 12, 'Al': 13,
    'Si': 14, 'P': 15, 'S': 16, 'Cl': 17, 'Ar': 18, 'K': 19,
    'Ca': 20, 'Sc': 21, 'Ti': 22, 'V': 23, 'Cr': 24, 'Mn': 25,
    'Fe': 26, 'Co': 27, 'Ni': 28, 'Cu': 29, 'Zn': 30, 'Ga': 31,
    'Ge': 32, 'As': 33, 'Se': 34, 'Br': 35, 'Kr': 36, 'Rb': 37,
    'Sr': 38, 'Y': 39, 'Zr': 40, 'Nb': 41, 'Mo': 42, 'Tc': 43,
    'Ru': 44, 'Rh': 45, 'Pd': 46, 'Ag': 47, 'Cd': 48, 'In': 49,
    'Sn': 50, 'Sb': 51, 'Te': 52, 'I': 53, 'Xe': 54, 'Cs': 55,
    'Ba': 56, 'La': 57, 'Ce': 58, 'Pr': 59, 'Nd': 60, 'Pm': 61,
    'Sm': 62, 'Eu': 63, 'Gd': 64, 'Tb': 65, 'Dy': 66, 'Ho': 67,
    'Er': 68, 'Tm': 69, 'Yb': 70, 'Lu': 71, 'Hf': 72, 'Ta': 73,
    'W': 74, 'Re': 75, 'Os': 76, 'Ir': 77, 'Pt': 78, 'Au': 79,
    'Hg': 80, 'Tl': 81, 'Pb': 82, 'Bi': 83, 'Po': 84, 'At': 85,
    'Rn': 86, 'Fr': 87, 'Ra': 88, 'Ac': 89, 'Th': 90, 'Pa': 91,
    'U': 92, 'Np': 93, 'Pu': 94, 'Am': 95, 'Cm': 96, 'Bk': 97,
    'Cf': 98, 'Es': 99, 'Fm': 100, 'Md': 101, 'No': 102, 'Lr': 103,
}

# Element symbols by atomic number (reverse lookup)
ELEMENT_SYMBOLS: Dict[int, str] = {v: k for k, v in ATOMIC_NUMBERS.items()}

# Typical bond lengths (Angstroms) for common bonds
TYPICAL_BOND_LENGTHS: Dict[str, float] = {
    'C-C': 1.54, 'C=C': 1.34, 'C#C': 1.20,
    'C-H': 1.09, 'C-N': 1.47, 'C=N': 1.29, 'C#N': 1.16,
    'C-O': 1.43, 'C=O': 1.23, 'C-S': 1.82, 'C=S': 1.60,
    'C-F': 1.35, 'C-Cl': 1.77, 'C-Br': 1.94, 'C-I': 2.14,
    'N-H': 1.01, 'N-N': 1.45, 'N=N': 1.25, 'N#N': 1.10,
    'N-O': 1.40, 'N=O': 1.21, 'O-H': 0.96, 'O-O': 1.48,
    'O=O': 1.21, 'S-H': 1.34, 'S-S': 2.05, 'S=S': 1.89,
    'P-O': 1.63, 'P=O': 1.48, 'P-H': 1.44,
}

# Electronegativity (Pauling scale)
ELECTRONEGATIVITY: Dict[str, float] = {
    'H': 2.20, 'Li': 0.98, 'Be': 1.57, 'B': 2.04, 'C': 2.55,
    'N': 3.04, 'O': 3.44, 'F': 3.98, 'Na': 0.93, 'Mg': 1.31,
    'Al': 1.61, 'Si': 1.90, 'P': 2.19, 'S': 2.58, 'Cl': 3.16,
    'K': 0.82, 'Ca': 1.00, 'Sc': 1.36, 'Ti': 1.54, 'V': 1.63,
    'Cr': 1.66, 'Mn': 1.55, 'Fe': 1.83, 'Co': 1.88, 'Ni': 1.91,
    'Cu': 1.90, 'Zn': 1.65, 'Ga': 1.81, 'Ge': 2.01, 'As': 2.18,
    'Se': 2.55, 'Br': 2.96, 'Rb': 0.82, 'Sr': 0.95, 'Y': 1.22,
    'Zr': 1.33, 'Nb': 1.60, 'Mo': 2.16, 'Tc': 1.90, 'Ru': 2.20,
    'Rh': 2.28, 'Pd': 2.20, 'Ag': 1.93, 'Cd': 1.69, 'In': 1.78,
    'Sn': 1.96, 'Sb': 2.05, 'Te': 2.10, 'I': 2.66, 'Xe': 2.60,
    'Cs': 0.79, 'Ba': 0.89, 'La': 1.10, 'Hf': 1.30, 'Ta': 1.50,
    'W': 2.36, 'Re': 1.90, 'Os': 2.20, 'Ir': 2.20, 'Pt': 2.28,
    'Au': 2.54, 'Hg': 2.00, 'Tl': 1.62, 'Pb': 2.33, 'Bi': 2.02,
}


def get_mass(element: str) -> float:
    """Get atomic mass for an element symbol."""
    elem = element.strip().capitalize()
    if len(elem) > 1:
        elem = elem[0] + elem[1:].lower()
    return ATOMIC_MASSES.get(elem, 12.0)  # Default to carbon


def get_covalent_radius(element: str) -> float:
    """Get covalent radius for an element symbol."""
    elem = element.strip().capitalize()
    if len(elem) > 1:
        elem = elem[0] + elem[1:].lower()
    return COVALENT_RADII.get(elem, 1.5)  # Default reasonable value


def get_vdw_radius(element: str) -> float:
    """Get van der Waals radius for an element symbol."""
    elem = element.strip().capitalize()
    if len(elem) > 1:
        elem = elem[0] + elem[1:].lower()
    return VDW_RADII.get(elem, 1.7)  # Default reasonable value


def is_phi_harmonic(value: float, tolerance: float = 0.05) -> bool:
    """Check if a value is harmonically related to the golden ratio.

    Tests if value is close to phi, phi^2, phi^-1, sqrt(phi), or integer multiples.
    """
    phi_harmonics = [
        PHI, PHI_SQUARED, PHI_INVERSE, SQRT_PHI,
        2 * PHI, 3 * PHI, PHI / 2, PHI / 3,
        PHI_SQUARED / 2, PHI_INVERSE * 2,
    ]
    for harmonic in phi_harmonics:
        if abs(value - harmonic) / harmonic < tolerance:
            return True
    return False


def phi_encode(value: float) -> float:
    """Encode a value using golden ratio compression (for Metatron integration)."""
    return value / PHI_SQUARED


def phi_decode(encoded: float) -> float:
    """Decode a phi-encoded value."""
    return encoded * PHI_SQUARED
