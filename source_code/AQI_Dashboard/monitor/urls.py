from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # API endpoints
    path('api/sensor-data/', views.receive_sensor_data, name='receive_sensor_data'),
    path('api/latest/', views.get_latest_data, name='get_latest_data'),
    path('api/historical/', views.get_historical_data, name='get_historical_data'),
    path('api/statistics/', views.get_statistics, name='get_statistics'),
    path('api/device-status/', views.get_device_status, name='get_device_status'),
    path('api/chart-data/', views.chart_data, name='chart_data'),
]
