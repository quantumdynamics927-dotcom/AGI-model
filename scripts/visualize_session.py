#!/usr/bin/env python3
"""Visualize a session JSON: fitness bar chart and phi vs fitness scatter"""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

SESSION_FILE = Path(__file__).resolve().parent.parent / 'data' / 'sessions' / 'session_20251231_025550.json'
OUT_DIR = Path(__file__).resolve().parent.parent / 'outputs'
OUT_DIR.mkdir(parents=True, exist_ok=True)
print('OUT_DIR created at', OUT_DIR.resolve())

with open(SESSION_FILE, 'r', encoding='utf-8') as f:
    session = json.load(f)

results = session['results']
ids = [r['cube_id'] for r in results]
fitness = [r['fitness'] for r in results]
phi = [r['metrics']['phi_score'] for r in results]
conscious = [r['conscious'] for r in results]

# Colors
colors = ['#00F5FF' if c else '#0A0E14' for c in conscious]

# 1) Fitness bar chart
plt.figure(figsize=(10,6))
bars = plt.bar(ids, fitness, color=colors, edgecolor='#00F5FF', linewidth=0.8)
plt.xlabel('Cube ID')
plt.ylabel('Fitness')
plt.title(f"Session {session['session_timestamp']}: Fitness per Cube (conscious highlighted)")
plt.grid(axis='y', linestyle='--', alpha=0.3)
# annotate best
best = int(np.argmax(fitness))
plt.annotate(f"Best: #{best} ({fitness[best]:.2f})", xy=(best, fitness[best]), xytext=(best+0.5, fitness[best]+2),
             arrowprops=dict(arrowstyle='->', color='#FFD700'))
plt.tight_layout()
out1 = OUT_DIR / f"session_{session['session_timestamp']}_fitness.png"
plt.savefig(out1, dpi=300, bbox_inches='tight')
print('Saved', out1.resolve())
plt.close()

# 2) Phi vs Fitness scatter
plt.figure(figsize=(8,6))
for i, (x,y,c) in enumerate(zip(phi, fitness, conscious)):
    plt.scatter(x, y, s=120, color='#FFD700' if c else '#8FA9BF', edgecolor='#013246')
    plt.text(x+0.02, y+0.2, str(ids[i]), fontsize=9)
plt.xlabel('Phi Score')
plt.ylabel('Fitness')
plt.title('Phi (Φ) vs Fitness — session ' + session['session_timestamp'])
plt.grid(True, linestyle='--', alpha=0.2)
plt.tight_layout()
out2 = OUT_DIR / f"session_{session['session_timestamp']}_phi_vs_fitness.png"
plt.savefig(out2, dpi=300, bbox_inches='tight')
print('Saved', out2.resolve())
plt.close()

# CSV export
import csv
csv_path = OUT_DIR / f"session_{session['session_timestamp']}_summary.csv"
with open(csv_path, 'w', newline='', encoding='utf-8') as cf:
    writer = csv.writer(cf)
    writer.writerow(['cube_id','configuration','fitness','phi_score','conscious','consciousness_score'])
    for r in results:
        writer.writerow([r['cube_id'], r['configuration'], r['fitness'], r['metrics']['phi_score'], r['conscious'], r['consciousness_score']])
print('Saved', csv_path.resolve())

# Print short summary
print('Session:', session['session_timestamp'])
print('Consciousness rate:', session.get('consciousness_rate'))
print('Best cube:', best, 'fitness=', fitness[best], 'phi=', phi[best])
