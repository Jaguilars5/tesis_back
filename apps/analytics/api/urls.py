from django.urls import path
from . import views

urlpatterns = [
    path("student-risk/list/", views.student_risk_list, name="student-risk-list"),
    path("student-risk/get/", views.student_risk_get, name="student-risk-get"),
    path("feature-snapshot/list/", views.feature_snapshot_list, name="feature-snapshot-list"),
    path("feature-snapshot/get/", views.feature_snapshot_get, name="feature-snapshot-get"),
]
