# JS Analysis

## Objetivo
Extraer endpoints, tokens, secrets y lógica interna de ficheros JavaScript para descubrir superficie de ataque no visible en la UI.

## Extracción de JS

```bash
# Con katana
katana -u https://example.com -js-crawl -depth 3 | grep "\.js" | anew js_files.txt

# Con getJS
getJS --url https://example.com --complete | anew js_files.txt

# Descargar todos
wget -i js_files.txt -P js_downloaded/
```

## Qué buscar

### Endpoints internos
```bash
# Rutas en JS
grep -rE '("/api/|\'\'/api/|fetch\(|axios\.|\$\.ajax)' js_downloaded/

# Con linkfinder
python3 linkfinder.py -i https://example.com -d -o cli
```

### Secrets y tokens
```bash
# Con secretfinder
python3 SecretFinder.py -i js_url -o cli

# Patrones manuales
grep -rE '(api_key|apikey|secret|token|password|aws_|bearer|private_key)' js_downloaded/ -i
```

### Rutas de interés
```bash
grep -rE '(/admin|/internal|/debug|/config|/v[0-9]|/graphql|/api/)' js_downloaded/
```

## Desofuscación
- Usar [de4js](https://de4js.kshift.me/) para JS ofuscado.
- Usar [prettier](https://prettier.io/) para minificado.
- Buscar `eval()`, `atob()`, strings en base64 inline.

## Source maps
- Si existe `app.js.map`, descargarlo → código fuente original expuesto.
- URL típica: `https://example.com/static/js/main.chunk.js.map`.

```bash
# Comprobar si existe
curl -I https://example.com/static/js/main.chunk.js.map
```

## Hallazgos comunes
- Endpoints `/api/v1/admin/*` no linkeados desde la UI.
- Tokens hardcodeados (AWS, Stripe, Firebase, Twilio).
- Rutas de debug o feature flags (`debug=true`, `isAdmin`, `featureFlag`).
- GraphQL queries y mutations con campos sensibles.
- Credenciales de staging embebidas.

## Prioridad
1. Source maps → código fuente real.
2. Secrets hardcodeados → impacto directo.
3. Endpoints admin/internal → superficie nueva.
4. Lógica de roles/permisos en cliente → bypass potencial.
