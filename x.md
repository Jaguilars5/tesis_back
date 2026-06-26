# Auditoría de ViewSets — Sistema de Gestión Académica

**Convención de operaciones:** `C`=create, `L`=list, `R`=retrieve/get, `U`=update, `P`=partial_update, `D`=destroy (hard delete), `SD`=acción `soft_delete` / anulación.

**Hallazgo transversal de arquitectura:** todas las clases `Base*ViewSet` (academic, institutions, grading, attendance, behavior, analytics) heredan `DestroyModelMixin` y su `destroy()` ejecuta el `perform_destroy()` por defecto → `instance.delete()` (**borrado físico**). `BaseRepository.delete()` también es físico. Por tanto, salvo que el ViewSet bloquee `destroy` (vía `http_method_names` o un override a 405) o lo reescriba como soft-delete, **toda llamada `DELETE` borra físicamente** y dispara los `on_delete=CASCADE`. El `AnalyticsRouter` enruta `POST→create`, `PUT→update`, `DELETE→destroy` (no enruta `PATCH`).

## Tabla de Auditoría

| ViewSet                             | Modelo                   | Patrón                                  | Ops. actuales                                    | Ops. correctas                                  | Cambio requerido                                                                                    | Riesgo |
| ----------------------------------- | ------------------------ | --------------------------------------- | ------------------------------------------------ | ----------------------------------------------- | --------------------------------------------------------------------------------------------------- | ------ |
| **RiskFactorViewSet**               | RiskFactor               | Catálogo (derivado/seed)                | L, R (C/U/D → 405)                               | L, R                                            | Ninguno (ya read-only)                                                                              | 🟢     |
| **StudentRiskFactorViewSet**        | StudentRiskFactor        | Sistema-exclusivo (derivado)            | L, R (C/U/D → 405)                               | L, R                                            | Ninguno                                                                                             | 🟢     |
| **StudentFeatureSnapshotViewSet**   | StudentFeatureSnapshot   | Sistema-exclusivo (analítico)           | **C**, L, R (U/D → 405)                          | L, R                                            | **Eliminar `create`**                                                                               | 🔴     |
| **StudentRiskScoreViewSet**         | StudentRiskScore         | Sistema-exclusivo (analítico)           | **C, L, R, U, D**                                | L, R (+ actions `calculate`/`batch`/`simulate`) | **Eliminar C/U/D**; dejar solo lectura + acciones async                                             | 🔴     |
| **RiskScoringConfigViewSet**        | RiskScoringConfig        | Catálogo (singleton config)             | L (C/U/D → 405) + `update_config`/`apply_preset` | L + acciones                                    | Ninguno                                                                                             | 🟢     |
| **EarlyAlertViewSet**               | EarlyAlert               | Sistema-exclusivo                       | L, R (C/U/P/D → 405) + `mark_attended`           | L, R + `mark_attended`                          | Ninguno                                                                                             | 🟢     |
| **DashboardViewSet**                | (sin modelo; reportes)   | Sistema-exclusivo (analítico)           | solo `@action` GET + `recalculate_period`        | igual                                           | Ninguno                                                                                             | 🟢     |
| **StudentNoteViewSet**              | StudentNote              | Ingreso controlado                      | C, L, R, U, P, **D**                             | C, L, R, U, P (D bloqueado / anulación)         | **Bloquear `destroy`** (borra nota + CASCADE de `GradeChangeHistory`); usar anulación               | 🔴     |
| **GradeChangeHistoryViewSet**       | GradeChangeHistory       | Sistema-exclusivo (log)                 | L, R (ReadOnly)                                  | L, R                                            | Ninguno                                                                                             | 🟢     |
| **PeriodGradeSummaryViewSet**       | PeriodGradeSummary       | Sistema-exclusivo (derivado)            | C, L, R, U, P (D bloqueado) + `recalculate`      | L, R + `recalculate`                            | Quitar C/U/P; recalcular vía acción                                                                 | 🟡     |
| **EvaluationBlockViewSet**          | EvaluationBlock          | Ingreso controlado / config             | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy` (ya hay `soft_delete`)                                                             | 🟡     |
| **BlockComponentViewSet**           | BlockComponent           | Ingreso controlado / config             | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy`                                                                                    | 🟡     |
| **EvaluativeActivityViewSet**       | EvaluativeActivity       | Ingreso controlado                      | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy`                                                                                    | 🟡     |
| **QualitativeScaleViewSet**         | QualitativeScale         | Catálogo                                | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy`                                                                                    | 🟡     |
| **QualitativeScaleSublevelViewSet** | QualitativeScaleSublevel | Catálogo (asignación)                   | C, L, R, U, P, **D**                             | C, L, R, U, P (D con validación)                | Validar antes de borrar / preferir SD                                                               | 🟡     |
| **ActivityTypeViewSet**             | ActivityType             | Catálogo                                | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy`                                                                                    | 🟡     |
| **AttendanceViewSet**               | Attendance               | Ingreso controlado                      | C, L, R, U, P (D bloqueado) + batch              | C, L, R, U, P                                   | Ninguno (D ya bloqueado); ideal anulación con traza                                                 | 🟢     |
| **AbsenceTypeViewSet**              | AbsenceType              | Catálogo                                | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy`                                                                                    | 🟡     |
| **AttendanceStatusViewSet**         | AttendanceStatus         | Catálogo                                | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy`                                                                                    | 🟡     |
| **ConductIncidentViewSet**          | ConductIncident          | Ingreso controlado                      | C, L, R, U, P (D bloqueado)                      | C, L, R, U, P                                   | Ninguno (D bloqueado, tiene `status`)                                                               | 🟢     |
| **BehaviorEvaluationViewSet**       | BehaviorEvaluation       | Sistema-exclusivo (derivado c/override) | C, L, R, U, P, **D** + `calculate`               | L, R, U(override), `calculate`                  | **Bloquear `destroy`**; C vía `calculate`                                                           | 🟡     |
| **IncidentTypeViewSet**             | IncidentType             | Catálogo                                | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy`                                                                                    | 🟡     |
| **SeverityViewSet**                 | Severity                 | Catálogo                                | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy`                                                                                    | 🟡     |
| **PeriodTypeViewSet**               | PeriodType               | Catálogo                                | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy`                                                                                    | 🟡     |
| **SubjectViewSet**                  | Subject                  | Catálogo                                | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy`                                                                                    | 🟡     |
| **SubjectAcademicConfigViewSet**    | SubjectAcademicConfig    | Catálogo / config                       | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy`                                                                                    | 🟡     |
| **TeacherSubjectSectionViewSet**    | TeacherSubjectSection    | Entidad maestra / asignación            | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy` (referenciado por notas/asistencia)                                                | 🟡     |
| **AcademicPeriodViewSet**           | AcademicPeriod           | Entidad maestra                         | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy` (CASCADE a notas/asistencia)                                                       | 🟡     |
| **SubjectOfferingViewSet**          | SubjectOffering          | Entidad maestra                         | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy`                                                                                    | 🟡     |
| **ClassScheduleViewSet**            | ClassSchedule            | Ingreso controlado / config             | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy`                                                                                    | 🟡     |
| **SchoolYearViewSet**               | SchoolYear               | Entidad maestra                         | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy` (CASCADE a todo el año)                                                            | 🟡     |
| **SectionViewSet**                  | Section                  | Entidad maestra                         | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy`                                                                                    | 🟡     |
| **AcademicSublevelViewSet**         | AcademicSublevel         | Catálogo                                | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy`                                                                                    | 🟡     |
| **AcademicLevelViewSet**            | AcademicLevel            | Catálogo                                | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy`                                                                                    | 🟡     |
| **AcademicGradeViewSet**            | AcademicGrade            | Catálogo                                | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy`                                                                                    | 🟡     |
| **StudentViewSet**                  | Student                  | Entidad maestra                         | C, L, R, U, P, D(=soft) + actions                | C, L, R, U, P, D(soft)                          | Ninguno (`destroy` ya es `deactivate_student`)                                                      | 🟢     |
| **StudentRepresentativeViewSet**    | StudentRepresentative    | Ingreso controlado / relación           | C, L, R, U, P, **D** + `unlink`                  | C, L, R, U, P, `unlink`                         | Quitar `destroy`; usar `unlink` (con servicio)                                                      | 🟡     |
| **EnrollmentViewSet**               | Enrollment               | Entidad maestra / transaccional         | C, L, R, U, P, **D** + SD + withdraw/transfer    | C, L, R, U, P, SD, withdraw                     | **Bloquear `destroy`** (CASCADE a notas/asistencia/incidentes)                                      | 🔴     |
| **SpecialNeedsTypeViewSet**         | SpecialNeedsType         | Catálogo                                | L, R (ReadOnly)                                  | L, R                                            | Ninguno                                                                                             | 🟢     |
| **KinshipViewSet**                  | Kinship                  | Catálogo                                | L, R (ReadOnly)                                  | L, R                                            | Ninguno                                                                                             | 🟢     |
| **CityViewSet**                     | City                     | Catálogo                                | L, R (ReadOnly)                                  | L, R                                            | Ninguno                                                                                             | 🟢     |
| **DocumentTypeViewSet**             | DocumentType             | Catálogo                                | C, L, R, U, P, **D**                             | C, L, R, U, P (sin D)                           | Quitar `destroy`; añadir `is_active`/soft-delete                                                    | 🟡     |
| **PersonViewSet**                   | Person                   | Entidad maestra                         | C, L, R, U, P, **D**                             | C, L, R, U, P (sin D)                           | **Reemplazar `destroy` por `is_active`** (CASCADE a User/Student)                                   | 🔴     |
| **PermissionViewSet**               | Permission               | Catálogo (sistema)                      | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy` (usar SD)                                                                          | 🟡     |
| **RoleViewSet**                     | Role                     | Catálogo (sistema)                      | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | Quitar `destroy` (usar SD)                                                                          | 🟡     |
| **UserViewSet**                     | User                     | Entidad maestra                         | C, L, R, U, P, **D** + SD                        | C, L, R, U, P, SD                               | **`destroy` hace borrado físico** pese a documentarse como "Desactivar"; reemplazar por soft-delete | 🔴     |

