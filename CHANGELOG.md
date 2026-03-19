# Horas+ — Changelog

Historial de cambios por fecha de implementación.
Formato: `[Tipo] Descripción — Archivos afectados`

---

## 2026-03-16

### Corrección crítica: Creación de facturas fallaba silenciosamente

**Problema:** Al hacer clic en "Create Invoice" el sistema mostraba el error genérico
*"Something went wrong creating the invoice"* sin ningún detalle. La causa raíz era
una divergencia entre el esquema de la base de datos y los modelos SQLAlchemy,
producto de que la migración 003 quedó registrada en `alembic_version` pero su DDL
no se persistió en PostgreSQL (rollback de transacción en el arranque).

**Columnas faltantes detectadas:**

| Tabla | Columna | Tipo | Estado |
|---|---|---|---|
| `invoices` | `cap_amount` | `NUMERIC(12,2) NULL` | Faltaba |
| `invoice_lines` | `discount_value` | `NUMERIC(10,2) NOT NULL DEFAULT 0` | Faltaba |
| `invoice_lines` | `user_id` | FK → `employees.id` NOT NULL | Bloqueaba líneas manuales |
| `invoice_lines` | `discount_type` | `NOT NULL DEFAULT 'fixed'` | Incompatible con modelo nullable |

#### `Backend/alembic/versions/011_schema_repair.py` *(nuevo)*
- Agrega `invoices.cap_amount NUMERIC(12,2) NULL` con `IF NOT EXISTS`
- Agrega `invoice_lines.discount_value NUMERIC(10,2) NOT NULL DEFAULT 0` con `IF NOT EXISTS`
- Migra valores del campo `discount` (legacy) a `discount_value` donde corresponde
- Elimina `NOT NULL` y `DEFAULT 'fixed'` de `invoice_lines.discount_type` para coincidir con el modelo
- Elimina FK constraint `invoice_lines_user_id_fkey` y el `NOT NULL` de `invoice_lines.user_id`
  (permite crear líneas manuales sin empleado asociado)

#### `Backend/models/invoice_lines.py`
- `user_id`: eliminado `ForeignKey("employees.id")`, cambiado a `nullable=True`
- Eliminado `relationship("Employee")` que dependía de la FK

#### `Backend/schemas/invoice_lines.py`
- `user_id`: cambiado de `str` (requerido) a `Optional[str] = None`

#### `Frontend/src/pages/invoices/InvoiceManualPage.tsx`
- Líneas manuales ahora envían `user_id: null` en lugar de `user_id: ''`
  (la cadena vacía violaba el FK constraint)

#### `Frontend/src/pages/invoices/InvoiceNewPage.tsx`
#### `Frontend/src/pages/invoices/InvoiceManualPage.tsx`
- Mensajes de error mejorados: el `catch` mapea códigos HTTP conocidos (401, 422, 500)
  a mensajes descriptivos; para otros errores muestra el `error.message` real
  en lugar del genérico "Something went wrong"

---

### Feature: Advertencia inline + formulario de factura en blanco

**Contexto:** El flujo de creación de facturas mostraba un diálogo popup cuando un
proyecto no tenía horas. Se rediseñó para mostrar el estado inline directamente
en el formulario, y el formulario manual se reescribió con todos los campos
solicitados por el producto.

#### `Frontend/src/pages/invoices/InvoiceNewPage.tsx` *(reescrito)*
**Antes:** Mostraba un `Dialog` popup cuando no había horas registradas.
**Ahora:**
- Al seleccionar un proyecto se dispara automáticamente `GET /invoices/check-hours`
  (via `useEffect` con cancelación de peticiones obsoletas)
- **Estado "verificando":** spinner + texto "Checking available hours…"
- **Estado "hay horas":** tarjeta verde con recuento de entradas y horas totales
  + botones Cancel / Create Invoice
- **Estado "sin horas":** tarjeta ámbar con advertencia inline y botones
  Cancel / Create Blank Invoice (navega a `/invoices/new/manual?project_id=…`)
