# Diagrama Entidad-Relación v2 — Sistema de Gestión Académica

```mermaid
erDiagram

%% ========================================================================
%% MÓDULO: CORE (Núcleo)
%% ========================================================================

    AuditLog {
        bigint id PK
        int user_id FK "(nullable, SET_NULL)"
        string action "(CREATE|UPDATE|DELETE|RECOVER)"
        string model_name "(max 100)"
        string record_id "(max 36)"
        json changes "(default dict)"
        string ip_address "(nullable)"
        string user_agent "(max 255)"
        datetime created_at
        datetime updated_at
    }

%% ========================================================================
%% MÓDULO: IAM (Identidad y Acceso)
%% ========================================================================

    User {
        bigint id PK
        int person_id FK "(nullable, SET_NULL, unique)"
        string username "(unique, max 50)"
        string email "(unique)"
        string password
        datetime last_login "(nullable)"
        bool is_active "(default True)"
        bool is_staff "(default False)"
        bool is_superuser "(default False)"
        datetime created_at
        datetime updated_at
    }

    Role {
        bigint id PK
        string name "(unique, max 100)"
        string code "(unique, nullable, max 50)"
        string description "(max 255, blank)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    Permission {
        bigint id PK
        string code "(unique, max 100)"
        string description "(max 255, blank)"
        string module "(max 50, blank)"
        datetime created_at
        datetime updated_at
    }

    UserRole {
        bigint id PK
        int user_id FK
        int role_id FK
        datetime assigned_at "(auto_now_add)"
        datetime expires_at "(nullable)"
        datetime created_at
        datetime updated_at
    }

    RolePermission {
        bigint id PK
        int role_id FK
        int permission_id FK
        datetime created_at
        datetime updated_at
    }

%% ========================================================================
%% MÓDULO: PEOPLE (Personas)
%% ========================================================================

    DocumentType {
        bigint id PK
        string code "(unique, max 10)"
        string name "(max 100)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    Person {
        bigint id PK
        int document_type_id FK "(nullable, PROTECT)"
        string document_number "(unique, max 20)"
        string names "(max 100)"
        string last_names "(max 100)"
        date birth_date "(nullable)"
        string email "(blank, max 254)"
        string phone "(blank, max 15)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

%% ========================================================================
%% MÓDULO: INSTITUTIONS (Instituciones)
%% ========================================================================

    SchoolYear {
        bigint id PK
        string name "(max 255)"
        date start_date
        date end_date
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    AcademicLevel {
        bigint id PK
        string code "(max 50, db_index, blank)"
        string name "(max 100)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    AcademicSublevel {
        bigint id PK
        int academic_level_id FK "(CASCADE)"
        string code "(unique, max 20)"
        string name "(max 100)"
        text description "(blank)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    AcademicGrade {
        bigint id PK
        string code "(max 50, db_index, blank)"
        int academic_sublevel_id FK "(nullable, PROTECT)"
        string name "(max 100)"
        int sequence_order
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    Section {
        bigint id PK
        string code "(max 50, db_index, blank)"
        int school_year_id FK "(CASCADE)"
        int academic_grade_id FK "(CASCADE, nullable)"
        string parallel "(max 255)"
        int capacity
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

%% ========================================================================
%% MÓDULO: ACADEMIC (Académico)
%% ========================================================================

    Subject {
        bigint id PK
        string name "(max 255)"
        string code "(unique, max 100)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    PeriodType {
        bigint id PK
        string code "(unique, max 20)"
        string name "(max 100)"
        text description "(blank)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    AcademicPeriod {
        bigint id PK
        string code "(max 50, db_index, blank)"
        int school_year_id FK
        int parent_period_id FK "(nullable, self)"
        string name "(max 80)"
        int period_type_id FK "(nullable)"
        date start_date
        date end_date
        bool is_regular_period "(default True)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    SubjectAcademicConfig {
        bigint id PK
        int subject_id FK
        int academic_grade_id FK
        int weekly_hours
        int pedagogical_order
        bool is_required "(default True)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    SubjectOffering {
        bigint id PK
        int school_year_id FK
        int section_id FK
        int subject_academic_config_id FK
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    TeacherSubjectSection {
        bigint id PK
        int user_id FK
        int subject_offering_id FK
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    InterdisciplinaryProject {
        bigint id PK
        int academic_period_id FK
        string title "(max 200)"
        text description "(nullable)"
        date start_date
        date delivery_date
        decimal product_max_score "(5,2, default 10.00)"
        decimal presentation_max_score "(5,2, default 10.00)"
        text product_rubric "(nullable)"
        text presentation_rubric "(nullable)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    SubjectProject {
        bigint id PK
        int interdisciplinary_project_id FK
        int subject_offering_id FK
        int responsible_teacher_id FK "(nullable, SET_NULL)"
        datetime created_at
        datetime updated_at
    }

    DayOfWeek {
        bigint id PK
        int code "(unique)"
        string name "(max 20)"
        datetime created_at
        datetime updated_at
    }

    ClassSchedule {
        bigint id PK
        int subject_offering_id FK
        int day_of_week_id FK "(PROTECT)"
        time start_time
        time end_time
        string classroom "(max 50, blank)"
        string building "(max 50, blank)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

%% ========================================================================
%% MÓDULO: STUDENTS (Estudiantes)
%% ========================================================================

    Student {
        bigint id PK
        int person_id FK "(nullable, CASCADE, unique)"
        string student_code "(unique, max 50)"
        int residential_zone_id FK "(nullable, SET_NULL)"
        decimal distance_to_school_km "(5,2, nullable)"
        bool has_special_needs "(default False)"
        int special_needs_type_id FK "(nullable, SET_NULL)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    ResidentialZone {
        bigint id PK
        string code "(unique, max 20)"
        string name "(max 100)"
        text description "(blank)"
        bool is_active "(default True)"
    }

    SpecialNeedsType {
        bigint id PK
        string code "(unique, max 30)"
        string name "(max 100)"
        text description "(blank)"
        bool is_active "(default True)"
    }

    EnrollmentStatus {
        bigint id PK
        string code "(unique, max 10)"
        string name "(max 100)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    WithdrawalReason {
        bigint id PK
        string code "(unique, max 20)"
        string name "(max 100)"
        text description "(blank)"
        bool is_active "(default True)"
    }

    Kinship {
        bigint id PK
        string code "(unique, max 30)"
        string name "(max 100)"
        text description "(blank)"
        bool is_active "(default True)"
    }

    Enrollment {
        bigint id PK
        int student_id FK "(CASCADE)"
        int section_id FK "(CASCADE)"
        int school_year_id FK "(CASCADE)"
        int enrollment_status_id FK "(PROTECT)"
        date enrollment_date "(auto_now_add)"
        date withdrawal_date "(nullable)"
        int withdrawal_reason_id FK "(nullable, SET_NULL)"
        bool is_repeat "(default False)"
        int repeated_school_year_id FK "(nullable)"
        int created_by_id FK "(nullable)"
        int approved_by_id FK "(nullable)"
        uuid uuid "(unique)"
        string sync_status "(default PENDING)"
        int sync_version "(default 1)"
        datetime synced_at "(nullable)"
        string device_origin "(nullable, max 40)"
        bool conflict_resolved "(default False)"
        text conflict_notes "(nullable)"
        datetime created_at
        datetime updated_at
    }

    EnrollmentHistory {
        bigint id PK
        int enrollment_id FK "(CASCADE)"
        int previous_status_id FK "(PROTECT)"
        int new_status_id FK "(PROTECT)"
        int changed_by_id FK "(nullable, SET_NULL)"
        text change_reason "(blank)"
        date effective_date
        datetime created_at
        datetime updated_at
    }

    StudentRepresentative {
        bigint id PK
        int student_id FK "(CASCADE)"
        int person_id FK "(nullable, CASCADE)"
        int kinship_id FK "(PROTECT)"
        bool is_primary "(default False)"
        bool can_pickup "(default True)"
        bool emergency_contact "(default False)"
        bool receives_notifications "(default True)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

%% ========================================================================
%% MÓDULO: GRADING (Calificaciones)
%% ========================================================================

    GradeType {
        bigint id PK
        string code "(unique)"
        string name "(max 100)"
        text description "(blank)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    QualitativeScale {
        bigint id PK
        string code "(unique)"
        string name "(max 100)"
        text description "(blank)"
        decimal numeric_equivalence "(4,2)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    QualitativeScaleSublevel {
        bigint id PK
        int scale_id FK
        int sublevel_id FK
    }

    EvaluationType {
        bigint id PK
        string code "(unique)"
        string name "(max 100)"
        text description "(blank)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    ActivityType {
        bigint id PK
        string code "(unique)"
        string name "(max 100)"
        text description "(blank)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    PromotionStatus {
        bigint id PK
        string code "(unique)"
        string name "(max 100)"
        text description "(blank)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    RecoveryProcessType {
        bigint id PK
        string code "(unique)"
        string name "(max 100)"
        text description "(blank)"
        bool allows_improvement_eval
        bool allows_suppletorio
        decimal min_grade_to_access "(4,2, default 7.00)"
        int max_recovery_attempts "(default 1)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    EvaluationBlock {
        bigint id PK
        string code
        int academic_period_id FK
        int subject_offering_id FK
        string name
        int evaluation_type_id FK "(nullable)"
        decimal weight_percentage "(5,2)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    BlockComponent {
        bigint id PK
        string code
        int evaluation_block_id FK
        string name
        decimal internal_weight "(5,2)"
        datetime created_at
        datetime updated_at
    }

    ComponentIndicator {
        bigint id PK
        string code
        int block_component_id FK
        string name
        decimal internal_weight "(5,2)"
        datetime created_at
        datetime updated_at
    }

    EvaluativeActivity {
        bigint id PK
        int component_indicator_id FK
        int teacher_subject_section_id FK
        string title
        int activity_type_id FK "(nullable)"
        decimal max_score "(5,2)"
        date due_date
        bool is_interdisciplinary_project "(default False)"
        uuid uuid "(unique)"
        string sync_status "(default PENDING)"
        int sync_version "(default 1)"
        datetime synced_at "(nullable)"
        string device_origin "(nullable, max 40)"
        bool conflict_resolved "(default False)"
        text conflict_notes "(nullable)"
        datetime created_at
        datetime updated_at
    }

    StudentNote {
        bigint id PK
        int enrollment_id FK
        int evaluative_activity_id FK "(nullable)"
        int grade_type_id FK "(nullable)"
        string grading_mode "(NUMERIC|QUALITATIVE)"
        int qualitative_scale_id FK "(nullable)"
        decimal numeric_score "(5,2, nullable)"
        bool manually_overridden "(default False)"
        text teacher_observation
        int created_by_id FK
        int modified_by_id FK
        uuid uuid "(unique)"
        string sync_status "(default PENDING)"
        int sync_version "(default 1)"
        datetime synced_at "(nullable)"
        string device_origin "(nullable, max 40)"
        bool conflict_resolved "(default False)"
        text conflict_notes "(nullable)"
        datetime created_at
        datetime updated_at
    }

    GradeChangeHistory {
        bigint id PK
        int student_note_id FK
        int modified_by_user_id FK
        int created_by_id FK
        decimal previous_score "(5,2)"
        decimal new_score "(5,2)"
        int previous_qualitative_id FK "(nullable)"
        int new_qualitative_id FK "(nullable)"
        text reason
        string reason_code
        string origin "(MANUAL|RECOVERY|IMPORT|SYNC)"
        string device_origin
        datetime modified_at
        datetime created_at
        datetime updated_at
    }

    PeriodGradeSummary {
        bigint id PK
        int enrollment_id FK
        int subject_offering_id FK
        int academic_period_id FK
        decimal formative_avg "(5,2)"
        decimal summative_avg "(5,2)"
        decimal final_avg_truncated "(5,2)"
        int qualitative_scale_id FK "(nullable)"
        bool requires_recovery "(default False)"
        int promotion_status_id FK "(nullable)"
        datetime calculated_at
        int calculated_by_id FK
        int approved_by_id FK "(nullable)"
        datetime created_at
        datetime updated_at
    }

    RecoveryProcess {
        bigint id PK
        int period_grade_summary_id FK
        int subject_offering_id FK
        int managed_by_user_id FK
        int process_type_id FK
        decimal initial_grade "(5,2)"
        decimal reinforcement_grade "(5,2, nullable)"
        decimal improvement_eval_grade "(5,2, nullable)"
        decimal final_calculated_grade "(5,2, nullable)"
        bool family_notified "(default False)"
        date family_notification_date "(nullable)"
        date start_date
        date end_date "(nullable)"
        text reinforcement_plan "(nullable)"
        text objectives "(nullable)"
        text observations "(nullable)"
        uuid uuid "(unique)"
        string sync_status "(default PENDING)"
        int sync_version "(default 1)"
        datetime synced_at "(nullable)"
        string device_origin "(nullable, max 40)"
        bool conflict_resolved "(default False)"
        text conflict_notes "(nullable)"
        datetime created_at
        datetime updated_at
    }

    RecoverySession {
        bigint id PK
        int recovery_process_id FK
        date session_date
        int duration_minutes "(default 60)"
        text topics_covered
        bool student_present "(default True)"
        text teacher_observation
        uuid uuid "(unique)"
        string sync_status "(default PENDING)"
        int sync_version "(default 1)"
        datetime synced_at "(nullable)"
        string device_origin "(nullable, max 40)"
        bool conflict_resolved "(default False)"
        text conflict_notes "(nullable)"
        datetime created_at
        datetime updated_at
    }

    RecoveryProcessHistory {
        bigint id PK
        int recovery_process_id FK
        string action "(STARTED|GRADE_UPDATED|SESSION_COMPLETED|COMPLETED|CANCELLED)"
        decimal previous_grade "(5,2, nullable)"
        decimal new_grade "(5,2, nullable)"
        int previous_status_id FK "(nullable)"
        int new_status_id FK "(nullable)"
        text notes
        int changed_by_id FK
        datetime created_at
        datetime updated_at
    }

    LearningReport {
        bigint id PK
        int enrollment_id FK
        int academic_period_id FK
        decimal formative_avg "(5,2)"
        decimal summative_avg "(5,2)"
        decimal final_avg "(5,2, nullable)"
        decimal attendance_rate "(5,2, nullable)"
        int behavior_scale_id FK
        text general_observations
        text recommendations
        int created_by_id FK
        int evaluated_by_id FK "(nullable)"
        int approved_by_id FK "(nullable)"
        bool is_final "(default False)"
        uuid uuid "(unique)"
        string sync_status "(default PENDING)"
        int sync_version "(default 1)"
        datetime synced_at "(nullable)"
        string device_origin "(nullable, max 40)"
        bool conflict_resolved "(default False)"
        text conflict_notes "(nullable)"
        datetime created_at
        datetime updated_at
    }

    ProjectNote {
        bigint id PK
        int enrollment_id FK
        int interdisciplinary_project_id FK
        decimal product_score "(5,2)"
        decimal presentation_score "(5,2)"
        decimal final_score "(5,2)"
        text observation "(nullable)"
        uuid uuid "(unique)"
        string sync_status "(default PENDING)"
        int sync_version "(default 1)"
        datetime synced_at "(nullable)"
        string device_origin "(nullable, max 40)"
        bool conflict_resolved "(default False)"
        text conflict_notes "(nullable)"
        datetime created_at
        datetime updated_at
    }

%% ========================================================================
%% MÓDULO: ATTENDANCE (Asistencia)
%% ========================================================================

    AttendanceStatus {
        bigint id PK
        string code "(unique, max 10)"
        string name "(max 100)"
        text description "(blank)"
        bool is_active "(default True)"
        string tipo "(POSITIVO|NEGATIVO, nullable)"
        datetime created_at
        datetime updated_at
    }

    AbsenceType {
        bigint id PK
        string code "(unique, max 30)"
        string name "(max 100)"
        text description "(blank)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    Attendance {
        bigint id PK
        int enrollment_id FK "(nullable)"
        int teacher_subject_section_id FK
        int academic_period_id FK
        int attendance_status_id FK "(nullable, PROTECT)"
        int absence_type_id FK "(nullable, SET_NULL)"
        date attendance_date
        text observation "(nullable)"
        int created_by_id FK "(nullable, SET_NULL)"
        int modified_by_id FK "(nullable, SET_NULL)"
        uuid uuid "(unique)"
        string sync_status "(default PENDING)"
        int sync_version "(default 1)"
        datetime synced_at "(nullable)"
        string device_origin "(nullable, max 40)"
        bool conflict_resolved "(default False)"
        text conflict_notes "(nullable)"
        datetime created_at
        datetime updated_at
    }

%% ========================================================================
%% MÓDULO: BEHAVIOR (Comportamiento)
%% ========================================================================

    IncidentType {
        bigint id PK
        string code "(unique, max 20)"
        string name "(max 100)"
        text description "(blank)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    Severity {
        bigint id PK
        string code "(unique, max 20)"
        string name "(max 100)"
        int numeric_level
        text description "(blank)"
        bool is_active "(default True)"
    }

    SocioemotionalSkill {
        bigint id PK
        string code "(unique, max 20)"
        string name "(max 100)"
        text description "(nullable)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    SocioemotionalArea {
        bigint id PK
        string code "(unique, max 30)"
        string name "(max 100)"
        text description "(blank)"
        bool is_active "(default True)"
    }

    DevelopmentLevel {
        bigint id PK
        string code "(unique, max 30)"
        string name "(max 100)"
        text description "(blank)"
        bool is_active "(default True)"
    }

    ConductIncident {
        bigint id PK
        int enrollment_id FK "(nullable)"
        int reported_by_user_id FK "(nullable, SET_NULL)"
        int academic_period_id FK
        int incident_type_id FK "(nullable, PROTECT)"
        int severity_id FK "(PROTECT)"
        date incident_date
        text description "(nullable)"
        text actions_taken "(nullable)"
        bool family_notified "(default False)"
        int created_by_id FK "(nullable, SET_NULL)"
        int modified_by_id FK "(nullable, SET_NULL)"
        int approved_by_id FK "(nullable, SET_NULL)"
        uuid uuid "(unique)"
        string sync_status "(default PENDING)"
        int sync_version "(default 1)"
        datetime synced_at "(nullable)"
        string device_origin "(nullable, max 40)"
        bool conflict_resolved "(default False)"
        text conflict_notes "(nullable)"
        datetime created_at
        datetime updated_at
    }

    SkillEvaluation {
        bigint id PK
        int enrollment_id FK
        int academic_period_id FK
        int socioemotional_skill_id FK
        int qualitative_scale_id FK "(PROTECT)"
        text observation "(nullable)"
        datetime evaluation_date "(auto_now_add)"
        uuid uuid "(unique)"
        string sync_status "(default PENDING)"
        int sync_version "(default 1)"
        datetime synced_at "(nullable)"
        string device_origin "(nullable, max 40)"
        bool conflict_resolved "(default False)"
        text conflict_notes "(nullable)"
        datetime created_at
        datetime updated_at
    }

    BehaviorEvaluation {
        bigint id PK
        int enrollment_id FK
        int academic_period_id FK
        int calculated_scale_id FK "(PROTECT)"
        int final_scale_id FK "(nullable, PROTECT)"
        text general_observation "(nullable)"
        text override_reason "(nullable)"
        date evaluation_date "(default today)"
        date approval_date "(nullable)"
        int created_by_id FK "(nullable, SET_NULL)"
        int evaluated_by_id FK "(nullable, SET_NULL)"
        int approved_by_id FK "(nullable, SET_NULL)"
        uuid uuid "(unique)"
        string sync_status "(default PENDING)"
        int sync_version "(default 1)"
        datetime synced_at "(nullable)"
        string device_origin "(nullable, max 40)"
        bool conflict_resolved "(default False)"
        text conflict_notes "(nullable)"
        datetime created_at
        datetime updated_at
    }

    DiagnosticEvaluation {
        bigint id PK
        int enrollment_id FK
        int academic_period_id FK
        int applied_by_user_id FK
        int socioemotional_area_id FK "(PROTECT)"
        int development_level_id FK "(PROTECT)"
        text findings_description
        date application_date
        text recommendations "(nullable)"
        uuid uuid "(unique)"
        string sync_status "(default PENDING)"
        int sync_version "(default 1)"
        datetime synced_at "(nullable)"
        string device_origin "(nullable, max 40)"
        bool conflict_resolved "(default False)"
        text conflict_notes "(nullable)"
        datetime created_at
        datetime updated_at
    }

%% ========================================================================
%% MÓDULO: ANALYTICS (Analítica)
%% ========================================================================

    AlertType {
        bigint id PK
        string code "(unique, max 50)"
        string name "(max 100)"
        text description "(blank)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    UrgencyLevel {
        bigint id PK
        string code "(unique, max 20)"
        string name "(max 100)"
        text description "(blank)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    RiskFactor {
        bigint id PK
        string code "(unique, max 30)"
        string name "(max 100)"
        text description "(nullable)"
        datetime created_at
        datetime updated_at
    }

    StudentFeatureSnapshot {
        bigint id PK
        int enrollment_id FK "(nullable)"
        int academic_period_id FK
        decimal attendance_rate "(5,2)"
        int consecutive_absences_max
        int tardiness_count
        int justified_absences
        int unjustified_absences
        decimal formative_avg_normalized "(5,2)"
        decimal summative_avg_normalized "(5,2)"
        decimal grade_trend_slope "(5,2)"
        int failing_subjects_count
        decimal conduct_score "(5,2)"
        int severe_incidents_count
        decimal family_notified_ratio "(5,2)"
        decimal prev_period_avg_grade "(5,2, nullable)"
        int age_grade_gap
        bool is_repeat
        bool has_special_needs
        int active_alerts
        datetime calculated_at "(auto_now_add)"
        datetime created_at
        datetime updated_at
    }

    StudentRiskScore {
        bigint id PK
        int enrollment_id FK "(nullable)"
        int academic_period_id FK
        decimal risk_score "(5,2)"
        string risk_label "(max 20)"
        string model_version "(max 50)"
        datetime calculated_at "(auto_now_add)"
        datetime created_at
        datetime updated_at
    }

    StudentRiskFactor {
        bigint id PK
        int student_risk_score_id FK
        int risk_factor_id FK
        decimal contribution_weight "(5,2)"
        datetime created_at
        datetime updated_at
    }

    EarlyAlert {
        bigint id PK
        int enrollment_id FK
        int academic_period_id FK
        int alert_type_id FK "(nullable, SET_NULL)"
        int urgency_level_id FK "(nullable, SET_NULL)"
        text description
        bool attended "(default False)"
        int attended_by_user_id FK "(nullable, SET_NULL)"
        datetime detected_at "(auto_now_add)"
        datetime attended_at "(nullable)"
        text response_actions "(nullable)"
        uuid uuid "(unique)"
        string sync_status "(default PENDING)"
        int sync_version "(default 1)"
        datetime synced_at "(nullable)"
        string device_origin "(nullable, max 40)"
        bool conflict_resolved "(default False)"
        text conflict_notes "(nullable)"
        datetime created_at
        datetime updated_at
    }

    DashboardMetric {
        bigint id PK
        int academic_period_id FK
        int section_id FK "(nullable)"
        int academic_grade_id FK "(nullable)"
        string metric_type "(max 50)"
        json metric_value
        datetime calculated_at "(auto_now_add)"
        datetime created_at
        datetime updated_at
    }

%% ========================================================================
%% MÓDULO: CONFIGURATION (Configuración)
%% ========================================================================

    SystemConfig {
        bigint id PK
        string key "(unique, max 255)"
        text value
        text description "(blank)"
        datetime created_at
        datetime updated_at
    }

%% ========================================================================
%% MÓDULO: INTEGRATION (Integración)
%% ========================================================================

    SyncOperation {
        bigint id PK
        string code "(unique, max 20)"
        string name "(max 100)"
        text description "(blank)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    SyncStatus {
        bigint id PK
        string code "(unique, max 20)"
        string name "(max 100)"
        text description "(blank)"
        bool is_active "(default True)"
        datetime created_at
        datetime updated_at
    }

    SyncSchemaVersion {
        bigint id PK
        string model_name "(unique, max 100)"
        int schema_version "(default 1)"
        string fields_hash "(max 64)"
        string min_client_version "(max 20, default 1.0.0)"
        datetime created_at
        datetime updated_at
    }

    SyncQueue {
        bigint id PK
        uuid uuid
        string idempotency_key "(unique, max 64)"
        int user_id FK
        string source_table "(max 100)"
        string record_uuid "(max 36)"
        int operation_id FK "(PROTECT)"
        json payload
        json previous_state
        int attempts "(default 0)"
        int max_attempts "(default 5)"
        text last_error "(nullable)"
        datetime last_attempt_at "(nullable)"
        int status_id FK "(nullable, PROTECT)"
        bool conflict_detected "(default False)"
        string resolution_strategy "(max 30)"
        int processed_by_id FK "(nullable, SET_NULL)"
        int resolved_by_id FK "(nullable, SET_NULL)"
        datetime processed_at "(nullable)"
        text resolution_notes "(nullable)"
        datetime created_at
        datetime updated_at
    }

%% ========================================================================
%% RELACIONES — CORE
%% ========================================================================

    User ||--o{ AuditLog : "registra"

%% ========================================================================
%% RELACIONES — IAM
%% ========================================================================

    User  ||--o{ UserRole : "tiene"
    Role  ||--o{ UserRole : "asignado a"
    Role  ||--o{ RolePermission : "contiene"
    Permission ||--o{ RolePermission : "asignado a"

%% ========================================================================
%% RELACIONES — PEOPLE
%% ========================================================================

    Person ||--o| User : "es usuario (1:1)"
    DocumentType ||--o{ Person : "clasifica"

%% ========================================================================
%% RELACIONES — INSTITUTIONS
%% ========================================================================

    AcademicLevel ||--o{ AcademicSublevel : "contiene"
    AcademicSublevel ||--o{ AcademicGrade : "agrupa"
    SchoolYear ||--o{ Section : "tiene"
    AcademicGrade ||--o{ Section : "clasifica"

%% ========================================================================
%% RELACIONES — ACADEMIC
%% ========================================================================

    SchoolYear ||--o{ AcademicPeriod : "contiene"
    AcademicPeriod ||--o| AcademicPeriod : "tiene padre (self)"
    PeriodType ||--o{ AcademicPeriod : "tipifica"

    Subject ||--o{ SubjectAcademicConfig : "configurado en"
    AcademicGrade ||--o{ SubjectAcademicConfig : "recibe"

    SchoolYear ||--o{ SubjectOffering : "ofrece en"
    Section ||--o{ SubjectOffering : "oferta"
    SubjectAcademicConfig ||--o{ SubjectOffering : "base de"

    User ||--o{ TeacherSubjectSection : "asignado como docente"
    SubjectOffering ||--o{ TeacherSubjectSection : "asignacion"

    SubjectOffering ||--o{ ClassSchedule : "tiene horario"
    DayOfWeek ||--o{ ClassSchedule : "dia"

    AcademicPeriod ||--o{ InterdisciplinaryProject : "proyectos"
    InterdisciplinaryProject ||--o{ SubjectProject : "incluye materias"
    SubjectOffering ||--o{ SubjectProject : "participa"
    User ||--o{ SubjectProject : "responsable"

%% ========================================================================
%% RELACIONES — STUDENTS
%% ========================================================================

    Person ||--o| Student : "es (1:1)"
    ResidentialZone ||--o{ Student : "residencia"
    SpecialNeedsType ||--o{ Student : "necesidad especial"

    Student ||--o{ Enrollment : "se matricula"
    Section ||--o{ Enrollment : "recibe matriculados"
    SchoolYear ||--o{ Enrollment : "periodo lectivo"
    EnrollmentStatus ||--o{ Enrollment : "estado actual"
    WithdrawalReason ||--o{ Enrollment : "motivo retiro"
    SchoolYear ||--o{ Enrollment : "año repetido"

    Enrollment ||--o{ EnrollmentHistory : "historial de cambios"
    EnrollmentStatus ||--o{ EnrollmentHistory : "estado anterior"
    EnrollmentStatus ||--o{ EnrollmentHistory : "nuevo estado"
    User ||--o{ EnrollmentHistory : "realiza cambio"

    Student ||--o{ StudentRepresentative : "tiene representante"
    Person ||--o{ StudentRepresentative : "es representante"
    Kinship ||--o{ StudentRepresentative : "parentesco"

%% ========================================================================
%% RELACIONES — GRADING
%% ========================================================================

    AcademicSublevel }|--|{ GradeType : "aplica a (M2M)"

    QualitativeScale ||--o{ QualitativeScaleSublevel : "disponible en"
    AcademicSublevel ||--o{ QualitativeScaleSublevel : "tiene escalas"

    AcademicPeriod ||--o{ EvaluationBlock : "evaluacion en"
    SubjectOffering ||--o{ EvaluationBlock : "bloques de"
    EvaluationType ||--o{ EvaluationBlock : "tipo de"

    EvaluationBlock ||--o{ BlockComponent : "componentes"
    BlockComponent ||--o{ ComponentIndicator : "indicadores"

    ComponentIndicator ||--o{ EvaluativeActivity : "actividades evalua"
    TeacherSubjectSection ||--o{ EvaluativeActivity : "creadas por"
    ActivityType ||--o{ EvaluativeActivity : "tipo de actividad"

    Enrollment ||--o{ StudentNote : "notas del estudiante"
    EvaluativeActivity ||--o{ StudentNote : "califica"
    GradeType ||--o{ StudentNote : "tipo calificacion"
    QualitativeScale ||--o{ StudentNote : "escala cualitativa"
    User ||--o{ StudentNote : "creada por"
    User ||--o{ StudentNote : "modificada por"

    StudentNote ||--o{ GradeChangeHistory : "historial de cambios"
    User ||--o{ GradeChangeHistory : "modificada por usuario"
    User ||--o{ GradeChangeHistory : "creada por"
    QualitativeScale ||--o{ GradeChangeHistory : "escala anterior"
    QualitativeScale ||--o{ GradeChangeHistory : "nueva escala"

    Enrollment ||--o{ PeriodGradeSummary : "resumen por periodo"
    SubjectOffering ||--o{ PeriodGradeSummary : "materia"
    AcademicPeriod ||--o{ PeriodGradeSummary : "periodo"
    QualitativeScale ||--o{ PeriodGradeSummary : "escala"
    PromotionStatus ||--o{ PeriodGradeSummary : "estado promocion"
    User ||--o{ PeriodGradeSummary : "calculado por"
    User ||--o{ PeriodGradeSummary : "aprobado por"

    PeriodGradeSummary ||--o{ RecoveryProcess : "recuperacion"
    SubjectOffering ||--o{ RecoveryProcess : "materia"
    User ||--o{ RecoveryProcess : "gestionado por"
    RecoveryProcessType ||--o{ RecoveryProcess : "tipo de proceso"

    RecoveryProcess ||--o{ RecoverySession : "sesiones de refuerzo"

    RecoveryProcess ||--o{ RecoveryProcessHistory : "historial"
    PromotionStatus ||--o{ RecoveryProcessHistory : "estado anterior"
    PromotionStatus ||--o{ RecoveryProcessHistory : "nuevo estado"
    User ||--o{ RecoveryProcessHistory : "cambiado por"

    Enrollment ||--o{ LearningReport : "informe de"
    AcademicPeriod ||--o{ LearningReport : "periodo"
    QualitativeScale ||--o{ LearningReport : "escala conducta"
    User ||--o{ LearningReport : "creado por"
    User ||--o{ LearningReport : "evaluado por"
    User ||--o{ LearningReport : "aprobado por"

    Enrollment ||--o{ ProjectNote : "nota proyecto"
    InterdisciplinaryProject ||--o{ ProjectNote : "califica"

%% ========================================================================
%% RELACIONES — ATTENDANCE
%% ========================================================================

    Enrollment ||--o{ Attendance : "asistencia"
    TeacherSubjectSection ||--o{ Attendance : "registro de"
    AcademicPeriod ||--o{ Attendance : "periodo"
    AttendanceStatus ||--o{ Attendance : "estado"
    AbsenceType ||--o{ Attendance : "tipo ausencia"
    User ||--o{ Attendance : "creado por"
    User ||--o{ Attendance : "modificado por"

%% ========================================================================
%% RELACIONES — BEHAVIOR
%% ========================================================================

    Enrollment ||--o{ ConductIncident : "incidentes"
    User ||--o{ ConductIncident : "reportado por"
    AcademicPeriod ||--o{ ConductIncident : "periodo"
    IncidentType ||--o{ ConductIncident : "tipo"
    Severity ||--o{ ConductIncident : "severidad"
    User ||--o{ ConductIncident : "creado por"
    User ||--o{ ConductIncident : "modificado por"
    User ||--o{ ConductIncident : "aprobado por"

    Enrollment ||--o{ SkillEvaluation : "habilidades"
    AcademicPeriod ||--o{ SkillEvaluation : "periodo"
    SocioemotionalSkill ||--o{ SkillEvaluation : "skill"
    QualitativeScale ||--o{ SkillEvaluation : "escala"

    Enrollment ||--o{ BehaviorEvaluation : "evaluacion conducta"
    AcademicPeriod ||--o{ BehaviorEvaluation : "periodo"
    QualitativeScale ||--o{ BehaviorEvaluation : "escala calculada"
    QualitativeScale ||--o{ BehaviorEvaluation : "escala final"
    User ||--o{ BehaviorEvaluation : "creado por"
    User ||--o{ BehaviorEvaluation : "evaluado por"
    User ||--o{ BehaviorEvaluation : "aprobado por"

    Enrollment ||--o{ DiagnosticEvaluation : "diagnosticos"
    AcademicPeriod ||--o{ DiagnosticEvaluation : "periodo"
    User ||--o{ DiagnosticEvaluation : "aplicado por"
    SocioemotionalArea ||--o{ DiagnosticEvaluation : "area"
    DevelopmentLevel ||--o{ DiagnosticEvaluation : "nivel desarrollo"

%% ========================================================================
%% RELACIONES — ANALYTICS
%% ========================================================================

    Enrollment ||--o{ StudentFeatureSnapshot : "metricas"
    AcademicPeriod ||--o{ StudentFeatureSnapshot : "periodo"

    Enrollment ||--o{ StudentRiskScore : "riesgo"
    AcademicPeriod ||--o{ StudentRiskScore : "periodo"

    StudentRiskScore ||--o{ StudentRiskFactor : "factores"
    RiskFactor ||--o{ StudentRiskFactor : "factor de"

    Enrollment ||--o{ EarlyAlert : "alertas"
    AcademicPeriod ||--o{ EarlyAlert : "periodo"
    AlertType ||--o{ EarlyAlert : "tipo"
    UrgencyLevel ||--o{ EarlyAlert : "urgencia"
    User ||--o{ EarlyAlert : "atendida por"

    AcademicPeriod ||--o{ DashboardMetric : "metrica"
    Section ||--o{ DashboardMetric : "seccion"
    AcademicGrade ||--o{ DashboardMetric : "grado"

%% ========================================================================
%% RELACIONES — INTEGRATION
%% ========================================================================

    User ||--o{ SyncQueue : "origina"
    SyncOperation ||--o{ SyncQueue : "operacion"
    SyncStatus ||--o{ SyncQueue : "estado"
    User ||--o{ SyncQueue : "procesado por"
    User ||--o{ SyncQueue : "resuelto por"
```

