
from .models import Factura
from typing import List
from .log_config import logger

class ReportManager:
    def __init__(self):
        self.invoices: List[Factura] = []
        logger.info("ReportManager inicializado.")

    def log_invoice(self, invoice: Factura):
        self.invoices.append(invoice)
        logger.info("Factura registrada: %s (cliente=%s, total=%.2f)", invoice.id, invoice.cliente_username, invoice.total)

    def total_sales(self):
        total = sum(inv.total for inv in self.invoices)
        logger.debug("Total de ventas calculado: %.2f", total)
        return total

    def invoices_for_user(self, username: str):
        invs = [inv for inv in self.invoices if inv.cliente_username == username]
        logger.info("Facturas consultadas para %s: %d", username, len(invs))
        return invs
