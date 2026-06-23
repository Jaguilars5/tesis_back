---
name: Estandarizacion Backend
overview: "Estandarizar el backend Django en cuatro ejes: soft-delete unificado via mixin compartido, rutas normalizadas a plural + acciones en kebab-case, filtrado consistente con DjangoFilterBackend/FilterSet, y formato de respuesta hibrido (renderer para CRUD + ok_response/error_response para acciones). Incluye actualizar los endpoints del frontend web por ser cambios rompedores."
todos:
  - id: core-mixin
    content: "Crear SoftDeleteModelMixin en apps/core/api/mixins.py con accion soft-delete kebab-case que retorna {id, is_active: false}"
    status: in_progress
  - id: softdelete-rollout
    content: Refactorizar base viewsets para heredar el mixin (academic, institutions, grading) y agregar soft-delete a los 7 viewsets con hard delete (User, Role, Person, DocumentType, AttendanceStatus, AbsenceType, StudentRepresentative)
    status: pending
  - id: softdelete-fixes
    content: Mapear permiso soft_delete en los 4 viewsets de grading; normalizar a {id, is_active} los retornos divergentes de behavior/Student/SchoolYear reemplazando destroy override por la accion del mixin
    status: pending
  - id: responses-hybrid
    content: Normalizar acciones custom y rutas de error a ok_response/error_response con msg curado en iam, analytics, students, grading y academic; eliminar anti-patrones {message} y Response(serializer.errors)
    status: pending
  - id: filters-institutions
    content: Crear apps/institutions/api/filters.py y convertir las 5 viewsets de institutions a filterset_class + SearchFilter + OrderingFilter, eliminando search/ordering manual
    status: pending
  - id: filters-attendance-grading
    content: Mover filtros manuales de AttendanceViewSet al AttendanceFilter; arreglar OrderingFilter faltante en EvaluativeActivityViewSet; estandarizar filter_backends para no perder ordering/RoleBased; registrar django_filters en INSTALLED_APPS
    status: pending
  - id: routes-plural
    content: Pluralizar prefijos singulares de router en academic, institutions, students (manteniendo singletons y mass-nouns)
    status: pending
  - id: routes-kebab
    content: Agregar url_path kebab-case explicito a TODAS las @action sin el (behavior soft_delete, 15+ acciones de analytics, by_section, set_primary, etc.)
    status: pending
  - id: routes-doc
    content: Crear ESTANDARIZACION_RUTAS.md con la tabla completa ruta-vieja -> ruta-nueva como fuente de verdad para consumidores
    status: pending
  - id: frontend-constants
    content: Actualizar los *.constants.ts del web-front a los nuevos prefijos plural y acciones kebab-case; verificar SOFT_DELETE; correr typecheck + lint
    status: pending
  - id: verify-tests
    content: Ejecutar la suite de tests del backend con --settings=config.settings.test y validar que no haya regresiones
    status: pending
isProject: false
---

# Plan de Estandarizacion del Backend

Decisiones confirmadas: prefijos a **plural** (rompedor) + acciones a **kebab-case**; soft-delete retorna **`{id, is_active: false}`** en todo; estilo de respuesta **hibrido**; catalogos read-only se quedan como estan; alcance: **backend + frontend web** (la app movil se actualiza despues con el mapeo documentado).

## Eje 1 - Soft-delete unificado

**Problema:** No hay mixin compartido; 7 viewsets con `is_active` hacen hard delete; 4 de `grading` heredan el endpoint pero no mapean permiso (403); formas de retorno divergentes (`{id}`, `{id, is_active}`, `{id, deleted}`, `{id, active}`).

**Accion:**

- Crear `SoftDeleteModelMixin` en [apps/core/api/mixins.py](apps/core/api/mixins.py) (archivo nuevo) con la accion canonica:

```python
class SoftDeleteModelMixin:
    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        instance = self.get_object()
        if hasattr(instance, "is_active"):
            instance.is_active = False
            instance.save(update_fields=["is_active"])
            return ok_response({"id": instance.id, "is_active": False})
        return error_response("Este modelo no soporta borrado logico")
```

