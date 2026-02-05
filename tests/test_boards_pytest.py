from clipboard_manager.boards import BoardRouter, Board


def test_default_routing_links():
    r = BoardRouter()
    b = r.route('Google Chrome', 'https://example.com')
    assert b == Board.LINKS


def test_editor_code_routing():
    r = BoardRouter()
    b = r.route('Visual Studio Code', 'function test() { return; }')
    assert b == Board.CODE


def test_terminal_commands_routing():
    r = BoardRouter()
    b = r.route('iTerm2', '$ ls -la')
    assert b == Board.COMMANDS
