# App: People

## Descripción
Gestión de personas físicas y sus tipos de documento.

## Modelos
- **Person** — Persona física con datos personales (nombres, documento, email)
- **DocumentType** — Catálogo de tipos de documento (CC, CE, PP, etc.)

## API Endpoints (`/api/people/`)
- `persons/` — CRUD de personas
- `document-types/` — CRUD de tipos de documento

## Dependencias
- `people.DocumentType` → Movido aquí desde sus apps de dominio/
