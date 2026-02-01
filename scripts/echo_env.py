from dotenv import load_dotenv
import os
load_dotenv()
print('PINATA_JWT present:', 'PINATA_JWT' in os.environ)
print('PINATA_JWT length:', len(os.environ.get('PINATA_JWT','')))
print('PINATA_API_KEY present:', os.environ.get('PINATA_API_KEY'))
