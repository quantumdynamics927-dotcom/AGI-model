#!/usr/bin/env python3
"""Generate placeholder PNG images for given meta_hash list and save into nft_metadata/ as <meta_hash>.png"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap

ROOT = Path(__file__).resolve().parent.parent
NFT_DIR = ROOT / 'nft_metadata'
NFT_DIR.mkdir(parents=True, exist_ok=True)

META_HASHES = [
    'b9dce4a6a511521d5135c0fb1c3dbfd2152d56f1d0e1e8788e436cd4244911ef',
    'b8f4b114c1a451314a720a67becdad8d50066a42c38e9feb98bc863aa38e6cfc',
    '00f058cf4541c3988f89423a1f505c5f069db5d965269b5000d11b9ff48db1c3',
    'a2780f2cf4a5d59080dde9a28197c412b0fc05bf8ddce25309a04965b548f68c',
    'db126c7505986f1fe1889910ae4740db7201e88426fbb1e23d083a17813a5923'
]

W = 1024
H = 1024
BG = (18, 18, 24)
FG = (230, 230, 255)

try:
    font = ImageFont.truetype('arial.ttf', 28)
except Exception:
    from PIL import ImageFont
    font = ImageFont.load_default()

for mh in META_HASHES:
    img = Image.new('RGB', (W, H), color=BG)
    draw = ImageDraw.Draw(img)
    # Draw a simple gradient bar
    for i in range(H):
        r = int(BG[0] + (FG[0]-BG[0]) * (i/H))
        g = int(BG[1] + (FG[1]-BG[1]) * (i/H))
        b = int(BG[2] + (FG[2]-BG[2]) * (i/H))
        draw.line([(0,i),(W,i)], fill=(r,g,b))
    # Overlay circle
    draw.ellipse((W*0.1, H*0.1, W*0.9, H*0.9), outline=(255,255,255), width=6)
    # Write meta hash center
    text = mh[:12]
    try:
        w,h = font.getsize(text)
    except Exception:
        bbox = draw.textbbox((0,0), text, font=font)
        w = bbox[2]-bbox[0]; h = bbox[3]-bbox[1]
    draw.text(((W-w)/2, H*0.45), text, font=font, fill=(10,10,30))
    # Save
    out = NFT_DIR / f"{mh}.png"
    img.save(out, format='PNG')
    print('Wrote', out)

print('Done')
