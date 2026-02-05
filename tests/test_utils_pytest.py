from clipboard_manager.utils import fuzzy_score, highlight_match


def test_fuzzy_score_basic():
    assert fuzzy_score('hello world', 'hell') > 80
    assert fuzzy_score('something else', 'xyz') in (0,)


def test_highlight_match():
    out = highlight_match('hello world', 'lo')
    assert '<b>' in out and 'lo' in out.lower()
