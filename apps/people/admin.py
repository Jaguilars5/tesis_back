from django.contrib import admin
from .models import DocumentType, Parish, Person


@admin.register(Parish)
class ParishAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "parish_type", "city", "is_active")
    list_filter = ("parish_type", "city", "is_active")
    search_fields = ("name", "code")


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("names", "last_names", "document_number", "email")
    search_fields = ("names", "last_names", "document_number", "email")
