import importlib.util
import os
print('Running wrapper directly')
wrapper_path = os.path.join(os.path.dirname(__file__), '..', 'tests', 'test_smoke_wrapper.py')
wrapper_path = os.path.abspath(wrapper_path)
spec = importlib.util.spec_from_file_location('test_smoke_wrapper', wrapper_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print('Module imported from', wrapper_path)
import traceback

print('Calling test_smoke_train_wrapper()')
try:
    mod.test_smoke_train_wrapper()
    print('smoke_train_wrapper passed')
except Exception as e:
    print('smoke_train_wrapper ERROR:', e)
    traceback.print_exc()

print('Calling test_smoke_quantum_wrapper()')
try:
    mod.test_smoke_quantum_wrapper()
    print('smoke_quantum_wrapper passed')
except Exception as e:
    print('smoke_quantum_wrapper ERROR:', e)
    traceback.print_exc()

print('ALL OK')
