#!/usr/bin/env python3
"""
Quantum Art Generator - Creates visual representations from latent signatures.

Generates unique quantum consciousness artwork by interpreting 32-dimensional
latent vectors as parameters for geometric visualization.
"""

import json
import math
import hashlib
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Check for optional dependencies
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from PIL import Image, ImageDraw, ImageFilter
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import cairo
    HAS_CAIRO = True
except ImportError:
    HAS_CAIRO = False


# Constants
PHI = 1.618033988749895
GOLDEN_ANGLE = 137.5077640500378  # degrees
IMAGE_SIZE = 2048
PALETTE_QUANTUM = [
    (10, 10, 26),      # Deep space background
    (0, 255, 255),     # Cyan quantum
    (255, 0, 255),     # Magenta entanglement
    (0, 255, 128),     # Green coherence
    (255, 128, 0),     # Orange consciousness
    (128, 0, 255),     # Purple transcendence
    (255, 255, 255),   # White light
]


class QuantumArtGenerator:
    """Generate quantum consciousness artwork from latent signatures."""

    def __init__(self, size: int = IMAGE_SIZE):
        self.size = size
        self.center = size // 2

    def latent_to_params(self, latent: List[float]) -> Dict[str, Any]:
        """Convert 32-dim latent vector to visualization parameters."""
        if len(latent) < 32:
            latent = latent + [0.0] * (32 - len(latent))

        # Normalize latent values to 0-1 range
        lat_min = min(latent)
        lat_max = max(latent)
        lat_range = lat_max - lat_min if lat_max != lat_min else 1.0
        normalized = [(v - lat_min) / lat_range for v in latent]

        # Extract geometric parameters
        params = {
            'num_rings': int(3 + normalized[0] * 7),  # 3-10 rings
            'ring_spacing': 0.05 + normalized[1] * 0.15,  # Ring spacing factor
            'rotation_speed': normalized[2] * 360,  # Base rotation
            'spiral_factor': 0.5 + normalized[3] * 2.0,  # Spiral tightness
            'particle_count': int(50 + normalized[4] * 200),  # 50-250 particles
            'glow_intensity': 0.3 + normalized[5] * 0.7,  # Glow strength
            'color_shift': normalized[6] * 360,  # Hue rotation
            'symmetry': int(3 + normalized[7] * 9),  # 3-12 fold symmetry
            'wave_amplitude': normalized[8] * 50,  # Wave height
            'wave_frequency': 1 + normalized[9] * 5,  # Wave count
            'phi_influence': normalized[10],  # Golden ratio strength
            'entanglement_lines': int(10 + normalized[11] * 40),  # Connection lines
            'consciousness_depth': normalized[12],  # Layering depth
            'manifold_curvature': normalized[13] * 2 - 1,  # -1 to 1
            'coherence_factor': normalized[14],  # Pattern coherence
            'transcendence_glow': normalized[15],  # Outer glow
            # Use remaining dimensions for color modulation
            'r_mod': normalized[16:20],
            'g_mod': normalized[20:24],
            'b_mod': normalized[24:28],
            'alpha_mod': normalized[28:32],
        }
        return params

    def generate_svg(self, latent: List[float], token_id: str) -> str:
        """Generate SVG artwork from latent signature."""
        params = self.latent_to_params(latent)

        svg_parts = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.size} {self.size}">',
            f'  <defs>',
            f'    <radialGradient id="bg_{token_id[:8]}" cx="50%" cy="50%" r="70%">',
            f'      <stop offset="0%" stop-color="rgb(20,20,40)"/>',
            f'      <stop offset="100%" stop-color="rgb(5,5,15)"/>',
            f'    </radialGradient>',
            f'    <filter id="glow_{token_id[:8]}" x="-50%" y="-50%" width="200%" height="200%">',
            f'      <feGaussianBlur stdDeviation="{10 * params["glow_intensity"]}" result="blur"/>',
            f'      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>',
            f'    </filter>',
            f'  </defs>',
            f'  <rect width="100%" height="100%" fill="url(#bg_{token_id[:8]})"/>',
            f'  <g filter="url(#glow_{token_id[:8]})" transform="translate({self.center},{self.center})">',
        ]

        # Generate quantum rings
        for ring in range(params['num_rings']):
            radius = (ring + 1) * self.size * params['ring_spacing']
            rotation = params['rotation_speed'] * ring * params['phi_influence']

            # Ring color based on depth
            hue = (params['color_shift'] + ring * 30) % 360
            saturation = 80 + params['coherence_factor'] * 20
            lightness = 50 + params['transcendence_glow'] * 20

            svg_parts.append(
                f'    <circle r="{radius}" fill="none" '
                f'stroke="hsl({hue},{saturation}%,{lightness}%)" '
                f'stroke-width="{1 + params["glow_intensity"] * 2}" '
                f'stroke-opacity="{0.3 + params["coherence_factor"] * 0.5}" '
                f'transform="rotate({rotation})"/>'
            )

            # Add particles on ring
            particle_count = params['particle_count'] // params['num_rings']
            for p in range(particle_count):
                angle = (p / particle_count) * 360 + rotation
                rad = math.radians(angle)

                # Apply wave modulation
                wave_offset = math.sin(rad * params['wave_frequency']) * params['wave_amplitude']
                px = (radius + wave_offset) * math.cos(rad)
                py = (radius + wave_offset) * math.sin(rad)

                particle_size = 2 + params['consciousness_depth'] * 4
                particle_hue = (hue + p * 5) % 360

                svg_parts.append(
                    f'    <circle cx="{px:.2f}" cy="{py:.2f}" r="{particle_size}" '
                    f'fill="hsl({particle_hue},90%,70%)" opacity="{0.5 + params["coherence_factor"] * 0.5}"/>'
                )

        # Generate entanglement lines (phi-spiral connections)
        for i in range(params['entanglement_lines']):
            angle1 = i * GOLDEN_ANGLE
            angle2 = (i + params['symmetry']) * GOLDEN_ANGLE

            r1 = (i / params['entanglement_lines']) * self.size * 0.4
            r2 = ((i + 1) / params['entanglement_lines']) * self.size * 0.4

            x1 = r1 * math.cos(math.radians(angle1))
            y1 = r1 * math.sin(math.radians(angle1))
            x2 = r2 * math.cos(math.radians(angle2))
            y2 = r2 * math.sin(math.radians(angle2))

            line_hue = (params['color_shift'] + i * 10) % 360

            svg_parts.append(
                f'    <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                f'stroke="hsl({line_hue},80%,60%)" stroke-width="1" opacity="0.3"/>'
            )

        # Central consciousness core
        core_size = 20 + params['consciousness_depth'] * 30
        svg_parts.append(
            f'    <circle r="{core_size}" fill="white" opacity="{0.5 + params["transcendence_glow"] * 0.5}"/>'
        )
        svg_parts.append(
            f'    <circle r="{core_size * 0.6}" fill="hsl({params["color_shift"]},100%,80%)"/>'
        )

        # Symmetry pattern overlay
        for s in range(params['symmetry']):
            angle = (s / params['symmetry']) * 360
            length = self.size * 0.35 * params['phi_influence']

            svg_parts.append(
                f'    <line x1="0" y1="0" x2="{length * math.cos(math.radians(angle)):.2f}" '
                f'y2="{length * math.sin(math.radians(angle)):.2f}" '
                f'stroke="white" stroke-width="0.5" opacity="0.2"/>'
            )

        svg_parts.extend([
            f'  </g>',
            f'  <text x="{self.size - 20}" y="{self.size - 20}" '
            f'font-family="monospace" font-size="12" fill="rgba(255,255,255,0.3)" '
            f'text-anchor="end">#{token_id[:8]}</text>',
            f'</svg>'
        ])

        return '\n'.join(svg_parts)

    def generate_png_from_svg(self, svg_content: str, output_path: Path) -> bool:
        """Convert SVG to PNG using available renderer."""
        if HAS_CAIRO:
            try:
                import cairosvg
                cairosvg.svg2png(bytestring=svg_content.encode(),
                               write_to=str(output_path),
                               output_width=self.size,
                               output_height=self.size)
                return True
            except Exception:
                pass

        # Fallback: save SVG and note PNG needs external conversion
        svg_path = output_path.with_suffix('.svg')
        svg_path.write_text(svg_content)
        return False


