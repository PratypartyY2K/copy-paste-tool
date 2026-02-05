import subprocess
import re
import json
from typing import List

# fuzzy search helpers
try:
    from rapidfuzz import fuzz as _rfuzz
except Exception:
    _rfuzz = None

from html import escape as _html_escape

def get_frontmost_app():
    try:
        script = 'tell application "System Events" to get name of first application process whose frontmost is true'
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        app_name = result.stdout.strip()
        return app_name
    except Exception as e:
        return "Unknown App"

def fuzzy_score(text: str, query: str) -> int:
    """Return a 0-100 fuzzy match score between text and query.
    Uses rapidfuzz if available, otherwise falls back to substring membership.
    """
    if not query:
        return 100
    if not text:
        return 0
    q = query.strip()
    if not q:
        return 100
    if _rfuzz is not None:
        try:
            return int(_rfuzz.partial_ratio(q, text))
        except Exception:
            pass
    # fallback: simple case-insensitive substring check
    return 100 if q.lower() in text.lower() else 0

def highlight_match(text: str, query: str) -> str:
    """Return HTML-safe text with query occurrences highlighted using <b> tags.
    If query is empty or not found, returns escaped text.
    This is a simple substring highlighter; fuzzy ranking may still rank items higher.
    """
    if not query or not text:
        return _html_escape(text or '')
    q = re.escape(query.strip())
    if not q:
        return _html_escape(text)
    pattern = re.compile(r'(' + q + r')', re.IGNORECASE)
    def _repl(m):
        return '<b>' + _html_escape(m.group(1)) + '</b>'
    parts = pattern.split(text)
    if len(parts) == 1:
        return _html_escape(text)
    out = []
    for i, p in enumerate(parts):
        if i % 2 == 1:
            out.append('<b>' + _html_escape(p) + '</b>')
        else:
            out.append(_html_escape(p))
    return ''.join(out)

def trim_whitespace(text: str) -> str:
    """Trim leading/trailing whitespace."""
    if text is None:
        return ''
    return text.strip()

def copy_one_line(text: str) -> str:
    """Convert text to a single line: collapse all whitespace/newlines to single spaces."""
    if text is None:
        return ''
    return ' '.join(text.split())

_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)

def extract_urls(text: str) -> List[str]:
    """Return list of URLs found in text (preserve order, dedupe)."""
    if not text:
        return []
    found = _URL_RE.findall(text)
    seen = set()
    out = []
    for u in found:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out

def extract_urls_text(text: str) -> str:
    """Return newline-separated URLs (or empty string if none)."""
    urls = extract_urls(text)
    return '\n'.join(urls)

def json_escape(text: str) -> str:
    """Return a JSON-escaped string (quotes and control chars escaped)."""
    if text is None:
        return json.dumps('')
    return json.dumps(text)

_word_re = re.compile(r"[A-Za-z0-9]+")

def to_camel_case(text: str) -> str:
    """Convert a string to camelCase. Non-alphanumeric characters are treated as separators."""
    if not text:
        return ''
    words = _word_re.findall(text)
    if not words:
        return ''
    first = words[0].lower()
    rest = ''.join(w.title() for w in words[1:])
    return first + rest

def to_snake_case(text: str) -> str:
    """Convert a string to snake_case. Non-alphanumeric characters are treated as separators."""
    if not text:
        return ''
    words = _word_re.findall(text)
    return '_'.join(w.lower() for w in words)
