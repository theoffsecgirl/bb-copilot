# IDOR — Insecure Direct Object Reference

## Señales de entrada
- IDs numéricos o UUID en rutas, query params, body o GraphQL.
- Objetos de usuario accesibles por otros usuarios.
- Funciones multi-tenant: orgs, proyectos, facturas, tickets, archivos.
- Endpoints de export, download, print, share.
- Campos: `user_id`, `account_id`, `org_id`, `invoice_id`, `doc_id`, `owner`.

## Metodología

### Setup
1. Crear dos cuentas (A y B) en el mismo rol.
2. Con A: crear un objeto y anotar su ID.
3. Con B: intentar acceder al objeto de A.

### Vectores de prueba
```
GET  /api/v1/invoices/{id}          ← acceso
PUT  /api/v1/invoices/{id}          ← modificación
DELETE /api/v1/invoices/{id}        ← borrado
GET  /api/v1/users/{id}/profile     ← PII
GET  /api/v1/orgs/{id}/members      ← enumeración
POST /api/v1/files/download         {"file_id": X}  ← body IDOR
```

### Escalado
- Probar con rol más bajo accediendo a objetos de rol más alto (vertical).
- Probar entre cuentas mismo rol (horizontal).
- Probar en listas/búsquedas: ¿devuelven objetos de otros usuarios?
- Probar en funciones batch: `DELETE /api/v1/items` con IDs mezclados.

### Casos especiales
- IDOR en referencias indirectas: `filename=invoice_march.pdf` → predecible.
- IDOR en GraphQL: cambiar `id` en mutations o queries.
- IDOR en WebSocket: cambiar `room_id` o `user_id` en el payload.
- IDOR en exportaciones: `GET /export?report_id=X`.

## Payloads / manipulación de IDs
```
ID original:  1000
Probar:       999, 1001, 1, 0, -1, null, undefined
UUID:         cambiar último bloque o usar UUID conocido
Base64:       decodificar, modificar, recodificar
HMAC/signed:  si es firmado, buscar bypass en otro endpoint
```

## Impacto alto
- Acceso a PII (nombre, email, teléfono, dirección, documentos).
- Acceso a datos financieros (facturas, pagos, tarjetas).
- Modificación de datos de otro usuario.
- Escalada de privilegios (acceso a objetos de admin).
- Enumeración masiva de usuarios o recursos.

## Falsos positivos
- IDs públicos por diseño (posts públicos, páginas públicas).
- Recursos compartidos explícitamente (links de share).
- Respuesta idéntica independientemente del ID (no hay diferencia).

## Evidencia mínima
- Request de cuenta B accediendo a objeto de cuenta A.
- Response con datos de A visible en sesión de B.
- Comparativa de respuesta con objeto propio vs ajeno.
