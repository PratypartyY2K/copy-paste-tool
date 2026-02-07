from clipboard_manager.history import History
from clipboard_manager import settings


def test_history_updates_secret_safe(tmp_path):
    # ensure settings loaded from a temp config dir
    import os
    orig = os.environ.get('XDG_CONFIG_HOME')
    os.environ['XDG_CONFIG_HOME'] = str(tmp_path)
    try:
        settings.load_settings()
        # ensure default is True
        assert settings.get('secret_safe_mode') in (True, 'True', 1, '1', None)
        h = History(persistence=None)
        # flip setting
        settings.set_('secret_safe_mode', False)
        # history should observe change
        assert h.get_secret_safe_enabled() is False
        # restore
        settings.set_('secret_safe_mode', True)
        assert h.get_secret_safe_enabled() is True
    finally:
        if orig is not None:
            os.environ['XDG_CONFIG_HOME'] = orig
        else:
            try:
                del os.environ['XDG_CONFIG_HOME']
            except Exception:
                pass

