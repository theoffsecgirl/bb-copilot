# API Hunting

## Objetivo
Enumerar, mapear y atacar APIs REST y GraphQL con foco en autorización, exposición de datos y lógica de negocio.

## Descubrimiento de APIs

```bash
# Fuerza bruta de rutas
ffuf -u https://api.example.com/FUZZ -w api_wordlist.txt -mc 200,201,401,403

# Buscar en JS (ver js-analysis.md)
grep -rE '/api/v[0-9]' js_downloaded/

# Swagger / OpenAPI
curl https://api.example.com/swagger.json
curl https://api.example.com/api-docs
curl https://api.example.com/openapi.yaml

# GraphQL
curl -X POST https://api.example.com/graphql -d '{"query":"{__schema{types{name}}}"}
curl -X POST https://api.example.com/graphql -d '{"query":"{__schema{queryType{fields{name}}}}"}
```

## Mapa de superficie
- Listar todos los endpoints (GET, POST, PUT, PATCH, DELETE).
- Identificar objetos: users, orgs, projects, invoices, files…
- Ver qué campos acepta cada endpoint.
- Buscar IDs: ¿numerales? ¿UUID? ¿predecibles?

## Checks de autorización

```
1. Crear dos cuentas (A y B)
2. Con A: crear objeto, anotar ID
3. Con B: acceder al mismo objeto → IDOR
4. Con B: modificar/eliminar objeto de A → IDOR write
5. Sin auth: repetir requests → broken auth
6. Con rol bajo: acceder a endpoint de rol alto → privilege escalation
```

## Manipulación de parámetros
- Cambiar `user_id`, `org_id`, `account_id`, `tenant_id`, `owner`.
- Añadir campos extra en body: `"role":"admin"`, `"is_admin":true`.
- Probar mass assignment: POST con campos no esperados.
- Cambiar Content-Type: `application/json` → `text/xml`, `application/x-www-form-urlencoded`.

## Versiones paralelas
- Si existe `/api/v2/users`, probar `/api/v1/users` → puede tener menos controles.
- Probar `/api/v0/`, `/api/beta/`, `/api/internal/`.

## Headers útiles
```
X-HTTP-Method-Override: DELETE
X-Forwarded-For: 127.0.0.1
Origin: https://evil.com  ← CORS test
Content-Type: application/xml  ← XXE
```

## Rate limiting y auth
- Probar sin token → ¿da datos?
- Token expirado → ¿sigue funcionando?
- Token de otro usuario → ¿valida o solo verifica firma?
- JWT: cambiar `alg` a `none`, probar `HS256` con clave vacía.

## GraphQL especifico
- Introspection habilitada → esquema completo expuesto.
- Buscar mutations con datos sensibles.
- Batching attacks (rate limit bypass).
- Field suggestions → nombres de campos internos.
