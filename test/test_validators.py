
from core.validators import validate_username, validate_password, validate_matricula

def test_validate_username_ok():
    assert validate_username("juan_23") is True

def test_validate_username_bad():
    assert validate_username("$$$") is False

def test_validate_password_ok():
    assert validate_password("Clave@123") is True

def test_validate_password_bad():
    assert validate_password("abc") is False

def test_validate_matricula_ok():
    assert validate_matricula("ABC-1234") is True
