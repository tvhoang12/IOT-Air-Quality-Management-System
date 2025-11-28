from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom User model với Firebase authentication
    """
    firebase_uid = models.CharField(max_length=128, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, verbose_name='Số điện thoại')
    fullname = models.CharField(max_length=255, blank=True, verbose_name='Họ và tên')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email or self.username
    
    @property
    def device_count(self):
        """Số lượng thiết bị của user"""
        return self.devices.count()
