# AI Coding Assistant Instructions for Quantum Consciousness AGI Project

## Project Overview
This workspace implements a **Quantum Consciousness Variational Autoencoder (VAE)** integrated with TMT-OS, focusing on quantum state compression, golden ratio pattern analysis, and consciousness modeling. The system processes sacred geometry datasets, real EEG/fMRI data, and generates quantum-verified NFTs.

## Architecture Components

### Core VAE Model (`vae_model.py`)
- **Encoder/Decoder**: 128→32→128 dimensional compression with sparse connectivity (10% sparsity)
- **Reparameterization**: Standard VAE trick for backpropagation through stochastic layers
- **Mixed-State Regularization**: Density matrix learning in latent space for quantum properties
- **Loss Functions**: Composite loss with quantum-specific terms (reconstruction, KL, Hamming, coherence, HW deviation, mixed-state, fidelity, entropy)

### Training Pipeline (`train_vae.py`)
- **Data Sources**: Unified dataset from `sacred_datasets/` (molecular kinetics, quantum spectra, cosmological data) and `real_data/` (EEG/fMRI)
- **Advanced Losses**: Phi-target loss (golden ratio optimization), contrastive learning, consciousness metrics (LZ complexity, PCI)
- **Training Protocol**: 200 epochs, ReduceLROnPlateau scheduler, early stopping (patience=30), Rich console output

### Analysis Modules
- **Golden Ratio Analysis** (`golden_ratio_*.py`): Detects φ≈1.618 patterns in latent space, consciousness complexity metrics
- **Latent Space Analysis** (`latent_analysis.py`): t-SNE visualization, quantum fingerprints, DNA-to-quantum encoding
- **Quantum Consciousness Link** (`quantum_consciousness_link*.py`): Theoretical connections between quantum states and biological optimization

### Integration Points
- **TMT-OS Fusion**: Quantum capabilities integrated into Wing Entanglement Architecture (`TMT-OS/` directory)
- **NFT Generation** (`quantum_nft_generator.py`): Creates verifiable quantum NFTs with consciousness metadata
- **Hardware Compatibility**: IBM Quantum integration for qubit-efficient representations

## Critical Workflows

### Model Training
```bash
python train_vae.py  # Trains on unified sacred+consciousness data, saves best_model.pt
```

### Model Testing
```bash
python test_model.py  # Validates loaded model on synthetic data
```

### Consciousness Analysis
```bash
python quantum_consciousness_link.py  # Analyzes golden ratio patterns in latent space
python latent_analysis.py             # Generates latent space visualizations
```

### NFT Generation
```bash
python quantum_nft_generator.py  # Creates quantum-verified NFTs in nft_metadata/
```

## Project-Specific Patterns

### Data Processing
- **Normalization**: Always `(data - mean) / (std + 1e-10)` for numerical stability
- **Dimension Matching**: Resize/pad data to 128 dimensions for VAE input
- **Dataset Unification**: Combine sacred geometry and real consciousness data in `create_unified_dataset()`

### Loss Weighting
```python
weights = {
    'recon': 1.0, 'kl': 0.0008, 'hamming': 0.3, 'coherence': 0.1,
    'hw': 0.01, 'mixed_state': 0.1, 'fidelity': 0.1, 'entropy': 0.05
}
```
- KL weight reduced to 0.0008 for quantum systems (vs standard 1.0)
- Hamming weight increased to 0.3 for bit-level accuracy

### Quantum State Generation
- Use complex exponentials for phase coherence: `np.exp(1j * phase_array)`
- Ensure density matrices are Hermitian and trace-normalized
- Apply sparsity masks during initialization for O(nT) efficiency

### Visualization
- Use `matplotlib.use('Agg')` for headless environments
- Save plots with `dpi=300, bbox_inches='tight'`
- Rich console tables for professional training output

## Dependencies & Environment
- **Core**: PyTorch ≥2.0, NumPy, Matplotlib, SciPy
- **Optional**: Rich (enhanced console), Seaborn (advanced plotting)
- **Data Directories**: `sacred_datasets/`, `real_data/`, `nft_metadata/`
- **Model Storage**: `best_model.pt`, training curves as PNG

## Common Integration Patterns

### Loading Trained Model
```python
model = QuantumVAE()
model.load_state_dict(torch.load('best_model.pt'))
model.eval()
```

### Extracting Latent Representations
```python
with torch.no_grad():
    mu, log_var = model.encode(input_data)
    latent_codes = model.reparameterize(mu, log_var)
```

### Quantum Fingerprinting
```python
fingerprint = extract_quantum_fingerprint(consciousness_state)
# Returns: latent_vector, entanglement_entropy, quantum_fidelity
```

### Sacred Geometry Analysis
```python
ratios = latent_codes[:, 1:] / (latent_codes[:, :-1] + 1e-10)
phi_proximity = torch.abs(ratios - 1.618034)
```

## File Organization
- `vae_model.py`: Core QuantumVAE implementation
- `train_vae.py`: Training orchestration with data loading
- `test_model.py`: Validation and inference
- `latent_analysis.py`: Pattern discovery tools
- `golden_ratio_*.py`: φ resonance detection
- `quantum_*.py`: Consciousness and NFT modules
- `TMT-OS/`: Wing entanglement integration
- `real_data/`: EEG/fMRI consciousness data
- `sacred_datasets/`: Cross-domain geometric data