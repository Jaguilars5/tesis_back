from ..repositories.document_type_repository import DocumentTypeRepository


class DocumentTypeService:
    @staticmethod
    def list_document_types(active_only=True):
        return DocumentTypeRepository.get_all(active_only=active_only)

    @staticmethod
    def get_document_type(doc_type_id):
        doc_type = DocumentTypeRepository.get_by_id(doc_type_id)
        if not doc_type:
            raise ValueError(f"Tipo de documento {doc_type_id} no encontrado")
        return doc_type

    @staticmethod
    def create_document_type(code, name, **kwargs):
        return DocumentTypeRepository.create(code=code, name=name, **kwargs)

    @staticmethod
    def update_document_type(doc_type_id, **kwargs):
        doc_type = DocumentTypeService.get_document_type(doc_type_id)
        for key, value in kwargs.items():
            if hasattr(doc_type, key):
                setattr(doc_type, key, value)
        doc_type.save()
        return doc_type

    @staticmethod
    def delete_document_type(doc_type_id):
        doc_type = DocumentTypeService.get_document_type(doc_type_id)
        doc_type.delete()
        return True
