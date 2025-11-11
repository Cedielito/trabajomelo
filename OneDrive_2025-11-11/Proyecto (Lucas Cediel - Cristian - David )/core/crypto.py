
import hashlib
from .log_config import logger

def hash_password_sha256(password: str) -> str:
    # DEBUG: hashing operation (no se loguea el contenido del password)
    logger.debug("Calculando hash SHA-256 de contraseña (contenido no visible).")
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
