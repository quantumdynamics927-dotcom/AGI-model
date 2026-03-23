# Quantum Consciousness VAE Dashboard

An interactive Streamlit dashboard for visualizing training metrics and quantum properties of the Variational Autoencoder designed for quantum consciousness modeling.

## Features

- **Training Metrics Visualization**: Monitor loss components and convergence over epochs
- **Quantum Properties Analysis**: Track quantum fidelity, entanglement entropy, and coherence preservation
- **Latent Space Analysis**: Visualize phi-shell geometry formation in the latent space
- **Interactive Exploration**: Upload your own metrics data for analysis

## Installation

```bash
cd dashboards/quantum_consciousness_dashboard
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

The dashboard will be available at http://localhost:8501

## Data Format

The dashboard expects a JSON file with the following structure:

```json
{
  "epochs": [1, 2, 3, ...],
  "train_metrics": {
    "total_loss": [...],
    "recon": [...],
    "kl": [...],
    "hamming": [...],
    "coherence": [...],
    "fidelity": [...],
    "entropy": [...]
  },
  "val_metrics": {
    "total_loss": [...],
    "recon": [...],
    "kl": [...],
    "hamming": [...],
    "coherence": [...],
    "fidelity": [...],
    "entropy": [...]
  },
  "quantum_metrics": {
    "quantum_fidelity": [...],
    "entanglement_entropy": [...],
    "coherence_preservation": [...],
    "consciousness_complexity": [...]
  }
}
```

## Screenshots

![Dashboard Overview](screenshots/dashboard_overview.png)
![Training Metrics](screenshots/training_metrics.png)
![Quantum Properties](screenshots/quantum_properties.png)
![Latent Space](screenshots/latent_space.png)

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](../../LICENSE) file for details.
