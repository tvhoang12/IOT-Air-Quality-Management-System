from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'User Management'
    
    def ready(self):
        """Khởi tạo Firebase khi Django khởi động"""
        from .firebase_config import initialize_firebase
        initialize_firebase()
