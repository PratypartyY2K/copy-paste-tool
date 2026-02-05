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
