import firebase_admin
from firebase_admin import credentials, auth
import os
from django.conf import settings


def initialize_firebase():
    """
    Khởi tạo Firebase Admin SDK
    """
    cred_path = os.path.join(settings.BASE_DIR, 'firebase-service-account.json')
    
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(cred_path)
            # Initialize with Database URL to allow Realtime Database usage
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://long-iot-default-rtdb.firebaseio.com/'
            })
            print("Firebase initialized successfully")
        except Exception as e:
            print(f"Error initializing Firebase: {e}")


def verify_firebase_token(id_token):
    """
    Xác thực Firebase ID token
    
    Args:
        id_token: Firebase ID token từ client
        
    Returns:
        decoded_token nếu hợp lệ, None nếu không hợp lệ
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None


def get_user_by_uid(firebase_uid):
    """
    Lấy thông tin user từ Firebase bằng UID
    
    Args:
        firebase_uid: Firebase UID
        
    Returns:
        User record hoặc None
    """
    try:
        user = auth.get_user(firebase_uid)
        return user
    except Exception as e:
        print(f"Error getting user: {e}")
        return None


def create_custom_token(firebase_uid):
    """
    Tạo custom token cho user
    
    Args:
        firebase_uid: Firebase UID
        
    Returns:
        Custom token hoặc None
    """
    try:
        token = auth.create_custom_token(firebase_uid)
        return token
    except Exception as e:
        print(f"Error creating custom token: {e}")
        return None
