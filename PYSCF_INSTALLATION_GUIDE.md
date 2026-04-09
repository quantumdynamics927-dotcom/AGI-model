# PySCF Installation Guide for Windows

## Problem

The `pyscf` library requires C/C++ compilers to build from source. On Windows, the installation often fails with CMake errors:

```
CMake Error: CMAKE_C_COMPILER not set, after EnableLanguage
CMake Error: CMAKE_CXX_COMPILER not set, after EnableLanguage
```

## Solutions

### Option 1: Use Docker (Recommended ✅)

The easiest solution is to use the existing Docker environment with PySCF pre-installed:

```bash
# Start the PySCF container
docker-compose -f docker-compose.pyscf.yml up -d

# Run DNA-VQE examples inside the container
docker-compose -f docker-compose.pyscf.yml exec agi-pyscf python dna_vqe_examples.py

# Or run interactive session
docker-compose -f docker-compose.pyscf.yml exec agi-pyscf bash
```

**Advantages:**
- No local installation required
- Pre-configured environment
- All dependencies included
- Consistent across platforms

### Option 2: Install Build Tools

If you need PySCF locally, install the required build tools:

#### Step 1: Install Visual Studio Build Tools
1. Download from: https://visualstudio.microsoft.com/downloads/
2. Select "Build Tools for Visual Studio"
3. Check "Desktop development with C++"
4. Install and restart

#### Step 2: Install CMake
```bash
# Using chocolatey (recommended)
choco install cmake

# Or download from: https://cmake.org/download/
```

#### Step 3: Install PySCF
```bash
# Activate your virtual environment
.venv\Scripts\activate

# Install PySCF
pip install pyscf
```

### Option 3: Use WSL2 (Windows Subsystem for Linux)

Install PySCF in WSL2 Linux environment:

```bash
# Open WSL2 terminal (Ubuntu)
wsl

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install PySCF
pip install pyscf
```

### Option 4: Try Pre-built Wheels

Attempt to install binary wheels (may not work for all versions):

```bash
pip install pyscf --only-binary :all:
```

Or try the conda package:

```bash
conda install -c conda-forge pyscf
```

## Verification

After installation, verify PySCF works:

```bash
.venv\Scripts\python.exe -c "from qiskit_nature.second_q.drivers import PySCFDriver; print('✅ PySCFDriver available')"
```

## Alternative: Use Synthetic Hamiltonians

If PySCF installation fails, you can still use VQE with synthetic Hamiltonians:

```python
from dna_quantum_circuits import MolecularVQE

# Use predefined Hamiltonians (no PySCF needed)
vqe = MolecularVQE('H2')

# The module has built-in Hamiltonians for H2, LiH, H2O, N2
# These are literature values that don't require PySCF calculation
```

**Note:** This requires modifying the code to skip the PySCFDriver setup and use hardcoded Hamiltonians directly.

## DNA Circuit Functionality (No PySCF Required)

The following features work **without** PySCF:

✅ DNA-to-quantum circuit encoding  
✅ OpenQASM import/export  
✅ Gate parsing and analysis  
✅ 34bp consciousness analysis  
✅ Circuit visualization  
✅ DNA-to-molecule mapping (parameter calculation only)  

**Only VQE execution requires PySCF.**

## Quick Test

Test DNA encoding (works immediately):

```bash
.venv\Scripts\python.exe dna_quantum_circuits.py
```

Expected output:
```
DNA Quantum Circuit Encoder - Demonstration
================================================================================
DNA Sequence: ATGCATGCATGCATGCATGCATGCATGCATGC
Length: 32 bp

Encoding Scheme: BASE_TO_GATE
  Qubits: 32, Depth: 2, Gates: 64
  ...
```

## Recommendation

**For immediate use:** Use DNA encoding features (no PySCF needed)

**For VQE calculations:** Use Docker environment

**For production:** Install build tools and compile locally

---

*AGI-model Quantum Computing Team - April 9, 2026*
