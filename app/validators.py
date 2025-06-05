import re
from typing import Optional
from urllib.parse import urlparse
from .logger import logger

class ValidationError(Exception):
    """Excepción personalizada para errores de validación."""
    pass

def validate_url(url: str) -> bool:
    """Valida que una URL sea válida y segura."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception as e:
        logger.error(f"Error validando URL {url}: {str(e)}")
        return False

def validate_prompt(prompt: str, max_length: int = 1000) -> bool:
    """Valida que un prompt sea válido."""
    if not prompt or not isinstance(prompt, str):
        return False
    
    if len(prompt) > max_length:
        return False
    
    # Verificar caracteres no permitidos
    if re.search(r'[<>]', prompt):
        return False
    
    return True

def sanitize_input(text: str) -> Optional[str]:
    """Sanitiza la entrada de texto."""
    if not text:
        return None
    
    # Eliminar caracteres de control
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    
    # Eliminar espacios múltiples
    text = re.sub(r'\s+', ' ', text)
    
    # Eliminar HTML/XML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    return text.strip()

def validate_api_key(api_key: str) -> bool:
    """Valida que una API key tenga el formato correcto."""
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Validación básica para OpenAI API key
    if api_key.startswith('sk-') and len(api_key) > 20:
        return True
    
    return False 