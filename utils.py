import html

def esc(text) -> str:
    return html.escape(str(text))

def split_text(text: str, max_length: int = 4000) -> list:
    """
    Разбивает длинный текст на части не длиннее max_length,
    стараясь сохранить целостность строк.
    """
    if len(text) <= max_length:
        return [text]
    
    parts = []
    lines = text.split('\n')
    current = ''
    
    for line in lines:
        if len(current) + len(line) + 1 <= max_length:
            current += line + '\n'
        else:
            if current:
                parts.append(current.strip())
            current = line + '\n'
    
    if current:
        parts.append(current.strip())
    
    return parts
