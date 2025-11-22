from core.models import LineItem
from core.factories import VehicleFactory, ServiceFactory

def test_purchase_invoice_creation(purchase_service, report_manager, catalog_service):

    # Crear items y agregarlos al catálogo
    v = VehicleFactory.create_vehicle("V001", "Toyota", "Corolla", 20000, 24, "gratis")
    catalog_service.add_vehicle(v)

    # Carrito
    li = LineItem(v, 1)

    factura = purchase_service.create_invoice(
        [li],
        cliente_username="juanito"
    )

    assert factura.total > 0
    assert factura.cliente_username == "juanito"
    assert len(report_manager.invoices) == 1

