
import tkinter as tk
from tkinter import messagebox, simpledialog
from core.adapters.json_auth_repo import JsonAuthRepository
from core.services.catalog_service import CatalogService
from core.services.purchase_service import PurchaseService
from core.services.authentication_service import AuthenticationService
from core.services.registration_service import RegistrationService
from core.services.user_admin_service import UserAdminService
from core.data_seed import seed_catalog
from core.report_manager import ReportManager
from core.models import LineItem, Factura
from core.factories import VehicleFactory, ServiceFactory
from core.validators import validate_matricula
from core.log_config import logger
import datetime, uuid

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mi Sistema - Intermediario")
        self.root.geometry("980x640")

        # Managers / Services
        self.auth = AuthManager()
        # ensure only superadmin is created here (no burned users)
        self.auth.ensure_superadmin("superadmin", "Admin@123")

        # catálogo en memoria + servicio de catálogo
        base_catalog = {"vehicles": [], "services": []}
        seed_catalog(base_catalog)
        self.catalog_service = CatalogService(base_catalog)

        # reportes + servicio de compras
        self.reports = ReportManager()
        self.purchase_service = PurchaseService(self.reports)

        # carrito actual
        self.current_cart = []

        # pantalla inicial
        self.build_welcome()

    def build_welcome(self):
        logger.info("Construyendo pantalla de bienvenida.")
        for w in self.root.winfo_children(): w.destroy()
        tk.Label(self.root, text="Sistema Intermediario (Demo)", font=("Helvetica", 20, "bold")).pack(pady=14)
        frame = tk.Frame(self.root); frame.pack(pady=8)
        tk.Button(frame, text="Registrarse", width=16, command=self.open_register).grid(row=0, column=0, padx=6)
        tk.Button(frame, text="Iniciar sesión", width=16, command=self.open_login).grid(row=0, column=1, padx=6)
        tk.Button(frame, text="Salir", width=16, command=self.root.quit).grid(row=0, column=2, padx=6)
        info = ("Usuario administrador por defecto:\n"
                "superadmin / Admin@123  (superadmin)\n\n"
                "Notas:\n- Solo SuperAdmin puede crear/gestionar administradores.\n- Concesionarios pueden agregar vehículos y repuestos desde su panel.\n")
        tk.Label(self.root, text=info, justify="left").pack(padx=12, pady=10)

    # Register
    def open_register(self):
        logger.info("Abriendo ventana de registro.")
        win = tk.Toplevel(self.root); win.title("Registro de Usuario"); win.geometry("440x380")
        tk.Label(win, text="Usuario:").pack(anchor="w", padx=8, pady=(8,0)); e_user = tk.Entry(win); e_user.pack(fill="x", padx=8)
        tk.Label(win, text="Contraseña:").pack(anchor="w", padx=8, pady=(8,0)); e_pw = tk.Entry(win, show="*"); e_pw.pack(fill="x", padx=8)
        tk.Label(win, text="Rol (no se permite 'administrador'):", anchor="w").pack(anchor="w", padx=8, pady=(8,0))
        role_var = tk.StringVar(value="comprador"); tk.OptionMenu(win, role_var, "comprador", "concesionario").pack(padx=8, pady=4, fill="x")
        tk.Label(win, text="(Si es concesionario, nombre opcional):").pack(anchor="w", padx=8); e_extra = tk.Entry(win); e_extra.pack(fill="x", padx=8, pady=(0,8))
        tk.Label(win, text="Requisitos de contraseña:\n- Mínimo 6 caracteres\n- Al menos 1 mayúscula\n- Al menos 1 símbolo especial", fg="gray").pack(anchor="w", padx=8, pady=(0,8))
        def do_register():
            username = e_user.get().strip(); password = e_pw.get().strip(); role = role_var.get()
            extra = {"dealer_name": e_extra.get().strip()} if role == "concesionario" else {}
            ok, msg = self.registration.register_user(username, password, role, extra)
            if not ok:
                logger.warning("Registro fallido para %s: %s", username, msg)
                messagebox.showerror("Registro", msg); return
            logger.info("Usuario registrado correctamente (UI): %s", username)
            messagebox.showinfo("Registro", msg); win.destroy()
        tk.Button(win, text="Registrar", width=18, command=do_register).pack(pady=10)

    # Login
    def open_login(self):
        logger.info("Abriendo ventana de login.")
        win = tk.Toplevel(self.root); win.title("Iniciar Sesión"); win.geometry("360x260")
        tk.Label(win, text="Usuario:").pack(anchor="w", padx=8, pady=(8,0)); e_user = tk.Entry(win); e_user.pack(fill="x", padx=8)
        tk.Label(win, text="Contraseña:").pack(anchor="w", padx=8, pady=(8,0)); e_pw = tk.Entry(win, show="*"); e_pw.pack(fill="x", padx=8)
        def do_login():
            u = e_user.get().strip(); p = e_pw.get().strip()
            if not u or not p:
                logger.warning("Intento de login con campos vacíos.")
                messagebox.showerror("Error", "Por favor completa todos los campos."); return
            rec = self.auth.authenticate(u, p)
            if not rec:
                logger.warning("Inicio de sesión fallido para %s", u)
                messagebox.showerror("Error", "Usuario o contraseña incorrectos."); return
            logger.info("Usuario %s ha iniciado sesión en la UI.", rec.username)
            messagebox.showinfo("Bienvenido", f"Hola {rec.username} (rol: {rec.role})")
            win.destroy(); self.current_cart = []; self.open_role_dashboard(rec)
        tk.Button(win, text="Entrar", width=18, command=do_login).pack(pady=12)

    # Dashboards
    def open_role_dashboard(self, user_rec):
        logger.info("Abriendo dashboard para %s (rol=%s)", user_rec.username, user_rec.role)
        for w in self.root.winfo_children(): w.destroy()
        header = tk.Frame(self.root); header.pack(fill="x", pady=8)
        tk.Label(header, text=f"Panel - {user_rec.username} ({user_rec.role})", font=("Helvetica", 16, "bold")).pack(side="left", padx=12)
        tk.Button(header, text="Cerrar sesión", command=self.do_logout).pack(side="right", padx=12)
        body = tk.Frame(self.root); body.pack(pady=12)

        if user_rec.role == "comprador":
            tk.Button(body, text="Buscar vehículos", width=22, command=self.screen_browse_vehicles).grid(row=0, column=0, padx=6, pady=6)
            tk.Button(body, text="Buscar repuestos/seguros", width=22, command=self.screen_browse_services).grid(row=0, column=1, padx=6, pady=6)
            tk.Button(body, text="Ver carrito", width=22, command=self.screen_view_cart).grid(row=1, column=0, padx=6, pady=6)
            tk.Button(body, text="Ver mis facturas", width=22, command=self.screen_view_my_invoices).grid(row=1, column=1, padx=6, pady=6)

        if user_rec.role == "concesionario":
            tk.Button(body, text="Listar vehículos", width=22, command=self.screen_browse_vehicles).grid(row=0, column=0, padx=6, pady=6)
            tk.Button(body, text="Agregar vehículo", width=22, command=self.screen_create_vehicle_dealer).grid(row=0, column=1, padx=6, pady=6)
            tk.Button(body, text="Agregar repuesto", width=22, command=self.screen_create_repuesto_dealer).grid(row=1, column=0, padx=6, pady=6)
            tk.Button(body, text="Ver facturas", width=22, command=self.screen_view_my_invoices).grid(row=1, column=1, padx=6, pady=6)

        if user_rec.role == "administrador":
            tk.Button(body, text="Ver reportes / facturas", width=22, command=self.screen_view_reports).grid(row=0, column=0, padx=6, pady=6)
            tk.Button(body, text="Ver usuarios (sin eliminar)", width=22, command=self.screen_view_users).grid(row=0, column=1, padx=6, pady=6)

        if user_rec.role == "superadmin":
            tk.Button(body, text="Gestionar Usuarios", width=22, command=self.screen_manage_users_superadmin).grid(row=0, column=0, padx=6, pady=6)
            tk.Button(body, text="Gestionar Vehículos", width=22, command=self.screen_manage_vehicles).grid(row=0, column=1, padx=6, pady=6)
            tk.Button(body, text="Gestionar Servicios", width=22, command=self.screen_manage_services).grid(row=1, column=0, padx=6, pady=6)
            tk.Button(body, text="Reportes / Facturas", width=22, command=self.screen_view_reports).grid(row=1, column=1, padx=6, pady=6)

        tk.Button(self.root, text="Volver al inicio", command=self.build_welcome).pack(pady=10)

    # Catalogs / Services
    # -------------------- Vehicle Catalog --------------------
    def screen_browse_vehicles(self):
        win = tk.Toplevel(self.root)
        win.title("Catálogo de vehículos")
        win.geometry("760x480")

        top = tk.Frame(win)
        top.pack(fill="x", pady=6)
        tk.Label(top, text="Filtrar por marca (vacío = todos):").pack(side="left", padx=8)
        e = tk.Entry(top)
        e.pack(side="left", padx=8)

        listbox = tk.Listbox(win, width=110, height=20)
        listbox.pack(pady=6, padx=8)

        def load(filter_text=""):
            listbox.delete(0, tk.END)
            vehicles = self.catalog_service.list_vehicles()
            for v in vehicles:
                if not filter_text or filter_text.lower() in v.marca.lower():
                    listbox.insert(tk.END, f"{v.id} | {v.marca} {v.modelo} - ${v.precio} - {v.descripcion}")

        def add_to_cart():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecciona un vehículo")
                return
            idx = sel[0]
            filt = e.get().strip()
            all_vehicles = self.catalog_service.list_vehicles()
            visible = [v for v in all_vehicles if not filt or filt.lower() in v.marca.lower()]
            chosen = visible[idx].clone()
            self.current_cart.append(LineItem(chosen, 1))
            messagebox.showinfo("Carrito", f"Añadido: {chosen.marca} {chosen.modelo}")

        btns = tk.Frame(win)
        btns.pack(pady=6)
        tk.Button(btns, text="Filtrar", command=lambda: load(e.get().strip())).pack(side="left", padx=6)
        tk.Button(btns, text="Añadir al carrito", command=add_to_cart).pack(side="left", padx=6)

        load()
    
     # -------------------- Services (Repuestos / Seguros) --------------------
    def screen_browse_services(self):
        win = tk.Toplevel(self.root)
        win.title("Repuestos y Seguros")
        win.geometry("760x480")

        lb = tk.Listbox(win, width=110, height=20)
        lb.pack(padx=8, pady=6)

        def load():
            lb.delete(0, tk.END)
            for s in self.catalog_service.list_services():
                if hasattr(s, "nombre"):
                    lb.insert(tk.END, f"Repuesto | {s.id} | {s.nombre} | ${s.precio} | Stock: {s.stock}")
                elif hasattr(s, "tipo"):
                    lb.insert(tk.END, f"Seguro  | {s.id} | {s.tipo} | ${s.precio} | Vigencia: {s.vigencia_meses} meses")
                else:
                    lb.insert(tk.END, f"Servicio | {s.id} | {getattr(s,'nombre',str(s))}")

        def add_selected():
            sel = lb.curselection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecciona un servicio.")
                return
            all_services = self.catalog_service.list_services()
            item = all_services[sel[0]]
            if hasattr(item, "stock"):
                qty = simpledialog.askinteger(
                    "Cantidad",
                    f"Stock disponible: {item.stock}\nCantidad a comprar:",
                    minvalue=1,
                    maxvalue=item.stock,
                )
                if not qty:
                    return
                self.current_cart.append(LineItem(item, qty))
                messagebox.showinfo("Carrito", f"Añadido repuesto {item.nombre} x{qty}")
            else:
                self.current_cart.append(LineItem(item, 1))
                if hasattr(item, "tipo"):
                    name = item.tipo
                else:
                    name = getattr(item, "nombre", "servicio")
                messagebox.showinfo("Carrito", f"Añadido servicio/seguro {name}")

        btns = tk.Frame(win)
        btns.pack(pady=6)
        tk.Button(btns, text="Actualizar lista", command=load).pack(side="left", padx=6)
        tk.Button(btns, text="Añadir seleccionado al carrito", command=add_selected).pack(side="left", padx=6)

        load()

    # Cart / Checkout
    def screen_view_cart(self):
        logger.info("Abriendo carrito de compras.")
        win = tk.Toplevel(self.root); win.title("Carrito"); win.geometry("620x480")
        tk.Label(win, text="Contenido del carrito:").pack(anchor="w", padx=8, pady=(8,0))
        txt = tk.Text(win, width=80, height=18); txt.pack(padx=8, pady=6)
        if not self.current_cart:
            txt.insert(tk.END, "Carrito vacío.\n")
        else:
            subtotal = 0
            for i, li in enumerate(self.current_cart, start=1):
                name = getattr(li.item, "modelo", getattr(li.item, "nombre", "item"))
                txt.insert(tk.END, f"{i}. {name} x{li.quantity} - Unit: ${li.item.get_price():.2f} - Total: ${li.line_total():.2f}\n")
                subtotal += li.line_total()
            txt.insert(tk.END, f"\nSubtotal: ${subtotal:.2f}\n")
        def vaciar():
            logger.info("Carrito vaciado por el usuario.")
            self.current_cart.clear(); messagebox.showinfo("Carrito", "Carrito vaciado."); win.destroy()
        def confirmar_compra():
            rec = self.auth.current_user
            if not rec:
                logger.warning("Intento de compra sin autenticación.")
                messagebox.showerror("Error", "Usuario no autenticado."); return
            if not self.current_cart:
                logger.warning("Intento de compra con carrito vacío.")
                messagebox.showwarning("Carrito", "Carrito vacío."); return
            resumen = ""
            for i, li in enumerate(self.current_cart, start=1):
                name = getattr(li.item, "modelo", getattr(li.item, "nombre", str(li.item)))
                resumen += f"{i}. {name} x{li.quantity} -> ${li.line_total():.2f}\n"
            subtotal = sum(li.line_total() for li in self.current_cart)
            impuestos = round(subtotal * 0.19, 2); total = round(subtotal + impuestos, 2)
            resumen += f"\nSubtotal: ${subtotal:.2f}\nImpuestos: ${impuestos:.2f}\nTotal: ${total:.2f}\n\n¿Confirmar compra?"
            if not messagebox.askyesno("Confirmar compra", resumen): 
                logger.info("Compra cancelada por el usuario.")
                return
            fid = str(uuid.uuid4())
            factura = Factura(id=fid, cliente_username=rec.username, items=list(self.current_cart), fecha=datetime.datetime.now())
            factura.calculate_totals(); self.reports.log_invoice(factura)
            for li in factura.items:
                if hasattr(li.item, "stock"):
                    orig = next((r for r in self.catalog["services"] if getattr(r, "id", None) == getattr(li.item, "id", None)), None)
                    if orig: orig.stock = max(0, orig.stock - li.quantity)
            logger.info("Factura generada para %s por $%.2f (ID=%s)", rec.username, factura.total, factura.id)
            messagebox.showinfo("Compra confirmada", f"Factura creada: {factura.id}\nTotal: ${factura.total:.2f}")
            self.current_cart.clear(); win.destroy()
        btns = tk.Frame(win); btns.pack(pady=8)
        tk.Button(btns, text="Vaciar carrito", command=vaciar).pack(side="left", padx=6)
        tk.Button(btns, text="Confirmar compra", command=confirmar_compra).pack(side="left", padx=6)
        tk.Button(btns, text="Cerrar", command=win.destroy).pack(side="left", padx=6)

    # Users / Reports
    def screen_view_my_invoices(self):
        rec = self.auth.current_user
        if not rec: return
        logger.info("Mostrando facturas de usuario: %s", rec.username)
        invs = self.reports.invoices_for_user(rec.username)
        win = tk.Toplevel(self.root); win.title("Mis facturas"); win.geometry("740x520")
        txt = tk.Text(win, width=100, height=26); txt.pack(padx=8, pady=6)
        if not invs:
            txt.insert(tk.END, "No hay facturas para este usuario.\n")
        else:
            for f in invs:
                txt.insert(tk.END, f"ID: {f.id}\nFecha: {f.fecha}\nSubtotal: ${f.subtotal}\nImpuestos: ${f.impuestos}\nTotal: ${f.total}\nMatrícula: {f.matricula}\nItems:\n")
                for li in f.items:
                    name = getattr(li.item, "modelo", getattr(li.item, "nombre", "item"))
                    txt.insert(tk.END, f" - {name} x{li.quantity} -> ${li.line_total():.2f}\n")
                txt.insert(tk.END, "\n---\n")

    def screen_view_reports(self):
        rec = self.auth.current_user
        if not rec or rec.role not in ("administrador", "superadmin"):
            logger.warning("Acceso denegado a Reportes: usuario=%s rol=%s", getattr(rec, 'username', 'N/A'), getattr(rec, 'role', 'N/A'))
            messagebox.showerror("Acceso denegado", "Solo administradores o superadmin."); return
        logger.info("Abriendo pantalla de reportes.")
        win = tk.Toplevel(self.root); win.title("Reportes / Facturas"); win.geometry("860x520")
        lb = tk.Listbox(win, width=120, height=20); lb.pack(padx=8, pady=6)
        def load():
            lb.delete(0, tk.END)
            for f in self.reports.invoices:
                lb.insert(tk.END, f"{f.id} | Cliente: {f.cliente_username} | Total: ${f.total:.2f} | Fecha: {f.fecha} | Matricula: {f.matricula}")
            logger.debug("Listado de facturas refrescado.")
        def view_selected():
            sel = lb.curselection()
            if not sel: 
                logger.warning("Ver factura sin selección.")
                messagebox.showwarning("Aviso", "Selecciona una factura."); return
            invoice = self.reports.invoices[sel[0]]
            detail = (f"ID: {invoice.id}\nCliente: {invoice.cliente_username}\nFecha: {invoice.fecha}\n"
                      f"Subtotal: ${invoice.subtotal}\nImpuestos: ${invoice.impuestos}\nTotal: ${invoice.total}\nMatrícula: {invoice.matricula}\n\nItems:\n")
            for li in invoice.items:
                name = getattr(li.item, "modelo", getattr(li.item, "nombre", "item"))
                detail += f"- {name} x{li.quantity} -> ${li.line_total():.2f}\n"
            messagebox.showinfo("Detalle Factura", detail)
        def delete_selected():
            sel = lb.curselection()
            if not sel:
                logger.warning("Eliminar factura sin selección.")
                messagebox.showwarning("Aviso", "Selecciona una factura."); return
            invoice = self.reports.invoices[sel[0]]
            if messagebox.askyesno("Confirmar", f"Eliminar factura {invoice.id}?"):
                self.reports.invoices.remove(invoice)
                logger.info("Factura eliminada: %s", invoice.id)
                messagebox.showinfo("Eliminado", "Factura eliminada."); load()
        btns = tk.Frame(win); btns.pack(pady=6)
        tk.Button(btns, text="Ver factura", command=view_selected).pack(side="left", padx=6)
        tk.Button(btns, text="Eliminar factura", command=delete_selected).pack(side="left", padx=6)
        tk.Button(btns, text="Cerrar", command=win.destroy).pack(side="left", padx=6)
        load()

    def screen_view_users(self):
        rec = self.auth.current_user
        if not rec or rec.role not in ("administrador", "superadmin"):
            logger.warning("Acceso denegado a Usuarios: usuario=%s rol=%s", getattr(rec, 'username', 'N/A'), getattr(rec, 'role', 'N/A'))
            messagebox.showerror("Acceso denegado", "Solo administradores o superadmin."); return
        logger.info("Mostrando usuarios para lectura.")
        users = self.users.list_users()
        win = tk.Toplevel(self.root); win.title("Usuarios"); win.geometry("520x420")
        lb = tk.Listbox(win, width=70, height=20); lb.pack(padx=8, pady=6)
        for u in users: lb.insert(tk.END, f"{u.username} — {u.role}")

    def screen_manage_users_superadmin(self):
        rec = self.auth.current_user
        if not rec or rec.role != "superadmin":
            logger.warning("Acceso denegado a Gestión de Usuarios (SuperAdmin).")
            messagebox.showerror("Acceso denegado", "Solo SuperAdmin puede gestionar usuarios."); return
        logger.info("Abriendo Gestión de Usuarios (SuperAdmin).")
        win = tk.Toplevel(self.root); win.title("Gestión de Usuarios (SuperAdmin)"); win.geometry("700x520")
        lb = tk.Listbox(win, width=80, height=18); lb.pack(padx=8, pady=8)
        def refresh():
            lb.delete(0, tk.END)
            for u in self.users.list_users():
                lb.insert(tk.END, f"{u.username} — {u.role}")
            logger.debug("Lista de usuarios refrescada (superadmin).")
        def create_admin():
            u = simpledialog.askstring("Nuevo Admin", "Nombre de usuario:"); 
            if not u: return
            p = simpledialog.askstring("Contraseña", "Contraseña (mínimo 6, 1 mayúscula y 1 símbolo):", show="*"); 
            if not p: return
            ok = self.users.create_user_by_admin(u, p, "administrador")
            if ok: 
                logger.info("Administrador creado (UI): %s", u)
                messagebox.showinfo("OK", "Administrador creado correctamente."); refresh()
            else:
                logger.error("Fallo creando administrador (UI) para %s", u)
                messagebox.showerror("Error", "No se pudo crear administrador (usuario existente o validación fallida).")
        def edit_user():
            sel = lb.curselection()
            if not sel: 
                logger.warning("Editar usuario sin selección.")
                messagebox.showwarning("Aviso", "Selecciona un usuario."); return
            user = self.users.list_users()[sel[0]]
            new_role = simpledialog.askstring("Editar rol", f"Rol actual: {user.role}\nNuevo rol (comprador/concesionario/administrador/superadmin):")
            new_pass = simpledialog.askstring("Cambiar contraseña", "Nueva contraseña (opcional):", show="*")
            if new_role == "": new_role = None
            if user.username == "superadmin" and new_role and new_role != "superadmin":
                logger.warning("Intento de despromover superadmin desde UI.")
                messagebox.showerror("Error", "No puedes despromover al superadmin desde aquí."); return
            ok = self.users.update_user(user.username, new_role, new_pass)
            if ok: 
                logger.info("Usuario actualizado (UI): %s", user.username)
                messagebox.showinfo("Actualizado", f"Usuario {user.username} actualizado."); refresh()
            else:
                logger.error("Fallo al actualizar usuario (UI): %s", user.username)
                messagebox.showerror("Error", "No se pudo actualizar usuario.")
        def delete_user():
            sel = lb.curselection()
            if not sel: 
                logger.warning("Eliminar usuario sin selección.")
                messagebox.showwarning("Aviso", "Selecciona un usuario."); return
            user = self.users.list_users()[sel[0]]
            if user.username == "superadmin":
                logger.warning("Intento de eliminar superadmin desde UI.")
                messagebox.showerror("Prohibido", "No puedes eliminar al SuperAdmin."); return
            if messagebox.askyesno("Confirmar", f"¿Eliminar usuario {user.username}?"):
                ok = self.users.delete_user(user.username)
                if ok: 
                    logger.info("Usuario eliminado (UI): %s", user.username)
                    messagebox.showinfo("Eliminado", "Usuario eliminado."); refresh()
                else:
                    logger.error("No se pudo eliminar usuario (UI): %s", user.username)
                    messagebox.showerror("Error", "No se pudo eliminar usuario.")
        btns = tk.Frame(win); btns.pack(pady=6)
        tk.Button(btns, text="Crear administrador", width=18, command=create_admin).grid(row=0, column=0, padx=6, pady=6)
        tk.Button(btns, text="Editar usuario", width=18, command=edit_user).grid(row=0, column=1, padx=6, pady=6)
        tk.Button(btns, text="Eliminar usuario", width=18, command=delete_user).grid(row=0, column=2, padx=6, pady=6)
        tk.Button(btns, text="Cerrar", width=12, command=win.destroy).grid(row=0, column=3, padx=6, pady=6)
        refresh()

    def screen_manage_vehicles(self):
        rec = self.auth.current_user
        if not rec or rec.role != "superadmin":
            logger.warning("Acceso denegado a Gestión de Vehículos.")
            messagebox.showerror("Acceso denegado", "Solo SuperAdmin puede gestionar vehículos."); return
        logger.info("Abriendo Gestión de Vehículos.")
        win = tk.Toplevel(self.root); win.title("Gestión de Vehículos (SuperAdmin)"); win.geometry("900x520")
        lb = tk.Listbox(win, width=120, height=18); lb.pack(padx=8, pady=8)
        def refresh():
            lb.delete(0, tk.END)
            for v in self.catalog_service.list_vehicles():
                lb.insert(tk.END, f"{v.id} | {v.marca} {v.modelo} | ${v.precio} | Garantía: {v.garantia_meses} meses | Mantenimiento: {v.mantenimiento_tipo}")
            logger.debug("Lista de vehículos refrescada.")
        def create_vehicle():
            try:
                vid = simpledialog.askstring("ID", "ID vehículo (ej: V004):")
                marca = simpledialog.askstring("Marca", "Marca:")
                modelo = simpledialog.askstring("Modelo", "Modelo:")
                precio = simpledialog.askfloat("Precio", "Precio:")
                garantia = simpledialog.askinteger("Garantía (meses)", "Meses de garantía:")
                mantenimiento = simpledialog.askstring("Mantenimiento", "Tipo mantenimiento:")
                descripcion = simpledialog.askstring("Descripción", "Descripción (opcional):")
                if not (vid and marca and modelo and precio is not None and garantia is not None and mantenimiento):
                    logger.warning("Intento de crear vehículo con campos incompletos.")
                    messagebox.showerror("Error", "Faltan campos obligatorios."); return
                v = VehicleFactory.create_vehicle(
                vid, marca, modelo, float(precio), int(garantia), mantenimiento, descripcion or "")
                self.catalog_service.add_vehicle(v); logger.info("Vehículo creado: %s %s", marca, modelo); messagebox.showinfo("OK", "Vehículo creado."); refresh()
            except Exception as e:
                logger.exception("Error creando vehículo: %s", e)
                messagebox.showerror("Error", "No se pudo crear el vehículo.")
        def edit_vehicle():
            sel = lb.curselection()
            if not sel: 
                logger.warning("Editar vehículo sin selección.")
                messagebox.showwarning("Aviso", "Selecciona un vehículo."); return
            v = self.catalog_service.list_vehicles()[sel[0]]
            try:
                marca = simpledialog.askstring("Marca", "Marca:", initialvalue=v.marca)
                modelo = simpledialog.askstring("Modelo", "Modelo:", initialvalue=v.modelo)
                precio = simpledialog.askfloat("Precio", "Precio:", initialvalue=v.precio)
                garantia = simpledialog.askinteger("Garantía (meses)", "Garantía:", initialvalue=v.garantia_meses)
                mantenimiento = simpledialog.askstring("Mantenimiento", "Mantenimiento:", initialvalue=v.mantenimiento_tipo)
                descripcion = simpledialog.askstring("Descripción", "Descripción:", initialvalue=v.descripcion)
                if marca: v.marca = marca
                if modelo: v.modelo = modelo
                if precio is not None: v.precio = float(precio)
                if garantia is not None: v.garantia_meses = int(garantia)
                if mantenimiento: v.mantenimiento_tipo = mantenimiento
                if descripcion is not None: v.descripcion = descripcion
                logger.info("Vehículo actualizado: %s %s", v.marca, v.modelo)
                messagebox.showinfo("OK", "Vehículo actualizado."); refresh()
            except Exception as e:
                logger.exception("Error actualizando vehículo: %s", e)
                messagebox.showerror("Error", "No se pudo actualizar el vehículo.")
        def delete_vehicle():
            sel = lb.curselection()
            if not sel: 
                logger.warning("Eliminar vehículo sin selección.")
                messagebox.showwarning("Aviso", "Selecciona un vehículo."); return
            v = self.catalog_service.list_vehicles()[sel[0]]
            if messagebox.askyesno("Confirmar", f"Eliminar vehículo {v.marca} {v.modelo}?"):
                self.catalog_service.remove_vehicle(v)
                logger.info("Vehículo eliminado: %s %s", v.marca, v.modelo)
                messagebox.showinfo("Eliminado", "Vehículo eliminado."); refresh()
        btns = tk.Frame(win); btns.pack(pady=6)
        tk.Button(btns, text="Crear", width=14, command=create_vehicle).grid(row=0, column=0, padx=6)
        tk.Button(btns, text="Editar", width=14, command=edit_vehicle).grid(row=0, column=1, padx=6)
        tk.Button(btns, text="Eliminar", width=14, command=delete_vehicle).grid(row=0, column=2, padx=6)
        tk.Button(btns, text="Cerrar", width=14, command=win.destroy).grid(row=0, column=3, padx=6)
        refresh()

    def screen_manage_services(self):
        rec = self.auth.current_user
        if not rec or rec.role != "superadmin":
            logger.warning("Acceso denegado a Gestión de Servicios.")
            messagebox.showerror("Acceso denegado", "Solo SuperAdmin puede gestionar servicios."); return
        logger.info("Abriendo Gestión de Servicios.")
        win = tk.Toplevel(self.root); win.title("Gestión de Servicios (SuperAdmin)"); win.geometry("900x520")
        lb = tk.Listbox(win, width=120, height=18); lb.pack(padx=8, pady=8)
        def refresh():
            lb.delete(0, tk.END)
            for s in self.catalog_service.list_services():
                if hasattr(s, "nombre"):
                    lb.insert(tk.END, f"Repuesto | {s.id} | {s.nombre} | ${s.precio} | Stock: {s.stock}")
                elif hasattr(s, "tipo"):
                    lb.insert(tk.END, f"Seguro  | {s.id} | {s.tipo} | ${s.precio} | Vigencia (meses): {s.vigencia_meses}")
                else:
                    lb.insert(tk.END, f"Servicio | {s.id} | {getattr(s,'nombre',str(s))}")
            logger.debug("Lista de servicios refrescada (gestión).")
        def create_repuesto():
            try:
                nombre = simpledialog.askstring("Nombre", "Nombre del repuesto:")
                precio = simpledialog.askfloat("Precio", "Precio:")
                stock = simpledialog.askinteger("Stock", "Stock:")
                if not (nombre and precio is not None and stock is not None):
                    logger.warning("Intento de crear repuesto con campos incompletos.")
                    messagebox.showerror("Error", "Faltan campos obligatorios."); return
                r = ServiceFactory.create_service("repuesto", nombre=nombre, precio=float(precio), stock=int(stock))
                self.catalog_service.add_service(r); logger.info("Repuesto creado: %s", nombre); messagebox.showinfo("OK", "Repuesto creado."); refresh()
            except Exception as e:
                logger.exception("Error creando repuesto: %s", e)
                messagebox.showerror("Error", "No se pudo crear el repuesto.")
        def create_seguro():
            try:
                tipo = simpledialog.askstring("Tipo", "Tipo de seguro (ej: Todo Riesgo):")
                precio = simpledialog.askfloat("Precio", "Precio:")
                vigencia = simpledialog.askinteger("Vigencia (meses)", "Vigencia:")
                if not (tipo and precio is not None and vigencia is not None):
                    logger.warning("Intento de crear seguro con campos incompletos.")
                    messagebox.showerror("Error", "Faltan campos obligatorios."); return
                s = ServiceFactory.create_service("seguro", tipo=tipo, precio=float(precio), vigencia_meses=int(vigencia))
                  self.catalog_service.add_service(s); logger.info("Seguro creado: %s", tipo); messagebox.showinfo("OK", "Seguro creado."); refresh()
            except Exception as e:
                logger.exception("Error creando seguro: %s", e)
                messagebox.showerror("Error", "No se pudo crear el seguro.")
        def edit_service():
            sel = lb.curselection()
            if not sel:
                logger.warning("Editar servicio sin selección.")
                messagebox.showwarning("Aviso", "Selecciona un servicio."); return
            s = self.catalog_service.list_services()[sel[0]]
            try:
                if hasattr(s, "nombre"):
                    nombre = simpledialog.askstring("Nombre", "Nombre:", initialvalue=s.nombre)
                    precio = simpledialog.askfloat("Precio", "Precio:", initialvalue=s.precio)
                    stock = simpledialog.askinteger("Stock", "Stock:", initialvalue=s.stock)
                    if nombre: s.nombre = nombre
                    if precio is not None: s.precio = float(precio)
                    if stock is not None: s.stock = int(stock)
                elif hasattr(s, "tipo"):
                    tipo = simpledialog.askstring("Tipo", "Tipo:", initialvalue=s.tipo)
                    precio = simpledialog.askfloat("Precio", "Precio:", initialvalue=s.precio)
                    vigencia = simpledialog.askinteger("Vigencia", "Vigencia (meses):", initialvalue=s.vigencia_meses)
                    if tipo: s.tipo = tipo
                    if precio is not None: s.precio = float(precio)
                    if vigencia is not None: s.vigencia_meses = int(vigencia)
                else:
                    logger.info("Tipo de servicio desconocido; no editable en este modo.")
                    messagebox.showinfo("Info", "Tipo desconocido, no editable en este modo.")
                logger.info("Servicio actualizado.")
                messagebox.showinfo("OK", "Servicio actualizado."); refresh()
            except Exception as e:
                logger.exception("Error actualizando servicio: %s", e)
                messagebox.showerror("Error", "No se pudo actualizar el servicio.")
        def delete_service():
            sel = lb.curselection()
            if not sel:
                logger.warning("Eliminar servicio sin selección.")
                messagebox.showwarning("Aviso", "Selecciona un servicio."); return
            s = self.catalog_service.list_services()[sel[0]]
            if messagebox.askyesno("Confirmar", "Eliminar servicio seleccionado?"):
                self.catalog_service.remove_service(s)
                logger.info("Servicio eliminado: %s", getattr(s, "nombre", getattr(s, "tipo", "N/A")))
                messagebox.showinfo("Eliminado", "Servicio eliminado."); refresh()
        btns = tk.Frame(win); btns.pack(pady=6)
        tk.Button(btns, text="Crear Repuesto", width=14, command=create_repuesto).grid(row=0, column=0, padx=6)
        tk.Button(btns, text="Crear Seguro", width=14, command=create_seguro).grid(row=0, column=1, padx=6)
        tk.Button(btns, text="Editar", width=14, command=edit_service).grid(row=0, column=2, padx=6)
        tk.Button(btns, text="Eliminar", width=14, command=delete_service).grid(row=0, column=3, padx=6)
        tk.Button(btns, text="Cerrar", width=12, command=win.destroy).grid(row=0, column=4, padx=6)
        refresh()

    def do_logout(self):
        self.auth.logout(); 
        logger.info("Logout ejecutado desde UI.")
        messagebox.showinfo("Sesión", "Has cerrado sesión."); self.build_welcome()
