
import pytest

from core.adapters.json_auth_repo import JsonAuthRepository
from core.services.authentication_service import AuthenticationService
from core.services.registration_service import RegistrationService
from core.services.user_admin_service import UserAdminService
from core.services.catalog_service import CatalogService
from core.services.purchase_service import PurchaseService
from core.report_manager import ReportManager

# Repositorio en memoria (no guardará archivo real)
@pytest.fixture
def clean_repo(tmp_path):
    repo = JsonAuthRepository(data_file=str(tmp_path / "users_test.json"))
    return repo

@pytest.fixture
def auth_service(clean_repo):
    return AuthenticationService(clean_repo)

@pytest.fixture
def registration_service(clean_repo):
    return RegistrationService(clean_repo)

@pytest.fixture
def user_admin_service(clean_repo):
    return UserAdminService(clean_repo)

@pytest.fixture
def catalog_service():
    return CatalogService()

@pytest.fixture
def report_manager():
    return ReportManager()

@pytest.fixture
def purchase_service(report_manager, catalog_service):
    return PurchaseService(report_manager, catalog_service)
