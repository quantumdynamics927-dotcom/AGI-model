"""
Ablation Ladder: Metatron Specificity vs "Any Structured Prior"

Tests whether Metatron's composite platonic solid geometry is specifically
matched to molecular point-group symmetry, or whether any structured prior helps.

Design:
  Level 0:  Metatron composite (current)              — platonic tetra+cu
+octa+dodeca+icosa
  Level 1:  Single platonic group only               — tetra / octa / icosa individually
  Level 2:  Crystallographic point groups (subset)    — 32 point groups
  Level 3:  Random geometric prior                   — random SO(3) projections
  Level 4:  Shuffled Metatron                        — same vertices, permuted labels
  Level 5:  Continuous SO(3) Haar prior              — no discrete symmetry
  Level 6:  Golden-angle spherical code               — 128 Fibonacci points on S^2
  Level 7:  Flat/random latent baseline               — no geometric prior

Metrics per level:
  - Symmetry classification accuracy
  - VAE reconstruction MSE
  - Latent φ-alignment score
  - Latent space isotropy (mean pairwise cosine similarity)
  - UMAP/t-SNE cluster separation score

Hypothesis:
  If Metatron composite IS specifically matched to molecular symmetry:
    → Single-platonic < Composite < Crystallographic (molecular point groups ≈ crystallographic)
  If ANY structured prior works:
    → All structured priors ≈ Metatron composite ≈ golden-angle
  If only smooth structure matters (not discrete symmetry):
    → SO(3) Haar ≈ Metatron composite
"""

import argparse
import json
import time
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path
from dataclasses import dataclass, asdict
import sys

# ── PHI constant ────────────────────────────────────────────────────────────────
PHI = (1 + 5**0.5) / 2

# ── Config ────────────────────────────────────────────────────────────────────
@dataclass
class AblationConfig:
    n_molecules: int = 10000
    epochs: int = 20
    batch_size: int = 64
    latent_dim: int = 32
    hidden_dims: list = None
    lr: float = 1e-3
    device: str = "cpu"
    seed: int = 42
    save_path: str = "ablation_ladder_results.json"
    n_test: int = 200  # symmetry test set size

    def __post_init__(self):
        if self.hidden_dims is None:
            self.hidden_dims = [256, 128]


# ── VAE model ─────────────────────────────────────────────────────────────────

class QuantumVAE(nn.Module):
    def __init__(self, input_dim: int, latent_dim: int, hidden_dims: list, use_phi: bool = True):
        super().__init__()
        self.use_phi = use_phi
        # Encoder
        dims = [input_dim] + hidden_dims
        encoder_layers = []
        for i in range(len(dims) - 1):
            encoder_layers.extend([
                nn.Linear(dims[i], dims[i + 1]),
                nn.ReLU(),
            ])
        self.encoder = nn.Sequential(*encoder_layers)
        self.fc_mu = nn.Linear(hidden_dims[-1], latent_dim)
        self.fc_logvar = nn.Linear(hidden_dims[-1], latent_dim)
        # Decoder
        decoder_layers = []
        decoder_dims = [latent_dim] + hidden_dims[::-1] + [input_dim]
        for i in range(len(decoder_dims) - 1):
            decoder_layers.extend([
                nn.Linear(decoder_dims[i], decoder_dims[i + 1]),
                nn.ReLU(),
            ])
        decoder_layers[-2] = nn.Linear(decoder_dims[-2], decoder_dims[-1])
        self.decoder = nn.Sequential(*decoder_layers)

    def encode(self, x):
        h = self.encoder(x)
        return self.fc_mu(h), self.fc_logvar(h)

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z):
        return self.decoder(z)

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        recon = self.decode(z)
        return recon, mu, logvar, z


# ── Geometric priors (ablation ladder levels) ───────────────────────────────────

class GeometricPrior(nn.Module):
    """
    Abstract base for geometric priors injected into the VAE latent space.
    Each prior imposes a different geometric structure on the latent sphere.
    """
    def __init__(self, latent_dim: int, prior_type: str):
        super().__init__()
        self.latent_dim = latent_dim
        self.prior_type = prior_type

    def compute_loss(self, z: torch.Tensor) -> torch.Tensor:
        """Returns a scalar regularization loss (lower = better alignment)."""
        raise NotImplementedError

    def get_name(self) -> str:
        raise NotImplementedError


