import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from clipboard_manager.utils import trim_whitespace, copy_one_line, extract_urls, extract_urls_text, json_escape, to_camel_case, to_snake_case


def test_trim():
    assert trim_whitespace('  hello \n') == 'hello'


def test_one_line():
    assert copy_one_line('a\n  b \t c') == 'a b c'


def test_extract_urls():
    s = 'visit https://example.com and http://foo.test/path and www.site.org'
    urls = extract_urls(s)
    assert 'https://example.com' in urls
    assert 'http://foo.test/path' in urls
    assert 'www.site.org' in urls


def test_extract_urls_text():
    s = 'here: https://x'
    assert extract_urls_text(s) == 'https://x'


def test_json_escape():
    s = 'He said "Hi"\n'
    esc = json_escape(s)
    assert esc.startswith('"') and esc.endswith('"')


def test_casing():
    s = 'hello world-test'
    assert to_camel_case(s) == 'helloWorldTest'
    assert to_snake_case(s) == 'hello_world_test'

if __name__ == '__main__':
    test_trim()
    test_one_line()
    test_extract_urls()
    test_extract_urls_text()
    test_json_escape()
    test_casing()
    print('UTILS_TESTS_OK')
