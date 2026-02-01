"""Run a short DL-QMC demo comparing Metropolis vs MALA and write results to a report file."""
import time
import torch
from dl_qmc import WaveFunctionNet, vmc_train

REPORT_PATH = 'reports/dl_qmc_demo_results.txt'

if __name__ == '__main__':
    torch.manual_seed(0)
    net = WaveFunctionNet(input_dim=3, hidden=64, layers=2)
    t0 = time.time()
    e_langevin, _ = vmc_train(net, n_walkers=256, steps_per_epoch=6, n_epochs=12, lr=1e-3, step_size=0.6, sampler='langevin')
    t1 = time.time()

    net2 = WaveFunctionNet(input_dim=3, hidden=64, layers=2)
    e_meta, _ = vmc_train(net2, n_walkers=256, steps_per_epoch=6, n_epochs=12, lr=1e-3, step_size=0.6, sampler='metropolis')
    t2 = time.time()

    with open(REPORT_PATH, 'w') as f:
        f.write('DL-QMC demo results\n')
        f.write(f'Langevin energy: {e_langevin:.6f} (time {t1-t0:.2f}s)\n')
        f.write(f'Metropolis energy: {e_meta:.6f} (time {t2-t1:.2f}s)\n')
    print('Wrote report to', REPORT_PATH)