#!/usr/bin/env python3
"""
Run a biomimetic "Apex Pulse" applying animal priors to existing sweep results.

This script applies a Mantis Shrimp "precision" boost to phi correlations for
entries with mutations in hotspot positions (2,4,5,6) and saves results to
`node5_out/apex_pulse_mantis.json`. Also writes a short report and appends a
governance log entry under `logs_resonancia/`.
"""
import sys
from pathlib import Path
import json
from datetime import datetime
import argparse
import os

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_SWEEP = ROOT / 'node12_out' / 'variation_sweep_extended.json'
OUT_DIR = ROOT / 'node5_out'
OUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR = ROOT / 'logs_resonancia'
LOG_DIR.mkdir(parents=True, exist_ok=True)


def load_sweep(path):
    with open(path, 'r', encoding='utf8') as f:
        d = json.load(f)
    # if envelope
    if isinstance(d, dict) and 'results' in d:
        return d['results']
    return d


def apply_mantis_boost(entries, baseline_seq='GGGGGGGG', boost=0.08, hotspots=(2,4,5,6)):
    out = []
    for e in entries:
        seq = e.get('seq', '')
        base_phi = float(e.get('phi_corr', 0))
        # count hotspot mutations vs baseline
        hits = 0
        for p in hotspots:
            if p < len(seq) and seq[p] != baseline_seq[p]:
                hits += 1
        improvement = boost * hits
        apex_phi = min(1.0, base_phi + improvement)
        rec = dict(seq=seq, meta=e.get('meta'), type=e.get('type'), pos=e.get('pos'),
                   baseline_phi=base_phi, apex_phi=apex_phi, improvement=apex_phi - base_phi, hits=hits)
        out.append(rec)
    return out


def write_outputs(results, out_dir=OUT_DIR, prefix='apex_pulse_mantis'):
    out_path = out_dir / f'{prefix}.json'
    with out_path.open('w', encoding='utf8') as f:
        json.dump(results, f, indent=2)

    # write a short plain-text report of top improvements
    report_path = out_dir / f'{prefix}_report.txt'
    top = sorted(results, key=lambda x: -x.get('improvement', 0))[:10]
    with report_path.open('w', encoding='utf8') as f:
        f.write(f'Apex Pulse Report - Mantis Shrimp prior\nGenerated: {datetime.utcnow().isoformat()}Z\n')
        f.write('\nTop improvements:\n')
        for i, r in enumerate(top, 1):
            f.write(f"{i}. seq={r['seq']} baseline_phi={r['baseline_phi']:.6f} apex_phi={r['apex_phi']:.6f} improvement={r['improvement']:.6f} hits={r['hits']}\n")

    return out_path, report_path


def append_log(animal_prior, out_path, operator=None):
    log_path = LOG_DIR / 'apex_pulse.log'
    entry = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'animal_prior': animal_prior,
        'operator': operator or os.getenv('USERNAME') or os.getenv('USER') or 'unknown',
        'result_file': str(out_path)
    }
    with log_path.open('a', encoding='utf8') as f:
        f.write(json.dumps(entry) + '\n')


def main():
    parser = argparse.ArgumentParser(description='Run biomimetic Apex Pulse')
    parser.add_argument('--animal_prior', default='mantis_shrimp')
    parser.add_argument('--sweep', default=str(DEFAULT_SWEEP))
    args = parser.parse_args()

    entries = load_sweep(args.sweep)
    if args.animal_prior == 'mantis_shrimp':
        # mantis precision -> boost on hotspot positions
        results = apply_mantis_boost(entries, boost=0.085, hotspots=(2,4,5,6))
    else:
        # default no-op
        results = apply_mantis_boost(entries, boost=0.0)

    out_path, report_path = write_outputs(results)
    append_log(args.animal_prior, out_path)

    print('Apex Pulse complete. Results:', out_path)
    print('Report:', report_path)


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Run a biomimetic 'Apex Pulse' that injects animal priors and measures impact
on Molecular Geometry (Node 5) accuracy using the Node12 sweep as input.

