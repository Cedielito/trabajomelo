# main.py
import tkinter as tk

from ui.gui import AppGUI

from core.adapters.json_auth_repo import JsonAuthRepository
from core.services.authentication_service import AuthenticationService
from core.services.registration_service import RegistrationService
from core.services.user_admin_service import UserAdminService


def main():
    # Repositorio concreto
    repo = JsonAuthRepository()

    # Servicios (inyección de dependencias)
    auth_service = AuthenticationService(repo)
    registration_service = RegistrationService(repo)
    user_admin_service = UserAdminService(repo)

    # Crear UI con servicios inyectados
    root = tk.Tk()
    app = AppGUI(root, auth_service, registration_service, user_admin_service)
    root.mainloop()


if __name__ == "__main__":
    main()
