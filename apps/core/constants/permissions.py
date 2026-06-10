from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class IamPermissions:
    VIEW_USER: Final[str] = "iam.view_user"
    CREATE_USER: Final[str] = "iam.create_user"
    UPDATE_USER: Final[str] = "iam.update_user"
    DELETE_USER: Final[str] = "iam.delete_user"
    VIEW_ROLE: Final[str] = "iam.view_role"
    CREATE_ROLE: Final[str] = "iam.create_role"
    UPDATE_ROLE: Final[str] = "iam.update_role"
    DELETE_ROLE: Final[str] = "iam.delete_role"
    VIEW_PERMISSION: Final[str] = "iam.view_permission"
    CREATE_PERMISSION: Final[str] = "iam.create_permission"
    UPDATE_PERMISSION: Final[str] = "iam.update_permission"
    DELETE_PERMISSION: Final[str] = "iam.delete_permission"


@dataclass(frozen=True)
class PeoplePermissions:
    VIEW_PERSON: Final[str] = "people.view_person"
    CREATE_PERSON: Final[str] = "people.create_person"
    UPDATE_PERSON: Final[str] = "people.update_person"
    DELETE_PERSON: Final[str] = "people.delete_person"
    VIEW_DOCUMENT_TYPE: Final[str] = "people.view_document_type"
    CREATE_DOCUMENT_TYPE: Final[str] = "people.create_document_type"
    UPDATE_DOCUMENT_TYPE: Final[str] = "people.update_document_type"
    DELETE_DOCUMENT_TYPE: Final[str] = "people.delete_document_type"


@dataclass(frozen=True)
class InstitutionsPermissions:
    VIEW_SCHOOL_YEAR: Final[str] = "institutions.view_school_year"
    CREATE_SCHOOL_YEAR: Final[str] = "institutions.create_school_year"
    UPDATE_SCHOOL_YEAR: Final[str] = "institutions.update_school_year"
    DELETE_SCHOOL_YEAR: Final[str] = "institutions.delete_school_year"
    VIEW_SECTION: Final[str] = "institutions.view_section"
    CREATE_SECTION: Final[str] = "institutions.create_section"
    UPDATE_SECTION: Final[str] = "institutions.update_section"
    DELETE_SECTION: Final[str] = "institutions.delete_section"
    VIEW_ACADEMIC_LEVEL: Final[str] = "institutions.view_academic_level"
    CREATE_ACADEMIC_LEVEL: Final[str] = "institutions.create_academic_level"
    UPDATE_ACADEMIC_LEVEL: Final[str] = "institutions.update_academic_level"
    DELETE_ACADEMIC_LEVEL: Final[str] = "institutions.delete_academic_level"
    VIEW_ACADEMIC_GRADE: Final[str] = "institutions.view_academic_grade"
    CREATE_ACADEMIC_GRADE: Final[str] = "institutions.create_academic_grade"
    UPDATE_ACADEMIC_GRADE: Final[str] = "institutions.update_academic_grade"
    DELETE_ACADEMIC_GRADE: Final[str] = "institutions.delete_academic_grade"
    VIEW_ACADEMIC_SUBLEVEL: Final[str] = "institutions.view_academic_sublevel"
    CREATE_ACADEMIC_SUBLEVEL: Final[str] = "institutions.create_academic_sublevel"
    UPDATE_ACADEMIC_SUBLEVEL: Final[str] = "institutions.update_academic_sublevel"
    DELETE_ACADEMIC_SUBLEVEL: Final[str] = "institutions.delete_academic_sublevel"


