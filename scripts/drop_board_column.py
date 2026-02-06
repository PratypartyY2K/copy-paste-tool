#!/usr/bin/env python3
"""
drop_board_column.py

Safely remove the deprecated `board` column from the persistence DB.
Approach (SQLite safe pattern):
 - Create a backup of the DB file
 - Create a new temporary table `items_new` with desired schema (no `board`)
 - Copy data from `items` to `items_new` mapping columns (omit `board`)
 - Drop old `items` and rename `items_new` -> `items`
 - Commit and close

Usage:
  python scripts/drop_board_column.py --db ./.local/persistence.db --apply
  python scripts/drop_board_column.py --db ./.local/persistence.db

Note: The script will BACKUP the DB to `<db>.bak` before applying changes.
"""
import sqlite3
import argparse
import os
import shutil

SCHEMA_ITEMS_NEW = '''
CREATE TABLE items_new (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    source_app TEXT,
    timestamp TEXT,
    is_temporary INTEGER DEFAULT 0,
    expire_at REAL NULL,
    pinned INTEGER DEFAULT 0
);
'''


def migrate(db_path: str, apply: bool = False):
    if not os.path.exists(db_path):
        raise SystemExit('DB not found: %s' % db_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(items)")
    cols = [r[1] for r in cur.fetchall()]
    print('Existing columns in items:', cols)
    if 'board' not in cols:
        print('No board column present — nothing to do.')
        conn.close()
        return

    cur.execute('SELECT COUNT(*) FROM items')
    total = cur.fetchone()[0]
    print('Total items rows:', total)

    cur.execute('SELECT id, board, source_app, substr(content,1,80) AS preview FROM items LIMIT 5')
    print('\nSample rows (before):')
    for r in cur.fetchall():
        print(dict(r))

    if not apply:
        print('\nDRY-RUN: No changes will be applied. To apply run with --apply')
        conn.close()
        return

    bak = db_path + '.bak'
    print('\nBacking up DB to', bak)
    shutil.copy2(db_path, bak)

    try:
        cur.executescript(SCHEMA_ITEMS_NEW)
        cur.execute("INSERT INTO items_new (id, content, source_app, timestamp, is_temporary, expire_at, pinned) SELECT id, content, source_app, timestamp, is_temporary, expire_at, pinned FROM items;")
        cur.execute('DROP TABLE items')
        cur.execute('ALTER TABLE items_new RENAME TO items')
        conn.commit()
        print('Migration completed successfully.')
    except Exception as e:
        conn.rollback()
        print('Migration failed:', e)
        try:
            shutil.copy2(bak, db_path)
            print('Restored DB from backup.')
        except Exception as e2:
            print('Failed to restore backup:', e2)
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--db', default='/.local/persistence.db')
    p.add_argument('--apply', action='store_true')
    args = p.parse_args()
    migrate(args.db, apply=args.apply)

