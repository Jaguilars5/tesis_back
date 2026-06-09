from django.utils import timezone

from apps.iam.models import User


class UserRepository:
    @staticmethod
    def get_by_id(user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_by_username(username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_by_email(email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_by_dni(dni):
        query = User.objects.filter(person__document_number=dni)
        try:
            return query.get()
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_all_active():
        return User.objects.filter(is_active=True).order_by("username")

    @staticmethod
    def get_by_role(role_id):
        return User.objects.filter(
            user_roles__role_id=role_id, is_active=True
        ).distinct().order_by("username")

    @staticmethod
    def create(person, password, is_superuser=False, **extra_fields):
        now = timezone.now()
        extra_fields.setdefault("created_at", now)
        extra_fields["updated_at"] = now
        return User.objects.create_user(
            person=person,
            password=password,
            is_superuser=is_superuser,
            **extra_fields,
        )

    @staticmethod
    def update(user, **kwargs):
        allowed_fields = {"username", "email", "is_active"}
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(user, key, value)
        user.updated_at = timezone.now()
        user.save()
        return user

    @staticmethod
    def delete(user):
        user.is_active = False
        user.save()

    @staticmethod
    def bulk_create(user_list):
        now = timezone.now()
        users = []
        for user_data in user_list:
            user = User(
                person=user_data["person"],
                email=user_data["email"],
                created_at=now,
                updated_at=now,
            )
            user.set_password(user_data["password"])
            users.append(user)
        return User.objects.bulk_create(users)

    @staticmethod
    def search(query_string):
        from django.db.models import Q
        return User.objects.filter(
            Q(person__names__icontains=query_string)
            | Q(person__last_names__icontains=query_string)
            | Q(username__icontains=query_string)
            | Q(email__icontains=query_string),
            is_active=True,
        ).order_by("username")