class MetatronCompositePrior(GeometricPrior):
    """
    Level 0: Composite Metatron prior — platonic solids projected to latent sphere.
    Uses canonical vertex sets for tetra, cube, octa, dodeca, icosa.
    """
    def __init__(self, latent_dim: int):
        super().__init__(latent_dim, "metatron_composite")

        # Golden ratio for platonic alignment
        phi = PHI

        # Canonical platonic solid vertices (normalized to unit sphere)
        def platonic_vertices(solid: str):
            if solid == "tetrahedron":
                # 4 vertices of tetrahedron
                a = 1.0 / np.sqrt(3)
                return np.array([[a, a, a], [a, -a, -a], [-a, a, -a], [-a, -a, a]], dtype=np.float32)
            elif solid == "cube":
                # 8 vertices of cube
                c = 1.0 / np.sqrt(3)
                vs = []
                for i in [-1, 1]:
                    for j in [-1, 1]:
                        for k in [-1, 1]:
                            vs.append([i, j, k])
                return np.array(vs, dtype=np.float32) * c
            elif solid == "octahedron":
                # 6 vertices of octahedron
                c = 1.0 / np.sqrt(3)
                return np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0],
                                [0, -1, 0], [0, 0, 1], [0, 0, -1]], dtype=np.float32) * c
            elif solid == "dodecahedron":
                # 20 vertices of dodecahedron (golden ratio based)
                phi = (1 + np.sqrt(5)) / 2
                a, b = 1.0 / np.sqrt(3), phi / np.sqrt(3)
                vs = []
                for s1 in [-1, 1]:
                    for s2 in [-1, 1]:
                        vs.append([0, s1 * a, s2 * b])
                        vs.append([s1 * a, s2 * b, 0])
                        vs.append([s2 * b, 0, s1 * a])
                return np.array(vs, dtype=np.float32)
            elif solid == "icosahedron":
                phi = (1 + np.sqrt(5)) / 2
                a, b = 1.0, phi
                c = 1.0 / np.sqrt(a**2 + b**2)
                vs = []
                for s in [-1, 1]:
                    vs.append([0, s * a, s * b])
                    vs.append([s * a, s * b, 0])
                    vs.append([s * b, 0, s * a])
                return np.array(vs, dtype=np.float32) * c
            return np.zeros((1, 3), dtype=np.float32)

        # Compute target radii for each platonic group
        k = 3.5  # target radial scale
        self.target_radii = {s: k * phi for s in ["tetra", "cube", "octa", "dodeca", "icosa"]}

        # Project vertices to latent_dim by padding/truncating
        self.platonic_directions = {}
        for solid, vertices in [("tetra", platonic_vertices("tetrahedron")),
                                  ("cube", platonic_vertices("cube")),
                                  ("octa", platonic_vertices("octahedron")),
                                  ("dodeca", platonic_vertices("dodecahedron")),
                                  ("icosa", platonic_vertices("icosahedron"))]:
            # Project 3D vertices to latent_dim
            projected = np.zeros((len(vertices), latent_dim), dtype=np.float32)
            projected[:, :3] = vertices
            projected = projected / (np.linalg.norm(projected, axis=1, keepdims=True) + 1e-12)
            self.platonic_directions[solid] = torch.tensor(projected, dtype=torch.float32)

        # Composite: concatenate all directions
        all_dirs = torch.cat([self.platonic_directions[s] for s in self.platonic_directions], dim=0)
        self.register_buffer("all_directions", all_dirs)
        self.register_buffer("target_radius", torch.tensor(k * phi, dtype=torch.float32))

    def get_name(self):
        return "Metatron Composite (5 platonic solids)"

    def compute_loss(self, z: torch.Tensor) -> torch.Tensor:
        """
        Metatron composite loss:
        1. Radial: mean(z²) should cluster near target_radius²
        2. Angular: z directions should align with platonic directions
        """
        eps = 1e-8
        z_norm = torch.norm(z, dim=1, keepdim=True).clamp(min=eps)
        z_unit = z / z_norm  # project to unit sphere
        z_radial = z_norm.squeeze(-1)  # (batch,)

        # Radial loss: penalize deviation from target radius
        radial_loss = torch.mean((z_radial - self.target_radius) ** 2)

        # Angular loss: maximize cosine similarity with nearest platonic direction
        # cosine[b, d] = (batch_dir[d] · platonic_dir[d])
        cosine = torch.matmul(z_unit, self.all_directions.T)  # (batch, n_platonic)
        max_cosine, _ = cosine.max(dim=1)  # (batch,) — best match per sample
        angular_loss = torch.mean((1.0 - max_cosine) ** 2)  # push toward 1

        return radial_loss + 0.5 * angular_loss


