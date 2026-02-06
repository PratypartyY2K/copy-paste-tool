import subprocess
from clipboard_manager import utils


def test_extract_urls_dedupe():
    s = 'http://a.com http://a.com https://b.com'
    urls = utils.extract_urls(s)
    assert urls == ['http://a.com', 'https://b.com']


def test_json_escape_and_one_line():
    s = 'hello "world"\nnew'
    j = utils.json_escape(s)
    assert j.startswith('"') and '\\n' in j
    assert utils.copy_one_line('a\n b  c') == 'a b c'


def test_casing_conversions():
    txt = 'Hello World_example'
    assert utils.to_camel_case(txt).startswith('hello')
    assert utils.to_snake_case(txt).startswith('hello_world')


def test_get_frontmost_app_fallback(monkeypatch):
    def fake_run(*args, **kwargs):
        raise RuntimeError('oops')
    monkeypatch.setattr(subprocess, 'run', fake_run)
    assert utils.get_frontmost_app() == 'Unknown App'


def test_get_frontmost_app_appkit(monkeypatch):
    # Simulate pyobjc available and appkit returning a stable app
    monkeypatch.setattr(utils, '_try_load_pyobjc', lambda: True)
    monkeypatch.setattr(utils, '_get_app_from_appkit', lambda: 'MyApp')
    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: subprocess.CompletedProcess(args=a, returncode=0, stdout=''))
    res = utils.get_frontmost_app()
    assert res == 'MyApp'


def test_timeline_probes_and_components(monkeypatch):
    class FakeCompleted:
        def __init__(self, out='AppX'):
            self.stdout = out
    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: FakeCompleted(out='OSA'))
    monkeypatch.setattr(utils, '_get_app_from_appkit', lambda: 'AK')
    monkeypatch.setattr(utils, '_get_app_from_ax', lambda: 'AX')
    monkeypatch.setattr(utils, '_get_app_from_mouse_window', lambda: 'MW')
    out = utils.timeline_probes(duration_sec=0.06, interval_sec=0.02)
    assert isinstance(out, list) and len(out) >= 1


def test_find_window_owner_by_content_no_pyobjc(monkeypatch):
    monkeypatch.setattr(utils, '_try_load_pyobjc', lambda: False)
    assert utils.find_window_owner_by_content('anything') is None


def test_is_ax_trusted_fallback(monkeypatch):
    monkeypatch.setattr(utils, '_try_load_pyobjc', lambda: False)
    assert utils.is_ax_trusted() is False
