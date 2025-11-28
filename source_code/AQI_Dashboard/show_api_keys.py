#!/usr/bin/env python
"""
Script để hiển thị tất cả API Keys của các thiết bị
Chạy: python show_api_keys.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aqi_dashboard.settings')
django.setup()

from apps.devices.models import Device, DeviceKey

def show_all_api_keys():
    """Hiển thị tất cả API keys"""
    devices = Device.objects.all()
    
    if not devices.exists():
        print("\n" + "="*60)
        print("❌ CHƯA CÓ THIẾT BỊ NÀO TRONG HỆ THỐNG!")
        print("="*60)
        print("\n📝 Hướng dẫn tạo thiết bị:")
        print("1. Truy cập: http://127.0.0.1:8000/devices/add/")
        print("2. Nhập thông tin thiết bị")
        print("3. API Key sẽ được tạo tự động\n")
        return
    
    print("\n" + "="*60)
    print("📡 DANH SÁCH THIẾT BỊ VÀ API KEYS")
    print("="*60 + "\n")
    
    for idx, device in enumerate(devices, 1):
        print(f"🔹 Thiết bị #{idx}")
        print(f"   Tên thiết bị: {device.device_name}")
        print(f"   Mã thiết bị: {device.device_id}")
        print(f"   Chủ sở hữu: {device.owner.email}")
        print(f"   Vị trí: {device.location or 'Chưa có'}")
        print(f"   Trạng thái: {device.get_status_display()}")
        print(f"   Đang online: {'✅ Có' if device.is_online else '❌ Không'}")
        
        try:
            device_key = device.key
            print(f"\n   🔑 API Key: {device_key.api_key}")
            print(f"   🔐 Secret Key: {device_key.secret_key}")
            print(f"   📅 Ngày tạo: {device_key.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
        except DeviceKey.DoesNotExist:
            print("\n   ⚠️  Chưa có API Key (lỗi dữ liệu)")
        
        print("\n" + "-"*60 + "\n")
    
    print(f"📊 Tổng cộng: {devices.count()} thiết bị\n")

if __name__ == "__main__":
    show_all_api_keys()
