#!/usr/bin/env python3
"""Quick persistence smoke test.
Creates a Persistence instance at ./.local/persistence.db, wires it into History,
adds a test clipboard item and then prints the rows loaded directly from the DB.
Run from the repo root with: PYTHONPATH=. python3 scripts/test_persistence_run.py
"""
import os
import time
from clipboard_manager.storage import Persistence
from clipboard_manager.history import History

DB_PATH = os.path.abspath('./.local/persistence.db')
print('Using DB:', DB_PATH)
# ensure directory
os.makedirs(os.path.dirname(DB_PATH) or '.', exist_ok=True)

p = Persistence(DB_PATH)
# create history backed by persistence
h = History(persistence=p)
# add a test item
now = time.time()
item = h.add_item('persistence test content - %s' % (time.ctime(now),), source_app='TestApp', timestamp=now)
print('History.add_item returned:', getattr(item, 'id', None))
# load items directly from persistence and print
rows = p.load_items()
print('Rows in DB:')
for r in rows:
    print('-', r['id'], r['source_app'], r['timestamp'], repr(r['content'])[:80])

p.close()
print('Done')

