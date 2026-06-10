"""
Tests de integración y unitarios adicionales para cubrir los vacíos (gaps) del módulo grading.

Prueba el control de acceso RBAC, respuestas de vistas (ViewSets) y formato de respuesta
estandarizado para los 11 ViewSets restantes.
"""

from datetime import date
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.iam.models import Permission, Role, RolePermission, User, UserRole
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.core.constants.permissions import grading, behavior

from apps.grading.models import GradeType, QualitativeScale, EvaluationType, ActivityType, RecoveryProcessType
from apps.grading.models import (
    StudentNote, EvaluationBlock, BlockComponent,
    ComponentIndicator, EvaluativeActivity, GradeChangeHistory, PeriodGradeSummary,
    RecoveryProcess, ProjectNote
)
from apps.academic.models import (PeriodType,
    AcademicPeriod, Subject, SubjectAcademicConfig, SubjectOffering, TeacherSubjectSection,
    InterdisciplinaryProject
)
from apps.institutions.models import SchoolYear, AcademicGrade, AcademicLevel, AcademicSublevel, Section
from apps.students.models import Enrollment, EnrollmentStatus


class GradingAPIGapsTest(TestCase):
    """Suite de pruebas de integración para cubrir brechas en la API de Grading."""

    def setUp(self):
        self.client = APIClient()

        # 1. Configuración básica de Institución y Academia
        self.school_year = SchoolYear.objects.create(
            name="2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_sublevel = AcademicSublevel.objects.create(
            academic_level=self.academic_level, code="BASICA", name="Básica"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_sublevel=self.academic_sublevel,
            name="7",
            sequence_order=1,
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.academic_grade,
            parallel="A",
            capacity=30,
        )
        self.subject = Subject.objects.create(
            name="Matemática",
            code="MAT-7A",
        )
        self.period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            name="P1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )

        # 2. Usuarios y Roles
        self.admin = create_test_user(
            email="admin_grading@test.com",
            dni="9999999991",
            names="Admin",
            last_names="Grading",
            is_superuser=True,
        )

        # Usamos user_type="ADMIN" para omitir filtros de seguridad de fila (RLS)
        # pero mantener verificación estricta de permisos RBAC en HasPermission
        self.authorized_user = create_test_user(
            email="auth_grading@test.com",
            dni="9999999992",
            names="Authorized",
            last_names="Grading",
            is_superuser=False,
        )

        self.noperm_user = create_test_user(
            email="noperm_grading@test.com",
            dni="9999999993",
            names="NoPerm",
            last_names="Grading",
            is_superuser=False,
        )

        # 3. Creación y asignación de permisos
        self.role_authorized = Role.objects.create(name="Authorized Role", code="ADMIN")
        UserRole.objects.create(user=self.authorized_user, role=self.role_authorized)

        # Permisos de Lectura
        self.perm_view_macro = Permission.objects.create(
            code=grading.VIEW_EVALUATION_MACRO, module="grading", description="Ver macro"
        )
        self.perm_view_criteria = Permission.objects.create(
            code=grading.VIEW_EVALUATION_CRITERIA, module="grading", description="Ver criteria"
        )
        self.perm_view_subcriteria = Permission.objects.create(
            code=grading.VIEW_EVALUATION_SUBCRITERIA, module="grading", description="Ver subcriteria"
        )
        self.perm_view_assignment = Permission.objects.create(
            code=grading.VIEW_CLASS_ASSIGNMENT, module="grading", description="Ver asignacion"
        )
        self.perm_view_history = Permission.objects.create(
            code=grading.VIEW_GRADE_HISTORY, module="grading", description="Ver historial"
        )
        self.perm_view_summary = Permission.objects.create(
            code=grading.VIEW_GRADE_SUMMARY, module="grading", description="Ver resumen"
        )
        self.perm_view_recovery = Permission.objects.create(
            code=grading.VIEW_RECOVERY_PROCESS, module="grading", description="Ver recuperacion"
        )
        self.perm_view_diagnostic = Permission.objects.create(
            code=behavior.VIEW_DIAGNOSTIC_EVALUATION, module="behavior", description="Ver diagnostico"
        )
        self.perm_view_project = Permission.objects.create(
            code=grading.VIEW_PROJECT_NOTE, module="grading", description="Ver nota proyecto"
        )
        self.perm_view_scale = Permission.objects.create(
            code=grading.VIEW_QUALITATIVE_SCALE, module="grading", description="Ver escalas"
        )
        self.perm_view_type = Permission.objects.create(
            code=grading.VIEW_GRADE_TYPE, module="grading", description="Ver tipos"
        )
        self.perm_view_eval_type = Permission.objects.create(
            code=grading.VIEW_EVALUATION_TYPE, module="grading", description="Ver tipos evaluación"
        )
        self.perm_view_act_type = Permission.objects.create(
            code=grading.VIEW_ACTIVITY_TYPE, module="grading", description="Ver tipos actividad"
        )
        self.perm_view_promo = Permission.objects.create(
            code=grading.VIEW_PROMOTION_STATUS, module="grading", description="Ver estados promoción"
        )
        self.perm_view_rec_type = Permission.objects.create(
            code=grading.VIEW_RECOVERY_PROCESS_TYPE, module="grading", description="Ver tipos recuperación"
        )

        # Permisos de Escritura/Creación
        self.perm_create_macro = Permission.objects.create(
            code=grading.CREATE_EVALUATION_MACRO, module="grading", description="Crear macro"
        )
        self.perm_create_criteria = Permission.objects.create(
            code=grading.CREATE_EVALUATION_CRITERIA, module="grading", description="Crear criterio"
        )
        self.perm_create_subcriteria = Permission.objects.create(
            code=grading.CREATE_EVALUATION_SUBCRITERIA, module="grading", description="Crear subcriterio"
        )
        self.perm_create_assignment = Permission.objects.create(
            code=grading.CREATE_CLASS_ASSIGNMENT, module="grading", description="Crear actividad"
        )
        self.perm_create_summary = Permission.objects.create(
            code=grading.CREATE_GRADE_SUMMARY, module="grading", description="Crear resumen"
        )
        self.perm_create_recovery = Permission.objects.create(
            code=grading.CREATE_RECOVERY_PROCESS, module="grading", description="Crear recuperacion"
        )
        self.perm_create_diagnostic = Permission.objects.create(
            code=behavior.CREATE_DIAGNOSTIC_EVALUATION, module="behavior", description="Crear diagnostica"
        )
        self.perm_create_project = Permission.objects.create(
            code=grading.CREATE_PROJECT_NOTE, module="grading", description="Crear nota proyecto"
        )
        self.perm_create_eval_type = Permission.objects.create(
            code=grading.CREATE_EVALUATION_TYPE, module="grading", description="Crear tipo evaluación"
        )
        self.perm_create_act_type = Permission.objects.create(
            code=grading.CREATE_ACTIVITY_TYPE, module="grading", description="Crear tipo actividad"
        )
        self.perm_create_promo = Permission.objects.create(
            code=grading.CREATE_PROMOTION_STATUS, module="grading", description="Crear estado promoción"
        )
        self.perm_create_rec_type = Permission.objects.create(
            code=grading.CREATE_RECOVERY_PROCESS_TYPE, module="grading", description="Crear tipo recuperación"
        )
        self.perm_create_grade_type = Permission.objects.create(
            code=grading.CREATE_GRADE_TYPE, module="grading", description="Crear tipo calificación"
        )
        self.perm_create_qual_scale = Permission.objects.create(
            code=grading.CREATE_QUALITATIVE_SCALE, module="grading", description="Crear escala cualitativa"
        )

        # Asociar todos los permisos creados al rol del usuario autorizado
        for perm in [
            self.perm_view_macro, self.perm_view_criteria, self.perm_view_subcriteria,
            self.perm_view_assignment, self.perm_view_history, self.perm_view_summary,
            self.perm_view_recovery, self.perm_view_diagnostic, self.perm_view_project,
            self.perm_view_scale, self.perm_view_type, self.perm_view_eval_type,
            self.perm_view_act_type, self.perm_view_promo, self.perm_view_rec_type,
            self.perm_create_macro, self.perm_create_criteria, self.perm_create_subcriteria,
            self.perm_create_assignment, self.perm_create_summary, self.perm_create_recovery,
            self.perm_create_diagnostic, self.perm_create_project, self.perm_create_eval_type,
            self.perm_create_act_type, self.perm_create_promo, self.perm_create_rec_type,
            self.perm_create_grade_type, self.perm_create_qual_scale
        ]:
            RolePermission.objects.create(role=self.role_authorized, permission=perm)

        # 4. Datos específicos del módulo Academic y Students
        subj_config = SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.academic_grade,
            weekly_hours=5,
            pedagogical_order=1,
        )
        offering = SubjectOffering.objects.create(
            school_year=self.school_year,
            section=self.section,
            subject_academic_config=subj_config,
        )
        self.teacher_subject_section = TeacherSubjectSection.objects.create(
            user=self.authorized_user,
            subject_offering=offering,
        )
        self.offering = offering
        self.student = create_test_student(
            document_number="0987654321",
            names="Carlos",
            last_names="Meza",
            birth_date=date(2011, 4, 10),
        )
        enr_status, _ = EnrollmentStatus.objects.get_or_create(
            code="ACT", defaults={"name": "Activa"}
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            section=self.section,
            school_year=self.school_year,
            enrollment_status=enr_status,
        )

        # Proyecto interdisciplinario de prueba
        self.project = InterdisciplinaryProject.objects.create(
            academic_period=self.period,
            title="Proyecto 1",
            start_date=date(2025, 1, 15),
            delivery_date=date(2025, 3, 1),
        )

        # 5. Inicialización de catálogos y estructuras de Grading
        self.grade_type, _ = GradeType.objects.get_or_create(code="NUM", defaults={"name": "Numérica"})
        self.qualitative_scale = QualitativeScale.objects.create(
            code="DA", description="Domina Aprendizaje", numeric_equivalence=Decimal("9.00")
        )
        self.eval_type_for = EvaluationType.objects.create(
            code="FORMATIVA", name="Formativa"
        )
        self.eval_type_sum = EvaluationType.objects.create(
            code="SUMATIVA", name="Sumativa"
        )
        self.activity_type_tarea = ActivityType.objects.create(
            code="TAREA", name="Tarea"
        )
        self.activity_type_examen = ActivityType.objects.create(
            code="EXAMEN", name="Examen"
        )
        self.recovery_process_type = RecoveryProcessType.objects.create(
            code="MEJORA_DIRECTA", name="Mejora Directa"
        )

        self.block = EvaluationBlock.objects.create(
            academic_period=self.period,
            subject_offering=self.offering,
            name="Macro 1",
            evaluation_type=self.eval_type_for,
            weight_percentage=Decimal("40.00"),
        )
        self.component = BlockComponent.objects.create(
            evaluation_block=self.block,
            name="Criterio 1",
            internal_weight=Decimal("50.00"),
        )
        self.indicator = ComponentIndicator.objects.create(
            block_component=self.component,
            name="Subcriterio 1",
            internal_weight=Decimal("100.00"),
        )
        self.activity = EvaluativeActivity.objects.create(
            component_indicator=self.indicator,
            teacher_subject_section=self.teacher_subject_section,
            title="Actividad 1",
            activity_type=self.activity_type_tarea,
            max_score=Decimal("10.00"),
            due_date=date(2025, 2, 20),
        )

    def test_evaluation_blocks_rbac_and_crud(self):
        """Prueba permisos RBAC y CRUD para EvaluationBlockViewSet (Macro)."""
        # Con permisos -> Listar
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/grading/evaluation-blocks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(response.json()["data"]["results"][0]["name"], self.block.name)

        # Crear con permisos
        data = {
            "academic_period": self.period.id,
            "subject_offering": self.offering.id,
            "name": "Macro 2",
            "evaluation_type": self.eval_type_sum.id,
            "weight_percentage": "60.00",
        }
        response = self.client.post("/api/grading/evaluation-blocks/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Sin permisos -> 403 Forbidden
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/grading/evaluation-blocks/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_block_components_rbac_and_crud(self):
        """Prueba permisos RBAC y CRUD para BlockComponentViewSet (Criterio)."""
        # Con permisos
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/grading/block-components/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])

        data = {
            "evaluation_block": self.block.id,
            "name": "Criterio 2",
            "internal_weight": "50.00",
        }
        response = self.client.post("/api/grading/block-components/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Sin permisos -> 403
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/grading/block-components/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_component_indicators_rbac_and_crud(self):
        """Prueba permisos RBAC y CRUD para ComponentIndicatorViewSet (Subcriterio)."""
        # Con permisos
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/grading/component-indicators/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])

        data = {
            "block_component": self.component.id,
            "name": "Subcriterio 2",
            "internal_weight": "100.00",
        }
        response = self.client.post("/api/grading/component-indicators/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Sin permisos -> 403
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/grading/component-indicators/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_evaluative_activities_rbac_and_crud(self):
        """Prueba permisos RBAC y CRUD para EvaluativeActivityViewSet."""
        # Con permisos
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/grading/evaluative-activities/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])

        data = {
            "component_indicator": self.indicator.id,
            "teacher_subject_section": self.teacher_subject_section.id,
            "title": "Actividad 2",
            "activity_type": self.activity_type_examen.id,
            "max_score": "10.00",
            "due_date": "2025-02-28",
        }
        response = self.client.post("/api/grading/evaluative-activities/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Sin permisos -> 403
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/grading/evaluative-activities/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_grade_history_api(self):
        """Prueba de solo lectura y RBAC para GradeChangeHistoryViewSet."""
        note = StudentNote.objects.create(
            enrollment=self.enrollment,
            evaluative_activity=self.activity,
            grade_type=self.grade_type,
            numeric_score=Decimal("8.50"),
        )
        history = GradeChangeHistory.objects.create(
            student_note=note,
            modified_by_user=self.admin,
            previous_score=Decimal("5.00"),
            new_score=Decimal("8.50"),
            reason="Corrección de nota",
        )

        # Con permisos
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/grading/grade-history/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])
        results = response.json()["data"]["results"]
        self.assertTrue(any(x["reason"] == "Corrección de nota" for x in results))

        # Sin permisos -> 403
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/grading/grade-history/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_period_grade_summaries_rbac_and_crud(self):
        """Prueba permisos RBAC y CRUD para PeriodGradeSummaryViewSet."""
        # Con permisos
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/grading/period-grade-summaries/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])

        data = {
            "enrollment": self.enrollment.id,
            "subject_offering": self.teacher_subject_section.subject_offering.id,
            "academic_period": self.period.id,
            "formative_avg": "8.50",
            "summative_avg": "9.00",
            "final_avg_truncated": "8.75",
            "qualitative_scale": self.qualitative_scale.id,
        }
        response = self.client.post("/api/grading/period-grade-summaries/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Sin permisos -> 403
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/grading/period-grade-summaries/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_recovery_processes_rbac_and_crud(self):
        """Prueba permisos RBAC y CRUD para RecoveryProcessViewSet."""
        # Primero creamos el PeriodGradeSummary requerido
        summary = PeriodGradeSummary.objects.create(
            enrollment=self.enrollment,
            subject_offering=self.teacher_subject_section.subject_offering,
            academic_period=self.period,
            formative_avg=Decimal("8.50"),
            summative_avg=Decimal("9.00"),
            final_avg_truncated=Decimal("8.75"),
        )

        # Con permisos
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/grading/recovery-processes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])

        data = {
            "period_grade_summary": summary.id,
            "subject_offering": self.teacher_subject_section.subject_offering.id,
            "managed_by_user": self.authorized_user.id,
            "process_type": self.recovery_process_type.id,
            "initial_grade": "8.75",
            "start_date": "2025-02-25",
        }
        response = self.client.post("/api/grading/recovery-processes/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Sin permisos -> 403
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/grading/recovery-processes/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_project_notes_rbac_and_crud(self):
        """Prueba permisos RBAC y CRUD para ProjectNoteViewSet."""
        # Con permisos
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/grading/project-notes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])

        data = {
            "enrollment": self.enrollment.id,
            "interdisciplinary_project": self.project.id,
            "product_score": "8.50",
            "presentation_score": "9.00",
            "final_score": "8.75",
        }
        response = self.client.post("/api/grading/project-notes/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Sin permisos -> 403
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/grading/project-notes/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_grade_types_api(self):
        """Prueba de solo lectura y RBAC para GradeTypeViewSet."""
        # Con permisos
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/grading/grade-types/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])
        results = response.json()["data"]["results"]
        self.assertTrue(any(x["code"] == "NUM" for x in results))

        # Crear como usuario autorizado -> 201 Created
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.post("/api/grading/grade-types/", {"code": "CUALI", "name": "Cualitativa"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Sin permisos -> 403
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/grading/grade-types/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_qualitative_scales_api(self):
        """Prueba de solo lectura y RBAC para QualitativeScaleViewSet."""
        # Con permisos
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/grading/qualitative-scales/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])
        results = response.json()["data"]["results"]
        self.assertTrue(any(x["code"] == "DA" for x in results))

        # Crear como usuario autorizado -> 201 Created
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.post("/api/grading/qualitative-scales/", {"code": "PR", "description": "Prueba", "numeric_equivalence": "7.00"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Sin permisos -> 403
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/grading/qualitative-scales/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_evaluation_types_api(self):
        """Prueba RBAC y CRUD para EvaluationTypeViewSet."""
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/grading/evaluation-types/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])

        data = {"code": "DIAGNOSTICA", "name": "Diagnóstica"}
        response = self.client.post("/api/grading/evaluation-types/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/grading/evaluation-types/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_activity_types_api(self):
        """Prueba RBAC y CRUD para ActivityTypeViewSet."""
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/grading/activity-types/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])

        data = {"code": "DEBER", "name": "Deber"}
        response = self.client.post("/api/grading/activity-types/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/grading/activity-types/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_promotion_statuses_api(self):
        """Prueba RBAC y CRUD para PromotionStatusViewSet."""
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/grading/promotion-statuses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])

        data = {"code": "REP", "name": "Reprobado"}
        response = self.client.post("/api/grading/promotion-statuses/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/grading/promotion-statuses/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_recovery_process_types_api(self):
        """Prueba RBAC y CRUD para RecoveryProcessTypeViewSet."""
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/grading/recovery-process-types/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])

        data = {"code": "EXAMEN", "name": "Examen"}
        response = self.client.post("/api/grading/recovery-process-types/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/grading/recovery-process-types/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
