import html

def esc(text) -> str:
    """Экранирует HTML-символы в тексте."""
    return html.escape(str(text))
