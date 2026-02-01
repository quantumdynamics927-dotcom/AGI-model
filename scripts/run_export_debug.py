import runpy
import traceback
print('Running export_portfolio_assets.py (debug runner)')
try:
    runpy.run_path('scripts/export_portfolio_assets.py', run_name='__main__')
    print('Completed without exception')
except Exception as e:
    print('EXPORT SCRIPT RAISED EXCEPTION:')
    traceback.print_exc()