- Refactorizar los base viewsets para heredar el mixin y **eliminar** sus copias locales: `BaseAcademicViewSet` ([apps/academic/api/views.py:62](apps/academic/api/views.py)), `BaseInstitutionsViewSet` ([apps/institutions/api/views.py:58](apps/institutions/api/views.py) - hoy usa `Response` plano), `BaseGradingViewSet` ([apps/grading/api/views.py:116](apps/grading/api/views.py)).
- Agregar soft-delete (via mixin) a los 7 viewsets con hard delete: `UserViewSet` ([apps/iam/api/views.py:251](apps/iam/api/views.py)), `RoleViewSet` ([apps/iam/api/views.py:153](apps/iam/api/views.py)), `PersonViewSet` ([apps/people/api/views/views.py:61](apps/people/api/views/views.py)), `DocumentTypeViewSet` ([apps/people/api/views/views.py:36](apps/people/api/views/views.py)), `AttendanceStatusViewSet` ([apps/attendance/api/views.py:220](apps/attendance/api/views.py)), `AbsenceTypeViewSet` ([apps/attendance/api/views.py:254](apps/attendance/api/views.py)), `StudentRepresentativeViewSet` ([apps/students/api/views.py:210](apps/students/api/views.py)).
- Mapear `"soft_delete"` en `action_permissions` de los 4 viewsets de grading: `EvaluationBlockViewSet`, `QualitativeScaleViewSet`, `QualitativeScaleSublevelViewSet`, `ActivityTypeViewSet`.
- Normalizar al estandar `{id, is_active}` los casos divergentes: `behavior` (repos `incident_type_repository.py:17` / `severity_repository.py:17` retornan `{id}`), `Student.destroy` ([apps/students/api/views.py:125](apps/students/api/views.py), `{id, deleted}`) y `SchoolYear.destroy` ([apps/institutions/api/views.py:136](apps/institutions/api/views.py), `{id, active}`). Reemplazar estos `destroy` override por la accion `soft_delete` del mixin.
- Catalogos read-only (`people.City`, `students.SpecialNeedsType`, `students.Kinship`, `students.WithdrawalReason`): **sin cambios**.

## Eje 2 - Rutas: plural + kebab-case (ROMPEDOR)

**Problema:** prefijos mezclan singular/plural; `@action` sin `url_path` caen a snake_case (`behavior /soft_delete/`, todo `analytics`, `by_section`, etc.).

**Accion A - pluralizar prefijos** (solo los singulares; los ya plural y singletons no cambian):

- academic: `subject->subjects`, `academic-period->academic-periods`, `teacher-subject-section->teacher-subject-sections`, `class-schedule->class-schedules`
- institutions: `school-year->school-years`, `academic-sublevel->academic-sublevels`, `section->sections`
- students: `student->students`, `student-representative->student-representatives`, `kinship->kinships`
- Se mantienen singulares por diseno: `analytics/dashboard`, `analytics/scoring-config`, `integration/sync-queue`, `grading/grade-history` (sustantivo incontable), `people/persons` (ya plural-ish).

**Accion B - kebab-case en todas las `@action`:** agregar `url_path` explicito kebab-case a TODA accion sin el (nunca depender del default snake_case). Casos clave: `behavior soft_delete` (`/soft_delete/`->`/soft-delete/`), y las 15+ acciones de `analytics` (`risk_distribution->risk-distribution`, `mark_attended->mark-attended`, `export_csv->export-csv`, `recalculate_period->recalculate-period`, etc.). Tambien unificar `by_section->by-section` y `set_primary->set-primary` en students/academic.

**Accion C - documentar mapeo:** crear `ESTANDARIZACION_RUTAS.md` en la raiz del backend con la tabla completa ruta-vieja -> ruta-nueva como fuente de verdad para consumidores (incluida la app movil).

## Eje 3 - Filtrado consistente