> `CustomTokenObtainPairView` / `CustomTokenRefreshView` (iam) son endpoints de autenticación (no exponen modelos) → fuera de alcance, correctos.

---

## Riesgos Críticos 🔴

### 1. `StudentRiskScoreViewSet` → `StudentRiskScore` (tabla analítica con escritura total)

El ViewSet hereda `BaseAnalyticsViewSet` y **no bloquea** `create`/`update`/`destroy`; define `perform_create`/`perform_update` y el `AnalyticsRouter` enruta `POST`, `PUT` y `DELETE`. Un usuario puede inyectar o editar puntajes de riesgo manualmente, corrompiendo las métricas que produce el motor (`calculate`/`batch_calculate`).

**Corrección concreta:** dejarlo de solo lectura conservando las `@action`. Sobrescribir las escrituras:

```python
class StudentRiskScoreViewSet(BaseAnalyticsViewSet):
    def create(self, request, *a, **k):
        return error_response("Los puntajes se generan vía calculate/batch_calculate", status_code=405)
    def update(self, request, *a, **k):
        return error_response("Operación no permitida", status_code=405)
    def destroy(self, request, *a, **k):
        return error_response("Operación no permitida", status_code=405)
    # eliminar perform_create / perform_update
```

(Mantener `calculate`, `batch_calculate`, `simulate`.)

