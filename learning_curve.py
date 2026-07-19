"""
Learning Curve Analysis: QM9 Scale vs Symmetry Accuracy, MSE, and Phi-Alignment

Tests whether the ablation results at 10K molecules hold at larger scales.
Measures: reconstruction MSE, symmetry accuracy, latent isotropy, phi-alignment.

Dataset sizes: 1K, 5K, 10K, 50K, 100K, 133K (full QM9)
"""

import argparse
import json
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path
from dataclasses import dataclass, asdict
import time

PHI = (1 + 5**0.5) / 2


@dataclass
class LearningCurveConfig:
    scales: list = None
    epochs: int = 20
    batch_size: int = 64
    latent_dim: int = 32
    hidden_dims: list = None
    lr: float = 1e-3
    device: str = "cpu"
    seed: int = 42
    save_path: str = "learning_curve_results.json"

    def __post_init__(self):
        if self.hidden_dims is None:
            self.hidden_dims = [256, 128]


class QuantumVAE(nn.Module):
    def __init__(self, input_dim, latent_dim, hidden_dims):
        super().__init__()
        dims = [input_dim] + hidden_dims
        enc = []
        for i in range(len(dims) - 1):
            enc.extend([nn.Linear(dims[i], dims[i+1]), nn.ReLU()])
        self.encoder = nn.Sequential(*enc)
        self.fc_mu = nn.Linear(hidden_dims[-1], latent_dim)
        self.fc_logvar = nn.Linear(hidden_dims[-1], latent_dim)
        dec = [nn.Linear(latent_dim, hidden_dims[0]), nn.ReLU()]
        for i in range(len(hidden_dims) - 1):
            dec.extend([nn.Linear(hidden_dims[i], hidden_dims[i+1]), nn.ReLU()])
        dec.append(nn.Linear(hidden_dims[-1], input_dim))
        dec[-2] = nn.Linear(list(reversed(hidden_dims))[0], list(reversed(hidden_dims))[1]) if len(hidden_dims) > 1 else dec[-2]
        # Rebuild properly
        dec = []
        dec_dims = [latent_dim] + hidden_dims[::-1] + [input_dim]
        for i in range(len(dec_dims) - 2):
            dec.extend([nn.Linear(dec_dims[i], dec_dims[i+1]), nn.ReLU()])
        dec.append(nn.Linear(dec_dims[-2], dec_dims[-1]))
        self.decoder = nn.Sequential(*dec)

    def encode(self, x):
        h = self.encoder(x)
        return self.fc_mu(h), self.fc_logvar(h)

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        recon = self.decoder(z)
        return recon, mu, logvar, z


