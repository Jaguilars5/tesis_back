from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class AccountsPermissions:
    VIEW_USER: Final[str] = "accounts.view_user"
    CREATE_USER: Final[str] = "accounts.create_user"
    UPDATE_USER: Final[str] = "accounts.update_user"
    DELETE_USER: Final[str] = "accounts.delete_user"
    VIEW_ROLE: Final[str] = "accounts.view_role"
    CREATE_ROLE: Final[str] = "accounts.create_role"
    UPDATE_ROLE: Final[str] = "accounts.update_role"
    DELETE_ROLE: Final[str] = "accounts.delete_role"
    VIEW_PERMISSION: Final[str] = "accounts.view_permission"
    CREATE_PERMISSION: Final[str] = "accounts.create_permission"
    UPDATE_PERMISSION: Final[str] = "accounts.update_permission"
    DELETE_PERMISSION: Final[str] = "accounts.delete_permission"
    VIEW_PERSON: Final[str] = "accounts.view_person"
    CREATE_PERSON: Final[str] = "accounts.create_person"
    UPDATE_PERSON: Final[str] = "accounts.update_person"
    DELETE_PERSON: Final[str] = "accounts.delete_person"


@dataclass(frozen=True)
class InstitutionsPermissions:
    VIEW_SCHOOL_YEAR: Final[str] = "institutions.view_school_year"
    CREATE_SCHOOL_YEAR: Final[str] = "institutions.create_school_year"
    UPDATE_SCHOOL_YEAR: Final[str] = "institutions.update_school_year"
    DELETE_SCHOOL_YEAR: Final[str] = "institutions.delete_school_year"
    VIEW_DOCUMENT_TYPE: Final[str] = "institutions.view_document_type"
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
    VIEW_ENROLLMENT: Final[str] = "students.view_enrollment"
    CREATE_ENROLLMENT: Final[str] = "students.create_enrollment"
    UPDATE_ENROLLMENT: Final[str] = "students.update_enrollment"
    DELETE_ENROLLMENT: Final[str] = "students.delete_enrollment"
    ENROLL_STUDENT: Final[str] = "students.enroll_student"
    WITHDRAW_STUDENT: Final[str] = "students.withdraw_student"
    TRANSFER_STUDENT: Final[str] = "students.transfer_student"


@dataclass(frozen=True)
class GradingPermissions:
    VIEW_NOTE: Final[str] = "grading.view_note"
    CREATE_NOTE: Final[str] = "grading.create_note"
    UPDATE_NOTE: Final[str] = "grading.update_note"
    DELETE_NOTE: Final[str] = "grading.delete_note"
    VIEW_GRADE_TYPE: Final[str] = "grading.view_grade_type"
    VIEW_QUALITATIVE_SCALE: Final[str] = "grading.view_qualitative_scale"
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
    VIEW_GRADE_SUMMARY: Final[str] = "grading.view_gradesummary"
    CREATE_GRADE_SUMMARY: Final[str] = "grading.create_gradesummary"
    UPDATE_GRADE_SUMMARY: Final[str] = "grading.update_gradesummary"
    DELETE_GRADE_SUMMARY: Final[str] = "grading.delete_gradesummary"
    VIEW_RECOVERY_PROCESS: Final[str] = "grading.view_recoveryprocess"
    CREATE_RECOVERY_PROCESS: Final[str] = "grading.create_recoveryprocess"
    UPDATE_RECOVERY_PROCESS: Final[str] = "grading.update_recoveryprocess"
    DELETE_RECOVERY_PROCESS: Final[str] = "grading.delete_recoveryprocess"
    VIEW_DIAGNOSTIC_EVALUATION: Final[str] = "grading.view_diagnosticevaluation"
    CREATE_DIAGNOSTIC_EVALUATION: Final[str] = "grading.create_diagnosticevaluation"
    UPDATE_DIAGNOSTIC_EVALUATION: Final[str] = "grading.update_diagnosticevaluation"
    DELETE_DIAGNOSTIC_EVALUATION: Final[str] = "grading.delete_diagnosticevaluation"
    VIEW_PROJECT_NOTE: Final[str] = "grading.view_projectnote"
    CREATE_PROJECT_NOTE: Final[str] = "grading.create_projectnote"
    UPDATE_PROJECT_NOTE: Final[str] = "grading.update_projectnote"
    DELETE_PROJECT_NOTE: Final[str] = "grading.delete_projectnote"


