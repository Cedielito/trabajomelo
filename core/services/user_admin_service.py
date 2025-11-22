from typing import List, Optional

from core.crypto import hash_password
from core.ports.auth_repo import IAuthRepository, UserRecord
from core.validators import validate_username, validate_password

class UserAdminService:
    def __init__(self, repo: IAuthRepository):
        self._repo = repo

    def ensure_superadmin(self, username="superadmin", password="Admin@123"):
        if not self._repo.get(username):
            self._repo.add(
                UserRecord(username, hash_password(password), "superadmin", {})
            )

    def list_users(self) -> List[UserRecord]:
        return self._repo.list_all()

    def create_user_by_admin(self, username: str, password: str, role="administrador") -> bool:
        if not validate_username(username) or not validate_password(password):
            return False
        if self._repo.get(username):
            return False
        user = UserRecord(username, hash_password(password), role, {})
        self._repo.add(user)
        return True

    def update_user(self, username: str, new_role=None, new_password=None) -> bool:
        user = self._repo.get(username)
        if not user:
            return False
        if new_role:
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
