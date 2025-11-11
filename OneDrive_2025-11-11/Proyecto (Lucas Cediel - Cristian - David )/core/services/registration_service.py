
from typing import Optional, Tuple, Dict
from ..ports.auth_repo import IAuthRepository, UserRecord
from ..validators import validate_username, validate_password
from ..crypto import hash_password_sha256
from ..log_config import logger

class RegistrationService:
    """Registro para roles no administrativos y bootstrap del superadmin."""
    def __init__(self, repo: IAuthRepository):
        self.repo = repo

    def ensure_superadmin(self, username: str = "superadmin", password: str = "Admin@123"):
        logger.info("Verificando superadmin inicial...")
        try:
            if not self.repo.get(username):
                self.repo.add(UserRecord(username=username, pw_hash=hash_password_sha256(password), role="superadmin", extra={}))
                logger.info("Superadmin inicializado correctamente.")
            else:
                logger.debug("Superadmin ya existe.")
        except Exception as e:
            logger.exception("Error creando superadmin: %s", e)

    def register_user(self, username: str, password: str, role: str = "comprador", extra: Optional[Dict] = None) -> Tuple[bool, str]:
        logger.info("Intentando registrar usuario: %s (rol=%s)", username, role)
        if role in ("administrador", "superadmin"):
            logger.warning("Intento de registro con rol administrativo: %s", role)
            return False, "No puedes crear administradores desde el registro normal."
        if not validate_username(username):
            return False, "Usuario inválido (solo letras, números, guion bajo, 3-20 caracteres)."
        if not validate_password(password):
            return False, "Contraseña inválida (mínimo 6 caracteres, 1 mayúscula y 1 símbolo)."
        if self.repo.get(username):
            logger.warning("Usuario ya registrado: %s", username)
            return False, "El usuario ya existe."
        try:
            self.repo.add(UserRecord(username=username, pw_hash=hash_password_sha256(password), role=role, extra=extra or {}))
            logger.info("Usuario registrado correctamente: %s", username)
            return True, f"Usuario {username} creado con rol {role}."
        except Exception as e:
            logger.error("No se pudo registrar usuario %s: %s", username, e)
            logger.exception("Stacktrace al registrar usuario:")
            return False, "No se pudo registrar el usuario por un error interno."