This is a simulation/analysis tool: it does not call external services.
"""
import os
import json
from pathlib import Path
from datetime import datetime
import argparse

ROOT = Path(__file__).resolve().parent.parent
SWEEP = ROOT / 'node12_out' / 'variation_sweep_extended.json'
OUT_DIR = ROOT / 'node5_out'
OUT_DIR.mkdir(parents=True, exist_ok=True)

def load_sweep():
    if not SWEEP.exists():
        raise SystemExit('Sweep file not found: ' + str(SWEEP))
    data = json.load(open(SWEEP, 'r', encoding='utf8'))
    if isinstance(data, dict) and 'results' in data:
        return data['results']
    return data

def apply_mantis_prior(entry):
    # Baseline accuracy proxy: scaled phi_corr
    phi = float(entry.get('phi_corr', 0))
    baseline = phi * 0.80

    seq = entry.get('seq', '') or ''
    # hotspot positions (1-based 4-6 => 0-based indices 3..5)
    hotspot_indices = [3,4,5]
    hotspot_count = 0
    for i in hotspot_indices:
        if i < len(seq) and seq[i] != 'G':
            hotspot_count += 1

    # Mantis spectral enhancement: each hotspot gives +8% accuracy
    enhanced = baseline * (1.0 + 0.08 * hotspot_count)

    return {
        'seq': seq,
        'phi_corr': phi,
        'baseline_accuracy': baseline,
        'enhanced_accuracy': enhanced,
        'hotspot_count': hotspot_count,
        'meta_hash': entry.get('meta', {}).get('hash')
    }

def run(animal_prior: str):
    entries = load_sweep()
    results = []
    if animal_prior.lower() in ('mantis','mantis_shrimp','mantis-shrimp'):
        for e in entries:
            r = apply_mantis_prior(e)
            results.append(r)
    else:
        raise SystemExit('Unsupported animal_prior: ' + animal_prior)

    # compute improvement and sort
    for r in results:
        r['improvement'] = r['enhanced_accuracy'] - r['baseline_accuracy']

    results_sorted = sorted(results, key=lambda x: -x['improvement'])

    out_file = OUT_DIR / f'apex_pulse_{animal_prior.lower()}.json'
    with out_file.open('w', encoding='utf8') as f:
        json.dump({'generated': datetime.utcnow().isoformat() + 'Z', 'results': results_sorted}, f, indent=2)

    # write a short report
    report = OUT_DIR / f'apex_pulse_{animal_prior.lower()}_report.txt'
    with report.open('w', encoding='utf8') as f:
        f.write(f'Apex Pulse Report - {animal_prior}\n')
        f.write(f'Generated: {datetime.utcnow().isoformat()}\n')
        f.write(f'Total evaluated: {len(results_sorted)}\n')
        f.write('\nTop 10 improvements:\n')
        for i, r in enumerate(results_sorted[:10], 1):
            f.write(f"{i}. seq={r['seq']} phi={r['phi_corr']:.6f} hotspot_count={r['hotspot_count']} ")
            f.write(f"baseline={r['baseline_accuracy']:.6f} enhanced={r['enhanced_accuracy']:.6f} ")
            f.write(f"improvement={r['improvement']:.6f} meta={r.get('meta_hash')}\n")

    # append to governance log
    log_dir = ROOT / 'logs_resonancia'
    log_dir.mkdir(parents=True, exist_ok=True)
    logp = log_dir / 'apex_pulse.log'
    with logp.open('a', encoding='utf8') as lg:
        lg.write(f"{datetime.utcnow().isoformat()}Z\tAPEX_PULSE\t{animal_prior}\n")

    print('Wrote', out_file)
    print('Wrote', report)
    print('Appended log', logp)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--animal_prior', required=True, help='animal prior to apply (mantis_shrimp)')
    args = parser.parse_args()
    run(args.animal_prior)
