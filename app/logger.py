import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name: str, log_file: str = 'app.log', level=logging.INFO):
    """Configura y retorna un logger con rotación de archivos."""
    
    # Crear el directorio de logs si no existe
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar el logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Formato del log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para archivo con rotación (máximo 5 archivos de 5MB cada uno)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, log_file),
        maxBytes=5*1024*1024,
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Agregar handlers al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Crear logger por defecto
logger = setup_logger('multiagent') 