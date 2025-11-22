# core/services/catalog_service.py
from typing import List, Any

from core.models import Vehiculo, Repuesto, Seguro


class CatalogService:
    """
    Servicio de catálogo.
    Es la ÚNICA capa que debe modificar el catálogo en memoria.

    La UI solo debería llamar a estos métodos para:
    - listar vehículos/servicios
    - agregar
    - eliminar
    - (si hace falta, podríamos añadir más adelante métodos de edición)
    """

    def __init__(self, catalog: dict):
        # Se espera un dict con claves "vehicles" y "services"
        self._catalog = catalog
        self._catalog.setdefault("vehicles", [])
        self._catalog.setdefault("services", [])

    # ---- acceso interno ----
    @property
    def vehicles(self) -> List[Vehiculo]:
        return self._catalog["vehicles"]

    @property
    def services(self) -> List[Any]:
        # puede ser Repuesto o Seguro
        return self._catalog["services"]

    # ---- operaciones de lectura ----
    def list_vehicles(self) -> List[Vehiculo]:
        # devolvemos copia para evitar modificaciones directas
        return list(self.vehicles)

    def list_services(self) -> List[Any]:
        return list(self.services)

    # ---- operaciones de escritura ----
    def add_vehicle(self, vehicle: Vehiculo) -> None:
        self.vehicles.append(vehicle)

    def remove_vehicle(self, vehicle: Vehiculo) -> None:
        if vehicle in self.vehicles:
            self.vehicles.remove(vehicle)

    def add_service(self, service_obj: Any) -> None:
        self.services.append(service_obj)

    def remove_service(self, service_obj: Any) -> None:
        if service_obj in self.services:
            self.services.remove(service_obj)
