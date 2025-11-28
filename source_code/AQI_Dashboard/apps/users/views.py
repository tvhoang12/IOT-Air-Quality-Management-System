from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from .firebase_config import verify_firebase_token
import json

User = get_user_model()


def login_view(request):
    """Trang đăng nhập"""
    if request.user.is_authenticated:
        return redirect('devices:device_list')
    return render(request, 'auth/login.html')


def register_view(request):
    """Trang đăng ký"""
    if request.user.is_authenticated:
        return redirect('devices:device_list')
    return render(request, 'auth/register.html')


@csrf_exempt
@require_http_methods(["POST"])
def firebase_auth(request):
    """
    API endpoint xác thực Firebase và tạo/cập nhật user trong database
    """
    try:
        data = json.loads(request.body)
        id_token = data.get('idToken')
        
        if not id_token:
            return JsonResponse({'error': 'Token is required'}, status=400)
        
        # Verify Firebase token
        decoded_token = verify_firebase_token(id_token)
        if not decoded_token:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        
        firebase_uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        
        # Tạo hoặc cập nhật user
        user, created = User.objects.get_or_create(
            firebase_uid=firebase_uid,
            defaults={
                'email': email,
                'username': email.split('@')[0] if email else firebase_uid[:30],
            }
        )
        
        # Cập nhật thông tin bổ sung nếu có
        if created or data.get('fullname') or data.get('phone'):
            if data.get('fullname'):
                user.fullname = data.get('fullname', '')
            if data.get('phone'):
                user.phone = data.get('phone', '')
            if email and not user.email:
                user.email = email
            user.save()
        
        # Django login
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'fullname': user.fullname,
                'phone': user.phone,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def logout_view(request):
    """Đăng xuất"""
    logout(request)
    return redirect('users:login')


@login_required
def profile_view(request):
    """Trang profile người dùng"""
    return render(request, 'auth/profile.html', {
        'user': request.user,
        'devices': request.user.devices.all()
    })


@login_required
@require_http_methods(["POST"])
def update_profile(request):
    """API cập nhật thông tin profile"""
    try:
        data = json.loads(request.body)
        user = request.user
        
        if 'fullname' in data:
            user.fullname = data['fullname']
        if 'phone' in data:
            user.phone = data['phone']
        
        user.save()
        
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'fullname': user.fullname,
                'phone': user.phone,
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
