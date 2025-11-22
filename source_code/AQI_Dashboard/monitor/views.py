from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Avg, Max, Min
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
import json

from .models import SensorData, DeviceStatus
from .serializers import SensorDataSerializer, DeviceStatusSerializer


def dashboard(request):
    """
    Trang dashboard chính hiển thị dữ liệu real-time
    """
    # Lấy dữ liệu mới nhất
    latest_data = SensorData.objects.first()
    
    # Lấy trạng thái thiết bị
    devices = DeviceStatus.objects.all()
    
    context = {
        'latest_data': latest_data,
        'devices': devices,
    }
    
    return render(request, 'monitor/dashboard.html', context)


@api_view(['POST'])
def receive_sensor_data(request):
    """
    API endpoint để nhận dữ liệu từ ESP32
    
    Expected JSON format:
    {
        "temperature": 25.5,
        "humidity": 60.0,
        "gas_level": 150.0,
        "dust_density": 35.0,
        "aqi": 85,
        "air_quality_status": "MODERATE",
        "device_id": "ESP32_001"
    }
    """
    serializer = SensorDataSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        
        # Cập nhật trạng thái thiết bị
        device_id = request.data.get('device_id', 'ESP32_001')
        ip_address = request.META.get('REMOTE_ADDR')
        
        device, created = DeviceStatus.objects.get_or_create(
            device_id=device_id,
            defaults={'device_name': f'Air Quality Monitor {device_id}'}
        )
        device.is_online = True
        device.ip_address = ip_address
        device.save()
        
        return Response({
            'status': 'success',
            'message': 'Dữ liệu đã được lưu thành công',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'status': 'error',
        'message': 'Dữ liệu không hợp lệ',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_latest_data(request):
    """
    API lấy dữ liệu mới nhất
    """
    device_id = request.GET.get('device_id', None)
    
    if device_id:
        latest = SensorData.objects.filter(device_id=device_id).first()
    else:
        latest = SensorData.objects.first()
    
    if latest:
        serializer = SensorDataSerializer(latest)
        return Response(serializer.data)
    
    return Response({
        'message': 'Không có dữ liệu'
    }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_historical_data(request):
    """
    API lấy dữ liệu lịch sử
    Parameters:
    - hours: số giờ lấy dữ liệu (mặc định 24)
    - device_id: mã thiết bị
    """
    hours = int(request.GET.get('hours', 24))
    device_id = request.GET.get('device_id', None)
    
    time_threshold = timezone.now() - timedelta(hours=hours)
    
    queryset = SensorData.objects.filter(timestamp__gte=time_threshold)
    
    if device_id:
        queryset = queryset.filter(device_id=device_id)
    
    data = queryset.order_by('timestamp')[:500]  # Giới hạn 500 điểm dữ liệu
    
    serializer = SensorDataSerializer(data, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_statistics(request):
    """
    API lấy thống kê dữ liệu
    Parameters:
    - hours: số giờ thống kê (mặc định 24)
    - device_id: mã thiết bị
    """
    hours = int(request.GET.get('hours', 24))
    device_id = request.GET.get('device_id', None)
    
    time_threshold = timezone.now() - timedelta(hours=hours)
    
    queryset = SensorData.objects.filter(timestamp__gte=time_threshold)
    
    if device_id:
        queryset = queryset.filter(device_id=device_id)
    
    stats = queryset.aggregate(
        avg_temp=Avg('temperature'),
        avg_humidity=Avg('humidity'),
        avg_gas=Avg('gas_level'),
        avg_dust=Avg('dust_density'),
        avg_aqi=Avg('aqi'),
        max_aqi=Max('aqi'),
        min_aqi=Min('aqi'),
    )
    
    # Đếm số lượng theo mức độ chất lượng không khí
    quality_distribution = {}
    for choice in SensorData.AIR_QUALITY_CHOICES:
        count = queryset.filter(air_quality_status=choice[0]).count()
        quality_distribution[choice[1]] = count
    
    return Response({
        'statistics': stats,
        'quality_distribution': quality_distribution,
        'total_records': queryset.count(),
        'time_range_hours': hours
    })


@api_view(['GET'])
def get_device_status(request):
    """
    API lấy trạng thái thiết bị
    """
    devices = DeviceStatus.objects.all()
    serializer = DeviceStatusSerializer(devices, many=True)
    return Response(serializer.data)


def chart_data(request):
    """
    API trả về dữ liệu cho biểu đồ
    """
    hours = int(request.GET.get('hours', 6))
    time_threshold = timezone.now() - timedelta(hours=hours)
    
    data = SensorData.objects.filter(
        timestamp__gte=time_threshold
    ).order_by('timestamp')[:100]
    
    chart_data = {
        'labels': [d.timestamp.strftime('%H:%M') for d in data],
        'temperature': [float(d.temperature) for d in data],
        'humidity': [float(d.humidity) for d in data],
        'gas_level': [float(d.gas_level) for d in data],
        'dust_density': [float(d.dust_density) for d in data],
        'aqi': [d.aqi for d in data],
    }
    
    return JsonResponse(chart_data)
