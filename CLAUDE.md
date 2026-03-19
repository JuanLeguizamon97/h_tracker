# H_Tracker — Horas+ (Impact Point Hours Tracker)

Sistema de seguimiento de horas y facturación para empresas de servicios profesionales.

---

## Stack técnico

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI 0.122, Python 3.12, SQLAlchemy 2.0, Alembic, Pydantic v2 |
| Base de datos | PostgreSQL 16 (Docker) |
| Frontend | React 18, TypeScript, Vite 5, React Router v6 |
| UI | Shadcn/ui, Tailwind CSS |
| Estado/Fetching | TanStack React Query v5 |
| Fechas | date-fns |
| Notificaciones | Sonner |
| Auth | Azure AD (fastapi-azure-auth) — modo `AUTH_MODE=mock` en dev |
| Scheduler | APScheduler 3.10 (background job para facturas mensuales) |
| Exportación | ReportLab (PDF), OpenPyXL (Excel) |
| Contenerización | Docker Compose + Nginx reverse proxy |

---

## Estructura de directorios

```
H_Tracker/
├── Backend/
│   ├── main.py                    # Entrada FastAPI, routers, scheduler startup/shutdown
│   ├── config/
│   │   └── database.py            # SQLAlchemy engine, SessionLocal, Base
│   ├── models/                    # 17 modelos SQLAlchemy
│   ├── schemas/                   # 15 schemas Pydantic (Create/Update/Out)
│   ├── services/                  # 21 servicios de negocio
│   ├── routers/                   # 16 routers FastAPI
│   ├── alembic/versions/          # 6 migraciones
│   ├── requirements.txt
│   └── seed.py                    # Datos iniciales
├── Frontend/
│   ├── src/
│   │   ├── App.tsx                # Rutas React Router (lazy loading)
│   │   ├── pages/                 # 19 páginas
│   │   ├── hooks/                 # 11 archivos de hooks (React Query)
│   │   ├── components/ui/         # Shadcn/ui components
│   │   ├── contexts/AuthContext.tsx
│   │   ├── lib/api.ts             # Cliente HTTP (fetch + Bearer token / mock)
│   │   └── types/index.ts         # Tipos TypeScript globales
├── backend.Dockerfile
├── frontend.Dockerfile
├── docker-compose.yml
├── nginx.conf
└── CLAUDE.md                      # Este archivo
```

---

## Docker

### docker-compose.yml
```
postgres  → puerto 5433:5432 (pgdata volume)
backend   → puerto 8001:8000 (uploads volume)
frontend  → puerto 3000:80
```

### Variables de entorno clave (backend)
```
DATABASE_URL        postgresql://hours_user:hours_pass@postgres:5432/hours_tracker
AUTH_MODE           mock | azure
CORS_ORIGINS        http://localhost:8080,http://localhost:3000
UPLOAD_DIR          /app/uploads
COP_TO_USD_RATE     4200
EUR_TO_USD_RATE     1.08
```

### Startup del backend
El `backend.Dockerfile` ejecuta al inicio:
```bash
alembic upgrade head && python seed.py && uvicorn main:app --host 0.0.0.0 --port 8000
```

### Nginx
- `/api/*` → `http://backend:8000/` (strips `/api` prefix)
- Todo lo demás → `index.html` (SPA fallback)

---

## Modelos de base de datos (17)

| Modelo | Tabla | Descripción |
|--------|-------|-------------|
| AppUser | app_users | Usuario Azure AD (azure_oid, email, display_name) |
| Employee | employees | Perfil de empleado (user_id FK a azure_oid, hourly_rate, title, department, business_unit) |
| Client | clients | Cliente con campos de facturación extendidos |
| Project | projects | Proyecto con client_id, manager_id, status, is_internal, project_code |
| ProjectCategory | project_categories | Categorías (area_category / business_unit) |
| ProjectRole | project_roles | Rol en proyecto con hourly_rate_usd |
| UserRole | user_roles | Roles de app (employee / admin) |
| EmployeeProject | employee_projects | Asignación empleado↔proyecto con role_id |
| TimeEntry | time_entries | Entrada de horas (date, hours, billable, status=normal) |
| Invoice | invoices | Factura (status: draft/sent/paid/cancelled/voided) |
| InvoiceLine | invoice_lines | Línea de factura (employee, hours, rate_snapshot, discount) |
| InvoiceManualLine | invoice_manual_lines | Línea manual (person_name, hours, rate_usd) |
| InvoiceFee | invoice_fees | Honorario (label, quantity, unit_price_usd) |
| InvoiceFeeAttachment | invoice_fee_attachments | Archivos adjuntos a honorarios |
| InvoiceTimeEntry | invoice_time_entries | Vínculo factura↔time_entry (evita doble facturación) |
| InvoiceExpense | invoice_expenses | Gasto (category, amount_usd, professional, vendor) |
| SchedulerLog | scheduler_log | Log de ejecuciones del scheduler de facturas |