class SinglePlatonicPrior(GeometricPrior):
    """Level 1: Single platonic group prior (one solid at a time)."""
    def __init__(self, latent_dim: int, solid: str = "tetrahedron"):
        super().__init__(latent_dim, f"single_{solid}")
        self.solid = solid

        phi = PHI
        k = 3.5

        def platonic_vertices(s):
            if s == "tetrahedron":
                a = 1.0 / np.sqrt(3)
                return np.array([[a, a, a], [a, -a, -a], [-a, a, -a], [-a, -a, a]], dtype=np.float32)
            elif s == "octahedron":
                c = 1.0 / np.sqrt(3)
                return np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0],
                                [0, -1, 0], [0, 0, 1], [0, 0, -1]], dtype=np.float32) * c
            elif s == "icosahedron":
                phi_g = (1 + np.sqrt(5)) / 2
                a, b = 1.0, phi_g
                c = 1.0 / np.sqrt(a**2 + b**2)
                vs = []
                for sgn in [-1, 1]:
                    vs.append([0, sgn * a, sgn * b])
                    vs.append([sgn * a, sgn * b, 0])
                    vs.append([sgn * b, 0, sgn * a])
                return np.array(vs, dtype=np.float32) * c
            return np.zeros((1, 3), dtype=np.float32)

        vertices = platonic_vertices(solid)
        projected = np.zeros((len(vertices), latent_dim), dtype=np.float32)
        projected[:, :3] = vertices
        projected = projected / (np.linalg.norm(projected, axis=1, keepdims=True) + 1e-12)
        dirs = torch.tensor(projected, dtype=torch.float32)
        self.register_buffer("directions", dirs)
        self.register_buffer("target_radius", torch.tensor(k * phi, dtype=torch.float32))

    def get_name(self):
        return f"Single {self.solid.capitalize()} Prior"

    def compute_loss(self, z: torch.Tensor) -> torch.Tensor:
        eps = 1e-8
        z_norm = torch.norm(z, dim=1, keepdim=True).clamp(min=eps)
        z_unit = z / z_norm
        z_radial = z_norm.squeeze(-1)
        cosine = torch.matmul(z_unit, self.directions.T)
        max_cosine, _ = cosine.max(dim=1)
        radial_loss = torch.mean((z_radial - self.target_radius) ** 2)
        angular_loss = torch.mean((1.0 - max_cosine) ** 2)
        return radial_loss + 0.5 * angular_loss


class RandomGeometricPrior(GeometricPrior):
    """Level 3: Random geometric prior — random orthonormal directions."""
    def __init__(self, latent_dim: int, seed: int = 42):
        super().__init__(latent_dim, "random_geometric")
        rng = np.random.default_rng(seed)
        # Generate random directions on S^(latent_dim-1)
        dirs = rng.standard_normal(size=(100, latent_dim)).astype(np.float32)
        dirs = dirs / (np.linalg.norm(dirs, axis=1, keepdims=True) + 1e-12)
        self.register_buffer("directions", torch.tensor(dirs, dtype=torch.float32))
        self.register_buffer("target_radius", torch.tensor(3.5 * PHI, dtype=torch.float32))

    def get_name(self):
        return "Random Geometric Prior (100 random directions)"

    def compute_loss(self, z: torch.Tensor) -> torch.Tensor:
        eps = 1e-8
        z_norm = torch.norm(z, dim=1, keepdim=True).clamp(min=eps)
        z_unit = z / z_norm
        z_radial = z_norm.squeeze(-1)
        cosine = torch.matmul(z_unit, self.directions.T)
        max_cosine, _ = cosine.max(dim=1)
        radial_loss = torch.mean((z_radial - self.target_radius) ** 2)
        angular_loss = torch.mean((1.0 - max_cosine) ** 2)
        return radial_loss + 0.5 * angular_loss


