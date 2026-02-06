from clipboard_manager.utils import fuzzy_score, highlight_match


def test_fuzzy_score_basic():
    assert fuzzy_score('hello world', 'hell') > 80
    assert fuzzy_score('something else', 'xyz') in (0,)


def test_highlight_match():
    out = highlight_match('hello world', 'lo')
    assert '<b>' in out and 'lo' in out.lower()


def test_trim_and_oneline():
    from clipboard_manager import utils
    s = "  hello\nworld  "
    assert utils.trim_whitespace(s) == "hello\nworld"
    assert utils.copy_one_line(s) == "hello world"


def test_extract_urls_and_json_cases():
    from clipboard_manager import utils
    text = "see https://example.com and http://foo.bar and www.site.org/page"
    urls = utils.extract_urls(text)
    assert 'https://example.com' in urls
    assert 'http://foo.bar' in urls
    assert 'www.site.org/page' in urls
    assert utils.extract_urls_text(text).startswith('https://example.com')

    txt = 'Hello "world"'
    js = utils.json_escape(txt)
    assert js.startswith('"') and js.endswith('"')
    assert utils.to_camel_case('hello world_test') == 'helloWorldTest'
    assert utils.to_snake_case('Hello World-Test') == 'hello_world_test'
