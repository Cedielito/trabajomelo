
from typing import List, Optional

from core.crypto import hash_password
from core.ports.auth_repo import IAuthRepository, UserRecord
from core.validators import validate_username, validate_password


class UserAdminService:
    """Operaciones de administración de usuarios (superadmin/admin)."""

    def __init__(self, repo: IAuthRepository):
        self._repo = repo

    # utilidades generales ---------------------
    def ensure_superadmin(self, username: str = "superadmin", password: str = "Admin@123") -> None:
        """Crea el superadmin inicial si no existe."""
        if self._repo.get(username):
            return
        user = UserRecord(
            username=username,
            pw_hash=hash_password(password),
            role="superadmin",
            extra={},
        )
        self._repo.add(user)

    def list_users(self) -> List[UserRecord]:
        return self._repo.list_all()

    # operaciones admin/superadmin -------------
    def create_user_by_admin(self, username: str, password: str, role: str = "administrador") -> bool:
        if role not in ("administrador", "superadmin"):
            return False
        if not validate_username(username) or not validate_password(password):
            return False
        if self._repo.get(username):
            return False

        user = UserRecord(
            username=username,
            pw_hash=hash_password(password),
            role=role,
            extra={},
        )
        self._repo.add(user)
        return True

    def update_user(
        self,
        username: str,
        new_role: Optional[str] = None,
        new_password: Optional[str] = None,
    ) -> bool:
        user = self._repo.get(username)
        if not user:
            return False

        if new_role:
            if new_role not in ("comprador", "concesionario", "administrador", "superadmin"):
                return False
            user.role = new_role

        if new_password:
            if not validate_password(new_password):
                return False
            user.pw_hash = hash_password(new_password)

        self._repo.update(user)
        return True

    def delete_user(self, username: str) -> bool:
        if username == "superadmin":
            return False
        if not self._repo.get(username):
            return False
        self._repo.delete(username)
        return True
