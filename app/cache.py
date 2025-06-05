import time
from typing import Any, Dict, Optional
from functools import wraps
from .logger import logger

class Cache:
    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds
    
    def _is_expired(self, timestamp: float) -> bool:
        """Verifica si un elemento del caché ha expirado."""
        return time.time() - timestamp > self.ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del caché si existe y no ha expirado."""
        if key not in self.cache:
            return None
        
        item = self.cache[key]
        if self._is_expired(item['timestamp']):
            logger.debug(f"Elemento expirado en caché: {key}")
            del self.cache[key]
            return None
        
        logger.debug(f"Cache hit para: {key}")
        return item['value']
    
    def set(self, key: str, value: Any):
        """Almacena un valor en el caché."""
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
        logger.debug(f"Elemento almacenado en caché: {key}")
    
    def clear(self):
        """Limpia todo el caché."""
        self.cache.clear()
        logger.info("Caché limpiado")

# Instancia global del caché
cache = Cache()

def cached(ttl_seconds: int = 3600):
    """Decorador para cachear resultados de funciones."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Crear una clave única basada en la función y sus argumentos
            key = f"{func.__name__}:{args}:{kwargs}"
            
            # Intentar obtener del caché
            result = cache.get(key)
            if result is not None:
                return result
            
            # Si no está en caché, ejecutar la función
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        return wrapper
    return decorator 