#!/usr/bin/env python3
try:
    from qiskit_aer import Aer as AerA
    AerPkg = AerA
except Exception:
    try:
        from qiskit import Aer as AerQ
        AerPkg = AerQ
    except Exception as e:
        print('No Aer package available:', type(e).__name__, e)
        raise

backend = None
try:
    backend = AerPkg.get_backend('aer_simulator')
    print('backend repr:', backend)
    print('has run:', hasattr(backend, 'run'))
    print('backend methods sample:', [m for m in dir(backend) if not m.startswith('_')][:30])
except Exception as e:
    print('Error getting backend:', type(e).__name__, e)
