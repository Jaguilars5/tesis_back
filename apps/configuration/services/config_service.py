from ..repositories import ConfigRepository


class ConfigService:
    @staticmethod
    def get_config(key):
        return ConfigRepository.get_by_key(key)

    @staticmethod
    def set_config(key, value, description=""):
        existing = ConfigRepository.get_by_key(key)
        if existing:
            existing.value = value
            if description:
                existing.description = description
            existing.save()
            return existing
        return ConfigRepository.create(key=key, value=value, description=description)

    @staticmethod
    def delete_config(key):
        obj = ConfigRepository.get_by_key(key)
        if not obj:
            raise ValueError(f"Configuración '{key}' no encontrada")
        obj.delete()
        return True