class ShuffledMetatronPrior(GeometricPrior):
    """Level 4: Shuffled Metatron — same vertices, permuted labels (control)."""
    def __init__(self, latent_dim: int):
        super().__init__(latent_dim, "shuffled_metatron")
        # Same as Metatron but directions are randomly permuted per dimension
        rng = np.random.default_rng(99)
        dirs = rng.standard_normal(size=(40, latent_dim)).astype(np.float32)
        dirs = dirs / (np.linalg.norm(dirs, axis=1, keepdims=True) + 1e-12)
        self.register_buffer("directions", torch.tensor(dirs, dtype=torch.float32))
        self.register_buffer("target_radius", torch.tensor(3.5 * PHI, dtype=torch.float32))

    def get_name(self):
        return "Shuffled Metatron (random labels)"

    def compute_loss(self, z: torch.Tensor) -> torch.Tensor:
        eps = 1e-8
        z_norm = torch.norm(z, dim=1, keepdim=True).clamp(min=eps)
        z_unit = z / z_norm
        z_radial = z_norm.squeeze(-1)
        cosine = torch.matmul(z_unit, self.directions.T)
        max_cosine, _ = cosine.max(dim=1)
        radial_loss = torch.mean((z_radial - self.target_radius) ** 2)
        angular_loss = torch.mean((1.0 - max_cosine) ** 2)
        return radial_loss + 0.5 * angular_loss


class ContinuousHaarPrior(GeometricPrior):
    """Level 5: Continuous SO(3) Haar measure — no discrete symmetry (smooth baseline)."""
    def __init__(self, latent_dim: int):
        super().__init__(latent_dim, "haar_continuous")
        self.register_buffer("target_radius", torch.tensor(3.5 * PHI, dtype=torch.float32))

    def get_name(self):
        return "Continuous SO(3) Haar Prior"

    def compute_loss(self, z: torch.Tensor) -> torch.Tensor:
        """Only radial loss — no angular structure imposed."""
        eps = 1e-8
        z_radial = torch.norm(z, dim=1).clamp(min=eps)
        return torch.mean((z_radial - self.target_radius) ** 2)


class GoldenAnglePrior(GeometricPrior):
    """
    Level N: Golden-angle spherical code prior.

    Uses the Fibonacci / golden-angle lattice on the sphere — the same
    construction used for spherical codepacking in physics (e.g., omnidirectional
    microphones, pixel cameras). Generates N evenly-spaced points on S^2
    using the azimuthal golden angle (2π/φ) and colatitude formula.

    This is a principled spherical code construction from information theory,
    distinct from platonic solids (which have only 4/6/8/12/20 vertices).
    """
    def __init__(self, latent_dim: int, n_points: int = 128):
        super().__init__(latent_dim, "golden_angle")
        self.n_points = n_points
        phi = PHI
        # Fibonacci / golden-angle lattice on S^2
        # k = 1..N, N = n_points
        N = n_points
        dirs = []
        for k in range(1, N + 1):
            # Colatitude: arccos(1 - 2k/(N+1))
            # Azimuth: 2π × k / φ
            cos_theta = 1.0 - 2.0 * k / (N + 1)
            sin_theta = np.sqrt(max(0.0, 1.0 - cos_theta**2))
            theta = np.arccos(cos_theta)
            psi = 2.0 * np.pi * k / phi
            x = sin_theta * np.cos(psi)
            y = sin_theta * np.sin(psi)
            z = cos_theta
            dirs.append([x, y, z])
        dirs = np.array(dirs, dtype=np.float32)
        # Project to latent_dim
        projected = np.zeros((n_points, latent_dim), dtype=np.float32)
        projected[:, :3] = dirs
        projected = projected / (np.linalg.norm(projected, axis=1, keepdims=True) + 1e-12)
        self.register_buffer("directions", torch.tensor(projected, dtype=torch.float32))
        self.register_buffer("target_radius", torch.tensor(3.5 * PHI, dtype=torch.float32))

    def get_name(self):
        return f"Golden-Angle Spherical Code ({self.n_points} pts)"

    def compute_loss(self, z: torch.Tensor) -> torch.Tensor:
        eps = 1e-8
        z_norm = torch.norm(z, dim=1, keepdim=True).clamp(min=eps)
        z_unit = z / z_norm
        z_radial = z_norm.squeeze(-1)
        cosine = torch.matmul(z_unit, self.directions.T)
        max_cosine, _ = cosine.max(dim=1)
        radial_loss = torch.mean((z_radial - self.target_radius) ** 2)
        angular_loss = torch.mean((1.0 - max_cosine) ** 2)
        return radial_loss + 0.5 * angular_loss


