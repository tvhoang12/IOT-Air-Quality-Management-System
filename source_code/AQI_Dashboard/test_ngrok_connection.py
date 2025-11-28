#!/usr/bin/env python3
"""
Script test kết nối ngrok
"""
import requests
import json

# Thay URL ngrok của bạn vào đây
NGROK_URL = "https://inequilateral-youlanda-hypermagical.ngrok-free.dev/api/sensor-data/"

print("=" * 70)
print("  TEST NGROK CONNECTION")
print("=" * 70)
print(f"URL: {NGROK_URL}\n")

# Test data
test_data = {
    "temperature": 28.5,
    "humidity": 65.0,
    "gas_level": 180.0,
    "dust_density": 75.0,
    "aqi": 120,
    "air_quality_status": "MODERATE",
    "device_id": "TEST_NGROK"
}

try:
    print("📤 Đang gửi test data...")
    response = requests.post(
        NGROK_URL, 
        json=test_data,
        headers={"Content-Type": "application/json"},
        timeout=15
    )
    
    print(f"✅ Response Code: {response.status_code}")
    print(f"Response Body: {response.text}\n")
    
    if response.status_code == 201:
        print("🎉 KẾT NỐI THÀNH CÔNG!")
        result = response.json()
        if result.get('saved_to_database'):
            print("💾 [SAVED TO DATABASE]")
        else:
            print("⚡ [CACHED ONLY]")
    else:
        print("❌ Lỗi: Status code không phải 201")
        
except requests.exceptions.Timeout:
    print("❌ TIMEOUT - Ngrok hoặc Django server không phản hồi")
    print("   Kiểm tra:")
    print("   1. Django server đang chạy? (python manage.py runserver 8000)")
    print("   2. Ngrok đang chạy? (ngrok http 8000)")
    print("   3. URL ngrok còn hoạt động?")
    
except requests.exceptions.ConnectionError as e:
    print(f"❌ CONNECTION ERROR - {e}")
    print("   Kiểm tra:")
    print("   1. URL ngrok đúng?")
    print("   2. Ngrok đang chạy?")
    
except Exception as e:
    print(f"❌ LỖI: {e}")

print("\n" + "=" * 70)
