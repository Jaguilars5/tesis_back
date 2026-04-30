"""
UserRepository - Acceso a datos para User.

Centraliza todas las queries complejas de User en este repositorio.
El service nunca escribe directamente User.objects.filter(...),
sino que delega al repository.
"""

from apps.accounts.models import User


class UserRepository:
    """
    Repositorio de acceso a datos para User.
    """

    @staticmethod
    def get_by_id(user_id):
        """Obtiene un usuario por ID."""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_by_email(email):
        """Obtiene un usuario por email."""
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_by_dni(dni, institution_id=None):
        """
        Obtiene un usuario por DNI.
        Si institution_id se proporciona, filtra también por institución.
        """
        query = User.objects.filter(dni=dni)
        if institution_id:
            query = query.filter(institution_id=institution_id)
        try:
            return query.get()
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_all_active(institution_id=None):
        """
        Obtiene todos los usuarios activos.
        Si institution_id se proporciona, filtra por institución.
        """
        query = User.objects.filter(active=True).select_related("role", "institution")
        if institution_id:
            query = query.filter(institution_id=institution_id)
        return query.order_by("email")

    @staticmethod
    def get_by_role(role_id, institution_id=None):
        """
        Obtiene todos los usuarios con un rol específico.
        """
        query = User.objects.filter(role_id=role_id, active=True).select_related(
            "role", "institution"
        )
        if institution_id:
            query = query.filter(institution_id=institution_id)
        return query.order_by("email")

    @staticmethod
    def get_by_institution(institution_id):
        """Obtiene todos los usuarios de una institución."""
        return (
            User.objects.filter(institution_id=institution_id, active=True)
            .select_related("role", "institution")
            .order_by("email")
        )

    @staticmethod
    def create(dni, names, last_names, email, password, role, institution):
        """
        Crea un nuevo usuario.
        """
        user = User(
            dni=dni,
            names=names,
            last_names=last_names,
            email=email,
            role=role,
            institution=institution,
        )
        user.set_password(password)
        user.save()
        return user

    @staticmethod
    def update(user, **kwargs):
        """
        Actualiza un usuario con los campos provistos.

        Campos soportados: names, last_names, email, role, active
        (No actualiza dni ni password directamente)
        """
        allowed_fields = {"names", "last_names", "email", "role", "active"}
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(user, key, value)
        user.save()
        return user

    @staticmethod
    def delete(user):
        """
        Soft-delete (marca como inactivo) o hard-delete.
        Por defecto hace soft-delete.
        """
        user.active = False
        user.save()

    @staticmethod
    def bulk_create(user_list):
        """
        Crea múltiples usuarios en una sola query.

        user_list: lista de dictionaries con claves:
          {'dni': ..., 'names': ..., 'last_names': ..., 'email': ..., 'password': ..., 'role': ..., 'institution': ...}
        """
        users = []
        for user_data in user_list:
            user = User(
                dni=user_data["dni"],
                names=user_data["names"],
                last_names=user_data["last_names"],
                email=user_data["email"],
                role=user_data["role"],
                institution=user_data["institution"],
            )
            user.set_password(user_data["password"])
            users.append(user)
        return User.objects.bulk_create(users)

    @staticmethod
    def search(query_string, institution_id=None):
        """
        Búsqueda por nombre, apellido o email (case-insensitive).
        """
        from django.db.models import Q

        query = User.objects.filter(
            Q(names__icontains=query_string)
            | Q(last_names__icontains=query_string)
            | Q(email__icontains=query_string),
            active=True,
        ).select_related("role", "institution")
        if institution_id:
            query = query.filter(institution_id=institution_id)
        return query.order_by("email")
