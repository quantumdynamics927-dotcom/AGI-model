print('TEST PRINT: start')
import os
print('cwd=', os.getcwd())
print('ENV PINATA_API_KEY present:', 'PINATA_API_KEY' in os.environ)
print('Done')
