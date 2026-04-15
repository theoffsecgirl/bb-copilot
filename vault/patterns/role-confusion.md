# Role Confusion Patterns

## Objetivo
Identificar fallos donde un usuario de menor privilegio puede ejecutar acciones reservadas a roles superiores.

## Tipos

### 1. Falta de validación de rol en backend
```
- La UI oculta el botón, pero el endpoint no valida el rol
- Llamar directamente al endpoint de admin desde cuenta normal
- Buscar en JS las rutas de admin y probarlas manualmente
```

### 2. Escalada horizontal dentro del mismo rol
```
- User A y User B son ambos 'editor'
- User A puede modificar proyectos de User B
- Mismo nivel pero sin aislamiento entre usuarios del mismo rol
```

### 3. Role en cliente vs servidor
```
- JWT contiene {"role": "user"} → modificar a "admin"
- Cookie contiene role codificado en base64
- Parámetro role= en request que el servidor acepta
```

### 4. Herencia de permisos mal implementada
```
- Rol 'editor' hereda de 'viewer' pero tiene permisos extra no documentados
- Permisos acumulativos: user con dos roles obtiene unión de permisos sin restricción
- Delegar permisos que no tienes: asignar rol admin desde rol user
```

### 5. API vs UI inconsistencia
```
- La API v1 no valida rol (legacy)
- La API v2 sí valida (nuevo)
- Usar v1 para operaciones que v2 restringe
```

## Metodología
1. Mapear todos los roles del sistema (documentación, JS, respuestas API).
2. Para cada rol, listar acciones disponibles en la UI.
3. Con rol bajo, intentar llamar a endpoints de rol alto directamente.
4. Verificar si el backend valida o solo la UI controla el acceso.
5. Probar cambio de rol en token/cookie/parámetro.

## Impacto alto
- Usuario normal ejecutando acciones de admin.
- Acceso a datos de todos los usuarios desde cuenta estándar.
- Modificación de configuración del sistema sin permisos.
- Borrado de datos ajenos.