### Relaciones clave
```
Employee ──< EmployeeProject >── Project
Employee ──< TimeEntry >── Project
Project ──< Invoice ──< InvoiceLine
                    ──< InvoiceManualLine
                    ──< InvoiceFee ──< InvoiceFeeAttachment
                    ──< InvoiceTimeEntry >── TimeEntry
                    ──< InvoiceExpense
```

### Nota FK importante
`time_entries.user_id` es FK a `employees.id` (UUID interno), **NO** a `employees.user_id` (Azure AD OID).
Siempre usar `employee.id` al crear TimeEntry desde el frontend.

---

## API Backend — Endpoints

### Auth
```
GET  /auth/me                     → AppUserOut (crea si no existe)
```

### Employees
```
GET  /employees/me                → EmployeeOut (auto-crea desde token)
POST /employees/                  → EmployeeOut
GET  /employees/                  → List[EmployeeOut] ?active ?user_role ?search
GET  /employees/{id}              → EmployeeOut
PUT  /employees/{id}              → EmployeeOut
DEL  /employees/{id}              → 204
```

### Clients
```
POST /clients/                    → ClientOut
GET  /clients/                    → List[ClientOut] ?active
GET  /clients/{id}                → ClientOut
PUT  /clients/{id}                → ClientOut
DEL  /clients/{id}                → 204
```

### Projects
```
GET  /projects/categories         → List[ProjectCategoryOut] ?type
POST /projects/                   → ProjectOut
GET  /projects/                   → List[ProjectOut] ?active ?client_id ?status
GET  /projects/{id}/assignments   → List[ProjectAssignmentOut]
GET  /projects/{id}               → ProjectOut
PUT  /projects/{id}               → ProjectOut
PATCH /projects/{id}              → ProjectOut
DEL  /projects/{id}               → 204
```

### Project Roles
```
POST /project-roles/              → ProjectRoleOut
GET  /project-roles/              → List[ProjectRoleOut] ?project_id
PUT  /project-roles/{id}          → ProjectRoleOut
DEL  /project-roles/{id}          → 204
```

### Employee Projects (asignaciones)
```
POST /employee-projects/          → EmployeeProjectOut
GET  /employee-projects/          → List[EmployeeProjectOut] ?user_id ?project_id
GET  /employee-projects/{uid}/details → List[EmployeeProjectWithDetails]
PUT  /employee-projects/{uid}/bulk    → List[EmployeeProjectOut] (reemplaza todas)
PUT  /employee-projects/{id}          → EmployeeProjectOut (actualizar role_id)
DEL  /employee-projects/{id}          → 204
```

### Time Entries
```
POST /time-entries/               → TimeEntryOut
GET  /time-entries/               → List[TimeEntryOut] ?user_id ?project_id ?date_gte ?date_lte ?billable ?status
GET  /time-entries/{id}           → TimeEntryOut
PUT  /time-entries/{id}           → TimeEntryOut
DEL  /time-entries/{id}           → 204
```

### Invoices
```
POST /invoices/                   → InvoiceOut
GET  /invoices/                   → List[InvoiceOut] ?project_id ?status
GET  /invoices/check-hours        → {has_entries, total_hours, total_amount, entry_count} ?project_id ?period_start ?period_end
POST /invoices/generate-monthly   → {generated, skipped, errors} body:{period_start, period_end}
GET  /invoices/scheduler-status   → {last_run, last_period, invoices_generated, next_run, status}
GET  /invoices/{id}/edit-data     → InvoiceEditDataOut (invoice + lines + expenses)
PATCH /invoices/{id}              → InvoiceOut body:InvoicePatch
GET  /invoices/{id}/export/pdf    → PDF binary
GET  /invoices/{id}/export/xlsx   → XLSX binary
GET  /invoices/{id}               → InvoiceOut
PUT  /invoices/{id}               → InvoiceOut
DEL  /invoices/{id}               → 204
```

