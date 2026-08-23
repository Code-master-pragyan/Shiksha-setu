import re

def clean_text(text: str) -> str:
    """
    Cleans extraction noise from text while preserving paragraph meaning,
    equations, and bullet points.
    """
    if not text:
        return ""
        
    # Replace multiple spaces with a single space, but keep newlines
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Replace 3 or more newlines with 2 newlines (preserve paragraph breaks)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Strip leading/trailing whitespace
    return text.strip()
