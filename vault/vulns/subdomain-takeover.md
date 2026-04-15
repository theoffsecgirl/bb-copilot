# Subdomain Takeover

## Señales de entrada
- CNAME apunta a servicio externo (GitHub Pages, Heroku, S3, Fastly, Shopify, etc.).
- Respuesta: "There isn't a GitHub Pages site here", "No such app", "NoSuchBucket".
- Subdominio resuelve pero el servicio no está configurado.

## Metodología

### Paso 1: enumeración
```bash
subfinder -d example.com -o subs.txt
dnsx -l subs.txt -a -cname -o resolved.txt
```

### Paso 2: identificar CNAMEs vulnerables
```bash
# Extraer CNAMEs
cat resolved.txt | grep CNAME | awk '{print $1, $NF}'

# Comprobar si el destino está sin reclamar
# Herramientas
subjack -w subs.txt -t 100 -o results.txt
nucleai -l subs.txt -t nuclei-templates/http/takeovers/
```

### Paso 3: verificar manualmente
```bash
# Ver CNAME
dig CNAME sub.example.com

# Ver respuesta HTTP
curl -I https://sub.example.com

# Mensaje de error = takeover potencial
# "Repository not found" (GitHub)
# "No such app" (Heroku)
# "NoSuchBucket" (S3)
# "404 Not Found" (Fastly, Azure)
```

### Paso 4: reclamar el servicio
- GitHub Pages: crear repositorio con el nombre del CNAME y activar Pages.
- Heroku: crear app con el nombre del subdominio.
- S3: crear bucket con el nombre exacto.
- Netlify/Vercel: añadir dominio custom en nuevo proyecto.

### Paso 5: demostrar sin causar daño
- Subir un fichero HTML con mensaje "Proof of Concept - Bug Bounty - [tu nombre]".
- No hacer nada más. No instalar nada. No capturar cookies.
- Screenshot del subdominio mostrando tu página + DNS proof.

## Servicios más comunes
| Servicio | Mensaje de error |
|---|---|
| GitHub Pages | "There isn't a GitHub Pages site here" |
| Heroku | "No such app" |
| AWS S3 | "NoSuchBucket" |
| Fastly | "Fastly error: unknown domain" |
| Shopify | "Sorry, this shop is currently unavailable" |
| Netlify | "Not Found - Request ID" |
| Azure | "404 Web Site not found" |
| Cargo | "404 Not Found" |

## Impacto
- Cookie theft si el subdominio es del mismo dominio padre (mismo eTLD+1).
- Phishing desde subdominio legítimo.
- Bypass de CSP que allow-list el dominio.
- Si tiene OAuth: robo de tokens via redirect a subdominio controlado.

## Evidencia mínima
- `dig CNAME sub.example.com` mostrando el CNAME.
- Screenshot de la página de error del servicio externo.
- Screenshot de tu PoC HTML en el subdominio reclamado.
- No es necesario (ni deseable) hacer nada más.
