"""
Lightweight Deep-Learning Quantum Monte Carlo (DL-QMC) utilities.

Features:
- Simple MLP wavefunction parameterization for bosonic systems (log-amplitude output)
- Metropolis sampling for electron coordinates
- Local energy computation via PyTorch autograd (kinetic + potential)
- VMC training loop using energy minimization

This implementation is intentionally minimal for research prototyping and unit tests.
"""
from typing import Callable, Tuple, Optional
import math
import torch
import torch.nn as nn
import torch.optim as optim


class WaveFunctionNet(nn.Module):
    """Simple MLP that returns log |psi(x)|. For bosonic H-atom psi>0 so sign is positive."""

    def __init__(self, input_dim: int = 3, hidden: int = 128, layers: int = 3):
        super().__init__()
        dims = [input_dim] + [hidden] * layers + [1]
        modules = []
        for i in range(len(dims) - 2):
            modules.append(nn.Linear(dims[i], dims[i + 1]))
            modules.append(nn.SiLU())
        modules.append(nn.Linear(dims[-2], dims[-1]))
        self.net = nn.Sequential(*modules)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, 3) positions
        return self.net(x).squeeze(-1)


def hydrogen_potential(x: torch.Tensor) -> torch.Tensor:
    """Coulomb potential for H nucleus at origin: V(r) = -1/|r| (Hartree units).
    x: (batch, 3)
    returns: (batch,)
    """
    r = torch.norm(x, dim=-1)
    return -1.0 / (r + 1e-10)


def laplacian(fn: Callable[[torch.Tensor], torch.Tensor], x: torch.Tensor) -> torch.Tensor:
    """Compute Laplacian of scalar function fn at x using autograd.
    x requires_grad=True.
    returns: (batch,) laplacian
    """
    x = x.requires_grad_(True)
    y = fn(x)
    grads = torch.autograd.grad(y, x, grad_outputs=torch.ones_like(y), create_graph=True)[0]
    lap = torch.zeros(x.shape[0], device=x.device)
    for d in range(x.shape[1]):
        grad_d = grads[:, d]
        grad2 = torch.autograd.grad(grad_d, x, grad_outputs=torch.ones_like(grad_d), retain_graph=True)[0][:, d]
        lap += grad2
    return lap


def local_energy(logpsi_fn: Callable[[torch.Tensor], torch.Tensor], x: torch.Tensor, potential_fn: Callable[[torch.Tensor], torch.Tensor]) -> torch.Tensor:
    """Compute local energy E_L = -1/2 * (nabla^2 psi)/psi + V
    Using logpsi: psi = exp(logpsi), so (nabla^2 psi)/psi = lap(logpsi) + |grad logpsi|^2
    """
    # compute logpsi
    logpsi = logpsi_fn(x)
    # compute gradients of logpsi
    grads = torch.autograd.grad(logpsi, x, grad_outputs=torch.ones_like(logpsi), create_graph=True)[0]
    grad2 = torch.sum(grads * grads, dim=-1)
    # laplacian of logpsi
    lap_logpsi = laplacian(logpsi_fn, x)
    kinetic = -0.5 * (lap_logpsi + grad2)
    potential = potential_fn(x)
    return kinetic + potential


def metropolis_step(x: torch.Tensor, logpsi_fn: Callable[[torch.Tensor], torch.Tensor], step_size: float = 0.5) -> Tuple[torch.Tensor, torch.Tensor]:
    """Do one Metropolis-Hastings step with symmetric gaussian proposal per walker.
    x: (batch, 3)
    returns new_x, accept_rate
    """
    device = x.device
    proposal = x + step_size * torch.randn_like(x)
    with torch.no_grad():
        logp_old = 2.0 * logpsi_fn(x)
        logp_new = 2.0 * logpsi_fn(proposal)
        log_accept = logp_new - logp_old
        accept = (torch.log(torch.rand(x.shape[0], device=device)) < log_accept).unsqueeze(-1)
        new_x = torch.where(accept, proposal, x)
        acc_rate = accept.float().mean()
    return new_x, acc_rate