### Invoice Lines
```
POST /invoice-lines/              → InvoiceLineOut
POST /invoice-lines/bulk          → List[InvoiceLineOut]
GET  /invoice-lines/              → List[InvoiceLineOut] ?invoice_id
PUT  /invoice-lines/{id}          → InvoiceLineOut
DEL  /invoice-lines/{id}          → 204
```

### Invoice Time Entries (vínculos)
```
GET  /invoice-time-entries/linked-ids → List[str]
POST /invoice-time-entries/bulk       → List[InvoiceTimeEntryOut] body:{invoice_id, time_entry_ids}
DEL  /invoice-time-entries/{id}       → 204
```

### Invoice Expenses
```
POST /invoice-expenses/           → InvoiceExpenseOut
GET  /invoice-expenses/           → List[InvoiceExpenseOut] ?invoice_id
PUT  /invoice-expenses/{id}       → InvoiceExpenseOut
DEL  /invoice-expenses/{id}       → 204
```

### Invoice Fees
```
POST /invoice-fees/               → InvoiceFeeOut
GET  /invoice-fees/               → List[InvoiceFeeOut] ?invoice_id
PUT  /invoice-fees/{id}           → InvoiceFeeOut
DEL  /invoice-fees/{id}           → 204
```

### Invoice Fee Attachments
```
POST /invoice-fee-attachments/upload → InvoiceFeeAttachmentOut (multipart: fee_id + file)
GET  /invoice-fee-attachments/       → List[InvoiceFeeAttachmentOut] ?fee_id
DEL  /invoice-fee-attachments/{id}   → 204
```

### Expensify
```
GET  /expensify/status            → {configured, last_sync, last_sync_count, last_sync_invoice_id}
GET  /expensify/reports           → {count, reports[]} preview ?project_code ?employee_email ?date_from ?date_to
POST /expensify/sync              → {imported, skipped, reports_processed} body o query params
```

### User Roles
```
GET  /user-roles/                 → List[UserRoleOut]
PUT  /user-roles/{user_id}        → UserRoleOut body:{role}
DEL  /user-roles/{user_id}        → 204
```

### Health
```
GET  /health                      → {status: "ok"}
```

---

## Frontend — Rutas

```
/                      Dashboard
/timesheet             Registro semanal de horas
/history               Historial de entradas
/projects              Lista de proyectos
/projects/new          Nuevo proyecto
/projects/:id          Detalle de proyecto
/projects/:id/edit     Editar proyecto
/clients               Lista de clientes
/employees             Lista de empleados
/invoices              Lista de facturas
/invoices/new          Nueva factura (desde time entries)
/invoices/new/manual   Factura manual (sin time entries)
/invoices/:id/edit     Editor completo de factura
/reports               Reportes y análisis
/auth                  Login (redirige a /)
```

---

## Frontend — Hooks React Query

| Hook | Archivo | Qué hace |
|------|---------|----------|
| useProjects / useActiveProjects | useProjects.ts | Lista proyectos |
| useClients | useClients.ts | Lista clientes |
| useEmployees | useEmployees.ts | Lista empleados |
| useTimeEntriesByWeek | useTimeEntries.ts | Entradas de una semana |
| useTimeEntriesByDateRange | useTimeEntries.ts | Entradas por rango |
| useCreateTimeEntry | useTimeEntries.ts | POST /time-entries |
| useUpdateTimeEntry | useTimeEntries.ts | PUT /time-entries/{id} |
| useDeleteTimeEntry | useTimeEntries.ts | DELETE /time-entries/{id} |
| useAssignedProjects | useAssignedProjects.ts | GET /employee-projects |
| useAssignedProjectsWithDetails | useAssignedProjects.ts | GET /employee-projects/{id}/details |
| useBulkAssignProjects | useAssignedProjects.ts | PUT /employee-projects/{id}/bulk |
| useInvoices | useInvoices.ts | GET /invoices |
| useCreateInvoice | useInvoices.ts | POST /invoices |
| useUpdateInvoice | useInvoices.ts | PUT /invoices/{id} |
| usePatchInvoice | useInvoices.ts | PATCH /invoices/{id} |
| useCreateInvoiceLines | useInvoices.ts | POST /invoice-lines/bulk |
| useLinkTimeEntries | useInvoices.ts | POST /invoice-time-entries/bulk |
| useGenerateMonthlyInvoices | useInvoices.ts | POST /invoices/generate-monthly |

