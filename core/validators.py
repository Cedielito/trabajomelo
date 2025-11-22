# core/validators.py
import re


def validate_username(username: str) -> bool:
    """
    Acepta entre 3 y 20 caracteres: letras, números y guiones bajos.
    """
    return bool(re.match(r"^[a-zA-Z0-9_]{3,20}$", username))


def validate_password(password: str) -> bool:
    """
    Mínimo 6 caracteres, al menos una mayúscula y un símbolo especial.
    """
    return bool(
        re.match(r'^(?=.*[A-Z])(?=.*[!@#$%^&*(),.?":{}|<>]).{6,}$', password)
    )


def validate_matricula(matricula: str) -> bool:
    """
    Matrícula aceptada: 4-10 caracteres alfanuméricos y guion.
    """
    return bool(re.match(r"^[A-Z0-9\-]{4,10}$", matricula.upper()))
