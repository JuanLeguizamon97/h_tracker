# Plan de Integracion Backend + Frontend

## Fase 1: Modificaciones al Backend

### 1.1 Agregar `role` y `hourly_rate` al modelo Employees
- `Backend/models/employees.py`: agregar columnas `role` (String, default="employee") y `hourly_rate` (Numeric(10,2))
- `Backend/schemas/employees.py`: agregar campos a Base, Update y Out
- Eliminar `database.sqlite` para que se recree con el nuevo schema

### 1.2 Agregar endpoint `GET /employees/me`
- `Backend/routers/employees.py`: nuevo endpoint que extrae `oid`/email del token Azure y retorna (o crea) el empleado
- `Backend/services/employees.py`: agregar `get_or_create_employee_by_email()`
- Esto es CRITICO: el Frontend necesita saber quien es el usuario despues del login MSAL

### 1.3 Agregar filtro por empleado y datos enriquecidos a assigned_projects
- `Backend/routers/assigned_projects.py`: `GET /assigned-projects/?employee_id=X` con join a projects+clients
- `Backend/schemas/assigned_projects.py`: nuevo schema `AssignedProjectWithDetails` con project_name y client_name
- `Backend/services/assigned_projects.py`: query con join

### 1.4 Agregar bulk assign y delete individual para assigned_projects
- `Backend/routers/assigned_projects.py`: `PUT /assigned-projects/employee/{id}/bulk` y `DELETE /assigned-projects/{id}`
- `Backend/services/assigned_projects.py`: funciones correspondientes

### 1.5 Actualizar CORS
- `Backend/main.py`: agregar `http://localhost:8080` a allow_origins

### 1.6 Auto-crear semanas en time_entries
- `Backend/services/time_entries.py`: al crear un time_entry, si la semana no existe, crearla automaticamente

## Fase 2: Migracion de Auth (Supabase -> MSAL)

### 2.1 Instalar dependencias MSAL
- `npm install @azure/msal-browser @azure/msal-react`
- `npm uninstall @supabase/supabase-js`

### 2.2 Crear configuracion MSAL
- Nuevo: `Frontend/src/config/msalConfig.ts` con clientId SPA, authority, scope

### 2.3 Crear cliente API con token
- Nuevo: `Frontend/src/lib/api.ts` - wrapper fetch con Bearer token de MSAL + prefijo /api

### 2.4 Configurar proxy en Vite
- `Frontend/vite.config.ts`: proxy `/api` -> `http://localhost:8000`

### 2.5 Reescribir AuthContext
- `Frontend/src/contexts/AuthContext.tsx`: reemplazar Supabase con MSAL + llamada a `GET /api/employees/me`
- Expone: employee, role, isAdmin, isAuthenticated, signOut

### 2.6 Envolver App con MsalProvider
- `Frontend/src/main.tsx`: inicializar PublicClientApplication y envolver con MsalProvider

### 2.7 Reescribir pagina Auth
- `Frontend/src/pages/Auth.tsx`: boton "Iniciar Sesion con Microsoft" (loginRedirect)

### 2.8 Actualizar ProtectedRoute y AppSidebar
- Adaptar a nueva interfaz AuthContext

### 2.9 Eliminar archivos Supabase
- Borrar `Frontend/src/integrations/supabase/`

## Fase 3: Tipos y capa API

### 3.1 Reescribir tipos TypeScript
- `Frontend/src/types/index.ts`: Employee, Client (composite PK), Project, TimeEntry (semanal), AssignedProject, Week

### 3.2 Crear funciones API por entidad
- `Frontend/src/lib/api/employees.ts`
- `Frontend/src/lib/api/clients.ts`
- `Frontend/src/lib/api/projects.ts`
- `Frontend/src/lib/api/timeEntries.ts`
- `Frontend/src/lib/api/weeks.ts`
- `Frontend/src/lib/api/assignedProjects.ts`

## Fase 4: Reescribir Hooks

### 4.1 useProfiles.ts -> useEmployees.ts
### 4.2 useClients.ts (adaptar a nuevo modelo)
### 4.3 useProjects.ts (adaptar campos)
### 4.4 useTimeEntries.ts (cambio a modelo semanal)
### 4.5 useEmployeeProjects.ts (adaptar a assigned_projects)
### 4.6 Nuevo useWeeks.ts

## Fase 5: Adaptar Paginas

### 5.1 Timesheet (CAMBIO MAYOR)
- Cambiar grid de 7 dias a input de total semanal por proyecto
- Selector de semana, buscar entries por week_start

### 5.2 History
- Agrupar por semana en vez de por dia
- Adaptar campos (id_project, total_hours, week_start)

### 5.3 Employees
- Usar Employee en vez de Profile, role es campo directo
- Eliminar supervisor_id (no existe en Backend)

### 5.4 Clients
- Adaptar a composite PK, client_name, contact_email, active

### 5.5 Projects
- Adaptar campos, eliminar description, lookup client name separado

### 5.6 Billing
- Adaptar a nuevos tipos, hourly_rate desde Employee

### 5.7 EmployeeProjectsDialog
- Adaptar a AssignedProject con client_id

## Fase 6: Limpieza
- Eliminar referencias a Supabase restantes
- Limpiar dependencias de package.json
