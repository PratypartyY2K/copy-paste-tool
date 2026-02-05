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