**Problema:** `institutions` (5 viewsets) hace search manual via repositorio; `AttendanceViewSet` es hibrido (FilterSet + query_params manual); `EvaluativeActivityViewSet` declara `ordering` pero no incluye `OrderingFilter`; varios viewsets que setean `filter_backends=[DjangoFilterBackend]` pierden silenciosamente `OrderingFilter` y `RoleBasedFilterBackend`.

**Accion:**

- Convertir las 5 viewsets de `institutions` a `filterset_class` + `SearchFilter` (`search_fields`) + `OrderingFilter`, eliminando el `get_queryset(search=...)` manual y `get_ordering` con alias ([apps/institutions/api/views.py:100-108](apps/institutions/api/views.py)). Crear `apps/institutions/api/filters.py`.
- `AttendanceViewSet`: mover los filtros manuales (`enrollment`, `teacher_subject_section`, `attendance_date`) al `AttendanceFilter` existente y dejar `get_queryset` solo con el scoping de seguridad ([apps/attendance/api/views.py:61-76](apps/attendance/api/views.py)).
- Regla de filter_backends: cuando un viewset declare `filter_backends`, incluir SIEMPRE la tupla completa (`DjangoFilterBackend`, `SearchFilter` si aplica, `OrderingFilter`, `RoleBasedFilterBackend`) para no perder ordering ni seguridad. Arreglar `EvaluativeActivityViewSet` ([apps/grading/api/views.py:233-239](apps/grading/api/views.py)).
- Registrar `django_filters` en `THIRD_PARTY_APPS` de [config/settings/base.py](config/settings/base.py) (limpieza menor).

## Eje 4 - Formato de respuesta hibrido

**Problema:** 5 apps solo usan `Response` plano (el renderer las salva pero deriva `msg` de `str(data)`), 1 usa helpers, 4 mezclan. Anti-patrones: `Response({"message": ...})` en iam, `Response(serializer.errors)` en grading.

**Accion (estilo hibrido):**

- CRUD por defecto: seguir delegando al renderer global (no tocar).
- TODAS las acciones custom y rutas de error: usar `ok_response`/`error_response` con `msg` curado en lugar de `Response(str(e))` o `Response(serializer.errors)`.
- Apps a normalizar: `iam` (quitar `{"message": ...}` -> `ok_response(data, msg=...)`), `analytics` (toda la superficie de acciones de `DashboardViewSet`/scoring), `students`, `institutions soft_delete` (ya cae en Eje 1), y los paths mixtos de `grading`/`academic` (ej. `EvaluativeActivityViewSet.create` que mezcla ambos en el mismo metodo).
- `error_response` para validaciones surfaceando el primer error en `msg`.

## Eje 5 - Frontend web (alineacion rompedora)

**Accion:** actualizar los `*.constants.ts` afectados por el Eje 2 en `web-front/src/features/**`:

- Prefijos plural: `academic-period`->`academic-periods`, `student`->`students`, `section`->`sections`, `school-year`->`school-years`, `class-schedule`->`class-schedules`, `academic-sublevel`->`academic-sublevels`, `teacher-subject-section`->`teacher-subject-sections`, `student-representative`->`student-representatives`, `kinship`->`kinships`, `subject`->`subjects`.
- Acciones analytics a kebab-case en [analytics.constants.ts](web-front/src/features/analytics/analytics.constants.ts) y [dashboard.constants.ts](web-front/src/features/dashboard/dashboard.constants.ts).
- Verificar que `SOFT_DELETE` apunte a `/soft-delete/` ahora que existe la accion en todos (hoy `student`/`section` la referencian sin que exista en backend).
- Ejecutar `npm run typecheck` + `npm run lint` en web-front.

## Orden de ejecucion y verificacion

1. Eje 1 (mixin core + rollout soft-delete).
2. Eje 4 (responses) - se solapa con viewsets ya tocados.
3. Eje 3 (filtros).
4. Eje 2 (rutas) - ultimo por ser rompedor; generar mapeo.
5. Eje 5 (frontend) - inmediatamente despues del Eje 2.
6. Migraciones (no se esperan cambios de modelo). Tests: `python manage.py test --settings=config.settings.test`.
