# Open Redirect

## Señales de entrada
- Parámetros: `redirect=`, `next=`, `return=`, `url=`, `to=`, `dest=`, `goto=`, `target=`.
- Respuestas 301/302 con `Location` header controlable.
- Login/logout con parámetro de retorno.
- OAuth flows con `redirect_uri`.

## Metodología

### Detección básica
```
https://example.com/login?next=https://evil.com
https://example.com/logout?redirect=https://evil.com
https://example.com/sso?return_to=https://evil.com
```

### Bypass de filtros
```
# Doble slash
https://example.com//evil.com

# @
https://example.com@evil.com
https://user@evil.com

# Subdominio falso
https://evil.com.example.com

# URL encoding
https://example.com/redirect?url=https%3A%2F%2Fevil.com

# Open redirect chaining para SSRF
https://example.com/redirect?url=http://169.254.169.254/

# javascript:
https://example.com/redirect?url=javascript:alert(1)
```

## Escalado de impacto
- Por sí solo: severidad baja-media (phishing).
- Encadenado con OAuth: robo de authorization code → ATO.
- Encadenado con SSRF: bypass de filtros de URL.
- Encadenado con XSS: si `javascript:` no se filtra.

## Impacto máximo
- `redirect_uri` en OAuth → robo de token → account takeover.
- Phishing con dominio legítimo → mayor credibilidad.

## Evidencia mínima
- Request y respuesta 302 con Location apuntando a dominio externo.
- Si se encadena con OAuth, mostrar el flujo completo.
