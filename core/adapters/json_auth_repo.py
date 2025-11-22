
# core/adapters/json_auth_repo.py
import json
import os
from typing import Dict, List, Optional

from core.ports.auth_repo import IAuthRepository, UserRecord

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "users.json")
DATA_FILE = os.path.normpath(DATA_FILE)


class JsonAuthRepository(IAuthRepository):
    """
    Implementación de IAuthRepository usando archivo JSON.
    Responsabilidad única: persistir y recuperar usuarios.
    """

    def __init__(self, data_file: str = DATA_FILE) -> None:
        self._data_file = data_file
        self._users: Dict[str, UserRecord] = {}
        self._ensure_data_file()
        self._load()

    # ----------------- helpers internos -----------------
    def _ensure_data_file(self) -> None:
        folder = os.path.dirname(self._data_file)
        os.makedirs(folder, exist_ok=True)
        if not os.path.exists(self._data_file):
            with open(self._data_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)

    def _load(self) -> None:
        try:
            with open(self._data_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            raw = []

        self._users.clear()
        for u in raw:
            self._users[u["username"]] = UserRecord(
                username=u["username"],
                pw_hash=u["pw_hash"],
                role=u.get("role", "comprador"),
                extra=u.get("extra") or {},
            )

    def _save(self) -> None:
        """Guardado atómico para evitar corrupción de archivo."""
        out = [
            {
                "username": u.username,
                "pw_hash": u.pw_hash,
                "role": u.role,
                "extra": u.extra or {},
            }
            for u in self._users.values()
        ]
        tmp = self._data_file + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=4)
        os.replace(tmp, self._data_file)

    # ----------------- implementación IAuthRepository -----------------
    def get(self, username: str) -> Optional[UserRecord]:
        return self._users.get(username)

    def list_all(self) -> List[UserRecord]:
        return list(self._users.values())

    def add(self, user: UserRecord) -> None:
        if user.username in self._users:
            raise ValueError(f"Usuario {user.username} ya existe")
        self._users[user.username] = user
        self._save()

    def update(self, user: UserRecord) -> None:
        if user.username not in self._users:
            raise KeyError(f"Usuario {user.username} no existe")
        self._users[user.username] = user
        self._save()

    def delete(self, username: str) -> None:
        if username in self._users:
            del self._users[username]
            self._save()
