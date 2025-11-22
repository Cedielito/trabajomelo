# core/services/authentication_service.py
from dataclasses import dataclass
from typing import Optional

from core.crypto import verify_password
from core.ports.auth_repo import IAuthRepository, UserRecord
from core.validators import validate_username, validate_password


@dataclass
class LoginResult:
    """
    Resultado tipado del login:
    - ok: True / False
    - user: usuario autenticado (o None)
    - code: código de estado para la UI
    """
    ok: bool
    user: Optional[UserRecord]
    code: str


class AuthenticationService:
    def __init__(self, repo: IAuthRepository):
        self._repo = repo
        self._current_user: Optional[UserRecord] = None

    @property
    def current_user(self) -> Optional[UserRecord]:
        return self._current_user

    def login(self, username: str, password: str) -> LoginResult:
        if not username or not password:
            return LoginResult(False, None, "EMPTY")

        if not validate_username(username):
            return LoginResult(False, None, "INVALID_USERNAME")

        # (opcional) no validamos formato de contraseña aquí para no filtrar info
        user = self._repo.get(username)
        if not user:
            return LoginResult(False, None, "NOT_FOUND")

        if not verify_password(password, user.pw_hash):
            return LoginResult(False, None, "BAD_PASSWORD")

        self._current_user = user
        return LoginResult(True, user, "OK")

    def logout(self) -> None:
        self._current_user = None
