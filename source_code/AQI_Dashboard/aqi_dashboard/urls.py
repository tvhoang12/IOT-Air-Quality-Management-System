"""
URL configuration for aqi_dashboard project.
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('apps.users.urls')),
    path('devices/', include('apps.devices.urls')),
    path('monitor/', include('monitor.urls')),
    path('', lambda request: redirect('devices:device_list')),
]
