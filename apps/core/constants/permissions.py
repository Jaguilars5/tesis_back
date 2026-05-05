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


@dataclass(frozen=True)
class InstitutionsPermissions:
    VIEW_INSTITUTION: Final[str] = "institutions.view_institution"
    CREATE_INSTITUTION: Final[str] = "institutions.create_institution"
    UPDATE_INSTITUTION: Final[str] = "institutions.update_institution"
    DELETE_INSTITUTION: Final[str] = "institutions.delete_institution"
    VIEW_SCHOOL_YEAR: Final[str] = "institutions.view_school_year"
    CREATE_SCHOOL_YEAR: Final[str] = "institutions.create_school_year"
    UPDATE_SCHOOL_YEAR: Final[str] = "institutions.update_school_year"
    DELETE_SCHOOL_YEAR: Final[str] = "institutions.delete_school_year"
    VIEW_CLASSROOM: Final[str] = "institutions.view_classroom"
    CREATE_CLASSROOM: Final[str] = "institutions.create_classroom"
    UPDATE_CLASSROOM: Final[str] = "institutions.update_classroom"
    DELETE_CLASSROOM: Final[str] = "institutions.delete_classroom"


@dataclass(frozen=True)
class AcademicPermissions:
    VIEW_SECTION: Final[str] = "academic.view_section"
    CREATE_SECTION: Final[str] = "academic.create_section"
    UPDATE_SECTION: Final[str] = "academic.update_section"
    DELETE_SECTION: Final[str] = "academic.delete_section"
    VIEW_SUBJECT: Final[str] = "academic.view_subject"
    CREATE_SUBJECT: Final[str] = "academic.create_subject"
    UPDATE_SUBJECT: Final[str] = "academic.update_subject"
    DELETE_SUBJECT: Final[str] = "academic.delete_subject"
    VIEW_PERIOD: Final[str] = "academic.view_period"
    CREATE_PERIOD: Final[str] = "academic.create_period"
    UPDATE_PERIOD: Final[str] = "academic.update_period"
    DELETE_PERIOD: Final[str] = "academic.delete_period"
    VIEW_ACTIVITY: Final[str] = "academic.view_activity"
    CREATE_ACTIVITY: Final[str] = "academic.create_activity"
    UPDATE_ACTIVITY: Final[str] = "academic.update_activity"
    DELETE_ACTIVITY: Final[str] = "academic.delete_activity"
    VIEW_REGIME: Final[str] = "academic.view_regime"
    CREATE_REGIME: Final[str] = "academic.create_regime"
    UPDATE_REGIME: Final[str] = "academic.update_regime"
    DELETE_REGIME: Final[str] = "academic.delete_regime"
    VIEW_TEACHER_SUBJECT: Final[str] = "academic.view_teacher_subject"
    CREATE_TEACHER_SUBJECT: Final[str] = "academic.create_teacher_subject"
    UPDATE_TEACHER_SUBJECT: Final[str] = "academic.update_teacher_subject"
    DELETE_TEACHER_SUBJECT: Final[str] = "academic.delete_teacher_subject"
    VIEW_CONFIG: Final[str] = "academic.view_config"
    CREATE_CONFIG: Final[str] = "academic.create_config"
    UPDATE_CONFIG: Final[str] = "academic.update_config"
    DELETE_CONFIG: Final[str] = "academic.delete_config"


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


@dataclass(frozen=True)
class GradingPermissions:
    VIEW_NOTE: Final[str] = "grading.view_note"
    CREATE_NOTE: Final[str] = "grading.create_note"
    UPDATE_NOTE: Final[str] = "grading.update_note"
    DELETE_NOTE: Final[str] = "grading.delete_note"
    VIEW_ATTENDANCE: Final[str] = "grading.view_attendance"
    CREATE_ATTENDANCE: Final[str] = "grading.create_attendance"
    UPDATE_ATTENDANCE: Final[str] = "grading.update_attendance"
    DELETE_ATTENDANCE: Final[str] = "grading.delete_attendance"
    VIEW_INCIDENT: Final[str] = "grading.view_incident"
    CREATE_INCIDENT: Final[str] = "grading.create_incident"
    UPDATE_INCIDENT: Final[str] = "grading.update_incident"
    DELETE_INCIDENT: Final[str] = "grading.delete_incident"


@dataclass(frozen=True)
class SchedulingPermissions:
    VIEW_SCHEDULE: Final[str] = "scheduling.view_schedule"
    CREATE_SCHEDULE: Final[str] = "scheduling.create_schedule"
    UPDATE_SCHEDULE: Final[str] = "scheduling.update_schedule"
    DELETE_SCHEDULE: Final[str] = "scheduling.delete_schedule"
    VIEW_TIMESLOT: Final[str] = "scheduling.view_timeslot"
    CREATE_TIMESLOT: Final[str] = "scheduling.create_timeslot"
    UPDATE_TIMESLOT: Final[str] = "scheduling.update_timeslot"
    DELETE_TIMESLOT: Final[str] = "scheduling.delete_timeslot"
    VIEW_AVAILABILITY: Final[str] = "scheduling.view_availability"
    CREATE_AVAILABILITY: Final[str] = "scheduling.create_availability"
    UPDATE_AVAILABILITY: Final[str] = "scheduling.update_availability"
    DELETE_AVAILABILITY: Final[str] = "scheduling.delete_availability"
    VIEW_CONSTRAINT: Final[str] = "scheduling.view_constraint"
    CREATE_CONSTRAINT: Final[str] = "scheduling.create_constraint"
    UPDATE_CONSTRAINT: Final[str] = "scheduling.update_constraint"
    DELETE_CONSTRAINT: Final[str] = "scheduling.delete_constraint"
    VIEW_TEMPLATE: Final[str] = "scheduling.view_template"
    CREATE_TEMPLATE: Final[str] = "scheduling.create_template"
    UPDATE_TEMPLATE: Final[str] = "scheduling.update_template"
    DELETE_TEMPLATE: Final[str] = "scheduling.delete_template"


@dataclass(frozen=True)
class AnalyticsPermissions:
    VIEW_RISK_SCORE: Final[str] = "analytics.view_risk_score"
    VIEW_FEATURE_SNAPSHOT: Final[str] = "analytics.view_feature_snapshot"


accounts = AccountsPermissions()
institutions = InstitutionsPermissions()
academic = AcademicPermissions()
students = StudentsPermissions()
grading = GradingPermissions()
scheduling = SchedulingPermissions()
analytics = AnalyticsPermissions()
