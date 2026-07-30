"""Celery tasks que resuelven destinatarios y despachan notificaciones.

Se encolan vía ``transaction.on_commit`` desde los servicios de dominio para
garantizar que el evento solo se dispare cuando la transacción se confirma.
"""

import logging

from celery import shared_task

from .recipients import section_students_and_reps_user_ids, student_and_reps_user_ids
from .service import NotificationService

logger = logging.getLogger(__name__)


@shared_task(bind=True, ignore_result=True)
def notify_activity_created(self, activity_id):
    from apps.grading.evaluation.infrastructure.repositories import (
        EvaluativeActivityRepository,
    )

    activity = EvaluativeActivityRepository.get_by_id(activity_id)
    if not activity:
        logger.warning("notify_activity_created: actividad %s no encontrada", activity_id)
        return {"skipped": "activity_not_found", "activity_id": activity_id}

    section_id = activity.teacher_subject_section.subject_offering.section_id
    user_ids = section_students_and_reps_user_ids(section_id)

    title = "Nueva actividad evaluativa"
    body = f"Se ha creado la actividad \"{activity.title}\" con fecha de entrega {activity.due_date}."
    return NotificationService.notify(
        user_ids=user_ids,
        notification_type="ACTIVITY_CREATED",
        title=title,
        body=body,
        data={"activity_id": activity.id, "section_id": section_id},
    )


@shared_task(bind=True, ignore_result=True)
def notify_activity_graded(self, note_id):
    from apps.grading.student_note.infrastructure.repositories import (
        StudentNoteRepository,
    )

    note = StudentNoteRepository.get_by_id(note_id)
    if not note:
        logger.warning("notify_activity_graded: nota %s no encontrada", note_id)
        return {"skipped": "note_not_found", "note_id": note_id}

    student = note.enrollment.student
    user_ids = student_and_reps_user_ids(student)

    activity_title = note.evaluative_activity.title if note.evaluative_activity_id else "una actividad"
    title = "Actividad calificada"
    student_name = student.get_full_name()
    if note.grading_mode == "NUMERIC" and note.numeric_score is not None:
        body = f"Se ha registrado la calificación de {student_name} para \"{activity_title}\": {note.numeric_score}/{note.evaluative_activity.max_score}."
    elif note.qualitative_scale:
        body = f"Se ha registrado la calificación de {student_name} para \"{activity_title}\": {note.qualitative_scale.name}."
    else:
        body = f"Se ha registrado la calificación de {student_name} para \"{activity_title}\"."
    return NotificationService.notify(
        user_ids=user_ids,
        notification_type="ACTIVITY_GRADED",
        title=title,
        body=body,
        data={
            "note_id": note.id,
            "activity_id": note.evaluative_activity_id,
            "student_id": student.id,
        },
    )


@shared_task(bind=True, ignore_result=True)
def notify_attendance_created(self, attendance_id):
    from apps.attendance.attendance_core.infrastructure.repositories import (
        AttendanceRepository,
    )

    attendance = AttendanceRepository.get_by_id(attendance_id)
    if not attendance:
        logger.warning("notify_attendance_created: asistencia %s no encontrada", attendance_id)
        return {"skipped": "attendance_not_found", "attendance_id": attendance_id}

    student = attendance.enrollment.student
    user_ids = student_and_reps_user_ids(student)

    status_label = (
        attendance.attendance_status.name
        if attendance.attendance_status_id
        else "registro"
    )
    title = "Registro de asistencia"
    body = f"Se ha registrado la asistencia de {student.get_full_name()}: {status_label} el {attendance.attendance_date}."
    return NotificationService.notify(
        user_ids=user_ids,
        notification_type="ATTENDANCE_CREATED",
        title=title,
        body=body,
        data={
            "attendance_id": attendance.id,
            "student_id": student.id,
            "date": str(attendance.attendance_date),
        },
    )


@shared_task(bind=True, ignore_result=True)
def notify_incident_created(self, incident_id):
    from apps.behavior.conduct_incident.infrastructure.repositories import (
        ConductIncidentRepository,
    )

    incident = ConductIncidentRepository.get_by_id(incident_id)
    if not incident:
        logger.warning("notify_incident_created: incidente %s no encontrado", incident_id)
        return {"skipped": "incident_not_found", "incident_id": incident_id}

    student = incident.enrollment.student
    user_ids = student_and_reps_user_ids(student)

    incident_label = incident.incident_type.name if incident.incident_type_id else "Incidente"
    title = "Incidente de conducta"
    severity_label = incident.severity.name if incident.severity else "Sin especificar"
    body = f"Se ha registrado un incidente de conducta de {student.get_full_name()}: {incident_label} - {severity_label} el {incident.incident_date}."
    return NotificationService.notify(
        user_ids=user_ids,
        notification_type="INCIDENT_CREATED",
        title=title,
        body=body,
        data={
            "incident_id": incident.id,
            "student_id": student.id,
            "date": str(incident.incident_date),
        },
    )
