# Reporting

## Objetivo
Escribir reportes que se acepten en primera revisión, con impacto claro y reproducción inequívoca.

## Estructura mínima

```
## Summary
[1-2 líneas: qué es, dónde está, impacto]

## Vulnerability Details
[Descripción técnica precisa]

## Steps to Reproduce
1. ...
2. ...
3. ...

## Proof of Concept
[Request/response o vídeo]

## Impact
[Impacto real, no teórico]

## Recommended Fix
[Opcional pero valorado]
```

## Summary: cómo escribirlo
- NO: "This vulnerability allows attackers to..."
- SÍ: "An authenticated user can access any other user's invoice PDF by replacing the `invoice_id` parameter in `GET /api/v1/invoices/{id}`. No further privileges required."

## Steps to Reproduce
- Cada paso debe ser reproducible sin contexto adicional.
- Incluir headers exactos, body completo, valores de ejemplo.
- Usar Burp request format si es posible.
- Añadir cuenta de prueba si el programa lo permite.

## Proof of Concept

```http
GET /api/v1/invoices/10293 HTTP/1.1
Host: app.example.com
Authorization: Bearer <token_usuario_B>
Content-Type: application/json

--- Response ---
HTTP/1.1 200 OK
{"id":10293,"owner":"usuario_A","amount":"$4500","pdf_url":"..."}
```

## Impact: cómo articularlo
- Relacionar con datos reales: PII, dinero, acceso a sistemas.
- Mencionar CVSS si el programa lo pide.
- Escalar el impacto: ¿es horizontal? ¿vertical? ¿masivo?
- Ejemplo: "An attacker can enumerate all user invoices by iterating `invoice_id` from 1 to N, exposing names, addresses and payment amounts of all customers."

## Severidades orientativas (CVSS)
| Severidad | Ejemplos |
|---|---|
| Critical | RCE, SQLi con dump, account takeover masivo |
| High | IDOR con PII, SSRF a metadata, stored XSS en admin |
| Medium | IDOR sin datos críticos, reflected XSS, open redirect |
| Low | Info disclosure menor, rate limit ausente |
| Info | Falta header de seguridad, versión expuesta |

## Errores comunes
- Describir la vuln sin demostrar el impacto.
- Steps que no se pueden reproducir sin tu sesión.
- Scope incorrecto (reportar un out-of-scope).
- Título vago: "IDOR en la API" vs "IDOR en /api/v1/invoices permite leer facturas de cualquier usuario".
- No adjuntar request/response completo.

## Escalado de duplicados
- Si te marcan como duplicado, pedir el ID del original.
- Comparar tu vector con el original: ¿es el mismo endpoint y mismo método?
- Si difiere, argumentar con datos.

## Comunicación con el programa
- Responder siempre con datos, nunca con emociones.
- Si reclamas la severidad, usar CVSS + impacto de negocio.
- Dar tiempo razonable (7-14 días) antes de hacer follow-up.
