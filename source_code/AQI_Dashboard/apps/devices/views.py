from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Device, DeviceKey
import json


@login_required
def device_list(request):
    """Danh sách thiết bị của user"""
    devices = Device.objects.filter(owner=request.user).select_related('key')
    return render(request, 'devices/device_list.html', {'devices': devices})


@login_required
def add_device(request):
    """Thêm thiết bị mới"""
    if request.method == 'POST':
        try:
            device_name = request.POST.get('device_name')
            device_id = request.POST.get('device_id')
            location = request.POST.get('location', '')
            description = request.POST.get('description', '')
            
            if not device_name or not device_id:
                return JsonResponse({'error': 'Tên thiết bị và mã thiết bị là bắt buộc'}, status=400)
            
            # Kiểm tra device_id đã tồn tại chưa
            if Device.objects.filter(device_id=device_id).exists():
                return JsonResponse({'error': 'Mã thiết bị đã tồn tại'}, status=400)
            
            # Tạo device
            device = Device.objects.create(
                device_id=device_id,
                device_name=device_name,
                owner=request.user,
                location=location,
                description=description
            )
            
            # Tạo API keys
            api_key, secret_key = DeviceKey.generate_keys()
            DeviceKey.objects.create(
                device=device,
                api_key=api_key,
                secret_key=secret_key
            )
            
            return JsonResponse({
                'success': True,
                'device_id': device.id,
                'api_key': api_key,
                'secret_key': secret_key,
                'message': 'Thiết bị đã được thêm thành công'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'devices/add_device.html')


@login_required
def device_detail(request, device_id):
    """Chi tiết thiết bị"""
    device = get_object_or_404(Device, id=device_id, owner=request.user)
    
    # Lấy dữ liệu sensor gần nhất
    from monitor.models import SensorData
    latest_data = SensorData.objects.filter(device=device).order_by('-timestamp').first()
    recent_data = SensorData.objects.filter(device=device).order_by('-timestamp')[:20]
    
    context = {
        'device': device,
        'latest_data': latest_data,
        'recent_data': recent_data,
    }
    return render(request, 'devices/device_detail.html', context)


@login_required
@require_http_methods(["POST"])
def delete_device(request, device_id):
    """Xóa thiết bị"""
    try:
        device = get_object_or_404(Device, id=device_id, owner=request.user)
        device.delete()
        return JsonResponse({'success': True, 'message': 'Thiết bị đã được xóa'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def update_device(request, device_id):
    """Cập nhật thông tin thiết bị"""
    try:
        device = get_object_or_404(Device, id=device_id, owner=request.user)
        data = json.loads(request.body)
        
        if 'device_name' in data:
            device.device_name = data['device_name']
        if 'location' in data:
            device.location = data['location']
        if 'description' in data:
            device.description = data['description']
        if 'status' in data:
            device.status = data['status']
        
        device.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Thiết bị đã được cập nhật'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def device_data_webhook(request):
    """
    Endpoint cho ESP32 gửi dữ liệu sensor
    Header: X-API-Key: <api_key>
    Body: JSON với temperature, humidity, gas_level, dust_density
    """
    try:
        # Lấy API key từ header
        api_key = request.META.get('HTTP_X_API_KEY')
        
        if not api_key:
            return JsonResponse({'error': 'API key is required'}, status=401)
        
        # Xác thực API key
        try:
            device_key = DeviceKey.objects.select_related('device').get(api_key=api_key)
            device = device_key.device
        except DeviceKey.DoesNotExist:
            return JsonResponse({'error': 'Invalid API key'}, status=401)
        
        # Parse dữ liệu
        data = json.loads(request.body)
        
        # Cập nhật trạng thái device
        device.update_last_seen()
        if 'ip_address' in data:
            device.ip_address = data['ip_address']
            device.save(update_fields=['ip_address'])
        
        # Lưu dữ liệu sensor
        from monitor.models import SensorData
        
        # Lấy giá trị sensor
        # Lấy giá trị sensor (Raw Data)
        temperature = float(data.get('temperature', 0))
        humidity = float(data.get('humidity', 0))
        raw_gas = float(data.get('gas_level', 0))
        raw_dust = float(data.get('dust_density', 0))

        # --- AI CALIBRATION START ---
        import joblib
        import pandas as pd
        import os
        from django.conf import settings

        try:
            model_path = os.path.join(settings.BASE_DIR, 'sensor_calibration_model.pkl')
            if os.path.exists(model_path):
                # Load model (nên cache model global để tối ưu performance, nhưng load ở đây cho đơn giản trước)
                model = joblib.load(model_path)
                
                # Prepare input dataframe
                input_df = pd.DataFrame({
                    'raw_dust': [raw_dust],
                    'raw_gas': [raw_gas],
                    'temperature': [temperature],
                    'humidity': [humidity]
                })
                
                # Predict corrected values
                prediction = model.predict(input_df)
                corrected_dust = prediction[0][0]
                corrected_gas = prediction[0][1]
                
                # Update values to use corrected ones
                # Giữ lại giá trị gốc nếu muốn lưu cả 2 (cần sửa model), ở đây ta ghi đè để tính AQI chuẩn hơn
                dust_density = max(0, corrected_dust) # Không âm
                gas_level = max(0, corrected_gas)
                
                print(f"AI Calibration: Dust {raw_dust}->{dust_density:.2f}, Gas {raw_gas}->{gas_level:.2f}")
            else:
                print("Model not found, using raw data")
                dust_density = raw_dust
                gas_level = raw_gas
        except Exception as e:
            print(f"AI Error: {e}")
            dust_density = raw_dust
            gas_level = raw_gas
        # --- AI CALIBRATION END ---
        
        # Tính AQI đơn giản (có thể cải tiến sau)
        # Công thức đơn giản hóa: tính AQI từ dust_density
        # Dust PM2.5: 0-50 = Good, 51-100 = Moderate, 101-150 = Unhealthy for Sensitive Groups
        if dust_density <= 50:
            aqi = int(dust_density)
        elif dust_density <= 100:
            aqi = int(50 + (dust_density - 50) * 0.5)
        else:
            aqi = int(75 + (dust_density - 100) * 0.75)
        
        # Giới hạn AQI trong khoảng hợp lý
        aqi = min(max(aqi, 0), 500)
        
        # Xác định air_quality_status dựa trên AQI
        if aqi <= 50:
            air_quality_status = 'GOOD'
        elif aqi <= 100:
            air_quality_status = 'MODERATE'
        elif aqi <= 150:
            air_quality_status = 'UNHEALTHY_SENSITIVE'
        elif aqi <= 200:
            air_quality_status = 'UNHEALTHY'
        elif aqi <= 300:
            air_quality_status = 'VERY_UNHEALTHY'
        else:
            air_quality_status = 'HAZARDOUS'
        
        sensor_data = SensorData.objects.create(
            device=device,
            temperature=temperature,
            humidity=humidity,
            gas_level=gas_level,
            dust_density=dust_density,
            aqi=aqi,
            air_quality_status=air_quality_status
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Data received',
            'data_id': sensor_data.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def device_api_key(request, device_id):
    """Xem API key của thiết bị"""
    device = get_object_or_404(Device, id=device_id, owner=request.user)
    try:
        device_key = device.key
        return JsonResponse({
            'api_key': device_key.api_key,
            'secret_key': device_key.secret_key,
        })
    except DeviceKey.DoesNotExist:
        return JsonResponse({'error': 'API key not found'}, status=404)