- Sin ningún popup/dialog

#### `Frontend/src/pages/invoices/InvoiceManualPage.tsx` *(reescrito completo)*
**Antes:** Formulario mínimo con nombre, rol, horas y tarifa.
**Ahora — secciones:**

**Invoice Details (grid 3 columnas):**
- Proyecto (select, pre-seleccionado desde URL param `?project_id=`)
- Cliente (auto-completado desde proyecto, campo de sólo lectura)
- Número de factura (editable, sugerido automáticamente como `INV-YYYY-MM-001`)
- Fecha de factura (date picker, valor por defecto: hoy)
- Fecha de vencimiento (date picker)
- Estado (dropdown: Draft / Sent / Paid)
- Periodo inicio / Periodo fin (date pickers, opcionales)

**Line Items (tabla dinámica):**
- Columnas: Descripción, Cantidad/Horas, Tarifa Unitaria, Monto
- Monto se calcula automáticamente (`qty × rate`)
- Si el usuario edita el monto directamente → flag `manualAmount: true`,
  borde ámbar, sin recalcular al cambiar qty/rate
- Si se cambia qty o rate → se limpia el flag y se recalcula
- Botón "+ Add Line" agrega filas vacías
- Botón trash por fila (deshabilitado cuando sólo hay una)

**Totales:**
- Subtotal (suma de todos los montos)
- Descuento (%) con campo inline; muestra monto en rojo si > 0
- Total final en color primario

**Notas (dos tarjetas side-by-side):**
- Notas para el cliente (se incluyen en la factura)
- Notas internas (se almacenan con prefijo `[Internal]`, no se muestran al cliente)

**Flujo de guardado:**
1. `POST /invoices` (crea borrador con project_id)
2. `POST /invoice-lines/bulk` (crea líneas con `user_id: null`)
3. `PUT /invoices/:id` (actualiza número, fechas, estado, subtotal, descuento, total, notas)
4. Navega a `/invoices/:id/edit`

---

### Feature: Sistema de notificaciones en la aplicación

#### Base de datos

**`Backend/alembic/versions/010_notifications.py`** *(nuevo)*
- Crea tabla `notifications`:
  ```
  id VARCHAR PK | user_id VARCHAR | type VARCHAR | title VARCHAR
  message TEXT | link VARCHAR | is_read BOOLEAN DEFAULT false | created_at TIMESTAMP
  ```
- Índice en `notifications.user_id`

#### Backend

**`Backend/models/notifications.py`** *(nuevo)*
- Modelo SQLAlchemy `Notification` mapeado a la tabla `notifications`
- `user_id` = `employees.id` (UUID interno, no el OID de Azure AD)

**`Backend/schemas/notifications.py`** *(nuevo)*
- `NotificationOut`: schema de salida con todos los campos

**`Backend/services/notifications.py`** *(nuevo)*
- `create_notification(db, user_id, type, title, message, link)` — crea una notificación
- `notify_invoice_generated(db, invoice_id, invoice_number, project_name, manager_id, total)` —
  helper que llama a `create_notification` con el mensaje y link correctos para el manager
- `get_notifications(db, user_id)` — lista notificaciones de un usuario (más recientes primero)
- `mark_read(db, notification_id, user_id)` — marca una notificación como leída
- `mark_all_read(db, user_id)` — marca todas como leídas, retorna el conteo

**`Backend/routers/notifications.py`** *(nuevo)*
- `GET /notifications?user_id=` — lista notificaciones del usuario
- `PATCH /notifications/{id}/read?user_id=` — marca una como leída
- `POST /notifications/mark-all-read?user_id=` — marca todas como leídas

**`Backend/main.py`**
- Registra `notifications_router` en la aplicación FastAPI

**`Backend/services/invoice_generator.py`**
- Después de crear cada factura auto-generada, llama a `notify_invoice_generated`
  si el proyecto tiene `manager_id` asignado

