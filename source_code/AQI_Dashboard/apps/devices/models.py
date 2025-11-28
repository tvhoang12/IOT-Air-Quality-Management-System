from django.db import models
from django.conf import settings
from django.utils import timezone
import secrets
import hashlib


class Device(models.Model):
    """
    Model cho IoT Device
    """
    DEVICE_STATUS = [
        ('active', 'Hoạt động'),
        ('inactive', 'Không hoạt động'),
        ('maintenance', 'Bảo trì'),
    ]
    
    device_id = models.CharField(max_length=100, unique=True, verbose_name='Mã thiết bị')
    device_name = models.CharField(max_length=255, verbose_name='Tên thiết bị')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='devices',
        verbose_name='Chủ sở hữu'
    )
    location = models.CharField(max_length=255, blank=True, verbose_name='Vị trí')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    status = models.CharField(
        max_length=20, 
        choices=DEVICE_STATUS, 
        default='active',
        verbose_name='Trạng thái'
    )
    is_online = models.BooleanField(default=False, verbose_name='Đang kết nối')
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name='Lần kết nối cuối')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='Địa chỉ IP')
    firmware_version = models.CharField(max_length=20, default='1.0.0', verbose_name='Phiên bản firmware')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')
    
    class Meta:
        db_table = 'devices'
        verbose_name = 'Thiết bị'
        verbose_name_plural = 'Thiết bị'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.device_name} ({self.device_id})"
    
    def update_last_seen(self):
        """Cập nhật thời gian kết nối cuối"""
        self.last_seen = timezone.now()
        self.is_online = True
        self.save(update_fields=['last_seen', 'is_online'])
    
    @property
    def sensor_data_count(self):
        """Số lượng dữ liệu sensor"""
        return self.sensor_data.count()


class DeviceKey(models.Model):
    """
    Model lưu API key và Secret key cho device
    """
    device = models.OneToOneField(
        Device, 
        on_delete=models.CASCADE, 
        related_name='key',
        verbose_name='Thiết bị'
    )
    api_key = models.CharField(max_length=64, unique=True, verbose_name='API Key')
    secret_key = models.CharField(max_length=128, verbose_name='Secret Key')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    
    class Meta:
        db_table = 'device_keys'
        verbose_name = 'Khóa thiết bị'
        verbose_name_plural = 'Khóa thiết bị'
    
    def __str__(self):
        return f"Key for {self.device.device_name}"
    
    @staticmethod
    def generate_keys():
        """Tạo API key và Secret key mới"""
        api_key = secrets.token_urlsafe(32)
        secret_key = hashlib.sha256(secrets.token_bytes(32)).hexdigest()
        return api_key, secret_key
