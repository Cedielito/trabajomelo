
from typing import Protocol, List, Optional, Dict
from dataclasses import dataclass

@dataclass
class UserRecord:
    username: str
    pw_hash: str   # SHA-256 hex
    role: str
    extra: Dict

class IAuthRepository(Protocol):
    def get(self, username: str) -> Optional[UserRecord]: ...
    def list_all(self) -> List[UserRecord]: ...
    def add(self, user: UserRecord) -> None: ...
    def update(self, user: UserRecord) -> None: ...
    def delete(self, username: str) -> None: ...
