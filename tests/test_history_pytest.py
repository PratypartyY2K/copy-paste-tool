import time
from clipboard_manager.history import HistoryStore


def test_add_and_dedupe():
    h = HistoryStore()
    it1 = h.add_item('hello', source_app='App')
    assert it1 is not None
    it2 = h.add_item('hello', source_app='App')
    assert it2 is it1


def test_token_temporary():
    h = HistoryStore()
    import clipboard_manager.history as hmod
    orig = hmod.TEMPORARY_TOKEN_SECONDS
    try:
        hmod.TEMPORARY_TOKEN_SECONDS = 1
        tkn = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc.def'
        it = h.add_item(tkn, source_app='Terminal')
        assert it is not None and it.is_temporary
        time.sleep(2)
        assert all(x.content != tkn for x in h.items)
    finally:
        hmod.TEMPORARY_TOKEN_SECONDS = orig


def test_blocklist_and_per_app_dedupe():
    h = HistoryStore()
    h.set_secret_safe_enabled(True)
    # include a substring that matches the test app name '1Password' (case-insensitive)
    h.set_blocklist(['1password', 'keychain'])
    # blocklisted app should be ignored
    item = h.add_item('secret', source_app='1Password')
    assert item is None

    # per-app dedupe
    it_a1 = h.add_item('dup content', source_app='AppA')
    assert it_a1 is not None
    it_a2 = h.add_item('dup content', source_app='AppA')
    assert it_a2 is it_a1
    # same content from different app should be allowed
    it_b = h.add_item('dup content', source_app='AppB')
    assert it_b is not None and it_b.id != it_a1.id
