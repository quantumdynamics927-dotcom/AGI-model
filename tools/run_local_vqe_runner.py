#!/usr/bin/env python3
import runpy
import traceback
import sys

try:
    runpy.run_path('tools/run_local_vqe.py', run_name='__main__')
except Exception:
    traceback.print_exc()
    sys.exit(2)
