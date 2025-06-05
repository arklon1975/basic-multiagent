import time
from functools import wraps
from typing import Dict, Optional
from .logger import logger

class RateLimiter:
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.calls: Dict[str, list] = {}
    
    def _clean_old_calls(self, key: str):
        """Elimina llamadas más antiguas que 1 minuto."""
        current_time = time.time()
        self.calls[key] = [t for t in self.calls.get(key, []) 
                          if current_time - t < 60]
    
    def is_rate_limited(self, key: str) -> bool:
        """Verifica si una clave está rate limited."""
        self._clean_old_calls(key)
        return len(self.calls.get(key, [])) >= self.calls_per_minute
    
    def add_call(self, key: str):
        """Registra una nueva llamada."""
        if key not in self.calls:
            self.calls[key] = []
        self.calls[key].append(time.time())
    
    def get_wait_time(self, key: str) -> float:
        """Calcula el tiempo de espera necesario."""
        self._clean_old_calls(key)
        if not self.calls.get(key):
            return 0
        
        oldest_call = min(self.calls[key])
        return max(0, 60 - (time.time() - oldest_call))

def rate_limit(calls_per_minute: int = 60):
    """Decorador para implementar rate limiting."""
    limiter = RateLimiter(calls_per_minute)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            
            if limiter.is_rate_limited(key):
                wait_time = limiter.get_wait_time(key)
                logger.warning(f"Rate limit alcanzado para {func.__name__}. "
                             f"Esperando {wait_time:.2f} segundos.")
                time.sleep(wait_time)
            
            limiter.add_call(key)
            return func(*args, **kwargs)
        return wrapper
    return decorator 