# Estado actual del proyecto — H_Tracker / Horas+

> Última actualización: 2026-03-16
> Documentación completa de arquitectura en CLAUDE.md

---

## Lo que está implementado y funcionando

### Backend (FastAPI + PostgreSQL)

- [x] Autenticación Azure AD con modo mock para desarrollo
- [x] CRUD completo: Employees, Clients, Projects, ProjectRoles
- [x] Asignación empleado↔proyecto con rol (EmployeeProject)
- [x] Time entries con filtros por usuario, proyecto, fecha, billable, status
- [x] Sistema completo de facturas:
  - [x] Creación manual y auto-generación desde time entries
  - [x] Líneas de factura con snapshot de tarifa
  - [x] Líneas manuales (sin time entries)
  - [x] Honorarios (fees) con archivos adjuntos
  - [x] Gastos con categorías
  - [x] Descuentos por línea (monto fijo o porcentaje)
  - [x] Vínculos factura↔time_entry (evita doble facturación)
  - [x] Export PDF y Excel
  - [x] Estados: draft / sent / paid / cancelled / voided
- [x] Scheduler APScheduler: genera facturas automáticamente el día 5 de cada mes
- [x] Integración Expensify (import de reportes de gastos)
- [x] Categorías de proyectos (area_category, business_unit)
- [x] Roles de app por usuario (employee / admin)
- [x] 6 migraciones Alembic aplicadas

### Frontend (React + TypeScript)

- [x] Dashboard con stats semanales, horas facturables, borradores pendientes
- [x] Weekly Timesheet: entrada de horas diaria por proyecto, billable toggle
- [x] Historial con filtros
- [x] Gestión de proyectos (CRUD + asignaciones + roles)
- [x] Gestión de clientes
- [x] Gestión de empleados (incluyendo roles de app)
- [x] Lista de facturas con filtros de estado y banner de auto-generación
- [x] Creación de factura desde time entries (con check de horas disponibles)
- [x] Creación de factura manual (sin time entries)
- [x] Editor completo de factura (líneas, gastos, descuentos, export)
- [x] Reportes y análisis
- [x] Lazy loading de páginas con React Router v6

### Infraestructura

- [x] Docker Compose (postgres + backend + frontend)
- [x] Nginx reverse proxy con SPA fallback y strip de prefijo /api
- [x] Volumes para datos persistentes (pgdata, uploads)

---

## Bugs conocidos resueltos

| Bug                                              | Fix                                                             | Archivo              |
| :----------------------------------------------- | :-------------------------------------------------------------- | :------------------- |
| Save Changes en Timesheet fallaba con error 500  | `employee.user_id` → `employee.id` al crear TimeEntry           | `Timesheet.tsx:141`  |
| Facturas creadas sin check de horas disponibles  | Pre-check con `/invoices/check-hours`, dialog si no hay entradas | `InvoiceNewPage.tsx` |

---

## Backlog / próximas mejoras

- [ ] Edición de facturas: preview en PDF antes de enviar
- [ ] Notificaciones por email al cambiar estado de factura a "sent"
- [ ] Timesheet: poder agregar proyectos no asignados (con confirmación de admin)
- [ ] Reports: exportar a Excel
- [ ] Dashboard: comparativa mes anterior vs mes actual
- [ ] Roles más granulares (manager puede ver su equipo pero no otros)
- [ ] Audit trail (quién cambió qué en una factura)
