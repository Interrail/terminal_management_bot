# utils/validators.py
import re
from typing import Optional


def validate_container_number(container_number: str) -> Optional[str]:
    """Validate container number format."""
    clean_text = re.sub(r'\s+', '', container_number)
    if re.match(r'^[A-Za-z]{4}\d{7}$', clean_text):
        return clean_text
    return None
