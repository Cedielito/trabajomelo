
from typing import Dict, Tuple

from core.crypto import hash_password
from core.ports.auth_repo import IAuthRepository, UserRecord
from core.validators import validate_username, validate_password


class RegistrationService:
    """Servicio para registro normal de compradores / concesionarios."""

    def __init__(self, repo: IAuthRepository):
        self._repo = repo

    def register_user(
        self,
        username: str,
        password: str,
        role: str = "comprador",
        extra: Dict | None = None,
    ) -> Tuple[bool, str]:
        if role == "administrador":
            return False, "No puedes crear administradores desde el registro normal."

        if not validate_username(username):
            return False, "Usuario inválido (3–20 letras/números/guion bajo)."

        if not validate_password(password):
            return False, "Contraseña inválida (mínimo 6, 1 mayúscula y 1 símbolo)."

        if self._repo.get(username):
            return False, "El usuario ya existe."

        user = UserRecord(
            username=username,
            pw_hash=hash_password(password),
            role=role,
            extra=extra or {},
        )
        self._repo.add(user)
        return True, f"Usuario {username} creado con rol {role}."
