"""Generate a polished certificate PNG from NFT metadata JSON."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime


def generate_certificate(nft_json_path: Path, output_path: Path = None):
    data = json.loads(Path(nft_json_path).read_text())
    name = data.get('name', 'TMT-OS Research')
    attributes = {a.get('trait_type'): a.get('value') for a in data.get('attributes', [])}
    client = attributes.get('Researcher', 'Unknown')
    timestamp = attributes.get('Timestamp', int(datetime.utcnow().timestamp()))

    if output_path is None:
        output_path = Path(str(nft_json_path) + '.certificate.png')

    fig, ax = plt.subplots(figsize=(11,8.5))
    ax.add_patch(patches.Rectangle((0,0),1,1, color='#0e1a2b'))
    ax.axis('off')

    # Title
    ax.text(0.5, 0.85, 'TMT-OS Certified Research Certificate', ha='center', va='center', fontsize=24, color='white', weight='bold')

    # Subtitle / name
    ax.text(0.5, 0.7, name, ha='center', va='center', fontsize=18, color='white')

    # Details box
    box_x = 0.1
    box_y = 0.08
    box_w = 0.8
    box_h = 0.5
    ax.add_patch(patches.Rectangle((box_x, box_y), box_w, box_h, fill=False, edgecolor='white', linewidth=1.0))

    # Metrics
    metrics_y = 0.65
    line_h = 0.06
    for i, (k, v) in enumerate(attributes.items()):
        ax.text(0.12, metrics_y - i*line_h, f"{k}: {v}", ha='left', va='center', fontsize=12, color='white')

    # Footer: timestamp
    dt = datetime.utcfromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%SZ')
    ax.text(0.5, 0.03, f"Issued: {dt} — TMT-OS Boveda Cuantica", ha='center', va='center', fontsize=10, color='white')

    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"[OK] Certificate generated: {output_path}")
    return output_path
