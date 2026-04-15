# Recon

## Objetivo
Mapear la superficie de ataque real antes de tocar nada. La calidad del recon define la calidad de los hallazgos.

## Fase 1 — Scope y reglas
- Leer el scope completo del programa antes de cualquier prueba.
- Identificar wildcards (`*.example.com`) vs dominios fijos.
- Anotar exclusiones explícitas (pagos, infra crítica, etc.).
- Revisar si hay assets fuera de scope que de hecho impacten in-scope.

## Fase 2 — Enumeración de subdominios

```bash
# Pasiva
subfinder -d example.com -all -recursive -o subs_passive.txt
amass enum -passive -d example.com -o subs_amass.txt
curl -s "https://crt.sh/?q=%25.example.com&output=json" | jq '.[].name_value' | sort -u

# Activa
shuffleDNS -d example.com -w wordlist.txt -r resolvers.txt -o subs_active.txt

# Merger
cat subs_passive.txt subs_amass.txt subs_active.txt | sort -u | anew all_subs.txt
```

## Fase 3 — Resolución y live hosts

```bash
dnsx -l all_subs.txt -a -cname -o resolved.txt
httpx -l resolved.txt -title -status-code -tech-detect -cdn -o live.txt
```

## Fase 4 — Fingerprinting rápido
- Tecnología (httpx tech-detect, Wappalyzer).
- CDN / WAF (CDN headers, Cloudflare, Akamai).
- Certificados TLS (SANs → nuevos subdominios).
- Headers de respuesta: `Server`, `X-Powered-By`, `X-Frame-Options`, `CSP`.

## Fase 5 — URLs y endpoints

```bash
# Wayback + gau
gau example.com --providers wayback,commoncrawl,otx | anew urls.txt
waybackurls example.com | anew urls.txt

# Spider activo
katana -u https://example.com -js-crawl -depth 3 -o spider.txt

# Filtrado interesante
grep -E "\.(php|asp|aspx|jsp|json|xml|yaml|env|bak|sql|log)" urls.txt
grep -E "(api|v1|v2|v3|admin|internal|dev|staging|debug)" urls.txt
```

## Fase 6 — Archivos JS
- Extraer con `katana` o `getJS`.
- Buscar endpoints, tokens, credenciales, funciones internas.
- Ver `vault/methodology/js-analysis.md`.

## Fase 7 — Puertos y servicios no estándar

```bash
nmap -T4 -p- --min-rate 5000 -oA scan example.com
naabu -l resolved.txt -top-ports 1000 -o ports.txt
```

## Prioridades después del recon
1. Subdominios con servicios cloud no configurados → takeover.
2. Panels de admin, staging, dev expuestos.
3. APIs v1/v2 sin documentar.
4. JS con endpoints no visibles en la UI.
5. Certificados con SANs raros.

## Señales de alto valor
- Subdominio resuelve pero da 403/401 → prueba bypass.
- CNAME apunta a servicio externo sin reclamar → takeover.
- Subdominio con panel de login diferente al principal.
- API con versiones antiguas (v1 junto a v3).
- JS minificado con rutas `/internal/`, `/admin/`, `/debug/`.
