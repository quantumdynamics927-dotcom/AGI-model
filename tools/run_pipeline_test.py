"""Temporary runner to execute the vault pipeline and capture logs for debugging (local-only).
"""
import os
import traceback
from pathlib import Path

# Ensure salt is set (for local tests)
if os.environ.get('PRIVATE_VAULT_SALT') is None:
    os.environ['PRIVATE_VAULT_SALT'] = 'local_demo_salt_123'

log_path = Path('vault/pipeline_debug.log')
log_path.parent.mkdir(parents=True, exist_ok=True)

try:
    from tools.vault_pipeline import run_pipeline
    print('Calling run_pipeline...')
    res = run_pipeline('data/test_examples/raw_samples.csv', epochs=1, latent=2, gen_n=2)
    print('run_pipeline returned:', res)
    with log_path.open('a', encoding='utf-8') as f:
        f.write('SUCCESS: run_pipeline returned: ' + str(res) + '\n')
except Exception as e:
    tb = traceback.format_exc()
    print('EXCEPTION:', e)
    print(tb)
    with log_path.open('a', encoding='utf-8') as f:
        f.write('EXCEPTION: ' + str(e) + '\n')
        f.write(tb + '\n')
