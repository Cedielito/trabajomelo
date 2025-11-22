from typing import Dict, Tuple

from core.ports.auth_repo import IAuthRepository, UserRecord
from core.crypto import hash_password
from core.validators import validate_username, validate_password

class RegistrationService:
    def __init__(self, repo: IAuthRepository):
        self._repo = repo

    def register_user(self, username: str, password: str, role="comprador", extra=None) -> Tuple[bool, str]:
        if role == "administrador":
            return False, "No puedes crear administradores desde aquí."

        if not validate_username(username):
            return False, "Usuario inválido."

        if not validate_password(password):
            return False, "Contraseña inválida."

        if self._repo.get(username):
            return False, "El usuario ya existe."

        user = UserRecord(username, hash_password(password), role, extra or {})
        self._repo.add(user)
        return True, f"Usuario {username} creado."