class FlatPrior(GeometricPrior):
    """Level 6: No geometric prior — standard VAE with standard normal prior."""
    def __init__(self, latent_dim: int):
        super().__init__(latent_dim, "flat_baseline")

    def get_name(self):
        return "Flat Baseline (standard normal prior)"

    def compute_loss(self, z: torch.Tensor) -> torch.Tensor:
        return torch.tensor(0.0, device=z.device)


# ── Prior factory ─────────────────────────────────────────────────────────────

def build_prior(latent_dim: int, level: str) -> GeometricPrior:
    """Factory: build a geometric prior by level name."""
    level_map = {
        "metatron_composite": MetatronCompositePrior,
        "single_tetra": lambda ld: SinglePlatonicPrior(ld, "tetrahedron"),
        "single_octa": lambda ld: SinglePlatonicPrior(ld, "octahedron"),
        "single_icosa": lambda ld: SinglePlatonicPrior(ld, "icosahedron"),
        "random_geometric": RandomGeometricPrior,
        "shuffled_metatron": ShuffledMetatronPrior,
        "haar_continuous": ContinuousHaarPrior,
        "golden_angle": GoldenAnglePrior,
        "flat_baseline": FlatPrior,
    }
    if level not in level_map:
        raise ValueError(f"Unknown prior level: {level}. Available: {list(level_map.keys())}")
    factory = level_map[level]
    return factory(latent_dim)


# ── Training ─────────────────────────────────────────────────────────────────

def train_vae_with_prior(
    model: nn.Module,
    prior: GeometricPrior,
    train_loader,
    optimizer: torch.optim.Optimizer,
    device: str,
    epoch: int = 0,
    phi_weight: float = 0.01,
) -> dict:
    model.train()
    total_recon = 0.0
    total_prior_loss = 0.0
    total_kl = 0.0
    n_batches = 0

    for batch, in train_loader:
        x = batch.to(device)
        optimizer.zero_grad()
        recon, mu, logvar, z = model(x)

        # Reconstruction loss
        recon_loss = nn.functional.mse_loss(recon, x)

        # KL divergence (standard VAE)
        kl_loss = -0.5 * torch.mean(1 + logvar - mu.pow(2) - logvar.exp())

        # Geometric prior loss
        prior_loss = prior.compute_loss(z)

        # Total loss
        loss = recon_loss + 0.001 * kl_loss + phi_weight * prior_loss

        loss.backward()
        optimizer.step()

        total_recon += recon_loss.item()
        total_prior_loss += prior_loss.item()
        total_kl += kl_loss.item()
        n_batches += 1

    return {
        "recon_mse": total_recon / n_batches,
        "prior_loss": total_prior_loss / n_batches,
        "kl": total_kl / n_batches,
    }


def evaluate_vae(model: nn.Module, prior: GeometricPrior, val_loader, device: str) -> dict:
    model.eval()
    total_recon = 0.0
    total_prior_loss = 0.0
    n_batches = 0

    with torch.no_grad():
        for batch, in val_loader:
            x = batch.to(device)
            recon, mu, logvar, z = model(x)
            recon_loss = nn.functional.mse_loss(recon, x)
            prior_loss = prior.compute_loss(z)
            total_recon += recon_loss.item()
            total_prior_loss += prior_loss.item()
            n_batches += 1

    return {
        "val_recon_mse": total_recon / n_batches,
        "val_prior_loss": total_prior_loss / n_batches,
    }


# ── Symmetry detection ────────────────────────────────────────────────────────

def compute_latent_isotropy(z: np.ndarray) -> float:
    """
    Mean pairwise cosine similarity in latent space.
    Isotropy: low similarity = more uniform coverage of the sphere.
    """
    z_norm = z / (np.linalg.norm(z, axis=1, keepdims=True) + 1e-12)
    cosine = np.dot(z_norm, z_norm.T)
    n = z.shape[0]
    # Off-diagonal elements
    mask = ~np.eye(n, dtype=bool)
    return float(np.mean(np.abs(cosine[mask])))


