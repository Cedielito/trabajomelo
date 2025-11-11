
from typing import Optional
from ..ports.auth_repo import IAuthRepository, UserRecord
from ..crypto import hash_password_sha256
from ..log_config import logger

class AuthenticationService:
    """Responsable solo de login/logout y sesión actual."""
    def __init__(self, repo: IAuthRepository):
        self.repo = repo
        self._current: Optional[UserRecord] = None

    @property
    def current_user(self) -> Optional[UserRecord]:
        return self._current

    def authenticate(self, username: str, password: str) -> Optional[UserRecord]:
        logger.info("Iniciando sesión de usuario: %s", username)
        try:
            rec = self.repo.get(username)
            if not rec:
                logger.warning("Usuario inexistente: %s", username)
                return None
            if rec.pw_hash == hash_password_sha256(password):
                self._current = rec
                logger.info("Usuario autenticado correctamente: %s", username)
                return rec
            logger.warning("Contraseña incorrecta para usuario: %s", username)
            return None
        except Exception as e:
            logger.exception("Error inesperado durante autenticación para %s: %s", username, e)
            return None

    def logout(self) -> None:
        if self._current:
            logger.info("Sesión cerrada por usuario %s", self._current.username)
        else:
            logger.info("Logout llamado sin usuario autenticado.")
        self._current = None
