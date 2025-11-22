# core/report_manager.py
from typing import List

from core.models import Factura


class ReportManager:
    """Almacena facturas en memoria y permite consultas agregadas."""

    def __init__(self):
        self.invoices: List[Factura] = []

    def log_invoice(self, invoice: Factura) -> None:
        self.invoices.append(invoice)

    def total_sales(self) -> float:
        return sum(inv.total for inv in self.invoices)

    def invoices_for_user(self, username: str):
        return [inv for inv in self.invoices if inv.cliente_username == username]