---

## Servicios backend clave

### invoice_generator.py
Genera facturas draft automáticamente para proyectos activos no internos:
1. Busca proyectos activos no internos sin factura en el período
2. Obtiene time entries billables no vinculadas a otra factura
3. Agrupa por empleado, busca rol en `employee_projects`, obtiene `hourly_rate_usd`
4. Crea `Invoice` + `InvoiceLine` por empleado + `InvoiceTimeEntry` links
5. Numeración: `INV-{YYYY}-{seq:03d}`

### invoice_scheduler.py
APScheduler `BackgroundScheduler`:
- Job: `auto_generate_monthly_invoices` — cron día 5, 00:00
- Genera para el mes anterior
- Registra en `scheduler_log`
- Se inicia/detiene en `@app.on_event("startup/shutdown")`

### expensify_service.py
- Llama a Expensify Partner API
- Convierte COP→USD usando `COP_TO_USD_RATE`
- Detecta duplicados por `expensify_report_id` (si existe en expenses)
- Categoriza automáticamente según campo `category` de Expensify

### export_pdf.py / export_excel.py
- Generan reportes con branding de Impact Point
- PDF: líneas, honorarios, gastos, totales, descuentos
- XLSX: hoja por sección (resumen, líneas, gastos)

---

## Migraciones Alembic

| Revisión | Descripción |
|----------|-------------|
| 001 | Schema inicial (todas las tablas core) |
| 002 | Alineación con frontend |
| 003 | Soporte edición facturas (discount_type, discount_value, manual_lines) |
| 004 | Adiciones fase 2 |
| 005 | Manager en proyectos + categorías |
| 006 | Tabla scheduler_log |

Para correr migraciones:
```bash
alembic upgrade head       # Aplicar todas
alembic downgrade -1       # Revertir última
```

---

## Flujo de creación de factura

### Automático (scheduler — día 5 de cada mes)
```
APScheduler → invoice_generator.generate_invoices_for_period(prev_month)
  → Por cada proyecto activo no interno:
    → Verificar que no existe factura para ese período
    → Buscar time entries billables no vinculadas
    → Agrupar por empleado → calcular horas × rate
    → Crear Invoice (draft) + InvoiceLines + InvoiceTimeEntry links
    → Registrar en SchedulerLog
```

### Manual desde frontend
```
InvoiceNewPage:
  1. Usuario selecciona proyecto
  2. GET /invoices/check-hours?project_id=...
     → Si has_entries=false: Dialog → "¿Crear manual?" → InvoiceManualPage
     → Si has_entries=true:
        POST /invoices/ (crea invoice vacía)
        GET /invoice-time-entries/linked-ids
        GET /time-entries?project_id=...&billable=true&status=normal
        Filtra no vinculadas → agrupa por empleado → calcula amounts
        POST /invoice-lines/bulk
        POST /invoice-time-entries/bulk
        PUT /invoices/{id} (actualiza subtotal/total)
        → Navegar a /invoices/{id}/edit
```

---

## Autenticación — modo dev (mock)

Con `AUTH_MODE=mock` el backend acepta header `X-Dev-User`:
```json
{ "oid": "...", "email": "...", "name": "..." }
```

El frontend en modo mock guarda el usuario en `localStorage` bajo la key `mock_user`.

En `AuthContext.tsx`:
- `GET /employees/me` → retorna el Employee del usuario logueado
- `employee.id` = UUID interno de `employees` table
- `employee.user_id` = Azure AD OID (diferente a `employee.id`)

**IMPORTANTE:** Al crear `TimeEntry`, usar siempre `employee.id` como `user_id`,
nunca `employee.user_id`. El campo `time_entries.user_id` es FK a `employees.id`.

---

## Comandos útiles

```bash
# Levantar todo
docker-compose up -d

# Rebuild completo desde cero
docker-compose down && docker-compose build --no-cache && docker-compose up -d

# Rebuild solo frontend
docker-compose build frontend --no-cache && docker-compose up -d frontend

# Ver logs backend
docker-compose logs backend --tail=50 -f

# Acceder a la DB
docker exec -it h_tracker-postgres-1 psql -U hours_user -d hours_tracker

# Correr migraciones manualmente
docker exec h_tracker-backend-1 alembic upgrade head
```

---

## URLs en desarrollo

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8001 |
| Swagger UI | http://localhost:8001/docs |
| PostgreSQL | localhost:5433 |
