from django.db import models
from ..models import Person


class PersonRepository:
    @staticmethod
    def get_all():
        return Person.objects.all().order_by("last_names", "names")

    @staticmethod
    def get_by_id(pk):
        try:
            return Person.objects.get(pk=pk)
        except Person.DoesNotExist:
            return None

    @staticmethod
    def get_by_document_number(doc_number):
        try:
            return Person.objects.get(document_number=doc_number)
        except Person.DoesNotExist:
            return None

    @staticmethod
    def search(query):
        return Person.objects.filter(
            models.Q(names__icontains=query)
            | models.Q(last_names__icontains=query)
            | models.Q(document_number__icontains=query)
            | models.Q(email__icontains=query)
        )

    @staticmethod
    def get_by_email(email):
        try:
            return Person.objects.get(email__iexact=email)
        except Person.DoesNotExist:
            return None