**`Backend/routers/invoice.py`**
- `POST /invoices/` (creación manual): llama a `notify_invoice_generated` al manager
  del proyecto tras crear la factura

#### Frontend

**`Frontend/src/types/index.ts`**
- Agrega interfaz `Notification`: `id, user_id, type, title, message, link, is_read, created_at`

**`Frontend/src/hooks/useNotifications.ts`** *(nuevo)*
- `useNotifications(userId)` — query con polling cada 30s (`refetchInterval: 30_000`)
- `useMarkNotificationRead(userId)` — mutation PATCH
- `useMarkAllNotificationsRead(userId)` — mutation POST

**`Frontend/src/components/NotificationBell.tsx`** *(nuevo)*
- Icono de campana en el header con badge de conteo de no leídas (máx. "9+")
- Popover con lista de notificaciones:
  - Punto azul para las no leídas
  - Indentación distinta para leídas vs no leídas
  - Tiempo relativo con `date-fns/formatDistanceToNow`
  - Al hacer clic: marca como leída + navega al `link` si existe
- Botón "Mark all read" visible sólo cuando hay no leídas

**`Frontend/src/components/layout/MainLayout.tsx`**
- Importa e incluye `<NotificationBell />` en el header, a la izquierda del nombre de usuario

---

### Feature: Página de detalle de factura (`/invoices/:id`)

#### `Frontend/src/pages/invoices/InvoiceDetailPage.tsx` *(nuevo)*
Vista de sólo lectura de una factura con acciones de estado.

**Secciones:**
- Breadcrumb: Invoices → número de factura
- Header: número, badge de estado, proyecto y cliente como subtítulo
- Tarjetas de metadatos: Issue Date, Due Date, Client, Project
- Tabla de líneas de horas (columnas: Employee, Hours, Rate, Discount, Amount)
- Tabla de honorarios/fees si existen
- Tabla de gastos/expenses si existen
- Totales: subtotal de horas, descuento, fees, gastos, **Total**
- Notas (si existen)

**Acciones por estado:**

| Estado actual | Acciones disponibles |
|---|---|
| Draft | Mark as Sent · Cancel · [botón Edit] |
| Sent | Mark as Paid · Revert to Draft · Void |
| Paid | — (terminal) |
| Cancelled | Revert to Draft |
| Voided | — (terminal) |

- Botones Export PDF y Export XLSX en todos los estados
- El botón Edit sólo aparece en facturas Draft

#### `Frontend/src/App.tsx`
- Agrega lazy import de `InvoiceDetailPage`
- Agrega ruta `/invoices/:invoiceId` (antes de `/invoices/:invoiceId/edit`)

#### `Frontend/src/pages/Invoices.tsx`
- Clic en fila navega a `/invoices/:id` (vista detalle) en lugar de ir directamente al editor
- El icono `ChevronRight` también navega a la vista detalle

---

### Fix: Scheduler cambiado al día 3 del mes a las 08:00

#### `Backend/services/invoice_scheduler.py`
- `CronTrigger(day=5, hour=0)` → `CronTrigger(day=3, hour=8, minute=0)`
- Mensaje de log actualizado

#### `Backend/routers/invoice.py` — endpoint `/scheduler-status`
- `next_run` calculado usando `day=3` en lugar de `day=5`

#### `Frontend/src/pages/Invoices.tsx`
- Banner de pre-generación: `dayOfMonth <= 3` en lugar de `<= 5`
- Texto del banner: "auto-generated on the 3rd"

---

### Fix: `check-hours` sin periodo devolvía cero entradas

**Problema:** El endpoint `GET /invoices/check-hours` filtraba por el mes anterior
cuando no se proporcionaban `period_start`/`period_end`. Esto causaba que entradas
del mes actual no se encontraran y el flujo de creación mostrara "no hay horas".

#### `Backend/routers/invoice.py`
- Eliminado el filtro de fechas por defecto. Sin `period_start`/`period_end`
  la query devuelve **todas** las entradas no vinculadas y billables del proyecto.

