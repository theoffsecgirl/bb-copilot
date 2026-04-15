# Asset Triage

## Objetivo
Clasificar los activos encontrados en el recon para priorizar dónde atacar primero según impacto potencial.

## Clasificación rápida

| Prioridad | Tipo de activo | Por qué |
|---|---|---|
| P0 | Admin panels, internal APIs, staging | Menor protección, mayor impacto |
| P0 | CNAME sin reclamar | Takeover directo |
| P1 | APIs con auth | IDOR, authz bugs |
| P1 | Upload endpoints | RCE, stored XSS |
| P1 | OAuth / SSO flows | Account takeover |
| P2 | Formularios públicos | XSS, injection |
| P2 | Redirecciones | Open redirect, phishing |
| P3 | Páginas estáticas | Bajo interés salvo JS jugoso |

## Preguntas de triage
- ¿Este activo maneja datos de usuario o dinero?
- ¿Tiene autenticación? ¿Qué tipo?
- ¿Hay diferencia entre roles (user/admin/org)?
- ¿Está en producción o es staging/dev?
- ¿Tiene integración con servicios internos (metadata, S3, DB)?

## Marcadores de interés en headers
```
X-Internal: true
X-Debug: 1
Server: Apache/2.2  ← versiones viejas
X-Powered-By: PHP/5.6
Access-Control-Allow-Origin: *
Set-Cookie: session=... (sin HttpOnly/Secure)
```

## Acciones por tipo

### API endpoints
- Buscar documentación (Swagger, OpenAPI, GraphQL introspection).
- Listar verbos permitidos (OPTIONS).
- Probar con y sin auth.
- Ver si hay versiones paralelas (v1 vs v2).

### Panels admin/staging
- Intentar bypass de 403 (`/admin`, `/.admin`, `/admin/`).
- Cabeceras: `X-Forwarded-For: 127.0.0.1`, `X-Real-IP`, `X-Original-URL`.
- Ver si hay credenciales por defecto.

### Subdominios con CNAME
- Verificar si el servicio de destino está sin reclamar.
- Ver `vault/vulns/subdomain-takeover.md`.