---

## Notas sobre el diagrama

1. **Modelo abstracto `TimeStampedModel`**: Todos los modelos (excepto `ResidentialZone`, `SpecialNeedsType`, `WithdrawalReason`, `Kinship`, `Severity`, `SocioemotionalArea`, `DevelopmentLevel`, `QualitativeScaleSublevel`) heredan de `TimeStampedModel` que provee `created_at` y `updated_at`. Los que no heredan son catálogos simples sin seguimiento de auditoría.

2. **Mixin abstracto `SyncableModel`**: Los siguientes modelos heredan campos de sincronización (`uuid`, `sync_status`, `sync_version`, `synced_at`, `device_origin`, `conflict_resolved`, `conflict_notes`):
   - `Enrollment`, `EvaluativeActivity`, `StudentNote`, `ProjectNote`, `RecoveryProcess`, `RecoverySession`, `LearningReport`, `Attendance`, `BehaviorEvaluation`, `ConductIncident`, `DiagnosticEvaluation`, `SkillEvaluation`, `EarlyAlert`

3. **Relación M2M entre `GradeType` y `AcademicSublevel`**: Es una relación muchos-a-muchos directa (Django crea la tabla intermedia automáticamente), no un modelo explícito.

4. **Relación M2M entre `InterdisciplinaryProject` y `SubjectOffering`**: Utiliza el modelo explícito `SubjectProject` como tabla intermedia (through model).

5. **Cardinalidades**:
   - `||--o|` = uno a uno (opcional en un lado)
   - `||--o{` = uno a muchos (opcional del lado muchos)
   - `||--||` = uno a uno (ambos obligatorios)
   - `}|--|{` = muchos a muchos