---

### Fix: Nombre de empleado mostraba "Unknown" en líneas de factura

**Problema:** `InvoiceNewPage` buscaba el empleado con `e.user_id === entry.user_id`
pero `time_entries.user_id` es FK a `employees.id` (UUID interno), no al Azure OID.

#### `Frontend/src/pages/invoices/InvoiceNewPage.tsx`
- Lookup cambiado a `e.id === entry.user_id`

---

## 2026-03-15 — Sprint anterior

### Feature: Perfil de empleado con Skills y Asignaciones

#### Base de datos

**`Backend/alembic/versions/008_employee_extended_profile_and_skills.py`** *(nuevo)*
- Extiende tabla `employees` con 24 nuevas columnas:
  - **Personal:** `first_name`, `last_name`, `date_of_birth`, `gender`, `personal_email`,
    `personal_phone`, `id_number`, `emergency_contact_name`, `emergency_contact_phone`
  - **Ubicación:** `country`, `state`, `city`, `timezone`, `street_address`, `zip_code`,
    `work_mode`
  - **Corporativo:** `corporate_phone`, `employee_code`, `employment_type`, `start_date`,
    `end_date`, `employment_status`, `billing_currency`, `notes`
- Crea tabla `skill_catalog`: `id, name, category, created_at`
- Crea tabla `employee_skills`: `id, employee_id (FK CASCADE), skill_catalog_id (FK),
  skill_name, category, proficiency_level (1–4), years_experience, certified,
  certificate_name, cert_expiry_date, notes, created_at`

**`Backend/alembic/versions/009_drop_employee_hourly_rate.py`** *(nuevo)*
- `ALTER TABLE employees DROP COLUMN IF EXISTS hourly_rate`

#### Modelos

**`Backend/models/employees.py`**
- Eliminado `hourly_rate`
- Agregadas 24 columnas nuevas (ver migración 008)
- Relación `skills = relationship("EmployeeSkill", cascade="all, delete-orphan")`

**`Backend/models/skill_catalog.py`** *(nuevo)*
- Modelo `SkillCatalog`

**`Backend/models/employee_skills.py`** *(nuevo)*
- Modelo `EmployeeSkill` con niveles de proficiencia 1–4

**`Backend/models/__init__.py`**
- Importa `SkillCatalog`, `EmployeeSkill`, `Notification`

#### Schemas

**`Backend/schemas/employees.py`**
- Eliminado `hourly_rate` de `EmployeeBase` y `EmployeeUpdate`
- Agregados todos los campos del perfil extendido

**`Backend/schemas/skills.py`** *(nuevo)*
- `SkillCatalogOut`, `SkillCatalogCreate`
- `EmployeeSkillBase`, `EmployeeSkillCreate`, `EmployeeSkillUpdate`, `EmployeeSkillOut`

#### Servicios

**`Backend/services/skills.py`** *(nuevo)*
- `list_skill_catalog`, `get_or_create_skill_catalog`
- `get_employee_skills`, `create_employee_skill`, `update_employee_skill`, `delete_employee_skill`

#### Routers

**`Backend/routers/employees.py`**
- `GET /{employee_id}/skills` — lista skills del empleado
- `POST /{employee_id}/skills` — crea skill
- `PATCH /{employee_id}/skills/{skill_id}` — actualiza skill
- `DELETE /{employee_id}/skills/{skill_id}` — elimina skill

**`Backend/routers/skill_catalog.py`** *(nuevo)*
- `GET /skill-catalog` — lista catálogo
- `POST /skill-catalog` — crea entrada en catálogo

**`Backend/main.py`**
- Registra `skill_catalog_router` y `notifications_router`

**`Backend/seed.py`**
- Eliminado `hourly_rate=Decimal(...)` de todos los constructores de `Employee`

#### Frontend — Tipos

**`Frontend/src/types/index.ts`**
- Eliminado `hourly_rate: number` de `Employee`
- Agregados 24 campos del perfil extendido a `Employee`
- Nuevas interfaces: `SkillCatalog`, `EmployeeSkill`

