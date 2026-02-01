#!/usr/bin/env python3
try:
    import scipy.optimize
    print('scipy.optimize OK')
except Exception as e:
    print('scipy missing', type(e).__name__, str(e))
