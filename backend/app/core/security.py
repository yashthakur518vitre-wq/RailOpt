import re

def get_cors_origins(origins_str: str) -> list[str]:
    """Splits a comma-separated string of origins into a list."""
    if not origins_str:
        return []
    return [origin.strip() for origin in origins_str.split(',') if origin.strip()]

def sanitize_input(text: str) -> str:
    """Basic input sanitization."""
    if not isinstance(text, str):
        return text
    # Remove null bytes and unprintable characters, keep basic punctuation
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text.strip()
