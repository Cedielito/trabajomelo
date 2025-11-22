# core/services/purchase_service.py
from typing import List, Any
import uuid
import datetime

from core.models import Factura
from core.report_manager import ReportManager


class PurchaseService:
    """
    Servicio responsable de:
    - crear facturas a partir del carrito
    - calcular totales (usando Factura.calculate_totals)
    - registrar la factura en ReportManager
    - actualizar stock de repuestos

    La UI NO debería crear Factura directamente ni manipular stock.
    """

    def __init__(self, report_manager: ReportManager):
        self._reports = report_manager

    def create_invoice_from_cart(
        self,
        cart_items: List[Any],
        cliente_username: str,
        matricula: str = "",
    ) -> Factura:
        """
        Crea la factura, calcula totales y la registra en ReportManager.
        """
        fid = str(uuid.uuid4())
        factura = Factura(
            id=fid,
            cliente_username=cliente_username,
            items=list(cart_items),  # copiamos lista
            fecha=datetime.datetime.now(),
            matricula=matricula,
        )
        factura.calculate_totals()
        self._reports.log_invoice(factura)
        return factura

    def decrease_stock_for_invoice(self, factura: Factura, services_catalog: List[Any]) -> None:
        """
        Reduce el stock de los repuestos en base a los items de la factura.
        """
        for li in factura.items:
            if hasattr(li.item, "stock"):
                # buscamos el repuesto original por id en la lista de servicios
                orig = next(
                    (
                        r
                        for r in services_catalog
                        if getattr(r, "id", None) == getattr(li.item, "id", None)
                    ),
                    None,
                )
                if orig is not None:
                    orig.stock = max(0, orig.stock - li.quantity)
