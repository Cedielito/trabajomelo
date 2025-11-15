
from .factories import VehicleFactory, ServiceFactory
from .log_config import logger

def seed_catalog(catalog: dict):
    logger.info("Sembrando catálogo inicial...")
    v1 = VehicleFactory.create_vehicle("V001", "Toyota", "Corolla 2024", 45000.0, 24, "gratis", "Sedán compacto")
    v2 = VehicleFactory.create_vehicle("V002", "Renault", "Kwid 2023", 12000.0, 12, "según uso", "Económico urbano")
    v3 = VehicleFactory.create_vehicle("V003", "Tesla", "Model 3", 60000.0, 36, "obligatorio", "Eléctrico")
    catalog["vehicles"].extend([v1, v2, v3])

    s1 = ServiceFactory.create_service("seguro", tipo="Todo Riesgo", precio=1200.0, vigencia_meses=12)
    r1 = ServiceFactory.create_service("repuesto", nombre="Filtro de aire", precio=45.0, stock=20)
    r2 = ServiceFactory.create_service("repuesto", nombre="Bujía", precio=15.0, stock=50)
    catalog["services"].extend([s1, r1, r2])

    logger.info("Catálogo cargado: %d vehículos, %d servicios.", len(catalog["vehicles"]), len(catalog["services"]))
