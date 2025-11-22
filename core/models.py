# core/models.py
from dataclasses import dataclass
from typing import List, Any
import copy
import datetime


@dataclass
class Vehiculo:
    id: str
    marca: str
    modelo: str
    precio: float
    garantia_meses: int
    mantenimiento_tipo: str
    descripcion: str = ""

    def get_price(self) -> float:
        return self.precio

    def clone(self):
        return copy.deepcopy(self)


@dataclass
class Repuesto:
    id: str
    nombre: str
    precio: float
    stock: int

    def get_price(self) -> float:
        return self.precio


@dataclass
class Seguro:
    id: str
    tipo: str
    precio: float
    vigencia_meses: int

    def get_price(self) -> float:
        return self.precio


@dataclass
class LineItem:
    item: Any
    quantity: int = 1

    def line_total(self) -> float:
        return self.item.get_price() * self.quantity


@dataclass
class Factura:
    id: str
    cliente_username: str
    items: List[LineItem]
    fecha: datetime.datetime
    subtotal: float = 0.0
    impuestos: float = 0.0
    total: float = 0.0
    matricula: str = ""

    def calculate_totals(self, tax_rate: float = 0.19):
        self.subtotal = sum(li.line_total() for li in self.items)
        self.impuestos = round(self.subtotal * tax_rate, 2)
        self.total = round(self.subtotal + self.impuestos, 2)
        return self.total
