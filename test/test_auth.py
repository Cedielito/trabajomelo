
def test_login_correct(auth_service, registration_service):
    # Registrar usuario
    registration_service.register_user("juan123", "Clave@123", "comprador")

    # Login correcto
    result = auth_service.login("juan123", "Clave@123")
    assert result.ok is True
    assert result.user.username == "juan123"
    assert result.code == "OK"


def test_login_user_not_found(auth_service):
    result = auth_service.login("noexiste", "Algo@123")
    assert result.ok is False
    assert result.code == "NOT_FOUND"


def test_login_wrong_password(auth_service, registration_service):
    registration_service.register_user("carlos", "Clave@123")

    result = auth_service.login("carlos", "MalaClave@1")
    assert result.ok is False
    assert result.code == "BAD_PASSWORD"