@dataclass(frozen=True)
class AcademicPermissions:
    VIEW_SUBJECT: Final[str] = "academic.view_subject"
    CREATE_SUBJECT: Final[str] = "academic.create_subject"
    UPDATE_SUBJECT: Final[str] = "academic.update_subject"
    DELETE_SUBJECT: Final[str] = "academic.delete_subject"
    VIEW_PERIOD: Final[str] = "academic.view_period"
    CREATE_PERIOD: Final[str] = "academic.create_period"
    UPDATE_PERIOD: Final[str] = "academic.update_period"
    DELETE_PERIOD: Final[str] = "academic.delete_period"
    VIEW_PERIOD_TYPE: Final[str] = "academic.view_period_type"
    CREATE_PERIOD_TYPE: Final[str] = "academic.create_period_type"
    UPDATE_PERIOD_TYPE: Final[str] = "academic.update_period_type"
    DELETE_PERIOD_TYPE: Final[str] = "academic.delete_period_type"
    VIEW_TEACHER_SUBJECT: Final[str] = "academic.view_teacher_subject"
    CREATE_TEACHER_SUBJECT: Final[str] = "academic.create_teacher_subject"
    UPDATE_TEACHER_SUBJECT: Final[str] = "academic.update_teacher_subject"
    DELETE_TEACHER_SUBJECT: Final[str] = "academic.delete_teacher_subject"
    VIEW_CONFIG: Final[str] = "academic.view_config"
    CREATE_CONFIG: Final[str] = "academic.create_config"
    UPDATE_CONFIG: Final[str] = "academic.update_config"
    DELETE_CONFIG: Final[str] = "academic.delete_config"
    VIEW_SUBJECT_CONFIG: Final[str] = "academic.view_subject_config"
    CREATE_SUBJECT_CONFIG: Final[str] = "academic.create_subject_config"
    UPDATE_SUBJECT_CONFIG: Final[str] = "academic.update_subject_config"
    DELETE_SUBJECT_CONFIG: Final[str] = "academic.delete_subject_config"
    VIEW_SUBJECT_OFFERING: Final[str] = "academic.view_subject_offering"
    CREATE_SUBJECT_OFFERING: Final[str] = "academic.create_subject_offering"
    UPDATE_SUBJECT_OFFERING: Final[str] = "academic.update_subject_offering"
    DELETE_SUBJECT_OFFERING: Final[str] = "academic.delete_subject_offering"
    VIEW_INTERDISCIPLINARY_PROJECT: Final[str] = (
        "academic.view_interdisciplinary_project"
    )
    CREATE_INTERDISCIPLINARY_PROJECT: Final[str] = (
        "academic.create_interdisciplinary_project"
    )
    UPDATE_INTERDISCIPLINARY_PROJECT: Final[str] = (
        "academic.update_interdisciplinary_project"
    )
    DELETE_INTERDISCIPLINARY_PROJECT: Final[str] = (
        "academic.delete_interdisciplinary_project"
    )
    VIEW_SUBJECT_PROJECT: Final[str] = "academic.view_subject_project"
    CREATE_SUBJECT_PROJECT: Final[str] = "academic.create_subject_project"
    UPDATE_SUBJECT_PROJECT: Final[str] = "academic.update_subject_project"
    DELETE_SUBJECT_PROJECT: Final[str] = "academic.delete_subject_project"
    VIEW_DAY_OF_WEEK: Final[str] = "academic.view_day_of_week"
    CREATE_DAY_OF_WEEK: Final[str] = "academic.create_day_of_week"
    UPDATE_DAY_OF_WEEK: Final[str] = "academic.update_day_of_week"
    DELETE_DAY_OF_WEEK: Final[str] = "academic.delete_day_of_week"
    VIEW_CLASS_SCHEDULE: Final[str] = "academic.view_class_schedule"
    CREATE_CLASS_SCHEDULE: Final[str] = "academic.create_class_schedule"
    UPDATE_CLASS_SCHEDULE: Final[str] = "academic.update_class_schedule"
    DELETE_CLASS_SCHEDULE: Final[str] = "academic.delete_class_schedule"


@dataclass(frozen=True)
class StudentsPermissions:
    VIEW_STUDENT: Final[str] = "students.view_student"
    CREATE_STUDENT: Final[str] = "students.create_student"
    UPDATE_STUDENT: Final[str] = "students.update_student"
    DELETE_STUDENT: Final[str] = "students.delete_student"
    VIEW_REPRESENTATIVE: Final[str] = "students.view_representative"
    CREATE_REPRESENTATIVE: Final[str] = "students.create_representative"
    UPDATE_REPRESENTATIVE: Final[str] = "students.update_representative"
    DELETE_REPRESENTATIVE: Final[str] = "students.delete_representative"
    VIEW_RELATIONSHIP: Final[str] = "students.view_relationship"
    CREATE_RELATIONSHIP: Final[str] = "students.create_relationship"
    UPDATE_RELATIONSHIP: Final[str] = "students.update_relationship"
    DELETE_RELATIONSHIP: Final[str] = "students.delete_relationship"
    VIEW_ENROLLMENT_STATUS: Final[str] = "students.view_enrollment_status"
    CREATE_ENROLLMENT_STATUS: Final[str] = "students.create_enrollment_status"
    UPDATE_ENROLLMENT_STATUS: Final[str] = "students.update_enrollment_status"
    DELETE_ENROLLMENT_STATUS: Final[str] = "students.delete_enrollment_status"
    VIEW_ENROLLMENT: Final[str] = "students.view_enrollment"
    CREATE_ENROLLMENT: Final[str] = "students.create_enrollment"
    UPDATE_ENROLLMENT: Final[str] = "students.update_enrollment"
    DELETE_ENROLLMENT: Final[str] = "students.delete_enrollment"
    WITHDRAW_STUDENT: Final[str] = "students.withdraw_student"
    TRANSFER_STUDENT: Final[str] = "students.transfer_student"


