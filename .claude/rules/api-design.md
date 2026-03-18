---
paths:
  - "app/routers/**"
  - "app/schemas/**"
---

# API Design Rules

- All list endpoints must have `skip`/`limit` pagination (max 100, enforce `limit >= 1`)
- Use `status.HTTP_*` constants consistently (not raw `404`, `403`)
- POST that creates a resource returns `201`, not `200`
- Schemas live in `app/schemas/`, not inline in routers
- Role enforcement: use `require_roles(UserRole.ADMIN)` etc. as FastAPI dependencies
- Race-condition-safe operations: use `SELECT FOR UPDATE` (e.g., event capacity checks)
- Error responses: don't leak internal details (e.g., generic "Invalid email or password")
- FK indexes: ensure all foreign key columns have indexes for JOIN performance
