from django.db import models
from django.utils import timezone


class SensorData(models.Model):
    """
    Model lưu trữ dữ liệu từ các cảm biến
    """
    # Dữ liệu từ cảm biến DHT11
    temperature = models.FloatField(
        verbose_name="Nhiệt độ (°C)",
        help_text="Nhiệt độ đo được từ cảm biến DHT11"
    )
    humidity = models.FloatField(
        verbose_name="Độ ẩm (%)",
        help_text="Độ ẩm đo được từ cảm biến DHT11"
    )
    
    # Dữ liệu từ cảm biến MQ-135
    gas_level = models.FloatField(
        verbose_name="Mức Gas (ppm)",
        help_text="Nồng độ khí độc hại từ cảm biến MQ-135"
    )
    
    # Dữ liệu từ cảm biến bụi GP2Y10
    dust_density = models.FloatField(
        verbose_name="Mật độ bụi (µg/m³)",
        help_text="Nồng độ bụi mịn từ cảm biến GP2Y10"
    )
    
    # Chỉ số AQI tính toán
    aqi = models.IntegerField(
        verbose_name="Chỉ số AQI",
        help_text="Air Quality Index được tính từ các cảm biến"
    )
    
    # Mức độ chất lượng không khí
    AIR_QUALITY_CHOICES = [
        ('GOOD', 'Tốt'),
        ('MODERATE', 'Trung bình'),
        ('UNHEALTHY_SENSITIVE', 'Không tốt cho nhóm nhạy cảm'),
        ('UNHEALTHY', 'Không tốt'),
        ('VERY_UNHEALTHY', 'Rất không tốt'),
        ('HAZARDOUS', 'Nguy hại'),
    ]
    
    air_quality_status = models.CharField(
        max_length=30,
        choices=AIR_QUALITY_CHOICES,
        verbose_name="Mức độ chất lượng không khí"
    )
    
    # Thông tin thêm
    device_id = models.CharField(
        max_length=50,
        default="ESP32_001",
        verbose_name="Mã thiết bị"
    )
    
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name="Thời gian ghi nhận"
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Dữ liệu cảm biến"
        verbose_name_plural = "Dữ liệu cảm biến"
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['device_id', '-timestamp']),
        ]
    
    def __str__(self):
        return f"AQI: {self.aqi} - {self.get_air_quality_status_display()} ({self.timestamp.strftime('%d/%m/%Y %H:%M:%S')})"
    
    def get_aqi_color(self):
        """Trả về màu sắc tương ứng với mức AQI"""
        if self.aqi <= 50:
            return '#00E400'  # Xanh lá
        elif self.aqi <= 100:
            return '#FFFF00'  # Vàng
        elif self.aqi <= 150:
            return '#FF7E00'  # Cam
        elif self.aqi <= 200:
            return '#FF0000'  # Đỏ
        elif self.aqi <= 300:
            return '#8F3F97'  # Tím
        else:
            return '#7E0023'  # Nâu đỏ
    
    def get_led_color(self):
        """Trả về màu LED tương ứng"""
        if self.aqi <= 100:
            return 'GREEN'
        elif self.aqi <= 200:
            return 'YELLOW'
        else:
            return 'RED'


class DeviceStatus(models.Model):
    """
    Model theo dõi trạng thái thiết bị
    """
    device_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Mã thiết bị"
    )
    device_name = models.CharField(
        max_length=100,
        verbose_name="Tên thiết bị"
    )
    is_online = models.BooleanField(
        default=False,
        verbose_name="Trạng thái kết nối"
    )
    last_seen = models.DateTimeField(
        auto_now=True,
        verbose_name="Lần kết nối cuối"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Địa chỉ IP"
    )
    firmware_version = models.CharField(
        max_length=20,
        default="1.0.0",
        verbose_name="Phiên bản firmware"
    )
    
    class Meta:
        verbose_name = "Trạng thái thiết bị"
        verbose_name_plural = "Trạng thái thiết bị"
    
    def __str__(self):
        status = "Online" if self.is_online else "Offline"
        return f"{self.device_name} - {status}"
