from django.urls import path
from . import views

app_name = 'devices'

urlpatterns = [
    path('', views.device_list, name='device_list'),
    path('add/', views.add_device, name='add_device'),
    path('<int:device_id>/', views.device_detail, name='device_detail'),
    path('<int:device_id>/delete/', views.delete_device, name='delete_device'),
    path('<int:device_id>/update/', views.update_device, name='update_device'),
    path('<int:device_id>/api-key/', views.device_api_key, name='device_api_key'),
    path('api/webhook/', views.device_data_webhook, name='webhook'),
]
