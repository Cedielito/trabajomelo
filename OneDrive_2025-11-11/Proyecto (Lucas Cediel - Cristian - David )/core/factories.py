
from .models import Vehiculo, Repuesto, Seguro
import uuid

class VehicleFactory:
    @staticmethod
    def create_vehicle(id:str, marca:str, modelo:str, precio:float, garantia:int, mantenimiento:str, descripcion:str=""):
        return Vehiculo(id=id, marca=marca, modelo=modelo, precio=precio, garantia_meses=garantia, mantenimiento_tipo=mantenimiento, descripcion=descripcion)

class ServiceFactory:
    @staticmethod
    def create_service(kind: str, **kwargs):
        if kind == "seguro":
            return Seguro(id=str(uuid.uuid4()), tipo=kwargs.get("tipo","Básico"), precio=float(kwargs.get("precio",100.0)), vigencia_meses=int(kwargs.get("vigencia_meses",12)))
        elif kind == "repuesto":
            return Repuesto(id=str(uuid.uuid4()), nombre=kwargs.get("nombre","Repuesto"), precio=float(kwargs.get("precio",10.0)), stock=int(kwargs.get("stock",10)))
        else:
            raise ValueError("Servicio desconocido")
