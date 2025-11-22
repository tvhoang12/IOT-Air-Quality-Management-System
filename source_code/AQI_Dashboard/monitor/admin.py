from django.contrib import admin
from .models import SensorData, DeviceStatus


@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'device_id', 'temperature', 'humidity', 'gas_level', 'dust_density', 'aqi', 'air_quality_status']
    list_filter = ['air_quality_status', 'device_id', 'timestamp']
    search_fields = ['device_id']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('Thông tin thiết bị', {
            'fields': ('device_id', 'timestamp')
        }),
        ('Dữ liệu cảm biến', {
            'fields': ('temperature', 'humidity', 'gas_level', 'dust_density')
        }),
        ('Chất lượng không khí', {
            'fields': ('aqi', 'air_quality_status')
        }),
    )


@admin.register(DeviceStatus)
class DeviceStatusAdmin(admin.ModelAdmin):
    list_display = ['device_id', 'device_name', 'is_online', 'last_seen', 'ip_address', 'firmware_version']
    list_filter = ['is_online']
    search_fields = ['device_id', 'device_name']
    readonly_fields = ['last_seen']
