#!/usr/bin/env python3
try:
    from agi_database import AGIDatabase
    print('Import successful')
    db = AGIDatabase()
    print('Database object created')
    db.connect()
    print('Connection successful')
    print(f'Database file: {db.connection_string}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()