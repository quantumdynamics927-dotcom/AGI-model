import importlib.util
import sys
from pathlib import Path

script_path = Path(__file__).resolve().parent / 'hydrogen_wavefunction.py'
spec = importlib.util.spec_from_file_location('hydrogen_wavefunction', str(script_path))
hw = importlib.util.module_from_spec(spec)
sys.modules['hydrogen_wavefunction'] = hw
spec.loader.exec_module(hw)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

try:
	print('Computing hydrogen 1s wavefunction...')
	X, Y, psi_real, prob = hw.hydrogen_wavefunction(n=1, l=0, m=0, grid_size=200, extent=20.0)
	print('Grid shape:', X.shape)

	fig, ax = plt.subplots(figsize=(6,6))
	pcm = ax.pcolormesh(X, Y, prob, shading='auto', cmap='viridis')
	ax.set_aspect('equal')
	ax.set_title('Hydrogen 1s Probability Density (z=0)')
	fig.colorbar(pcm, ax=ax, label='Probability density')
	out_path = Path.cwd() / 'hydrogen_1s_prob.png'
	plt.savefig(str(out_path), dpi=150, bbox_inches='tight')
	print('Saved', out_path)
except Exception as e:
	import traceback
	log_path = Path(__file__).resolve().parent / 'run_log.txt'
	with log_path.open('w', encoding='utf-8') as f:
		f.write('Exception during run:\n')
		traceback.print_exc(file=f)
	print('Error occurred; details written to', log_path)
