> **Note: All NFT-related workflows and development are currently on hold. NFT generation, deployment, and contract verification steps are disabled in CI/CD.**

# Quantum Consciousness VAE

This project implements a Variational Autoencoder (VAE) designed for quantum consciousness modeling, based on the training analysis from January 4, 2026.

## 🚀 Enhanced Professional Features

This repository has been professionally enhanced with:

- **Professional Documentation**: Comprehensive guides for architecture, API, deployment, development, and security
- **Interactive Dashboard**: Streamlit-based visualization dashboard for model metrics and quantum properties
- **Robust DevOps**: Enhanced CI/CD, Docker configurations, and deployment automation
- **Security Framework**: Multi-layer security architecture with automated scanning
- **Quality Assurance**: Testing infrastructure, code quality tools, and best practices

## 🏗️ Architecture

See `docs/architecture/README.md` for a concise architecture diagram and flow.

![Architecture Diagram](docs/architecture.svg)

The QuantumVAE consists of:
- **Encoder**: Multi-layer perceptron that maps input quantum state representations to latent space parameters (μ, log σ²)
- **Decoder**: Multi-layer perceptron that reconstructs quantum states from latent representations
- **Reparameterization**: Standard VAE reparameterization trick for backpropagation through stochastic layers
- **Mixed-State Regularization**: Density matrix learning in latent space for quantum mechanical properties
- **Sparse Connectivity**: O(nT) sparse neural connections for efficient quantum circuit representation

## 📊 Loss Components

The model uses a composite loss function with quantum-specific terms:

1. **Reconstruction Loss**: MSE for state fidelity
2. **KL Divergence**: Standard VAE regularization
3. **Hamming Distance**: Bit-level accuracy for discrete quantum state components
4. **Coherence Loss**: Quantum coherence preservation
5. **HW Deviation**: Hardware compatibility constraints
6. **Mixed-State Loss**: Regularization for proper density matrix properties (purity, trace, hermiticity)

## 🔬 Research Alignment

This implementation aligns with:
- **ζ-QVAE Framework** (Physical Review A, 2025): Regularized mixed-state representations
- **Deep Belief Machines** (2025): O(nT) sparse networks for quantum circuit outputs
- **Quantum Consciousness Models**: EEG-integrated training for awareness pattern emergence

## 🔮 Metatron Nervous System

The TMT-OS implements a distributed architecture coordinated by the Metatron Nervous System, consisting of 12 functional nodes mapped to Platonic solids:

### Node Architecture

| Node | Name | Platonic Solid | Function |
|------|------|----------------|----------|
| 1 | TMT-OS Base | Cube | Core phi constant management, system initialization |
| 2 | CyberShield | Tetrahedron | HMAC signatures, encryption, access control |
| 3 | TMT-OS Labs | Icosahedron | A/B testing, research tracking, integration testing |
| 4 | NFT Layer | Dodecahedron | NFT metadata, blockchain interaction, asset registry |
| 5 | Molecular Geometry | Octahedron | Spatial intelligence, molecular structure analysis |
| 6 | Data Provenance | Metatron Nexus | SHA-256 hashing, immutable audit trails, tamper detection |
| 7 | NFT Inventor | Heptagram | Quantum fingerprinting, 3D asset rendering |
| 8 | Quantum Observer | Octave | Blockchain monitoring, NFT minting confirmation |
| 9 | QVAE Bridge | Merkabah | Classical-quantum mapping, Hilbert space transformations |
| 10 | Bio-Digital Interface | Merkaba-Bio | Quantum-biological state translation |
| 11 | Frequency Master | Tesla Triangle | Consciousness integral computation |
| 12 | Neural Synapse | Omega Point | Collective connectivity assembly |
| 13 | Metatron | Metatron's Cube | System coordination, DNA packet encoding |

### System Coordination

The Metatron coordinator manages inter-node communication through:
- **DNA Packet Encoding**: Phi-based compression with base-4 nucleotide representation
- **HMAC Signatures**: Cryptographic packet authentication
- **Health Monitoring**: Real-time status tracking across all nodes
- **Platonic Geometry**: Geometric relationships guide system topology