@dataclass(frozen=True)
class GradingPermissions:
    VIEW_NOTE: Final[str] = "grading.view_note"
    CREATE_NOTE: Final[str] = "grading.create_note"
    UPDATE_NOTE: Final[str] = "grading.update_note"
    DELETE_NOTE: Final[str] = "grading.delete_note"
    VIEW_GRADE_TYPE: Final[str] = "grading.view_grade_type"
    CREATE_GRADE_TYPE: Final[str] = "grading.create_grade_type"
    UPDATE_GRADE_TYPE: Final[str] = "grading.update_grade_type"
    DELETE_GRADE_TYPE: Final[str] = "grading.delete_grade_type"
    VIEW_QUALITATIVE_SCALE: Final[str] = "grading.view_qualitative_scale"
    CREATE_QUALITATIVE_SCALE: Final[str] = "grading.create_qualitative_scale"
    UPDATE_QUALITATIVE_SCALE: Final[str] = "grading.update_qualitative_scale"
    DELETE_QUALITATIVE_SCALE: Final[str] = "grading.delete_qualitative_scale"
    VIEW_EVALUATION_TYPE: Final[str] = "grading.view_evaluation_type"
    CREATE_EVALUATION_TYPE: Final[str] = "grading.create_evaluation_type"
    UPDATE_EVALUATION_TYPE: Final[str] = "grading.update_evaluation_type"
    DELETE_EVALUATION_TYPE: Final[str] = "grading.delete_evaluation_type"
    VIEW_ACTIVITY_TYPE: Final[str] = "grading.view_activity_type"
    CREATE_ACTIVITY_TYPE: Final[str] = "grading.create_activity_type"
    UPDATE_ACTIVITY_TYPE: Final[str] = "grading.update_activity_type"
    DELETE_ACTIVITY_TYPE: Final[str] = "grading.delete_activity_type"
    VIEW_PROMOTION_STATUS: Final[str] = "grading.view_promotion_status"
    CREATE_PROMOTION_STATUS: Final[str] = "grading.create_promotion_status"
    UPDATE_PROMOTION_STATUS: Final[str] = "grading.update_promotion_status"
    DELETE_PROMOTION_STATUS: Final[str] = "grading.delete_promotion_status"
    VIEW_RECOVERY_PROCESS_TYPE: Final[str] = "grading.view_recovery_process_type"
    CREATE_RECOVERY_PROCESS_TYPE: Final[str] = "grading.create_recovery_process_type"
    UPDATE_RECOVERY_PROCESS_TYPE: Final[str] = "grading.update_recovery_process_type"
    DELETE_RECOVERY_PROCESS_TYPE: Final[str] = "grading.delete_recovery_process_type"
    VIEW_EVALUATION_MACRO: Final[str] = "grading.view_evaluation_macro"
    CREATE_EVALUATION_MACRO: Final[str] = "grading.create_evaluation_macro"
    UPDATE_EVALUATION_MACRO: Final[str] = "grading.update_evaluation_macro"
    DELETE_EVALUATION_MACRO: Final[str] = "grading.delete_evaluation_macro"
    VIEW_EVALUATION_CRITERIA: Final[str] = "grading.view_evaluation_criteria"
    CREATE_EVALUATION_CRITERIA: Final[str] = "grading.create_evaluation_criteria"
    UPDATE_EVALUATION_CRITERIA: Final[str] = "grading.update_evaluation_criteria"
    DELETE_EVALUATION_CRITERIA: Final[str] = "grading.delete_evaluation_criteria"
    VIEW_EVALUATION_SUBCRITERIA: Final[str] = "grading.view_evaluation_subcriteria"
    CREATE_EVALUATION_SUBCRITERIA: Final[str] = "grading.create_evaluation_subcriteria"
    UPDATE_EVALUATION_SUBCRITERIA: Final[str] = "grading.update_evaluation_subcriteria"
    DELETE_EVALUATION_SUBCRITERIA: Final[str] = "grading.delete_evaluation_subcriteria"
    VIEW_CLASS_ASSIGNMENT: Final[str] = "grading.view_class_assignment"
    CREATE_CLASS_ASSIGNMENT: Final[str] = "grading.create_class_assignment"
    UPDATE_CLASS_ASSIGNMENT: Final[str] = "grading.update_class_assignment"
    DELETE_CLASS_ASSIGNMENT: Final[str] = "grading.delete_class_assignment"
    VIEW_GRADE_HISTORY: Final[str] = "grading.view_grade_history"
    VIEW_GRADE_SUMMARY: Final[str] = "grading.view_grade_summary"
    CREATE_GRADE_SUMMARY: Final[str] = "grading.create_grade_summary"
    UPDATE_GRADE_SUMMARY: Final[str] = "grading.update_grade_summary"
    DELETE_GRADE_SUMMARY: Final[str] = "grading.delete_grade_summary"
    VIEW_RECOVERY_PROCESS: Final[str] = "grading.view_recovery_process"
    CREATE_RECOVERY_PROCESS: Final[str] = "grading.create_recovery_process"
    UPDATE_RECOVERY_PROCESS: Final[str] = "grading.update_recovery_process"
    DELETE_RECOVERY_PROCESS: Final[str] = "grading.delete_recovery_process"
    VIEW_PROJECT_NOTE: Final[str] = "grading.view_project_note"
    CREATE_PROJECT_NOTE: Final[str] = "grading.create_project_note"
    UPDATE_PROJECT_NOTE: Final[str] = "grading.update_project_note"
    DELETE_PROJECT_NOTE: Final[str] = "grading.delete_project_note"


