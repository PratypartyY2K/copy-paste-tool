#!/usr/bin/env python3
# scripts/monitor_db.py
import time
from clipboard_manager.storage import Persistence

DB = './.local/persistence.db'
p = Persistence(DB)
last_ts = None
print('Monitoring', DB)
try:
    while True:
        rows = p.load_items()
        if rows:
            newest = rows[0]['timestamp']
            if newest != last_ts:
                last_ts = newest
                print('NEW:', rows[0]['id'], rows[0]['source_app'], newest, repr(rows[0]['content'])[:160].replace('\n','\\n'))
        else:
            if last_ts is not None:
                last_ts = None
                print('No rows')
        time.sleep(0.5)
finally:
    p.close()
