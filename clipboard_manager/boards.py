import re
from typing import Optional
from enum import Enum
class Board(Enum):
    LINKS = "links"
    CODE = "code"
    COMMANDS = "commands"
    NOTES = "notes"
    OTHER = "other"

class BoardRouter:
    _url_re = re.compile(r'https?://', re.IGNORECASE)
    _domain_like_re = re.compile(r'^[\w-]+(.[\w-]+)+(/|$)', re.IGNORECASE)

    @classmethod
    def route(cls, app_name: Optional[str], content: Optional[str]) -> Board:
        app = (app_name or "").lower()
        text = (content or "").strip()

        if any(browser in app for browser in ("chrome", "safari", "firefox", "edge", "brave")):
            if cls._url_re.search(text) or cls._domain_like_re.search(text) or text.startswith("www."):
                return Board.LINKS

        if any(term in app for term in ("terminal", "iterm", "kitty", "alacritty", "wezterm")):
            if text.startswith("$") or "--" in text or text.startswith("sudo ") or re.match(r'^[a-zA-Z0-9_\-]+ .*', text):
                return Board.COMMANDS

        if any(editor in app for editor in ("vscode", "visual studio code", "code", "sublime", "atom")):
            if "{" in text or "}" in text or ";" in text or re.search(r'\bdef\b|\bclass\b|\bimport\b', text):
                return Board.CODE

        if cls._url_re.search(text) or cls._domain_like_re.search(text):
            return Board.LINKS
        if text.startswith("$") or "--" in text:
            return Board.COMMANDS
        if "{" in text or "}" in text or ";" in text:
            return Board.CODE

        return Board.NOTES

    @classmethod
    def assign_board_to_item(cls, item) -> None:
        """
        Mutates `item` by setting `item.board` to the routed Board.
        Expected `item` to have `source_app` and `content` attributes.
        """
        item.board = cls.route(getattr(item, "source_app", None), getattr(item, "content", None))
