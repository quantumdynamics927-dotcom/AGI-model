"""Runner utility for Node 9 (QVAE Bridge)

Usage:
    python tools/run_qvae.py --build            # build circuit and print summary
    python tools/run_qvae.py --simulate         # try Aer simulation (if available)
    python tools/run_qvae.py --submit           # attempt remote IBM submission when env vars set

This script uses lazy imports to avoid requiring Qiskit for other workflows.
"""
import argparse
import os
from pathlib import Path
import json
import logging

logger = logging.getLogger('run_qvae')
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(ch)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build', action='store_true')
    parser.add_argument('--simulate', action='store_true')
    parser.add_argument('--submit', action='store_true')
    parser.add_argument('--num-qubits', type=int, default=127)
    parser.add_argument('--shots', type=int, default=1024)
    args = parser.parse_args()

    try:
        from qvae_bridge import create_wedjat_qvae_circuit, submit_circuit
    except Exception as e:
        logger.error('QVAE bridge unavailable: %s', e)
        return

    qc = create_wedjat_qvae_circuit(num_qubits=args.num_qubits)
    logger.info('Built QVAE circuit with %s qubits', args.num_qubits)

    if args.build:
        try:
            print(qc)
        except Exception:
            logger.info('Circuit built (print not available in this environment)')

    if args.simulate:
        try:
            res = submit_circuit(qc, shots=args.shots, run_remote=False)
            logger.info('Simulation result type: %s', type(res))
            try:
                print(res.get_counts())
            except Exception:
                logger.info('Simulator result; inspect object manually')
        except Exception as e:
            logger.error('Simulation failed: %s', e)

    if args.submit:
        # submit remote if env vars set
        if os.getenv('IBM_API_TOKEN') and os.getenv('IBM_INSTANCE'):
            try:
                job = submit_circuit(qc, shots=args.shots, run_remote=True)
                logger.info('Submitted job: %s', job)
            except Exception as e:
                logger.error('Remote submit failed: %s', e)
        else:
            logger.error('IBM credentials not found in environment; set IBM_API_TOKEN and IBM_INSTANCE')


if __name__ == '__main__':
    main()
