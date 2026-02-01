#!/usr/bin/env python3
import importlib

mods = ['qiskit', 'qiskit_aer', 'qiskit.providers.aer', 'qiskit_aer.providers']

for m in mods:
    try:
        mod = importlib.import_module(m)
        ver = getattr(mod, '__version__', getattr(mod, 'version', 'no-version'))
        print(m, 'OK', ver)
    except Exception as e:
        print(m, 'ERROR', type(e).__name__, str(e))

try:
    # check Aer backend discovery
    try:
        from qiskit_aer import Aer as AerA
        print('qiskit_aer.Aer OK')
    except Exception:
        from qiskit import Aer as AerQ
        print('qiskit.Aer OK')
except Exception as e:
    print('Aer import overall ERROR', type(e).__name__, str(e))
