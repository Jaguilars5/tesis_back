from django.urls import path, include

urlpatterns = [
    path("", include("apps.grading.activity_type.urls")),
    path("", include("apps.grading.qualitative_scale.urls")),
    path("", include("apps.grading.evaluation.urls")),
    path("", include("apps.grading.student_note.urls")),
]
