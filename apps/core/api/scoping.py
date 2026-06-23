def scope_student_to_enrollment(request, qs, field_name="enrollment"):
    """If the user has role ESTUDIANTE, scope the queryset to their active enrollment.

    This provides row-level security for student-facing endpoints,
    ensuring students can only see data linked to their own active enrollment.
    """
    user = request.user

    if not user.is_authenticated:
        return qs

    if user.is_superuser:
        return qs

    user_roles = getattr(user, "user_roles", None)
    if user_roles is None:
        return qs

    if not user_roles.filter(role__code="ESTUDIANTE").exists():
        return qs

    from apps.students.models import Student, Enrollment

    student = Student.objects.filter(user=user).first()
    if not student:
        return qs.none()

    enrollment = Enrollment.objects.filter(
        student=student, enrollment_status="ACT"
    ).first()
    if not enrollment:
        return qs.none()

    return qs.filter(**{field_name: enrollment})
