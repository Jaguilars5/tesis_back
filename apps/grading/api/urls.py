from django.urls import path

from . import views

urlpatterns = []


def add_model_urls(model_name_kebab, views_prefix):
    urlpatterns.extend(
        [
            path(
                f"{model_name_kebab}/list/",
                getattr(views, f"{views_prefix}_list"),
                name=f"{model_name_kebab}-list",
            ),
            path(
                f"{model_name_kebab}/get/",
                getattr(views, f"{views_prefix}_get"),
                name=f"{model_name_kebab}-get",
            ),
            path(
                f"{model_name_kebab}/add/",
                getattr(views, f"{views_prefix}_add"),
                name=f"{model_name_kebab}-add",
            ),
            path(
                f"{model_name_kebab}/update/",
                getattr(views, f"{views_prefix}_update"),
                name=f"{model_name_kebab}-update",
            ),
            path(
                f"{model_name_kebab}/soft-delete/",
                getattr(views, f"{views_prefix}_soft_delete"),
                name=f"{model_name_kebab}-soft-delete",
            ),
            path(
                f"{model_name_kebab}/delete/",
                getattr(views, f"{views_prefix}_delete"),
                name=f"{model_name_kebab}-delete",
            ),
        ]
    )


add_model_urls("student-note", "student_note")
add_model_urls("attendance", "attendance")
add_model_urls("conduct-incident", "conduct_incident")
