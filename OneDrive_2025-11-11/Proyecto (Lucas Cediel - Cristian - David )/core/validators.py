
import re
from .log_config import logger

def validate_username(username: str) -> bool:
    ok = bool(re.match(r"^[a-zA-Z0-9_]{3,20}$", username))
    if not ok:
        logger.warning("Validación fallida de username: %s", username)
    return ok

def validate_password(password: str) -> bool:
    ok = bool(re.match(r"^(?=.*[A-Z])(?=.*[!@#$%^&*(),.?\":{}|<>]).{6,}$", password))
    if not ok:
        logger.warning("Contraseña débil detectada.")
    return ok

def validate_matricula(matricula: str) -> bool:
    ok = bool(re.match(r"^[A-Z0-9\-]{4,10}$", matricula.upper()))
    if not ok:
        logger.warning("Matrícula inválida: %s", matricula)
    return ok