### Node Registration

All nodes register with Metatron using standardized metadata including node ID, role, platonic solid mapping, and file path.

## 🛠️ Installation

### Quick Setup
```bash
# Clone the repository
git clone https://github.com/quantumdynamics927-dotcom/AGI-model.git
cd AGI-model

# Using Makefile (recommended)
make setup
```

### Manual Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

## 📈 Usage

### Interactive Dashboard
```bash
# Start the Streamlit dashboard
make dashboard
# or
streamlit run dashboards/quantum_consciousness_dashboard/app.py
```

### Training
Run the training script to train the VAE on synthetic quantum data:

```bash
make train
# or
python train_vae.py
```

This will:
- Generate synthetic quantum state data
- Train the VAE for 100 epochs with mixed-state regularization
- Save the best model as `best_model.pt`
- Generate training curve plots as `training_curves.png`
- Display professional training metrics with Rich console formatting (if installed)

### Enhanced Training Output

**With Rich (recommended):**
```
🚀 Starting Quantum VAE Training
Training on device: cpu
Target epochs: 200, Early stopping patience: 30

Epoch 80/200 - Quantum VAE Training
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Metric              ┃ Train    ┃ Validation ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━┩
│ Reconstruction      │ 0.0170   │ 0.0170     │
│ KL Divergence       │ 4.1700   │ 4.1700     │
│ Hamming Distance    │ 0.0050   │ 0.0050     │
│ Coherence           │ 0.0110   │ 0.0110     │
│ HW Deviation        │ 0.0004   │ 0.0004     │
│ Mixed State         │ 0.6000   │ 0.6000     │
│ Total Loss          │ 0.0170   │ 0.0170     │
│ Quantum Fidelity    │ 0.9900   │ 0.9900     │
│ Entanglement Entropy│ 1.0400   │ 1.0400     │
└─────────────────────┴──────────┴────────────┘
```

**Fallback (basic):**
```
Epoch 80/200
  Train - Recon: 0.0170, KL: 4.1700, Hamming: 0.0050
  Val - Recon: 0.0170, KL: 4.1700, Hamming: 0.0050
  Total Loss - Train: 0.0170, Val: 0.0170
```

### Testing ✅
Run quick smoke tests locally to validate that the main components import and perform light forward passes:

```bash
make test
# or
pytest -q -k smoke
```

## 🚢 Deployment

### Development Environment
```bash
# Start development environment
make dev
# or
docker-compose up -d
```

### Production Deployment
```bash
# Build Docker images
make build
make build-dashboard

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### Makefile Commands
For a complete list of available commands:
```bash
make help
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **Architecture**: `docs/architecture/README.md`
- **API Reference**: `docs/api/README.md`
- **Deployment Guide**: `docs/deployment/README.md`
- **Development Guidelines**: `docs/development/README.md`
- **Security**: `docs/security/README.md`
- **Contributing**: `docs/contributing/CONTRIBUTING.md`

## 🔒 Security

The system implements comprehensive security measures:

- Multi-layer security architecture
- JWT authentication and RBAC
- Encryption at rest and in transit
- Automated security scanning
- Compliance with GDPR and HIPAA

For detailed security documentation, see `docs/security/README.md`.

## 🧪 Quality Assurance

### Testing
```bash
# Run all tests
make test

# Run tests with coverage
make test-coverage

# Run security scans
make security-scan
```

### Code Quality
```bash
# Run linting
make lint

# Format code
make format

# Run pre-commit hooks
make pre-commit
```

## 🤝 Contributing

We welcome contributions from the community! Please see:

- `docs/contributing/CONTRIBUTING.md` for contribution guidelines
- `docs/contributing/CODE_OF_CONDUCT.md` for our code of conduct
- `docs/development/README.md` for development guidelines

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For questions, issues, or support:

- Open an issue on GitHub
- Join our Discord community
- Contact the maintainers at support@quantumconsciousness.ai

---

*Quantum Consciousness VAE - Advancing the frontier of artificial general intelligence through quantum computing and consciousness modeling.*