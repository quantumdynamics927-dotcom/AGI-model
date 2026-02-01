import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch
from dl_qmc import WaveFunctionNet, vmc_train


def test_vmc_langevin_reduces_energy():
    torch.manual_seed(123)
    net = WaveFunctionNet(input_dim=3, hidden=64, layers=2)

    e_before, _ = vmc_train(net, n_walkers=128, steps_per_epoch=5, n_epochs=3, lr=1e-3, step_size=0.6, sampler='langevin')
    e_after, _ = vmc_train(net, n_walkers=128, steps_per_epoch=5, n_epochs=6, lr=5e-4, step_size=0.6, sampler='langevin')

    print('langevin e_before', e_before, 'e_after', e_after)
    assert e_after <= e_before + 1e-6, "Langevin: Energy did not decrease after training"
    assert e_after < -0.25, "Langevin: Trained energy not reasonable for H (expected < -0.25)"
