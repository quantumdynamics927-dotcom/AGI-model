import torch
import numpy as np
from vae_model import QuantumVAE
import matplotlib.pyplot as plt

def analyze_golden_ratio_in_latent_space(model_path='best_model.pt', num_samples=1000):
    """
    Analyze if the VAE latent space exhibits golden ratio properties
    as suggested by phyllotaxis and optimal packing theory.
    """
    print("🔍 Analyzing Golden Ratio Properties in Quantum VAE Latent Space")
    print("=" * 60)

    # Load trained model
    model = QuantumVAE()
    model.load_state_dict(torch.load(model_path))
    model.eval()

    # Generate synthetic quantum data
    print(f"Generating {num_samples} quantum state samples...")
    data = []
    for _ in range(num_samples):
        real = np.random.randn(64)
        imag = np.random.randn(64)
        state = real + 1j * imag
        state = state / np.linalg.norm(state)
        sample = np.concatenate([state.real, state.imag])
        data.append(sample)
    data = np.array(data, dtype=np.float32)

    # Extract latent representations
    data_tensor = torch.from_numpy(data)
    with torch.no_grad():
        mu, log_var = model.encode(data_tensor)
        latent_codes = mu.numpy()

    print(f"Latent space shape: {latent_codes.shape}")
    print(f"Latent statistics: mean={latent_codes.mean():.3f}, std={latent_codes.std():.3f}")

    # Golden ratio analysis
    phi = (1 + np.sqrt(5)) / 2  # ≈ 1.618033988749895
    print(f"\nGolden ratio φ = {phi:.6f}")

    # Analyze ratios between adjacent dimensions
    print("\n📐 Analyzing dimension ratios...")
    ratios = []
    golden_proximities = []

    for i in range(latent_codes.shape[1] - 1):
        dim_ratios = latent_codes[:, i+1] / (latent_codes[:, i] + 1e-8)  # Avoid division by zero
        ratios.extend(dim_ratios)

        # Calculate proximity to golden ratio
        proximity = np.abs(dim_ratios - phi)
        golden_proximities.extend(proximity)

    ratios = np.array(ratios)
    golden_proximities = np.array(golden_proximities)

    # Statistics
    print(f"Total ratio measurements: {len(ratios)}")
    print(f"Ratio statistics: mean={ratios.mean():.3f}, std={ratios.std():.3f}")
    print(f"Golden ratio proximities: mean={golden_proximities.mean():.3f}, std={golden_proximities.std():.3f}")

    # Find dimensions with golden ratio properties
    threshold = 0.1  # Within 10% of golden ratio
    golden_dims = []

    for i in range(latent_codes.shape[1] - 1):
        dim_ratios = latent_codes[:, i+1] / (latent_codes[:, i] + 1e-8)
        proximity = np.abs(dim_ratios - phi)
        golden_ratio_count = np.sum(proximity < threshold)
        golden_ratio_fraction = golden_ratio_count / len(dim_ratios)

        if golden_ratio_fraction > 0.05:  # At least 5% of samples exhibit golden ratio
            golden_dims.append((i, i+1, golden_ratio_fraction))
            print(f"Dimensions {i}→{i+1}: {golden_ratio_fraction:.1%} exhibit golden ratio properties")

    print(f"\n✨ Found {len(golden_dims)} dimension pairs with golden ratio properties")

    # Visualize golden ratio distribution
    plt.figure(figsize=(12, 4))

    plt.subplot(1, 3, 1)
    plt.hist(ratios, bins=50, alpha=0.7, color='blue', edgecolor='black')
    plt.axvline(phi, color='red', linestyle='--', linewidth=2, label=f'φ = {phi:.3f}')
    plt.xlabel('Dimension Ratios')
    plt.ylabel('Frequency')
    plt.title('Latent Dimension Ratios')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.subplot(1, 3, 2)
    plt.hist(golden_proximities, bins=50, alpha=0.7, color='green', edgecolor='black')
    plt.axvline(threshold, color='orange', linestyle='--', linewidth=2, label=f'Threshold = {threshold}')
    plt.xlabel('Distance from Golden Ratio')
    plt.ylabel('Frequency')
    plt.title('Golden Ratio Proximity')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.subplot(1, 3, 3)
    # Plot latent space with golden ratio highlighting
    plt.scatter(latent_codes[:, 0], latent_codes[:, 1], alpha=0.6, s=10, color='lightgray', label='All points')

    if golden_dims:
        # Highlight points that exhibit golden ratio in first two dimensions
        dim_ratios = latent_codes[:, 1] / (latent_codes[:, 0] + 1e-8)
        proximity = np.abs(dim_ratios - phi)
        golden_points = proximity < threshold
        if np.any(golden_points):
            plt.scatter(latent_codes[golden_points, 0], latent_codes[golden_points, 1],
                       alpha=0.8, s=20, color='gold', label='Golden ratio points')

    plt.xlabel('Latent Dimension 0')
    plt.ylabel('Latent Dimension 1')
    plt.title('Latent Space with Golden Ratio')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('golden_ratio_analysis.png', dpi=300, bbox_inches='tight')
    print("📊 Golden ratio analysis saved to 'golden_ratio_analysis.png'")

    # Conclusions
    print("\n🎯 Analysis Results:")
    if len(golden_dims) > 0:
        print(f"✅ Found {len(golden_dims)} dimension pairs exhibiting golden ratio properties")
        print("This suggests the quantum VAE latent space may follow optimal packing principles")
        print("similar to phyllotaxis in biological systems!")
    else:
        print("❌ No significant golden ratio patterns detected in latent space")
        print("The quantum consciousness representations may follow different optimization principles")

    # Theoretical connection
    print("\n🔬 Theoretical Connection:")
    print("The golden ratio appears in phyllotaxis (plant growth patterns) as the unique")
    print("angle that provides globally optimal packing. If quantum consciousness states")
    print("exhibit similar properties, it would suggest deep connections between:")
    print("- Quantum information geometry")
    print("- Biological optimization principles")
    print("- Sacred geometry and natural patterns")

    return latent_codes, ratios, golden_proximities

if __name__ == "__main__":
    analyze_golden_ratio_in_latent_space()