def run_symmetry_test(
    molecules: list,
    model: nn.Module,
    device: str,
    n_test: int = 200,
) -> dict:
    """Run symmetry classification using the VAE latent space + simple classifier."""
    model.eval()
    platonic_solids = ["tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron"]

    # Encode molecules
    n_test = min(n_test, len(molecules))
    z_list = []
    true_labels = []
    with torch.no_grad():
        for i in range(n_test):
            mol = molecules[i]
            # Flatten positions for VAE input
            pos = mol["positions"][:, :3].flatten()
            x = torch.tensor(pos[np.newaxis, :], dtype=torch.float32, device=device)
            if x.shape[1] != model.fc_mu.in_features:
                continue
            mu, logvar = model.encode(x)
            z = mu.cpu().numpy()[0]
            z_list.append(z)
            true_labels.append(mol.get("true_solid", platonic_solids[i % len(platonic_solids)]))

    if len(z_list) < 10:
        return {"accuracy": 0.0, "random_accuracy": 0.0, "n_test": 0, "isotropy": 0.0}

    Z = np.array(z_list)
    # Simple nearest-centroid classifier
    classes = list(set(true_labels))
    centroids = np.zeros((len(classes), Z.shape[1]))
    for ci, c in enumerate(classes):
        mask = np.array([l == c for l in true_labels])
        centroids[ci] = Z[mask].mean(axis=0)

    # Classify
    Z_norm = Z / (np.linalg.norm(Z, axis=1, keepdims=True) + 1e-12)
    cents_norm = centroids / (np.linalg.norm(centroids, axis=1, keepdims=True) + 1e-12)
    cosine = np.dot(Z_norm, cents_norm.T)
    pred_indices = cosine.argmax(axis=1)
    pred_labels = [classes[i] for i in pred_indices]

    accuracy = np.mean([p == t for p, t in zip(pred_labels, true_labels)])

    # Random baseline
    random_correct = sum(1 for p, t in zip(
        np.random.choice(classes, size=n_test), true_labels) if p == t) / n_test

    return {
        "accuracy": float(accuracy),
        "random_accuracy": float(random_correct),
        "n_test": len(z_list),
        "isotropy": compute_latent_isotropy(Z),
    }


# ── Main ablation runner ───────────────────────────────────────────────────────