### 2. `StudentFeatureSnapshotViewSet` → `StudentFeatureSnapshot` (snapshot ML editable por `create`)

Bloquea `update`/`destroy` pero **deja `create` abierto** (`perform_create` invoca el repositorio). Permitir crear snapshots de features a mano contamina el dataset de entrenamiento/inferencia.

**Corrección concreta:** convertir a estrictamente read-only.

```python
def create(self, request, *a, **k):
    return error_response("Los snapshots se generan automáticamente", status_code=405)
```

### 3. `StudentNoteViewSet` → `StudentNote` (borrado físico de calificación + del historial)

`destroy` ejecuta borrado físico, y como `GradeChangeHistory.student_note` es `on_delete=CASCADE`, **se pierde también la trazabilidad de cambios**. Además el ViewSet hace `soft_delete = None`, anulando la acción de borrado lógico heredada. La nota ya posee `manually_overridden` para anulación.

**Corrección concreta:** bloquear `destroy` y usar anulación con traza.

```python
class StudentNoteViewSet(BaseGradingViewSet):
    http_method_names = ["get", "post", "put", "patch", "head", "options"]  # sin "delete"
```

Exponer en su lugar una acción `anular` que marque `manually_overridden=True` y registre `GradeChangeHistory` (igual que `AttendanceViewSet`/`ConductIncidentViewSet`, que ya bloquean `delete`).

