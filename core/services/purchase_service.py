# core/services/purchase_service.py
import datetime
import uuid
from typing import List

from core.models import LineItem, Factura
from core.report_manager import ReportManager
from core.services.catalog_service import CatalogService


class PurchaseService:
    """
    Servicio que encapsula la creación de facturas:
    - Crea Factura
    - Calcula totales
    - Registra en ReportManager
    - Ajusta stock de repuestos
    """

    def __init__(self, report_manager: ReportManager, catalog_service: CatalogService):
        self._reports = report_manager
        self._catalog = catalog_service

    def create_invoice(
        self,
        cart_items: List[LineItem],
        cliente_username: str,
        matricula: str = "",
    ) -> Factura:
        fid = str(uuid.uuid4())
        factura = Factura(
            id=fid,
            cliente_username=cliente_username,
            items=list(cart_items),
            fecha=datetime.datetime.now(),
            matricula=matricula.upper() if matricula else "",
        )
        factura.calculate_totals()

        # Registrar en reportes
        self._reports.log_invoice(factura)

        # Ajustar stock de repuestos
        for li in factura.items:
            item = li.item
            sid = getattr(item, "id", None)
            if sid is not None and hasattr(item, "stock"):
                self._catalog.decrement_repuesto_stock(sid, li.quantity)

        return factura
