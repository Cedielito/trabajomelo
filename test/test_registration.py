
def test_registration_valid(registration_service, clean_repo):
    ok, msg = registration_service.register_user("ana99", "Pass@123", "comprador")
    assert ok is True
    assert "creado" in msg.lower()

def test_registration_invalid_username(registration_service):
    ok, msg = registration_service.register_user("!!", "Pass@123", "comprador")
    assert ok is False

def test_registration_invalid_password(registration_service):
    ok, msg = registration_service.register_user("user123", "abc", "comprador")
    assert ok is False
