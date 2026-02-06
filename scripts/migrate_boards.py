#!/usr/bin/env python3
"""
migrate_boards.py

Scan the SQLite persistence DB and re-run the BoardRouter on every row to
correct the stored `board` column. Useful after fixing BoardRouter/History bugs.

Usage:
  python scripts/migrate_boards.py --db ./.local/persistence.db --apply
  python scripts/migrate_boards.py --db ./.local/persistence.db

The script prints a summary and can optionally apply updates in-place.
"""
import sqlite3
import argparse
import os
import sys
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

try:
    from clipboard_manager.boards import BoardRouter
except Exception as exc:
    print('\nERROR: Failed to import package `clipboard_manager`.', file=sys.stderr)
    print('Exception:', repr(exc), file=sys.stderr)
    print('\nDiagnostic: sys.path entries (first 10):', file=sys.stderr)
    for i, p in enumerate(sys.path[:10]):
        print(f'  {i:2}: {p}', file=sys.stderr)
    print('\nIf you run this script from a different working directory or without the repo on PYTHONPATH,', file=sys.stderr)
    print('either run it with `PYTHONPATH=. python scripts/migrate_boards.py ...` or activate your venv where', file=sys.stderr)
    print('the package is installed.', file=sys.stderr)
    sys.exit(2)


def open_db(path):
    conn = sqlite3.connect(path, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def compute_board(router, source_app, content):
    try:
        b = router.route(source_app, content)
        return b.name if hasattr(b, 'name') else str(b)
    except Exception:
        return 'OTHER'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--db', default='./.local/persistence.db', help='Path to SQLite DB')
    p.add_argument('--debug', action='store_true', help='Print debug info (first rows and computed values)')
    p.add_argument('--apply', action='store_true', help='Apply updates to DB')
    args = p.parse_args()

    conn = open_db(args.db)
    cur = conn.cursor()
    cur.execute('SELECT id, source_app, content, board FROM items')
    rows = cur.fetchall()
    if args.debug:
        print('\nDEBUG: first 5 rows from DB:')
        for r in rows[:5]:
            print('  id=', r['id'], 'board=', r['board'], 'app=', r['source_app'], 'preview=', (r['content'] or '')[:80].replace('\n','\\n'))
    router = BoardRouter()

    changed = 0
    total = 0
    updates = []
    for r in rows:
        total += 1
        sid = r['id']
        src = r['source_app'] if r['source_app'] is not None else ''
        content = r['content'] if r['content'] is not None else ''
        stored = (r['board'] or 'OTHER')
        computed = compute_board(router, src, content)
        if computed != stored:
            changed += 1
            updates.append((computed, sid, stored, src, content[:80].replace('\n','\\n')))

    print(f'Total rows: {total}, would change: {changed}')
    if changed:
        print('\nSample changes (computed -> stored)')
        for new, sid, old, src, preview in updates[:50]:
            print(f'{new:10} <- {old:10}  id={sid} app={src} preview="{preview}"')

    if args.apply and changed:
        print('\nApplying updates...')
        for new, sid, old, src, preview in updates:
            try:
                cur.execute('UPDATE items SET board=? WHERE id=?', (new, sid))
            except Exception as e:
                print('ERROR updating', sid, e)
        conn.commit()
        print('Applied updates:', changed)

    conn.close()

if __name__ == '__main__':
    main()

