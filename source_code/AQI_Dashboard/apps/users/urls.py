from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('api/auth/', views.firebase_auth, name='firebase_auth'),
    path('api/profile/update/', views.update_profile, name='update_profile'),
]
