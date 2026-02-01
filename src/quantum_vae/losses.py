import torch


def reconstruction_loss(recon_x, x):
    """Mean squared error reconstruction loss."""
    return torch.nn.functional.mse_loss(recon_x, x, reduction='mean')


def kl_divergence(mu, logvar):
    """Standard VAE KL divergence (mean over batch)."""
    return -0.5 * torch.mean(1 + logvar - mu.pow(2) - logvar.exp())


def hamming_loss(recon_x, x):
    """Approximate Hamming distance for continuous outputs by thresholding at 0.5.

    Returns mean fraction of differing bits.
    """
    recon_bits = (recon_x > 0.5).float()
    x_bits = (x > 0.5).float()
    return torch.mean((recon_bits != x_bits).float())


def coherence_loss(recon_x, x):
    """Simple phase-coherence proxy using normalized cross-correlation.

    This treats inputs as real-valued amplitudes and encourages aligned phases
    via normalized dot-product (1 - cosine similarity).
    """
    rx = recon_x.view(recon_x.size(0), -1)
    tx = x.view(x.size(0), -1)
    rx = rx - rx.mean(dim=1, keepdim=True)
    tx = tx - tx.mean(dim=1, keepdim=True)
    rx_norm = torch.nn.functional.normalize(rx, dim=1)
    tx_norm = torch.nn.functional.normalize(tx, dim=1)
    cos = (rx_norm * tx_norm).sum(dim=1)
    return torch.mean(1.0 - cos)


def mixed_state_loss(mu):
    """Proxy loss to encourage latent codes to form well-behaved density matrices.

    Builds a simple empirical covariance matrix and penalizes negative eigenvalues
    to encourage positive-semidefiniteness and trace normalization.
    """
    z = mu - mu.mean(dim=0, keepdim=True)
    cov = (z.t() @ z) / (z.size(0) - 1 + 1e-8)
    # symmetricize
    cov = 0.5 * (cov + cov.t())
    # eigenvalues (small latent_dim so this is acceptable)
    evals = torch.linalg.eigvalsh(cov)
    # penalize negative eigenvalues and deviation from unit trace
    neg_penalty = torch.sum(torch.clamp(-evals, min=0.0))
    trace_penalty = torch.abs(torch.trace(cov) - 1.0)
    return neg_penalty + trace_penalty


def fidelity_loss(recon_x, x):
    """Proxy for quantum fidelity using normalized inner product.

    For normalized real vectors, fidelity ~ |<psi|phi>|^2; we use normalized dot.
    """
    rx = recon_x.view(recon_x.size(0), -1)
    tx = x.view(x.size(0), -1)
    rx = rx / (rx.norm(dim=1, keepdim=True) + 1e-8)
    tx = tx / (tx.norm(dim=1, keepdim=True) + 1e-8)
    overlap = (rx * tx).sum(dim=1)
    return torch.mean(1.0 - overlap.pow(2))


def entropy_loss(mu):
    """Proxy entropy loss on latent marginals encouraging non-degenerate codes.

    Uses differential entropy approximation via log-variance.
    """
    var = torch.var(mu, dim=0) + 1e-8
    # differential entropy for Gaussian ~ 0.5 * log(2*pi*e*var)
    ent = 0.5 * torch.log(2.0 * torch.pi * torch.e * var)
    return -torch.mean(ent)  # maximize entropy -> minimize negative


def hw_deviation_loss(mu):
    """Placeholder hardware-deviation loss.

    Penalizes large latent magnitudes as a proxy for hardware compatibility.
    """
    return torch.mean(torch.relu(torch.abs(mu) - 3.0))