### 4. `EnrollmentViewSet` → `Enrollment` (borrado físico de matrícula con CASCADE masivo)

Es un `ModelViewSet` con `destroy` por defecto (físico). Borrar una matrícula **elimina en cascada notas (`StudentNote.enrollment` → CASCADE), asistencias, incidentes y evaluaciones** asociados. Ya existen `withdraw`, `transfer` y `soft_delete`, por lo que `destroy` es innecesario y peligroso.

**Corrección concreta:**

```python
class EnrollmentViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "put", "patch", "head", "options"]  # sin "delete"
```

Canalizar las bajas por `withdraw` / `soft_delete` (cambio de estado con trazabilidad).

### 5. `PersonViewSet` → `Person` (entidad maestra con borrado físico)

`ModelViewSet` completo sin override de `destroy` ni `is_active`. `Person` es entidad raíz referenciada por `User`/`Student`; el borrado físico rompe integridad histórica en cascada.

**Corrección concreta:** quitar `delete` y migrar a borrado lógico.

```python
class PersonViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "put", "patch", "head", "options"]
```

Añadir campo `is_active` + acción `soft-delete` (patrón `SoftDeleteModelMixin`).

### 6. `UserViewSet` → `User` (borrado físico documentado falsamente como "Desactivar")

El `extend_schema` declara `destroy=… "Desactivar usuario"`, pero **no hay override de `destroy`**: se ejecuta el borrado físico de `ModelViewSet`, con CASCADE sobre toda la actividad del usuario. El `SoftDeleteModelMixin` solo añade la acción `soft-delete`, no cambia `destroy`.

**Corrección concreta:** alinear el comportamiento con la documentación.

```python
class UserViewSet(SoftDeleteModelMixin, viewsets.ModelViewSet):
    http_method_names = ["get", "post", "put", "patch", "head", "options"]  # sin "delete"
    # o bien:
    def destroy(self, request, *a, **k):
        user = self.service.deactivate_user(k["pk"])  # is_active=False
        return ok_response({"id": user.id, "is_active": False})
```

---

## Patrón sistémico recomendado (resuelve casi todos los 🟡)

La mayoría de los 🟡 comparten una causa raíz: **`destroy` físico coexistiendo con una acción `soft_delete`**. En lugar de parchear ViewSet por ViewSet, conviene corregir las clases base para que el borrado lógico sea el comportamiento por defecto:

- **Opción A (mínima, por ViewSet):** añadir `http_method_names = [..., sin "delete"]` en cada catálogo/entidad maestra, dejando `soft-delete` como única vía de baja.
- **Opción B (estructural, recomendada):** sobrescribir `destroy()` en `Base{Academic,Institutions,Grading,Attendance,Behavior}ViewSet` para que ejecute borrado lógico (`is_active=False`) en lugar de `perform_destroy()`, de modo que todas las subclases hereden la baja segura sin duplicar `soft_delete`.

Los ViewSets que ya son ejemplares y sirven de referencia: `EarlyAlertViewSet`, `RiskScoringConfigViewSet`, `GradeChangeHistoryViewSet` (read-only estricto), `AttendanceViewSet` y `ConductIncidentViewSet` (`http_method_names` sin `delete`), y `StudentViewSet` (`destroy` reescrito como desactivación).
