
import os, json
from typing import List, Optional
from dataclasses import asdict
from ..ports.auth_repo import IAuthRepository, UserRecord
from ..log_config import logger

DATA_FILE = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data", "users.json"))

class JsonAuthRepository(IAuthRepository):
    def __init__(self, data_file: str = DATA_FILE):
        self.data_file = data_file
        self._ensure_file()

    def _ensure_file(self):
        try:
            folder = os.path.dirname(self.data_file)
            os.makedirs(folder, exist_ok=True)
            if not os.path.exists(self.data_file):
                logger.info("Archivo JSON no encontrado. Creando nuevo en %s.", self.data_file)
                with open(self.data_file, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=2)
        except Exception as e:
            logger.critical("Error fatal: base de datos no disponible. Detalle: %s", e)
            raise

    def _load(self) -> List[UserRecord]:
        logger.info("Cargando usuarios desde archivo JSON.")
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            users = [UserRecord(**{
                "username": u["username"],
                "pw_hash": u["pw_hash"],
                "role": u.get("role","comprador"),
                "extra": u.get("extra",{}),
            }) for u in data]
            logger.debug("Usuarios cargados: %d", len(users))
            return users
        except json.JSONDecodeError as e:
            logger.critical("Archivo JSON corrupto o ilegible: %s", e)
            return []
        except Exception as e:
            logger.error("No se pudo acceder al archivo JSON. %s", e)
            logger.exception("Stacktrace de error al leer JSON:")
            return []

    def _save(self, users: List[UserRecord]) -> None:
        logger.info("Guardando %d usuarios en archivo JSON.", len(users))
        try:
            payload = [asdict(u) for u in users]
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            logger.error("Error al guardar usuarios en JSON: %s", e)
            logger.exception("Stacktrace de error al escribir JSON:")
            raise

    def get(self, username: str) -> Optional[UserRecord]:
        logger.debug("Buscando usuario: %s", username)
        for u in self._load():
            if u.username == username:
                logger.debug("Usuario encontrado: %s", username)
                return u
        logger.debug("Usuario no encontrado: %s", username)
        return None

    def list_all(self) -> List[UserRecord]:
        users = self._load()
        logger.info("Listando usuarios. Total: %d", len(users))
        return users

    def add(self, user: UserRecord) -> None:
        logger.info("Agregando usuario: %s (rol=%s)", user.username, user.role)
        users = self._load()
        if any(u.username == user.username for u in users):
            logger.warning("Usuario ya registrado (duplicado): %s", user.username)
            raise ValueError("user_exists")
        users.append(user)
        self._save(users)

    def update(self, user: UserRecord) -> None:
        logger.info("Actualizando usuario: %s", user.username)
        users = self._load()
        for i, u in enumerate(users):
            if u.username == user.username:
                users[i] = user
                self._save(users)
                return
        logger.error("No se encontró usuario a actualizar: %s", user.username)
        raise ValueError("user_not_found")

    def delete(self, username: str) -> None:
        logger.info("Eliminando usuario: %s", username)
        users = self._load()
        if not any(u.username == username for u in users):
            logger.warning("Intento de eliminar usuario inexistente: %s", username)
        users = [u for u in users if u.username != username]
        self._save(users)
