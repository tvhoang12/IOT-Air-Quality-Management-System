from rest_framework import serializers
from .models import SensorData, DeviceStatus


class SensorDataSerializer(serializers.ModelSerializer):
    """
    Serializer cho dữ liệu cảm biến
    """
    class Meta:
        model = SensorData
        fields = ['id', 'temperature', 'humidity', 'gas_level', 'dust_density', 
                  'aqi', 'air_quality_status', 'device_id', 'timestamp']
        read_only_fields = ['id', 'timestamp']
    
    def validate_temperature(self, value):
        if value < -40 or value > 80:
            raise serializers.ValidationError("Nhiệt độ không hợp lệ")
        return value
    
    def validate_humidity(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Độ ẩm phải từ 0-100%")
        return value
    
    def validate_aqi(self, value):
        if value < 0 or value > 500:
            raise serializers.ValidationError("AQI phải từ 0-500")
        return value


class DeviceStatusSerializer(serializers.ModelSerializer):
    """
    Serializer cho trạng thái thiết bị
    """
    class Meta:
        model = DeviceStatus
        fields = ['device_id', 'device_name', 'is_online', 'last_seen', 
                  'ip_address', 'firmware_version']
        read_only_fields = ['last_seen']
