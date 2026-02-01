#!/usr/bin/env python3
"""Create PNG versions (standard and retina) for cube 8 DNA thumbnail"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'portfolio_exports'
OUT.mkdir(parents=True, exist_ok=True)

# Data for cube 8 (from session)
cid = 8
seq = 'CGGCATAATTATAGCGCCGCCGTAAAC'
phi = 2.0
fitness = 47.65833682071481
entropy = 1.9726869288759223

# Generate PNG via matplotlib
fig = plt.figure(figsize=(12,6), facecolor='#041024')
ax = fig.add_axes([0,0,1,1])
ax.set_xlim(0,1200)
ax.set_ylim(0,600)
ax.set_axis_off()
ax.text(60, 520, f'TOP PERFORMING CONFIGURATION (ID: {cid})', color='#E6F7FF', fontsize=20, fontweight='bold')
ax.add_patch(plt.Rectangle((60,110),1080,120, facecolor='#021226', edgecolor='#013246', linewidth=1))
ax.add_patch(plt.Rectangle((60,340),420,110, facecolor='#021226', edgecolor='#013246', linewidth=1))
ax.text(80, 170, seq, color='#E6F7FF', fontsize=22, family='monospace')
# highlights
ax.text(80, 170, 'CGG', color='#00F5FF', fontsize=22, family='monospace')
ax.text(200,170, 'TAA', color='#FFD700', fontsize=22, family='monospace')
# footer stats
ax.text(80, 380, f'Phi Integration: {phi}', color='#E6F7FF', fontsize=16)
ax.text(80, 410, f'Fitness: {fitness:.2f}', color='#00F5FF', fontsize=16)
ax.text(80, 440, f'Entropy: {entropy:.2f}', color='#00F5FF', fontsize=16)

png_out = OUT / f'cube_{cid}_dna.png'
fig.savefig(png_out, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close(fig)
print('Saved PNG:', png_out.resolve())

# Create retina version by resizing
retina_out = OUT / f'cube_{cid}_dna@2x.png'
with Image.open(png_out) as im:
    im2 = im.resize((im.width*2, im.height*2), Image.LANCZOS)
    im2.save(retina_out)
print('Saved Retina PNG:', retina_out.resolve())

# Copy session outputs to portfolio_exports
session_out = ROOT / 'outputs'
for fname in ['session_20251231_025550_fitness.png','session_20251231_025550_phi_vs_fitness.png']:
    src = session_out / fname
    if src.exists():
        dst = OUT / fname
        dst.write_bytes(src.read_bytes())
        print('Copied', src.resolve(), '->', dst.resolve())
        # create retina
        with Image.open(dst) as im:
            rdst = OUT / (dst.stem + '@2x' + dst.suffix)
            im2 = im.resize((im.width*2, im.height*2), Image.LANCZOS)
            im2.save(rdst)
            print('Saved retina', rdst.resolve())
    else:
        print('Missing source', src)
