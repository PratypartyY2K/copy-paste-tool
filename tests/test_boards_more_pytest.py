from clipboard_manager.boards import BoardRouter, Board


def test_rules_serialization_and_set():
    r = BoardRouter()
    spec = r.rules_as_spec()
    r.set_rules(spec)
    assert isinstance(r.route('Chrome', 'https://x.com'), Board)


def test_custom_rule_override():
    custom = [
        {'predicates':[{'type':'content_contains','value':'SECRET'}], 'board':'NOTES'},
        {'predicates':[{'type':'always','value':True}], 'board':'LINKS'}
    ]
    r = BoardRouter(custom)
    assert r.route('Any', 'SECRET DATA') == Board.NOTES
    assert r.route('Any', 'http://ok') == Board.LINKS