@dataclass(frozen=True)
class AnalyticsPermissions:
    VIEW_RISK_SCORE: Final[str] = "analytics.view_risk_score"
    VIEW_FEATURE_SNAPSHOT: Final[str] = "analytics.view_feature_snapshot"
    VIEW_RISK_FACTOR: Final[str] = "analytics.view_risk_factor"
    VIEW_STUDENT_RISK_FACTOR: Final[str] = "analytics.view_student_risk_factor"
    CREATE_STUDENT_RISK_FACTOR: Final[str] = "analytics.create_student_risk_factor"
    DELETE_STUDENT_RISK_FACTOR: Final[str] = "analytics.delete_student_risk_factor"
    VIEW_EARLY_ALERT: Final[str] = "analytics.view_earlyalert"
    CREATE_EARLY_ALERT: Final[str] = "analytics.create_earlyalert"
    UPDATE_EARLY_ALERT: Final[str] = "analytics.update_earlyalert"
    DELETE_EARLY_ALERT: Final[str] = "analytics.delete_earlyalert"


@dataclass(frozen=True)
class AttendancePermissions:
    VIEW_ATTENDANCE: Final[str] = "attendance.view_attendance"
    CREATE_ATTENDANCE: Final[str] = "attendance.create_attendance"
    UPDATE_ATTENDANCE: Final[str] = "attendance.update_attendance"
    DELETE_ATTENDANCE: Final[str] = "attendance.delete_attendance"
    VIEW_CONDUCT_INCIDENT: Final[str] = "attendance.view_conductincident"
    CREATE_CONDUCT_INCIDENT: Final[str] = "attendance.create_conductincident"
    UPDATE_CONDUCT_INCIDENT: Final[str] = "attendance.update_conductincident"
    DELETE_CONDUCT_INCIDENT: Final[str] = "attendance.delete_conductincident"
    VIEW_BEHAVIOR_EVALUATION: Final[str] = "attendance.view_behaviorevaluation"
    CREATE_BEHAVIOR_EVALUATION: Final[str] = "attendance.create_behaviorevaluation"
    UPDATE_BEHAVIOR_EVALUATION: Final[str] = "attendance.update_behaviorevaluation"
    DELETE_BEHAVIOR_EVALUATION: Final[str] = "attendance.delete_behaviorevaluation"
    VIEW_INCIDENT_TYPE: Final[str] = "attendance.view_incidenttype"
    CREATE_INCIDENT_TYPE: Final[str] = "attendance.create_incidenttype"
    UPDATE_INCIDENT_TYPE: Final[str] = "attendance.update_incidenttype"
    DELETE_INCIDENT_TYPE: Final[str] = "attendance.delete_incidenttype"
    VIEW_SOCIOEMOTIONAL_SKILL: Final[str] = "attendance.view_socioemotionalskill"
    CREATE_SOCIOEMOTIONAL_SKILL: Final[str] = "attendance.create_socioemotionalskill"
    UPDATE_SOCIOEMOTIONAL_SKILL: Final[str] = "attendance.update_socioemotionalskill"
    DELETE_SOCIOEMOTIONAL_SKILL: Final[str] = "attendance.delete_socioemotionalskill"
    VIEW_SKILL_EVALUATION: Final[str] = "attendance.view_skillevaluation"
    CREATE_SKILL_EVALUATION: Final[str] = "attendance.create_skillevaluation"
    UPDATE_SKILL_EVALUATION: Final[str] = "attendance.update_skillevaluation"
    DELETE_SKILL_EVALUATION: Final[str] = "attendance.delete_skillevaluation"
    VIEW_ATTENDANCE_STATUS: Final[str] = "attendance.view_attendancestatus"
    CREATE_ATTENDANCE_STATUS: Final[str] = "attendance.create_attendancestatus"
    UPDATE_ATTENDANCE_STATUS: Final[str] = "attendance.update_attendancestatus"
    DELETE_ATTENDANCE_STATUS: Final[str] = "attendance.delete_attendancestatus"


accounts = AccountsPermissions()
institutions = InstitutionsPermissions()
academic = AcademicPermissions()
students = StudentsPermissions()
grading = GradingPermissions()
analytics = AnalyticsPermissions()
attendance = AttendancePermissions()
