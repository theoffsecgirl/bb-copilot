# Business Logic Vulnerabilities

## Señales de entrada
- Flujos multi-paso (compra, verificación, aprobación).
- Descuentos, cupones, precios, cantidades.
- Funciones de share/invite/referral.
- Cambios de estado (draft → published, pending → approved).
- Lógica diferente entre roles.
- Acciones que dependen de un estado previo.

## Vulnerabilidades comunes

### Race conditions
```
Escenario: cupones de un solo uso, transferencias, validaciones
Método: enviar múltiples requests simultáneas antes de que el estado se actualice

# Con Burp: "Send group in parallel" (HTTP/2)
# Con Turbo Intruder: race_single_packet_attack
```

### Manipulación de precio/cantidad
```
Modificar en Burp:
- price: 100 → -100 (precio negativo)
- quantity: 1 → -1 (cantidad negativa)
- discount: 10 → 110 (descuento mayor al 100%)
- total: calculado en cliente → manipular antes de enviar
```

### Saltar pasos de flujo
```
Flujo normal: paso1 → paso2 → paso3 (pago) → paso4 (confirmación)
Test: ir directamente de paso2 a paso4 sin pasar por pago
Test: repetir paso4 sin haber hecho paso3
```

### Abuso de funciones de invite/referral
```
- Invitarse a uno mismo con otro email
- Referral circular (A invita a B, B invita a A)
- Reutilizar código de referral infinitamente
- Obtener crédito por invitar cuentas desactivadas
```

### Estado inconsistente
```
- Cambiar estado de objeto que no debería ser editable (ej: pedido ya enviado)
- Añadir items a carrito después de aplicar descuento
- Cancelar y volver a activar para resetear límites
```

### Privilege escalation por flujo
```
- Completar flujo de admin desde cuenta normal si los pasos intermedios no validan rol
- Usar token de invitación de admin en cuenta normal
- Aceptar invitación de org con rol más alto del asignado
```

## Impacto alto
- Obtener productos/servicios gratis o a precio negativo.
- Saltarse verificación de pago.
- Acumular créditos/beneficios infinitamente.
- Aprobar contenido sin los permisos necesarios.
- Escalar a rol de admin via flujo mal implementado.

## Evidencia mínima
- Request/response mostrando el estado inconsistente.
- Para precios: respuesta con total incorrecto o pedido confirmado sin cobro real.
- Para race: capturas de requests paralelos + resultado inesperado.
- Para privilege escalation: acción completada con cuenta sin permisos.
