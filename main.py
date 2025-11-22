# main.py
import tkinter as tk

from ui.gui import AppGUI
from core.adapters.json_auth_repo import JsonAuthRepository
from core.services.authentication_service import AuthenticationService
from core.services.registration_service import RegistrationService
from core.services.user_admin_service import UserAdminService
from core.services.catalog_service import CatalogService
from core.services.purchase_service import PurchaseService
from core.data_seed import seed_catalog
from core.report_manager import ReportManager


def main():
    # Repositorio concreto
    repo = JsonAuthRepository()

    # Servicios de usuarios
    auth_service = AuthenticationService(repo)
    registration_service = RegistrationService(repo)
    user_admin_service = UserAdminService(repo)

    # Catalogo + reportes + compras
    catalog_service = CatalogService()
    seed_catalog(catalog_service)

    report_manager = ReportManager()
    purchase_service = PurchaseService(report_manager, catalog_service)

    # UI con inyección de dependencias
    root = tk.Tk()
    app = AppGUI(
        root,
        auth_service,
        registration_service,
        user_admin_service,
        catalog_service,
        purchase_service,
        report_manager,
    )
    root.mainloop()


if __name__ == "__main__":
    main()