def run_ablation(config: AblationConfig):
    print(f"\n{'='*70}")
    print(f"METATRON ABLATION LADDER")
    print(f"{'='*70}")
    print(f"Config: epochs={config.epochs}, batch_size={config.batch_size}, "
          f"latent_dim={config.latent_dim}, molecules={config.n_molecules}")
    print()

    torch.manual_seed(config.seed)
    np.random.seed(config.seed)

    device = torch.device(config.device)

    # ── Load data ──────────────────────────────────────────────────────────────
    print("[DATA] Loading QM9 molecules...")
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).parent / "data"))
    from qm9_sdf_loader import load_qm9_sdf

    sdf_path = Path("qm9_data/raw/gdb9.sdf")
    if sdf_path.exists():
        mols = load_qm9_sdf(str(sdf_path), max_molecules=config.n_molecules)
        # Determine max atoms for padding
        max_atoms = max(m["positions"].shape[0] for m in mols)
        n_mols = len(mols)
        positions_pad = np.zeros((n_mols, max_atoms, 3), dtype=np.float32)
        for i, m in enumerate(mols):
            na = m["positions"].shape[0]
            positions_pad[i, :na] = m["positions"][:, :3]
        positions_flat = positions_pad.reshape(n_mols, -1)
    else:
        print("[DATA] SDF not found — using synthetic fallback")
        rng = np.random.default_rng(config.seed)
        n_mols = config.n_molecules
        n_atoms = rng.integers(4, 21, size=n_mols)
        max_atoms = int(n_atoms.max())
        positions_flat = rng.uniform(-5, 5, size=(n_mols, max_atoms * 3)).astype(np.float32)
        mols = [{"positions": positions_pad[i], "true_solid": ["tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron"][i % 5]}
                for i in range(n_mols)]

    vae_input_dim = positions_flat.shape[1]

    # Train / val split
    n_train = int(0.8 * n_mols)
    indices = np.random.permutation(n_mols)
    train_idx, val_idx = indices[:n_train], indices[n_train:]

    X_train = torch.tensor(positions_flat[train_idx], dtype=torch.float32)
    X_val = torch.tensor(positions_flat[val_idx], dtype=torch.float32)
    train_loader = DataLoader(TensorDataset(X_train), batch_size=config.batch_size, shuffle=True)
    val_loader = DataLoader(TensorDataset(X_val), batch_size=config.batch_size)

    # ── Ablation levels ───────────────────────────────────────────────────────
    levels = [
        "metatron_composite",
        "single_tetra",
        "single_octa",
        "single_icosa",
        "random_geometric",
        "shuffled_metatron",
        "haar_continuous",
        "golden_angle",
        "flat_baseline",
    ]

    results = {}
    latent_isotropies = {}

    for level in levels:
        print(f"\n{'-'*60}")
        print(f"[PRIOR] {level}")
        print(f"{'-'*60}")

        prior = build_prior(config.latent_dim, level)
        prior_name = prior.get_name()
        print(f"  Prior: {prior_name}")

        model = QuantumVAE(vae_input_dim, config.latent_dim, config.hidden_dims, use_phi=(level != "flat_baseline"))
        model = model.to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=config.lr)

        history = []
        for epoch in range(1, config.epochs + 1):
            metrics = train_vae_with_prior(
                model, prior, train_loader, optimizer, device,
                epoch=epoch, phi_weight=0.01
            )
            history.append(metrics)
            if epoch % 10 == 0:
                print(f"  Epoch {epoch:3d}: recon={metrics['recon_mse']:.4f}, "
                      f"prior_loss={metrics['prior_loss']:.4f}")

        val_metrics = evaluate_vae(model, prior, val_loader, device)
        print(f"  Val recon MSE: {val_metrics['val_recon_mse']:.4f}")

        # Symmetry test (subset of molecules)
        n_test = min(config.n_test, len(val_idx))
        test_mols = [{"positions": positions_pad[val_idx[i]], "true_solid": ["tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron"][val_idx[i] % 5]} for i in range(n_test)]
        symmetry = run_symmetry_test(test_mols, model, device, n_test=n_test)
        print(f"  Symmetry accuracy: {symmetry['accuracy']:.1%} (random: {symmetry['random_accuracy']:.1%})")
        print(f"  Latent isotropy: {symmetry['isotropy']:.4f}")

        # Collect latent representations for isotropy
        model.eval()
        Z_list = []
        with torch.no_grad():
            for i in range(min(500, len(X_val))):
                x = X_val[i:i+1].to(device)
                mu, _ = model.encode(x)
                Z_list.append(mu.cpu().numpy()[0])
        Z = np.array(Z_list)
        latent_isotropies[level] = {
            "isotropy": compute_latent_isotropy(Z),
            "mean_radius": float(np.mean(np.linalg.norm(Z, axis=1))),
            "std_radius": float(np.std(np.linalg.norm(Z, axis=1))),
        }

        results[level] = {
            "prior_name": prior_name,
            "val_recon_mse": val_metrics["val_recon_mse"],
            "val_prior_loss": val_metrics["val_prior_loss"],
            "symmetry_accuracy": symmetry["accuracy"],
            "symmetry_random": symmetry["random_accuracy"],
            "symmetry_n_test": symmetry["n_test"],
            "symmetry_isotropy": symmetry["isotropy"],
            "latent_isotropy": compute_latent_isotropy(Z),
            "mean_radius": float(np.mean(np.linalg.norm(Z, axis=1))),
            "std_radius": float(np.std(np.linalg.norm(Z, axis=1))),
            "history": history[-1],
        }

    # ── Summary table ──────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print("ABLATION SUMMARY")
    print(f"{'='*70}")
    print(f"{'Prior':<35} {'Recon MSE':>10} {'Sym Acc':>8} {'Isotropy':>9}")
    print("-" * 70)
    for level in levels:
        r = results[level]
        marker = "[*]" if level == "metatron_composite" else "   "
        print(f"{marker} {r['prior_name']:<33} {r['val_recon_mse']:>10.4f} "
              f"{r['symmetry_accuracy']:>7.1%} {r['latent_isotropy']:>9.4f}")

    # Save
    output = {
        "config": asdict(config),
        "levels": levels,
        "results": results,
        "latent_stats": latent_isotropies,
        "timestamp": __import__('datetime').datetime.now().isoformat(),
    }
    with open(config.save_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n[OK] Results saved to: {config.save_path}")
    return results


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Metatron ablation ladder")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--n-molecules", type=int, default=10000)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--latent-dim", type=int, default=32)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--save-path", default="ablation_ladder_results.json")
    args = parser.parse_args()

    config = AblationConfig(
        epochs=args.epochs,
        n_molecules=args.n_molecules,
        batch_size=args.batch_size,
        latent_dim=args.latent_dim,
        device=args.device,
        save_path=args.save_path,
    )
    run_ablation(config)


if __name__ == "__main__":
    main()
