# Multi-Tenant Patterns

## Objetivo
Identificar fallos en el aislamiento entre tenants (organizaciones, cuentas, clientes) que permitan acceso cruzado a datos o funciones.

## Señales de multi-tenancy
- Parámetros: `org_id`, `tenant_id`, `account_id`, `workspace_id`, `company_id`.
- Subdominios por tenant: `company.example.com`.
- Paths por tenant: `/org/acme/settings`.
- Contexto implícito via token (el org_id va en el JWT).

## Vectores de prueba

### 1. Manipulación directa de tenant ID
```
# Cambiar org_id en requests
GET /api/v1/orgs/{org_id}/users
GET /api/v1/orgs/{org_id}/billing
GET /api/v1/orgs/{org_id}/settings

# En body
{"org_id": "otro_org", "action": "export"}
```

### 2. Cross-tenant via objeto compartido
```
- Crear objeto en org A con ID conocido
- Desde org B, acceder al objeto con ese ID
- Incluso si el endpoint valida org, el objeto puede no validar
```

### 3. Subdomain confusion
```
- Login en orgA.example.com
- Cambiar cookie/token y acceder a orgB.example.com
- Ver si la sesión es válida en el otro tenant
```

### 4. Shared resources
```
- Plantillas, ficheros, configuraciones compartidas entre orgs
- Buscar endpoints de `copy`, `duplicate`, `share`, `template`
- Objetos con `visibility: org` que pasan a `visibility: global`
```

### 5. Invite como vector
```
- Invitar email de org B a org A
- Aceptar con cuenta de org B
- Ver qué acceso tiene en org A y viceversa
- Revocar invite pero mantener acceso
```

## Impacto alto
- Acceso a datos de otro cliente (PII, documentos, configuración).
- Exfiltración de miembros, roles, billing de otra org.
- Ejecución de acciones en nombre de otra org.
- Escalada: acceder a org con plan premium desde org free.
