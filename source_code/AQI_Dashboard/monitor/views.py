from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json

from .models import SensorData
# from .firebase_service import firebase_service  # Commented out - using Django models now
# from .data_cache import data_cache  # Commented out - using Django models now


def dashboard(request):
    """
    Trang dashboard chính hiển thị dữ liệu real-time
    """
    from apps.devices.models import Device
    
    # Lấy dữ liệu mới nhất từ Django database
    latest_data = SensorData.objects.order_by('-timestamp').first()
    
    # Lấy danh sách thiết bị (nếu user đã đăng nhập)
    devices = []
    if request.user.is_authenticated:
        devices = Device.objects.filter(owner=request.user).prefetch_related('sensor_data')
    
    # Lấy 20 dữ liệu gần nhất
    recent_data = SensorData.objects.order_by('-timestamp')[:20]
    
    # Thống kê
    total_data = SensorData.objects.count()

    context = {
        'latest_data': latest_data,
        'devices': devices,
        'recent_data': recent_data,
        'total_data': total_data,
    }

    return render(request, 'monitor/dashboard.html', context)


@api_view(['POST'])
def receive_sensor_data(request):
    """
    API endpoint để nhận dữ liệu từ ESP32
    
    Dữ liệu được cập nhật vào cache mỗi lần nhận (real-time)
    Nhưng chỉ lưu vào Firebase database mỗi 5 phút

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
    # Validate required fields
    required_fields = ['temperature', 'humidity', 'gas_level', 'dust_density', 'aqi', 'air_quality_status', 'device_id']
    data = request.data

    for field in required_fields:
        if field not in data:
            return Response({
                'status': 'error',
                'message': f'Thiếu trường bắt buộc: {field}'
            }, status=status.HTTP_400_BAD_REQUEST)

    # 1. Luôn cập nhật cache (real-time display)
    data_cache.update_latest(data)
    
    # 2. Chỉ lưu vào Firebase database mỗi 5 phút
    saved_to_db = False
    doc_id = None
    
    if data_cache.should_save_to_db():
        doc_id = firebase_service.add_sensor_data(data)
        if doc_id:
            data_cache.mark_saved()
            saved_to_db = True
    
    # Response
    response_data = {
        'status': 'success',
        'message': 'Dữ liệu đã được cập nhật',
        'cached': True,
        'saved_to_database': saved_to_db,
        'data': data
    }
    
    if saved_to_db:
        response_data['document_id'] = doc_id
        response_data['message'] = 'Dữ liệu đã được lưu vào Firebase (5 phút interval)'
    
    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_latest_data(request):
    """
    API lấy dữ liệu mới nhất (real-time)
    """
    # Lấy từ Django database
    latest = SensorData.objects.order_by('-timestamp').first()

    if latest:
        return Response({
            'temperature': latest.temperature,
            'humidity': latest.humidity,
            'gas_level': latest.gas_level,
            'dust_density': latest.dust_density,
            'aqi': latest.aqi,
            'air_quality': latest.air_quality_status,
            'timestamp': latest.timestamp.isoformat(),
        })

    return Response({
        'message': 'Không có dữ liệu'
    }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_historical_data(request):
    """
    API lấy dữ liệu lịch sử
    Parameters:
    - hours: số giờ lấy dữ liệu (mặc định 24)
    """
    from datetime import timedelta
    from django.utils import timezone
    
    hours = int(request.GET.get('hours', 24))
    time_threshold = timezone.now() - timedelta(hours=hours)
    
    data = SensorData.objects.filter(
        timestamp__gte=time_threshold
    ).order_by('-timestamp').values(
        'temperature', 'humidity', 'gas_level', 'dust_density', 
        'aqi', 'air_quality_status', 'timestamp'
    )
    
    # Convert to list and format timestamps
    result = []
    for item in data:
        item['timestamp'] = item['timestamp'].isoformat()
        item['air_quality'] = item.pop('air_quality_status')  # Rename for frontend
        result.append(item)

    return Response(result)


@api_view(['GET'])
def get_statistics(request):
    """
    API lấy thống kê dữ liệu
    Parameters:
    - hours: số giờ thống kê (mặc định 24)
    """
    stats = firebase_service.get_statistics()

    return Response({
        'statistics': stats,
        'total_records': stats.get('total_records', 0),
        'time_range_hours': 24
    })


@api_view(['GET'])
def get_device_status(request):
    """
    API lấy trạng thái thiết bị (Firebase không hỗ trợ device status)
    """
    return Response([])


def chart_data(request):
    """
    API trả về dữ liệu cho biểu đồ
    """
    from datetime import timedelta
    from django.utils import timezone
    
    hours = int(request.GET.get('hours', 6))
    time_threshold = timezone.now() - timedelta(hours=hours)
    
    data = SensorData.objects.filter(
        timestamp__gte=time_threshold
    ).order_by('timestamp').values(
        'temperature', 'humidity', 'gas_level', 'dust_density', 
        'aqi', 'timestamp'
    )

    # Format data for Chart.js
    chart_data = {
        'labels': [d['timestamp'].strftime('%H:%M') for d in data],
        'temperature': [float(d['temperature']) for d in data],
        'humidity': [float(d['humidity']) for d in data],
        'gas_level': [float(d['gas_level']) for d in data],
        'dust_density': [float(d['dust_density']) for d in data],
        'aqi': [d['aqi'] for d in data],
    }

    return JsonResponse(chart_data)
