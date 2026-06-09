# App: IAM (Identity & Access Management)

## Descripción
Gestión de identidad, roles y permisos. Administra usuarios, sus roles y los permisos asociados a cada rol.

## Modelos
- **User** (AbstractBaseUser) — Usuario del sistema con autenticación por email. `AUTH_USER_MODEL = "iam.User"`
- **Role** — Rol funcional (ESTUDIANTE, DOCENTE, ADMIN, etc.)
- **Permission** — Permiso granular con formato `<módulo>.<acción>`
- **UserRole** — Asignación de rol a usuario
- **RolePermission** — Permisos asociados a un rol

## API Endpoints (`/api/iam/`)
- `POST /login/` — Iniciar sesión (JWT)
- `POST /refresh/` — Refrescar token
- `users/` — CRUD de usuarios
- `roles/` — CRUD de roles
- `permissions/` — CRUD de permisos

## Dependencias
- `people.Person` — Perfil físico asociado al usuario