def langevin_step(x: torch.Tensor, logpsi_fn: Callable[[torch.Tensor], torch.Tensor], step_size: float = 0.5) -> Tuple[torch.Tensor, torch.Tensor]:
    """Perform one Metropolis-adjusted Langevin (MALA) step.

    Proposal: y = x + 0.5 * step_size^2 * grad log p(x) + step_size * N(0,1)
    where log p = 2 * logpsi.
    Acceptance uses forward/backward Gaussian transition probabilities.
    """
    device = x.device
    x = x.requires_grad_(True)
    # compute gradient of logpsi at x
    logpsi_x = logpsi_fn(x)
    grads_x = torch.autograd.grad(logpsi_x, x, grad_outputs=torch.ones_like(logpsi_x), create_graph=False)[0]
    grad_logp_x = 2.0 * grads_x
    drift_x = 0.5 * (step_size ** 2) * grad_logp_x
    noise = step_size * torch.randn_like(x)
    proposal = (x + drift_x + noise).detach()

    # compute reverse drift at proposal
    proposal = proposal.requires_grad_(True)
    logpsi_y = logpsi_fn(proposal)
    grads_y = torch.autograd.grad(logpsi_y, proposal, grad_outputs=torch.ones_like(logpsi_y), create_graph=False)[0]
    grad_logp_y = 2.0 * grads_y
    drift_y = 0.5 * (step_size ** 2) * grad_logp_y

    # log target (unnormalized): log p = 2 * logpsi
    with torch.no_grad():
        logp_x = 2.0 * logpsi_x.detach()
        logp_y = 2.0 * logpsi_y.detach()

        def gaussian_logpdf(z, mean, sigma):
            var = (sigma ** 2)
            dim = z.shape[1]
            exponent = -0.5 * torch.sum((z - mean) ** 2, dim=1) / (var + 1e-12)
            norm = -0.5 * dim * math.log(2 * math.pi * var)
            return exponent + norm

        log_q_xy = gaussian_logpdf(proposal, x + drift_x, step_size)
        log_q_yx = gaussian_logpdf(x, proposal + drift_y, step_size)
        log_accept = (logp_y + log_q_yx) - (logp_x + log_q_xy)
        accept = (torch.log(torch.rand(x.shape[0], device=device)) < log_accept).unsqueeze(-1)
        new_x = torch.where(accept, proposal.detach(), x.detach())
        acc_rate = accept.float().mean()
    return new_x, acc_rate


def sample_positions(initial: torch.Tensor, logpsi_fn: Callable[[torch.Tensor], torch.Tensor], n_steps: int = 100, step_size: float = 0.5, sampler: str = 'metropolis') -> torch.Tensor:
    """Run a short MCMC chain for each walker and return final positions.

    sampler: 'metropolis' (default) or 'langevin'
    initial: (n_walkers, 3)
    returns positions (n_walkers, 3) and average acceptance rate
    """
    x = initial.clone()
    acc = 0.0
    for _ in range(n_steps):
        if sampler == 'langevin':
            x, a = langevin_step(x, logpsi_fn, step_size=step_size)
        else:
            x, a = metropolis_step(x, logpsi_fn, step_size=step_size)
        acc += a
    return x, (acc / n_steps)


def estimate_energy(model: nn.Module, x: torch.Tensor, potential_fn: Callable[[torch.Tensor], torch.Tensor]) -> torch.Tensor:
    """Estimate mean local energy for positions x (requires_grad=True)."""
    # logpsi_fn wrapper
    def lp(z: torch.Tensor):
        return model(z)

    x = x.requires_grad_(True)
    E_L = local_energy(lp, x, potential_fn)
    return E_L.mean().detach()


def vmc_train(model: nn.Module,
              n_walkers: int = 256,
              steps_per_epoch: int = 20,
              n_epochs: int = 200,
              lr: float = 1e-3,
              step_size: float = 0.5,
              sampler: str = 'metropolis',
              device: Optional[torch.device] = None):
    """Train the wavefunction model via simple VMC energy minimization.

    sampler: 'metropolis' (default) or 'langevin' (MALA)

    Returns the final estimated energy and the trained model.
    """
    device = device or (torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu'))
    model.to(device)
    opt = optim.Adam(model.parameters(), lr=lr)

    # initialize walkers from gaussian around origin
    x = 0.1 * torch.randn(n_walkers, 3, device=device)

    def logpsi_fn(z: torch.Tensor):
        return model(z)

    for epoch in range(n_epochs):
        # sample positions using chosen sampler
        x, acc = sample_positions(x, logpsi_fn, n_steps=steps_per_epoch, step_size=step_size, sampler=sampler)
        x = x.detach().requires_grad_(True)
        # compute local energies per walker
        E_L = local_energy(logpsi_fn, x, hydrogen_potential)
        loss = E_L.mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
        if epoch % max(1, n_epochs // 10) == 0:
            print(f"Epoch {epoch}/{n_epochs}: E = {loss.item():.6f}, acc={acc:.3f}, sampler={sampler}")
    # final energy estimate
    x = x.detach().requires_grad_(True)
    final_energy = local_energy(logpsi_fn, x, hydrogen_potential).mean().item()
    return final_energy, model

if __name__ == '__main__':
    # quick sanity check: train small model for hydrogen
    torch.manual_seed(0)
    net = WaveFunctionNet(input_dim=3, hidden=64, layers=2)
    e, _ = vmc_train(net, n_walkers=512, steps_per_epoch=10, n_epochs=60, lr=5e-3, step_size=0.8)
    print('Final energy (Hartree):', e)