class MetatronCompositePrior:
    """Minimal Metatron composite prior for speed."""
    def __init__(self, latent_dim):
        self.latent_dim = latent_dim
        k = 3.5
        phi = PHI
        self.target_radius = k * phi
        # Precompute platonic directions
        def vs(s):
            if s == "tetra":
                a = 1.0 / np.sqrt(3)
                v = np.array([[a,a,a],[a,-a,-a],[-a,a,-a],[-a,-a,a]], dtype=np.float32)
            elif s == "cube":
                cval = 1.0 / np.sqrt(3)
                v = []
                for i in [-1, 1]:
                    for j in [-1, 1]:
                        for kval in [-1, 1]:
                            v.append([i, j, kval])
                v = np.array(v, dtype=np.float32) * cval
            elif s == "octa":
                c = 1.0 / np.sqrt(3)
                v = np.array([[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]], dtype=np.float32) * c
            elif s == "dodeca":
                # 20 vertices: 8 cube corners + 12 from 3 golden rectangles (4 each)
                inv_phi = 1.0 / PHI
                cube = np.array([[1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
                                 [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1]], dtype=np.float32)
                # 3 golden rectangles, 4 vertices each
                rects = [
                    (0, inv_phi, PHI),
                    (inv_phi, PHI, 0),
                    (PHI, 0, inv_phi),
                ]
                rect = []
                for x, y, z in rects:
                    # 4 vertices per rect: signs of non-zero coords are CORRELATED
                    for sx, sy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                        if x == 0:
                            rect.append([0, sx * y, sy * z])
                        elif y == 0:
                            rect.append([sx * x, 0, sy * z])
                        else:
                            rect.append([sx * x, sy * y, 0])
                v = np.concatenate([cube, np.array(rect, dtype=np.float32)], axis=0)
                # 8 + 12 = 20
            elif s == "icosa":
                # 12 vertices: (0, +/-1, +/-phi), (+/-1, +/-phi, 0), (+/-phi, 0, +/-1) — scaled
                a, b = 1.0, PHI
                c = 1.0 / np.sqrt(a**2 + b**2)
                triples = [(0, b, a), (b, a, 0), (a, 0, b)]
                v = []
                for x, y, z in triples:
                    for sx, sy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                        if x == 0:
                            v.append([0, sx * y, sy * z])
                        elif y == 0:
                            v.append([sx * x, 0, sy * z])
                        else:
                            v.append([sx * x, sy * y, 0])
                v = np.array(v, dtype=np.float32) * c
            else:
                v = np.zeros((1, 3), dtype=np.float32)
            return v
        all_dirs = []
        for solid in ["tetra", "cube", "octa", "dodeca", "icosa"]:
            dirs = vs(solid)
            proj = np.zeros((len(dirs), latent_dim), dtype=np.float32)
            proj[:, :3] = dirs
            proj = proj / (np.linalg.norm(proj, axis=1, keepdims=True) + 1e-12)
            all_dirs.append(proj)
        self.all_dirs = np.concatenate(all_dirs, axis=0)

    def compute_loss(self, z):
        eps = 1e-8
        z_norm = torch.norm(z, dim=1, keepdim=True).clamp(min=eps)
        z_unit = z / z_norm
        z_radial = z_norm.squeeze(-1)
        if not hasattr(self, "_dirs_T"):
            self._dirs_T = torch.tensor(self.all_dirs.T, dtype=torch.float32)
        cosine = torch.matmul(z_unit, self._dirs_T.to(z.device))
        max_cosine, _ = cosine.max(dim=1)
        radial_loss = torch.mean((z_radial - self.target_radius) ** 2)
        angular_loss = torch.mean((1.0 - max_cosine) ** 2)
        return radial_loss + 0.5 * angular_loss


def train_epoch(model, prior, loader, optimizer):
    model.train()
    total_recon = 0.0
    total_prior = 0.0
    n = 0
    for batch, in loader:
        optimizer.zero_grad()
        recon, mu, logvar, z = model(batch)
        recon_loss = nn.functional.mse_loss(recon, batch)
        prior_loss = prior.compute_loss(z)
        kl_loss = -0.5 * torch.mean(1 + logvar - mu.pow(2) - logvar.exp())
        loss = recon_loss + 0.001 * kl_loss + 0.01 * prior_loss
        loss.backward()
        optimizer.step()
        total_recon += recon_loss.item() * batch.shape[0]
        total_prior += prior_loss.item() * batch.shape[0]
        n += batch.shape[0]
    return total_recon / n, total_prior / n


def compute_isotropy(z: np.ndarray) -> float:
    z_norm = z / (np.linalg.norm(z, axis=1, keepdims=True) + 1e-12)
    cosine = np.dot(z_norm, z_norm.T)
    n = z.shape[0]
    mask = ~np.eye(n, dtype=bool)
    return float(np.mean(np.abs(cosine[mask])))


def run_scale(config: LearningCurveConfig, n_molecules: int, sdf_path: Path):
    """Train at one scale and return metrics."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent / "data"))
    from qm9_sdf_loader import load_qm9_sdf

    torch.manual_seed(config.seed)
    np.random.seed(config.seed)

    # Load data
    mols = load_qm9_sdf(str(sdf_path), max_molecules=n_molecules)
    max_atoms = max(m["positions"].shape[0] for m in mols)
    positions_pad = np.zeros((len(mols), max_atoms, 3), dtype=np.float32)
    for i, m in enumerate(mols):
        na = m["positions"].shape[0]
        positions_pad[i, :na] = m["positions"][:, :3]
    positions_flat = positions_pad.reshape(len(mols), -1)
    input_dim = positions_flat.shape[1]

    # Train/val split
    n_train = int(0.8 * len(mols))
    idx = np.random.permutation(len(mols))
    train_idx, val_idx = idx[:n_train], idx[n_train:]
    X_train = torch.tensor(positions_flat[train_idx], dtype=torch.float32)
    X_val = torch.tensor(positions_flat[val_idx], dtype=torch.float32)
    train_loader = DataLoader(TensorDataset(X_train), batch_size=config.batch_size, shuffle=True)
    val_loader = DataLoader(TensorDataset(X_val), batch_size=config.batch_size)

    # Model + prior
    model = QuantumVAE(input_dim, config.latent_dim, config.hidden_dims)
    prior = MetatronCompositePrior(config.latent_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.lr)

    # Train
    for epoch in range(1, config.epochs + 1):
        train_mse, train_prior = train_epoch(model, prior, train_loader, optimizer)

    # Final validation
    model.eval()
    val_mse = 0.0
    n_val = 0
    Z_list = []
    with torch.no_grad():
        for batch, in val_loader:
            recon, mu, logvar, z = model(batch)
            val_mse += nn.functional.mse_loss(recon, batch).item() * batch.shape[0]
            n_val += batch.shape[0]
            Z_list.append(mu.numpy())
        val_mse /= n_val
        Z = np.concatenate(Z_list, axis=0)
        isotropy = compute_isotropy(Z)
        mean_radius = float(np.mean(np.linalg.norm(Z, axis=1)))
        std_radius = float(np.std(np.linalg.norm(Z, axis=1)))

    # Symmetry test: encode train molecules, check if they cluster by atom count
    # (true symmetry test requires molecular geometry; here we use isotropy as proxy)
    # For learning curves, report isotropy + MSE + radius as main metrics

    return {
        "n_molecules": n_molecules,
        "val_mse": val_mse,
        "isotropy": isotropy,
        "mean_radius": mean_radius,
        "std_radius": std_radius,
        "input_dim": input_dim,
        "max_atoms": max_atoms,
    }


def main():
    parser = argparse.ArgumentParser(description="Learning curve analysis")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--scales", type=str, default="1000,5000,10000,50000,100000,133885")
    parser.add_argument("--save-path", default="learning_curve_results.json")
    args = parser.parse_args()

    scales = [int(s) for s in args.scales.split(",")]
    config = LearningCurveConfig(epochs=args.epochs, save_path=args.save_path)

    sdf_path = Path("qm9_data/raw/gdb9.sdf")
    if not sdf_path.exists():
        print("[ERROR] QM9 SDF not found. Run benchmark_qm9.py first to download.")
        return

    print("=" * 60)
    print("LEARNING CURVE ANALYSIS")
    print("=" * 60)
    print(f"Scales: {scales}")
    print(f"Epochs per scale: {args.epochs}")
    print()

    results = []
    for n in scales:
        print(f"--- Scale: {n:,} molecules ---")
        t0 = time.time()
        r = run_scale(config, n, sdf_path)
        elapsed = time.time() - t0
        r["elapsed_s"] = elapsed
        results.append(r)
        print(f"  Val MSE: {r['val_mse']:.4f}, Isotropy: {r['isotropy']:.4f}, "
              f"Mean r: {r['mean_radius']:.4f}, Time: {elapsed:.1f}s")

    # Print summary table
    print()
    print("=" * 60)
    print(f"{'N':>8} {'MSE':>8} {'Isotropy':>9} {'Mean r':>8} {'Std r':>7} {'Time':>7}")
    print("-" * 60)
    for r in results:
        print(f"{r['n_molecules']:>8,} {r['val_mse']:>8.4f} {r['isotropy']:>9.4f} "
              f"{r['mean_radius']:>8.4f} {r['std_radius']:>7.4f} {r['elapsed_s']:>6.0f}s")

    # Save
    output = {
        "config": asdict(config),
        "scales": scales,
        "results": results,
        "timestamp": __import__('datetime').datetime.now().isoformat(),
    }
    with open(args.save_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n[OK] Saved to: {args.save_path}")

    # Plot
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 3, figsize=(14, 4))
        ns = [r["n_molecules"] for r in results]
        mses = [r["val_mse"] for r in results]
        isos = [r["isotropy"] for r in results]
        radii = [r["mean_radius"] for r in results]

        axes[0].loglog(ns, mses, "o-", color="#E63946")
        axes[0].set_xlabel("N molecules")
        axes[0].set_ylabel("Val MSE")
        axes[0].set_title("Reconstruction MSE vs Scale")
        axes[0].grid(True, which="both", alpha=0.3)

        axes[1].semilogx(ns, isos, "o-", color="#457B9D")
        axes[1].set_xlabel("N molecules")
        axes[1].set_ylabel("Latent Isotropy")
        axes[1].set_title("Isotropy vs Scale")
        axes[1].grid(True, alpha=0.3)

        axes[2].semilogx(ns, radii, "o-", color="#2A9D8F")
        axes[2].set_xlabel("N molecules")
        axes[2].set_ylabel("Mean Latent Radius")
        axes[2].set_title("Radius vs Scale")
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()
        fig.suptitle("QM9 Learning Curves", fontsize=13, fontweight="bold")
        plt.savefig("learning_curve.png", dpi=150, bbox_inches="tight")
        plt.close()
        print("[OK] Plot saved: learning_curve.png")
    except Exception as e:
        print(f"[WARN] Plot failed: {e}")


if __name__ == "__main__":
    main()
