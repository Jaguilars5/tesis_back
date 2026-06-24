from django.urls import path, include

urlpatterns = [
    path("", include("apps.academic.academic_period.urls")),
    path("", include("apps.academic.subject.urls")),
    path("", include("apps.academic.period_type.urls")),
    path("", include("apps.academic.subject_academic_config.urls")),
    path("", include("apps.academic.subject_offering.urls")),
    path("", include("apps.academic.teacher_subject_section.urls")),
    path("", include("apps.academic.class_schedule.urls")),
]
