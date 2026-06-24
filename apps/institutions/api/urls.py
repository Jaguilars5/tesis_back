from django.urls import path, include

urlpatterns = [
    path("", include("apps.institutions.school_year.urls")),
    path("", include("apps.institutions.academic_level.urls")),
    path("", include("apps.institutions.academic_sublevel.urls")),
    path("", include("apps.institutions.academic_grade.urls")),
    path("", include("apps.institutions.section.urls")),
]
