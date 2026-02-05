import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from clipboard_manager.history import HistoryStore, TEMPORARY_TOKEN_SECONDS


def test_blocklist_and_toggle():
    hs = HistoryStore()
    # ensure secret-safe default is enabled
    assert hs.get_secret_safe_enabled() is True
    # set blocklist and verify blocking
    hs.set_blocklist(['TestBlock'])
    hs.set_secret_safe_enabled(True)
    item = hs.add_item('somedata', source_app='MyTestBlockApp')
    assert item is None, 'Expected blocklisted app to be blocked when secret-safe enabled'

    # disabling secret-safe should allow storage
    hs.set_secret_safe_enabled(False)
    item2 = hs.add_item('somedata', source_app='MyTestBlockApp')
    assert item2 is not None, 'Expected app to be stored when secret-safe disabled'


def test_temporary_token_removal():
    hs = HistoryStore()
    # shorten expiry for test
    orig = TEMPORARY_TOKEN_SECONDS
    try:
        # set module constant to 1 second
        import clipboard_manager.history as hmod
        hmod.TEMPORARY_TOKEN_SECONDS = 1
        hs.set_secret_safe_enabled(True)
        token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc.def'
        it = hs.add_item(token, source_app='Terminal')
        assert it is not None and it.is_temporary is True
        # wait >1s for cleanup
        time.sleep(2)
        # give cleanup thread a moment
        time.sleep(1)
        # item should be removed from store
        items = [x for x in hs.items if x.content == token]
        assert len(items) == 0, 'Temporary token should have been cleaned up'
    finally:
        # restore constant
        import clipboard_manager.history as hmod2
        hmod2.TEMPORARY_TOKEN_SECONDS = orig


if __name__ == '__main__':
    test_blocklist_and_toggle()
    test_temporary_token_removal()
    print('SECRET_SAFE_TESTS_OK')
