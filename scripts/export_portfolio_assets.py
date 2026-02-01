#!/usr/bin/env python3
"""Export portfolio assets for a session JSON:
- Generate per-cube DNA SVG (populated from session data)
- Generate a PNG variant (retina and standard)
- Copy or regenerate session plots into portfolio_exports at retina sizes
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SESSION_FILE = ROOT / 'data' / 'sessions' / 'session_20251231_025550.json'
OUT = ROOT / 'portfolio_exports'
OUT.mkdir(parents=True, exist_ok=True)

print('Export script starting; SESSION_FILE=', SESSION_FILE.resolve())
try:
    with open(SESSION_FILE, 'r', encoding='utf-8') as f:
        session = json.load(f)
except Exception as e:
    print('ERROR loading session JSON:', type(e), e)
    raise

# Helper: generate SVG per cube
SVG_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8" ?>
<svg width="1200" height="600" viewBox="0 0 1200 600" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#041024" />
  <text x="60" y="70" font-family="Helvetica, Arial, monospace" font-size="28" fill="#E6F7FF" font-weight="bold">TOP PERFORMING CONFIGURATION (ID: {cube_id})</text>
  <rect x="60" y="110" width="1080" height="120" rx="8" fill="#021226" stroke="#013246" stroke-width="1" />
  <text x="80" y="170" font-family="Consolas, 'Courier New', monospace" font-size="28" fill="#E6F7FF">{dna_seq}</text>
  <!-- Highlights: seq placeholders -->
  <text x="80" y="170" font-family="Consolas, 'Courier New', monospace" font-size="28" fill="{highlight1_color}">{highlight1}</text>
  <text x="200" y="170" font-family="Consolas, 'Courier New', monospace" font-size="28" fill="{highlight2_color}">{highlight2}</text>
  <line x1="100" y1="190" x2="100" y2="240" stroke="{highlight1_color}" stroke-width="2" marker-end="url(#arrow)" />
  <text x="120" y="260" font-family="Helvetica" font-size="14" fill="{highlight1_color}">{highlight1_label}</text>
  <line x1="220" y1="190" x2="220" y2="240" stroke="{highlight2_color}" stroke-width="2" marker-end="url(#arrow)" />
  <text x="240" y="260" font-family="Helvetica" font-size="14" fill="{highlight2_color}">{highlight2_label}</text>
  <rect x="60" y="340" width="420" height="110" rx="10" fill="#021226" stroke="#014" stroke-width="1" />
  <text x="80" y="380" font-family="Helvetica" font-size="18" fill="#E6F7FF">Phi Integration: <tspan fill="#FFD700" font-weight="bold">{phi}</tspan></text>
  <text x="80" y="410" font-family="Helvetica" font-size="18" fill="#E6F7FF">Fitness: <tspan fill="#00F5FF" font-weight="bold">{fitness}</tspan></text>
  <text x="80" y="440" font-family="Helvetica" font-size="18" fill="#E6F7FF">Entropy: <tspan fill="#00F5FF" font-weight="bold">{entropy}</tspan></text>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#00F5FF" />
    </marker>
  </defs>
</svg>
'''

# choose highlights heuristically: look for CGG and TAA
for r in session['results']:
    cid = r['cube_id']
    if cid == 8:
        seq = r['configuration']
        phi = r['metrics']['phi_score']
        fitness = r['fitness']
        entropy = r['metrics']['entropy']

        # find highlights
        highlight1 = 'CGG' if 'CGG' in seq else seq[:3]
        highlight2 = 'TAA' if 'TAA' in seq else seq[-3:]
        svg_text = SVG_TEMPLATE.format(cube_id=cid, dna_seq=seq, highlight1=highlight1, highlight2=highlight2,
                                       highlight1_label='High GC Stability Cluster', highlight2_label='Palindromic Symmetry Vertex',
                                       highlight1_color='#00F5FF', highlight2_color='#FFD700', phi=phi, fitness=fitness, entropy=entropy)

        svg_out = OUT / f'cube_{cid}_dna.svg'
        with open(svg_out, 'w', encoding='utf-8') as f:
            f.write(svg_text)
        print('Saved SVG:', svg_out.resolve())

        # Also generate a PNG rendition using matplotlib (so we have raster PNG)
        fig = plt.figure(figsize=(12,6), facecolor='#041024')
        ax = fig.add_axes([0,0,1,1])
        ax.set_xlim(0,1200)
        ax.set_ylim(0,600)
        ax.set_axis_off()
        ax.text(60, 520, f'TOP PERFORMING CONFIGURATION (ID: {cid})', color='#E6F7FF', fontsize=20, fontweight='bold')
        ax.add_patch(plt.Rectangle((60,340),420,110, facecolor='#021226', edgecolor='#013246', linewidth=1))
        ax.text(80, 380, f'Phi Integration: {phi}', color='#E6F7FF', fontsize=14)
        ax.text(80, 410, f'Fitness: {fitness:.2f}', color='#00F5FF', fontsize=14)
        ax.text(80, 440, f'Entropy: {entropy:.2f}', color='#00F5FF', fontsize=14)
        ax.text(80, 170, seq, color='#E6F7FF', fontsize=20, family='monospace')
        ax.text(80, 170, highlight1, color='#00F5FF', fontsize=20, family='monospace')
        ax.text(200,170, highlight2, color='#FFD700', fontsize=20, family='monospace')

        png_out = OUT / f'cube_{cid}_dna.png'
        plt.savefig(png_out, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
        print('Saved PNG:', png_out.resolve())

        # Retina: scale up 2x using PIL
        retina_out = OUT / f'cube_{cid}_dna@2x.png'
        with Image.open(png_out) as im:
            im2 = im.resize((im.width*2, im.height*2), Image.LANCZOS)
            im2.save(retina_out)
        print('Saved Retina PNG:', retina_out.resolve())

# Copy session charts to portfolio_exports and make retina versions
from shutil import copy2
SESSION_OUT = ROOT / 'outputs'
for fname in ['session_20251231_025550_fitness.png','session_20251231_025550_phi_vs_fitness.png']:
    src = SESSION_OUT / fname
    if src.exists():
        dst = OUT / fname
        copy2(src, dst)
        print('Copied', src.resolve(), '->', dst.resolve())
        # make retina
        with Image.open(dst) as im:
            rdst = OUT / (dst.stem + '@2x' + dst.suffix)
            im2 = im.resize((im.width*2, im.height*2), Image.LANCZOS)
            im2.save(rdst)
            print('Saved retina', rdst.resolve())

print('Export completed. Portfolio assets are in', OUT.resolve())
