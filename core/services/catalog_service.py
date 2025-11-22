# core/services/catalog_service.py
from typing import Dict, List, Any, Optional

from core.models import Vehiculo


class CatalogService:
    """
    Única fuente para mutar el catálogo en memoria.
    Maneja vehículos y servicios (repuestos/seguros).
    """

    def __init__(self):
        self._vehicles: Dict[str, Vehiculo] = {}
        self._services: Dict[str, Any] = {}

    # ---------- Vehículos ----------
    def list_vehicles(self) -> List[Vehiculo]:
        return list(self._vehicles.values())

    def get_vehicle(self, vehicle_id: str) -> Optional[Vehiculo]:
        return self._vehicles.get(vehicle_id)

    def add_vehicle(self, vehicle: Vehiculo) -> None:
        self._vehicles[vehicle.id] = vehicle

    def edit_vehicle(self, vehicle_id: str, changes: Dict[str, Any]) -> bool:
        v = self._vehicles.get(vehicle_id)
        if not v:
            return False
        for field, value in changes.items():
            if hasattr(v, field) and value is not None:
                setattr(v, field, value)
        return True

    def delete_vehicle(self, vehicle_id: str) -> bool:
        if vehicle_id in self._vehicles:
            del self._vehicles[vehicle_id]
            return True
        return False

    # ---------- Servicios ----------
    def list_services(self) -> List[Any]:
        return list(self._services.values())

    def add_service(self, service: Any) -> None:
        sid = getattr(service, "id", None)
        if sid is None:
            raise ValueError("Servicio sin id")
        self._services[sid] = service

    def get_service(self, service_id: str) -> Optional[Any]:
        return self._services.get(service_id)

    def delete_service(self, service_id: str) -> bool:
        if service_id in self._services:
            del self._services[service_id]
            return True
        return False

    def decrement_repuesto_stock(self, service_id: str, quantity: int) -> None:
        s = self._services.get(service_id)
        if s is not None and hasattr(s, "stock"):
            s.stock = max(0, s.stock - quantity)
