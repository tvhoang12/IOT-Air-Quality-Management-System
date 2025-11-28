from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .firebase_config import verify_firebase_token

User = get_user_model()


class FirebaseAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware xác thực Firebase token cho API requests
    """
    
    def process_request(self, request):
        # Bỏ qua các static files và admin
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return None
        
        # Lấy token từ header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            id_token = auth_header.split('Bearer ')[1]
            decoded_token = verify_firebase_token(id_token)
            
            if decoded_token:
                firebase_uid = decoded_token['uid']
                try:
                    user = User.objects.get(firebase_uid=firebase_uid)
                    request.user = user
                    request.firebase_user = decoded_token
                except User.DoesNotExist:
                    # User chưa tồn tại trong database
                    pass
        
        return None
