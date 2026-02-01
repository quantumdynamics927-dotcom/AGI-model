import torch
from dl_qmc import WaveFunctionNet, vmc_train, hydrogen_potential


def test_vmc_reduces_energy():
    torch.manual_seed(42)
    net = WaveFunctionNet(input_dim=3, hidden=64, layers=2)
    # short training for test purposes
    initial_net = WaveFunctionNet(input_dim=3, hidden=64, layers=2)
    # copy state to make starting energies comparable
    initial_net.load_state_dict(net.state_dict())

    e_before, _ = vmc_train(net, n_walkers=128, steps_per_epoch=5, n_epochs=5, lr=1e-3, step_size=0.7)
    # small additional pass to get reference
    e_after, _ = vmc_train(net, n_walkers=128, steps_per_epoch=5, n_epochs=10, lr=5e-4, step_size=0.7)

    print('e_before', e_before, 'e_after', e_after)
    assert e_after <= e_before + 1e-6, "Energy did not decrease after training"
    # sanity check that we move toward hydrogen ground state (-0.5 Hartree) loosely
    assert e_after < -0.3, "Trained energy not reasonable for H (expected < -0.3)"