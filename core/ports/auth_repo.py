# core/ports/auth_repo.py
from dataclasses import dataclass
from typing import Protocol, Optional, List, Dict


@dataclass
class UserRecord:
    username: str
    pw_hash: str
    role: str
    extra: Dict | None = None


class IAuthRepository(Protocol):
    """Contrato para cualquier repositorio de usuarios."""

    def get(self, username: str) -> Optional[UserRecord]:
        ...

    def list_all(self) -> List[UserRecord]:
        ...

    def add(self, user: UserRecord) -> None:
        ...

    def update(self, user: UserRecord) -> None:
        ...

    def delete(self, username: str) -> None:
        ...
