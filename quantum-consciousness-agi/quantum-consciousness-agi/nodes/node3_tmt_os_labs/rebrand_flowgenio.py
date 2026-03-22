"""Rebrand helper: replace 'FlowGenio' strings in a local repo with 'TMT-OS Labs'.

Usage: python rebrand_flowgenio.py <path-to-repo>
This script will scan text files and replace occurrences of 'FlowGenio' -> 'TMT-OS Labs' and 'FlowGenio-Landing' -> 'TMT-OS-Labs-Portal'.
It will create backups (*.bak) before modifying files.
"""
import sys
from pathlib import Path

REPLACEMENTS = [
    ('FlowGenio-Landing', 'TMT-OS-Labs-Portal'),
    ('FlowGenio', 'TMT-OS Labs')
]


def rebrand(repo_path: Path):
    if not repo_path.exists():
        print('Path does not exist:', repo_path)
        return
    for p in repo_path.rglob('*'):
        if p.is_file() and p.suffix.lower() in ['.html', '.htm', '.js', '.py', '.md', '.json', '.txt']:
            text = p.read_text(encoding='utf-8', errors='ignore')
            new_text = text
            for old, new in REPLACEMENTS:
                new_text = new_text.replace(old, new)
            if new_text != text:
                bak = p.with_suffix(p.suffix + '.bak')
                bak.write_text(text, encoding='utf-8')
                p.write_text(new_text, encoding='utf-8')
                print('[OK] Rebranded:', p)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python rebrand_flowgenio.py <path-to-repo>')
        raise SystemExit(1)
    rebrand(Path(sys.argv[1]))