@dataclass(frozen=True)
class AnalyticsPermissions:
    VIEW_RISK_SCORE: Final[str] = "analytics.view_risk_score"
    VIEW_FEATURE_SNAPSHOT: Final[str] = "analytics.view_feature_snapshot"
    VIEW_RISK_FACTOR: Final[str] = "analytics.view_risk_factor"
    VIEW_STUDENT_RISK_FACTOR: Final[str] = "analytics.view_student_risk_factor"
    CREATE_STUDENT_RISK_FACTOR: Final[str] = "analytics.create_student_risk_factor"
    DELETE_STUDENT_RISK_FACTOR: Final[str] = "analytics.delete_student_risk_factor"
    VIEW_EARLY_ALERT: Final[str] = "analytics.view_early_alert"
    CREATE_EARLY_ALERT: Final[str] = "analytics.create_early_alert"
    UPDATE_EARLY_ALERT: Final[str] = "analytics.update_early_alert"
    DELETE_EARLY_ALERT: Final[str] = "analytics.delete_early_alert"
    VIEW_ALERT_TYPE: Final[str] = "analytics.view_alert_type"
    CREATE_ALERT_TYPE: Final[str] = "analytics.create_alert_type"
    UPDATE_ALERT_TYPE: Final[str] = "analytics.update_alert_type"
    DELETE_ALERT_TYPE: Final[str] = "analytics.delete_alert_type"
    VIEW_URGENCY_LEVEL: Final[str] = "analytics.view_urgency_level"
    CREATE_URGENCY_LEVEL: Final[str] = "analytics.create_urgency_level"
    UPDATE_URGENCY_LEVEL: Final[str] = "analytics.update_urgency_level"
    DELETE_URGENCY_LEVEL: Final[str] = "analytics.delete_urgency_level"


@dataclass(frozen=True)
class AttendancePermissions:
    VIEW_ATTENDANCE: Final[str] = "attendance.view_attendance"
    CREATE_ATTENDANCE: Final[str] = "attendance.create_attendance"
    UPDATE_ATTENDANCE: Final[str] = "attendance.update_attendance"
    DELETE_ATTENDANCE: Final[str] = "attendance.delete_attendance"
    VIEW_ATTENDANCE_STATUS: Final[str] = "attendance.view_attendance_status"
    CREATE_ATTENDANCE_STATUS: Final[str] = "attendance.create_attendance_status"
    UPDATE_ATTENDANCE_STATUS: Final[str] = "attendance.update_attendance_status"
    DELETE_ATTENDANCE_STATUS: Final[str] = "attendance.delete_attendance_status"
    VIEW_ABSENCE_TYPE: Final[str] = "attendance.view_absence_type"
    CREATE_ABSENCE_TYPE: Final[str] = "attendance.create_absence_type"
    UPDATE_ABSENCE_TYPE: Final[str] = "attendance.update_absence_type"
    DELETE_ABSENCE_TYPE: Final[str] = "attendance.delete_absence_type"


