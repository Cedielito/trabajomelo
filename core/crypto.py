# core/crypto.py
import hashlib


def hash_password(password: str) -> str:
    """Devuelve un hash SHA-256 en hexadecimal."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Compara una contraseña en claro con el hash almacenado."""
    return hash_password(plain_password) == stored_hash