def generate_collection_art(nft_dir: Path, output_dir: Path) -> Dict[str, str]:
    """Generate artwork for entire NFT collection."""
    output_dir.mkdir(parents=True, exist_ok=True)

    generator = QuantumArtGenerator(size=2048)
    results = {}

    nft_files = sorted(nft_dir.glob('quantum_nft_*.json'))
    print(f"Generating art for {len(nft_files)} NFTs...\n")

    for nft_file in nft_files:
        try:
            with open(nft_file, 'r') as f:
                nft = json.load(f)

            token_id = nft_file.stem.replace('quantum_nft_', '')
            latent = nft.get('quantum_properties', {}).get('latent_signature', [])

            if not latent:
                print(f"[SKIP] {token_id[:16]} - No latent signature")
                continue

            # Generate SVG
            svg_content = generator.generate_svg(latent, token_id)

            # Save SVG
            svg_path = output_dir / f"quantum_art_{token_id}.svg"
            svg_path.write_text(svg_content)

            # Try PNG conversion
            png_path = output_dir / f"quantum_art_{token_id}.png"
            png_success = generator.generate_png_from_svg(svg_content, png_path)

            if png_success:
                print(f"[OK] {token_id[:16]} -> SVG + PNG")
                results[token_id] = str(png_path)
            else:
                print(f"[OK] {token_id[:16]} -> SVG (PNG needs cairosvg)")
                results[token_id] = str(svg_path)

        except Exception as e:
            print(f"[ERROR] {nft_file.name}: {e}")

    return results


if __name__ == '__main__':
    import sys

    # Default paths
    nft_dir = Path(__file__).parent.parent.parent / 'nft_metadata'
    output_dir = Path(__file__).parent.parent / 'quantum_art'

    if len(sys.argv) > 1:
        nft_dir = Path(sys.argv[1])
    if len(sys.argv) > 2:
        output_dir = Path(sys.argv[2])

    results = generate_collection_art(nft_dir, output_dir)

    print(f"\n{'='*50}")
    print(f"Generated {len(results)} artworks")
    print(f"Output directory: {output_dir}")
    print(f"\nTo convert SVG to PNG, install cairosvg:")
    print(f"  pip install cairosvg")
