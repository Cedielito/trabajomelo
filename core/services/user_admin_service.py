
from typing import Optional, List
from ..ports.auth_repo import IAuthRepository, UserRecord
from ..validators import validate_username, validate_password
from ..crypto import hash_password_sha256
from ..log_config import logger

class UserAdminService:
    """Operaciones administrativas: crear admin, actualizar, borrar, listar."""
    def __init__(self, repo: IAuthRepository):
        self.repo = repo

    def list_users(self) -> List[UserRecord]:
        users = self.repo.list_all()
        logger.info("Listado de usuarios solicitado. Total: %d", len(users))
        return users

    def create_user_by_admin(self, username: str, password: str, role: str = "administrador") -> bool:
        logger.info("Creando usuario administrativo: %s (rol=%s)", username, role)
        if role not in ("administrador", "superadmin"):
            logger.warning("Rol administrativo inválido para creación: %s", role)
            return False
        if not validate_username(username) or not validate_password(password):
            logger.warning("Datos inválidos para creación admin: username=%s", username)
            return False
        if self.repo.get(username):
            logger.warning("Usuario admin duplicado: %s", username)
            return False
        try:
            self.repo.add(UserRecord(username=username, pw_hash=hash_password_sha256(password), role=role, extra={}))
            logger.info("Administrador creado: %s", username)
            return True
        except Exception as e:
            logger.error("Error al crear administrador %s: %s", username, e)
            logger.exception("Stacktrace creando admin:")
            return False

    def update_user(self, username: str, new_role: Optional[str] = None, new_password: Optional[str] = None) -> bool:
        logger.info("Actualizando usuario: %s", username)
        user = self.repo.get(username)
        if not user:
            logger.warning("Actualización fallida: usuario no existe %s", username)
            return False
        if new_role:
            if new_role not in ("comprador", "concesionario", "administrador", "superadmin"):
                logger.warning("Rol inválido en actualización: %s", new_role)
                return False
            if user.username == "superadmin" and new_role != "superadmin":
                logger.warning("Intento de despromover superadmin.")
                return False
            user.role = new_role
            logger.info("Rol actualizado para %s: %s", username, new_role)
        if new_password:
            if not validate_password(new_password):
                logger.warning("Contraseña nueva inválida para %s", username)
                return False
            user.pw_hash = hash_password_sha256(new_password)
            logger.info("Contraseña actualizada para %s", username)
        try:
            self.repo.update(user)
            return True
        except Exception as e:
            logger.error("Error actualizando datos de usuario %s: %s", username, e)
            logger.exception("Stacktrace actualización usuario:")
            return False

    def delete_user(self, username: str) -> bool:
        logger.info("Eliminando usuario: %s", username)
        if username == "superadmin":
            logger.warning("Intento de eliminar superadmin bloqueado.")
            return False
        if not self.repo.get(username):
            logger.warning("Intento de eliminar usuario inexistente: %s", username)
            return False
        try:
            self.repo.delete(username)
            logger.info("Usuario eliminado: %s", username)
            return True
        except Exception as e:
            logger.error("No se pudo eliminar usuario %s: %s", username, e)
            logger.exception("Stacktrace eliminación usuario:")
            return False
