
---

###  Pegar contenido

```markdown


# CHANGELOG

# CHANGELOG

Este archivo documenta todos los cambios realizados en el proyecto según los requerimientos y entregables solicitados.



## v1.0.0 - 2025-11-14
- Se crea la estructura inicial del proyecto.
- Implementación del sistema de autenticación con SHA-256.
- Repositorio JSON y carga inicial de datos.

## v1.1.0 - 2025-11-15
- Separación completa por servicios (SOLID).
- Logging defensivo centralizado.
- Validaciones robustas para usuario, contraseña y matrícula.

## v1.2.0 - 2025-11-16
-(Tkinter Notebook).
- Servicios de catálogo, carrito y facturación completamente desacoplados.
- JsonAuthRepository con manejo atómico de archivo JSON.

## [1.3.0] - 2025-11-21
### Refactorización de autenticación (RF-01)
- Implementada interfaz `IAuthRepository` con tipado y métodos estándar.
- Implementado `JsonAuthRepository` como adaptador a repositorio JSON.
- Creado `LoginResult` como objeto de resultado para login.
- `AuthenticationService` ahora utiliza inyección de dependencias (DIP).
- Registro y administración de usuarios delegados a `RegistrationService` y `UserAdminService`.

## [1.4.0] - 2025-11-21
### Implementación de servicios principales (RF-02 y RF-03)
- Creado `CatalogService` para gestionar vehículos, repuestos y seguros.
- Eliminada la manipulación directa del catálogo desde la GUI.
- Creado `PurchaseService` para generar facturas de forma centralizada.
- GUI ahora usa exclusivamente `catalog_service` y `purchase_service`.
- Eliminado código duplicado en creación de facturas.

## [1.5.0] - 2025-11-22
### Tests unitarios añadidos (RF-05)
- Se creó carpeta `tests/` con las pruebas:
  - `test_auth.py` (login correcto, usuario inexistente, contraseña incorrecta)
  - `test_registration.py` (validación de username y password)
  - `test_validators.py` (validación de matrícula)
  - `test_purchase.py` (creación de factura y cálculo de totales)
- Configurado pytest para ejecución completa.
- Cobertura superior al 90% en los tests escritos.


