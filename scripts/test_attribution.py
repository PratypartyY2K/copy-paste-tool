#!/usr/bin/env python3
"""Deterministic attribution probe for ClipboardWatcher.
Seeds history and runs pick/score logic, printing results.
"""
import time
from collections import deque
from clipboard_manager.watcher import ClipboardWatcher

w = object.__new__(ClipboardWatcher)
# minimal state
w._app_history = deque()
w._last_sampled_app = None
w._ignore_until = 0.0

now = time.time()
entries = [
    ('PyCharm', now-20), ('Python', now-19), ('Notes', now-17), ('Python', now-16),
    ('Notes', now-14), ('Python', now-12), ('Brave Browser', now-10), ('PyCharm', now-9),
    ('Brave Browser', now-8), ('Python', now-7), ('Discord', now-5), ('Visual Studio Code', now-4),
    ('PyCharm', now-3), ('Discord', now-2), ('Python', now-1)
]
for name, ts in entries:
    w._app_history.append((ts, name))

print('HISTORY:')
for t,n in list(w._app_history)[-12:]:
    print(' ', int(t), n)

now = time.time()
print('\nPick from history (allow_ide=True):', w._pick_recent_source_app(now, allow_ide=True, code_like=False))
print('\nOwner scores for URL')
url = 'https://calendar.google.com/calendar/u/2/r'
print(' Brave:', w.score_owner('Brave Browser', url.lower(), True, False))
print(' Discord:', w.score_owner('Discord', url.lower(), True, False))

print('\nOwner scores for code')
code = '    def my_function():\n        pass'
print(' PyCharm:', w.score_owner('PyCharm', code.lower(), True, True))
print(' VSCode:', w.score_owner('Visual Studio Code', code.lower(), True, True))
print(' Discord:', w.score_owner('Discord', code.lower(), True, True))

print('\nFinal picks for simulated clipboard events:')
# 1: Notes-like
print(' Event1 (notes):', w._pick_recent_source_app(now, allow_ide=True, code_like=False))
# 2: PyCharm code
print(' Event2 (code):', w._pick_recent_source_app(now, allow_ide=True, code_like=True))
# 3: VSCode code
print(' Event3 (js):', w._pick_recent_source_app(now, allow_ide=True, code_like=True))
