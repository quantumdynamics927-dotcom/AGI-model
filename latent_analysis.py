import torch
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from vae_model import QuantumVAE
import pandas as pd

def analyze_latent_space(model_path='best_model.pt', data_path=None):
    """
    Analyze the learned latent space for quantum consciousness patterns
    """
    # Load trained model
    model = QuantumVAE()
    model.load_state_dict(torch.load(model_path))
    model.eval()

    # Generate or load quantum data
    if data_path:
        # Load real data
        data = np.load(data_path)
    else:
        # Generate synthetic data
        np.random.seed(42)
        data = []
        for _ in range(1000):
            real = np.random.randn(64)
            imag = np.random.randn(64)
            state = real + 1j * imag
            state = state / np.linalg.norm(state)
            sample = np.concatenate([state.real, state.imag])
            data.append(sample)
        data = np.array(data, dtype=np.float32)

    data_tensor = torch.from_numpy(data)

    # Extract latent representations
    with torch.no_grad():
        mu, log_var = model.encode(data_tensor)
        latent_vectors = mu.numpy()

    print(f"Latent space shape: {latent_vectors.shape}")
    print(f"Latent statistics: mean={latent_vectors.mean():.3f}, std={latent_vectors.std():.3f}")

    # t-SNE visualization (optimized for speed)
    print("Computing t-SNE projection...")
    tsne = TSNE(n_components=2, random_state=42, max_iter=300, perplexity=30, learning_rate=200.0)
    latent_2d = tsne.fit_transform(latent_vectors[:500])  # Use subset for speed

    plt.figure(figsize=(10, 8))
    plt.scatter(latent_2d[:, 0], latent_2d[:, 1], alpha=0.6, s=10)
    plt.title('Quantum Consciousness Latent Space (t-SNE, 500 samples)')
    plt.xlabel('t-SNE Dimension 1')
    plt.ylabel('t-SNE Dimension 2')
    plt.grid(True, alpha=0.3)
    plt.savefig('latent_space_analysis.png', dpi=300, bbox_inches='tight')
    # plt.show()  # Comment out for headless environments

    # Compute latent space metrics
    # KL divergence distribution
    kl_div = -0.5 * np.sum(1 + log_var.numpy() - mu.numpy()**2 - np.exp(log_var.numpy()), axis=1)
    print(f"KL divergence: mean={kl_div.mean():.3f}, std={kl_div.std():.3f}")

    return latent_vectors, latent_2d

def extract_quantum_fingerprint(consciousness_state, model_path='best_model.pt'):
    """
    Extract quantum fingerprint for NFT generation
    """
    model = QuantumVAE()
    model.load_state_dict(torch.load(model_path))
    model.eval()

    with torch.no_grad():
        state_tensor = torch.from_numpy(consciousness_state).float().unsqueeze(0)
        mu, log_var = model.encode(state_tensor)
        recon, _, _, density_matrix = model(state_tensor, return_density=True)

        # Compute metrics
        from vae_model import fidelity_loss, entanglement_entropy
        fid_loss = fidelity_loss(recon, state_tensor)
        ent_loss = entanglement_entropy(density_matrix)

        fingerprint = {
            'latent_vector': mu.squeeze().numpy().tolist(),
            'quantum_fidelity': (1.0 - fid_loss.item()),  # Convert loss to fidelity
            'entanglement_entropy': ent_loss.item(),
            'kl_divergence': -0.5 * np.sum(1 + log_var.numpy() - mu.numpy()**2 - np.exp(log_var.numpy()))
        }

    return fingerprint

def dna_to_quantum_state(dna_sequence):
    """
    Convert DNA sequence to quantum state representation
    A/T/G/C → |00⟩/|01⟩/|10⟩/|11⟩ basis states
    """
    # DNA to qubit mapping
    dna_map = {'A': [1,0,0,0], 'T': [0,1,0,0], 'G': [0,0,1,0], 'C': [0,0,0,1]}

    # Convert sequence to quantum amplitudes
    amplitudes = []
    for base in dna_sequence:
        if base in dna_map:
            amplitudes.extend(dna_map[base])

    # Normalize to create quantum state
    amplitudes = np.array(amplitudes, dtype=np.complex64)
    norm = np.linalg.norm(amplitudes)
    if norm > 0:
        amplitudes /= norm

    # Split into real and imaginary parts (assuming real for simplicity)
    state_vector = np.concatenate([amplitudes.real, amplitudes.imag])

    return state_vector.astype(np.float32)

if __name__ == "__main__":
    # Example usage
    print("Analyzing latent space...")
    latent_vectors, latent_2d = analyze_latent_space()

    print("\nExtracting quantum fingerprint...")
    # Use a state from the training data for realistic fingerprint
    consciousness_state = data[0]  # First sample from training data
    fingerprint = extract_quantum_fingerprint(consciousness_state)
    print(f"Quantum Fingerprint: Fidelity={fingerprint['quantum_fidelity']:.3f}, Entropy={fingerprint['entanglement_entropy']:.3f}")

    print("\nDNA to Quantum conversion example...")
    dna_seq = "ATCGATCG"
    quantum_state = dna_to_quantum_state(dna_seq)
    print(f"DNA sequence '{dna_seq}' → Quantum state shape: {quantum_state.shape}")

    print("\nAnalysis complete! Check 'latent_space_analysis.png' for visualization.")
