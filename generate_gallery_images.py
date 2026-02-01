import matplotlib.pyplot as plt
import numpy as np

# --- Data from your session log ---
epochs = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60] # Added 60 for final
energy = [-0.323197, -0.465487, -2.765948, -12.654775, -45.752335,
          -141.574982, -395.156128, -1013.291992, -2422.864014, -5430.550293, -11504.823242]
acceptance = [0.980, 0.721, 0.595, 0.547, 0.531, 0.514, 0.516, 0.492, 0.506, 0.501, 0.500]

# Set a professional style
plt.style.use('ggplot')

# --- Plot 1: Energy Convergence (The "Result") ---
fig1, ax1 = plt.subplots(figsize=(10, 6))

# Plotting negative energy to show "descent" or raw values
ax1.plot(epochs, energy, marker='o', color='#2ecc71', linewidth=2.5, label='Variational Energy')

ax1.set_title('DL-QMC Energy Minimization', fontsize=16, fontweight='bold', color='#333333')
ax1.set_xlabel('Training Epochs', fontsize=12)
ax1.set_ylabel('Energy (Hartree)', fontsize=12)
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.legend(fontsize=12)

# Annotation for the final result
final_e = energy[-1]
ax1.annotate(f'Final Energy:\n{final_e:.2f} Ha', xy=(epochs[-1], final_e), xytext=(epochs[-1]-15, final_e+2000),
             arrowprops=dict(facecolor='black', shrink=0.05), fontsize=10,
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=1))

plt.tight_layout()
plt.savefig('upwork_gallery_energy_convergence.png', dpi=300)
print("Generated: upwork_gallery_energy_convergence.png")

# --- Plot 2: Metropolis Acceptance Rate (The "Stability") ---
fig2, ax2 = plt.subplots(figsize=(10, 6))

ax2.plot(epochs, acceptance, marker='s', color='#3498db', linewidth=2.5)
ax2.axhline(y=0.5, color='r', linestyle='--', alpha=0.5, label='Ideal Acceptance (0.5)')

ax2.set_title('Sampler Stability (Metropolis-Hastings)', fontsize=16, fontweight='bold', color='#333333')
ax2.set_xlabel('Training Epochs', fontsize=12)
ax2.set_ylabel('Acceptance Ratio', fontsize=12)
ax2.set_ylim(0, 1.1)
ax2.legend()

# Highlight the stability region
ax2.text(30, 0.6, 'Stable Regime\n(Optimization Phase)', fontsize=11, color='#2c3e50',
         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

plt.tight_layout()
plt.savefig('upwork_gallery_sampler_stability.png', dpi=300)
print("Generated: upwork_gallery_sampler_stability.png")

print("\nBoth images saved successfully!")