@dataclass(frozen=True)
class BehaviorPermissions:
    VIEW_CONDUCT_INCIDENT: Final[str] = "behavior.view_conduct_incident"
    CREATE_CONDUCT_INCIDENT: Final[str] = "behavior.create_conduct_incident"
    UPDATE_CONDUCT_INCIDENT: Final[str] = "behavior.update_conduct_incident"
    DELETE_CONDUCT_INCIDENT: Final[str] = "behavior.delete_conduct_incident"
    VIEW_BEHAVIOR_EVALUATION: Final[str] = "behavior.view_behavior_evaluation"
    CREATE_BEHAVIOR_EVALUATION: Final[str] = "behavior.create_behavior_evaluation"
    UPDATE_BEHAVIOR_EVALUATION: Final[str] = "behavior.update_behavior_evaluation"
    DELETE_BEHAVIOR_EVALUATION: Final[str] = "behavior.delete_behavior_evaluation"
    VIEW_INCIDENT_TYPE: Final[str] = "behavior.view_incident_type"
    CREATE_INCIDENT_TYPE: Final[str] = "behavior.create_incident_type"
    UPDATE_INCIDENT_TYPE: Final[str] = "behavior.update_incident_type"
    DELETE_INCIDENT_TYPE: Final[str] = "behavior.delete_incident_type"
    VIEW_SOCIOEMOTIONAL_SKILL: Final[str] = "behavior.view_socioemotional_skill"
    CREATE_SOCIOEMOTIONAL_SKILL: Final[str] = "behavior.create_socioemotional_skill"
    UPDATE_SOCIOEMOTIONAL_SKILL: Final[str] = "behavior.update_socioemotional_skill"
    DELETE_SOCIOEMOTIONAL_SKILL: Final[str] = "behavior.delete_socioemotional_skill"
    VIEW_SKILL_EVALUATION: Final[str] = "behavior.view_skill_evaluation"
    CREATE_SKILL_EVALUATION: Final[str] = "behavior.create_skill_evaluation"
    UPDATE_SKILL_EVALUATION: Final[str] = "behavior.update_skill_evaluation"
    DELETE_SKILL_EVALUATION: Final[str] = "behavior.delete_skill_evaluation"
    VIEW_DIAGNOSTIC_EVALUATION: Final[str] = "behavior.view_diagnostic_evaluation"
    CREATE_DIAGNOSTIC_EVALUATION: Final[str] = "behavior.create_diagnostic_evaluation"
    UPDATE_DIAGNOSTIC_EVALUATION: Final[str] = "behavior.update_diagnostic_evaluation"
    DELETE_DIAGNOSTIC_EVALUATION: Final[str] = "behavior.delete_diagnostic_evaluation"


@dataclass(frozen=True)
class ConfigurationPermissions:
    VIEW_SYSTEM_CONFIG: Final[str] = "configuration.view_systemconfig"
    CREATE_SYSTEM_CONFIG: Final[str] = "configuration.create_systemconfig"
    UPDATE_SYSTEM_CONFIG: Final[str] = "configuration.update_systemconfig"
    DELETE_SYSTEM_CONFIG: Final[str] = "configuration.delete_systemconfig"


@dataclass(frozen=True)
class IntegrationPermissions:
    VIEW_SYNC_QUEUE: Final[str] = "integration.view_syncqueue"
    CREATE_SYNC_QUEUE: Final[str] = "integration.create_syncqueue"
    UPDATE_SYNC_QUEUE: Final[str] = "integration.update_syncqueue"
    DELETE_SYNC_QUEUE: Final[str] = "integration.delete_syncqueue"
    VIEW_SYNC_OPERATION: Final[str] = "integration.view_sync_operation"
    CREATE_SYNC_OPERATION: Final[str] = "integration.create_sync_operation"
    UPDATE_SYNC_OPERATION: Final[str] = "integration.update_sync_operation"
    DELETE_SYNC_OPERATION: Final[str] = "integration.delete_sync_operation"
    VIEW_SYNC_STATUS: Final[str] = "integration.view_sync_status"
    CREATE_SYNC_STATUS: Final[str] = "integration.create_sync_status"
    UPDATE_SYNC_STATUS: Final[str] = "integration.update_sync_status"
    DELETE_SYNC_STATUS: Final[str] = "integration.delete_sync_status"


iam = IamPermissions()
people = PeoplePermissions()
institutions = InstitutionsPermissions()
academic = AcademicPermissions()
students = StudentsPermissions()
grading = GradingPermissions()
analytics = AnalyticsPermissions()
attendance = AttendancePermissions()
behavior = BehaviorPermissions()
configuration = ConfigurationPermissions()
integration = IntegrationPermissions()
