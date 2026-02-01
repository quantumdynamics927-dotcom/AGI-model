import sys
import os
print('PYTHON:', sys.executable)
print('sys.path[0:3]:', sys.path[:3])
print('cwd:', os.getcwd())
try:
    import pytest
    print('pytest imported', pytest.__version__)
    rc = pytest.main(['-k', 'smoke', '-qq', '--maxfail=1'])
    print('pytest exit code:', rc)
except Exception as e:
    print('IMPORT/EXEC ERROR:', type(e), e)
    raise