#### Frontend — Hooks

**`Frontend/src/hooks/useSkills.ts`** *(nuevo)*
- `useSkillCatalog()` — catálogo global
- `useEmployeeSkills(employeeId)` — skills del empleado
- `useCreateEmployeeSkill`, `useUpdateEmployeeSkill`, `useDeleteEmployeeSkill`

**`Frontend/src/hooks/useEmployees.ts`**
- Eliminado `hourly_rate` del payload de `useCreateEmployee`

#### Frontend — Páginas

**`Frontend/src/pages/employees/EmployeeFormPage.tsx`** *(nuevo)*
- Maneja rutas `/employees/new` y `/employees/:employeeId/edit`
- Tres secciones: Personal Information, Location, Corporate Information
- Guard de cambios no guardados al cancelar

**`Frontend/src/pages/employees/EmployeeProfilePage.tsx`** *(nuevo)*
- Tres tabs:
  - **Profile** — vista de sólo lectura en grilla de campos
  - **Skills** — RadarChart de categorías (renderizado solo con ≥ 3 categorías),
    listado agrupado por categoría, diálogo de añadir/editar con autocompletado del catálogo,
    niveles de proficiencia 1–4 con etiquetas Beginner/Intermediate/Advanced/Expert
  - **Projects** — tarjetas de proyectos asignados (navegan al detalle del proyecto)

**`Frontend/src/pages/Employees.tsx`**
- Eliminados todos los diálogos de crear/editar empleado
- "New Employee" → `navigate('/employees/new')`
- Clic en fila → `navigate('/employees/${emp.id}')`
- Mantenido diálogo de cambio de rol (app role)
- Fix: `getAssignedProjectsCount` usa `emp.id` (era `emp.user_id`)

**`Frontend/src/App.tsx`**
- Lazy imports: `EmployeeFormPage`, `EmployeeProfilePage`, `InvoiceDetailPage`
- Rutas nuevas: `/employees/new`, `/employees/:employeeId`, `/employees/:employeeId/edit`,
  `/invoices/:invoiceId`

#### Frontend — Componentes

**`Frontend/src/components/EmployeeProjectsDialog.tsx`**
- Fix crítico: `employee.user_id` → `employee.id` en filtro de asignaciones y `bulkAssign`
  (en Azure AD mode `user_id` ≠ `id`; en mock son iguales, ocultando el bug)

**`Frontend/src/pages/Billing.tsx`**
- `emp.hourly_rate` → `0` (página legacy, redirige a `/invoices`)

---

## Notas de arquitectura

### Patrón FK crítico: `employee.id` vs `employee.user_id`

**Regla:** Todas las FK en tablas de datos (`time_entries.user_id`,
`employee_projects.user_id`, `invoice_lines.user_id`, `notifications.user_id`)
apuntan a `employees.id` (UUID interno de la tabla `employees`).

`employees.user_id` es el OID de Azure AD y se usa **sólo para autenticación**.
En modo `AUTH_MODE=mock` ambos valores coinciden, lo que puede ocultar bugs
que sólo aparecen con Azure AD real.

### Migraciones — estado actual

| Revisión | Descripción |
|---|---|
| 001 | Schema inicial — todas las tablas core |
| 002 | Alineación con frontend |
| 003 | `cap_amount`, descuentos en líneas, tabla `invoice_expenses` *(DDL no persistió)* |
| 004 | Fase 2 — campos adicionales en project/client/employee |
| 005 | `manager_id` en proyectos, tabla `project_categories` |
| 006 | Tabla `scheduler_log` |
| 007 | Campos extendidos en clientes |
| 008 | Perfil extendido de empleados, `skill_catalog`, `employee_skills` |
| 009 | Elimina `employees.hourly_rate` |
| 010 | Tabla `notifications` |
| 011 | **Reparación de schema:** agrega columnas faltantes de 003, corrige `invoice_lines.user_id` |
