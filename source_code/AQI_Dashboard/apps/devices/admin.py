from django.contrib import admin
from .models import Device, DeviceKey


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'device_id', 'owner', 'status', 'is_online', 'last_seen', 'created_at')
    list_filter = ('status', 'is_online', 'created_at')
    search_fields = ('device_name', 'device_id', 'owner__username', 'owner__email', 'location')
    readonly_fields = ('created_at', 'updated_at', 'last_seen')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('device_id', 'device_name', 'owner', 'location', 'description')
        }),
        ('Trạng thái', {
            'fields': ('status', 'is_online', 'last_seen', 'ip_address', 'firmware_version')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DeviceKey)
class DeviceKeyAdmin(admin.ModelAdmin):
    list_display = ('device', 'api_key', 'created_at')
    search_fields = ('device__device_name', 'api_key')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
