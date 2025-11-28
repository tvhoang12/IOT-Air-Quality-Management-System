#!/usr/bin/env python3
"""
Test nhanh Firebase Realtime Database connection
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from monitor.firebase_service import firebase_service
import requests

print("=" * 60)
print("  TEST FIREBASE REALTIME DATABASE CONNECTION")
print("=" * 60)

# Test 1: Gửi dữ liệu qua API
print("\n📤 Test 1: Gửi dữ liệu qua Django API...")
test_data = {
    "temperature": 27.5,
    "humidity": 68.0,
    "gas_level": 150.0,
    "dust_density": 55.0,
    "aqi": 95,
    "air_quality_status": "MODERATE",
    "device_id": "TEST_SCRIPT"
}

try:
    response = requests.post(
        "http://localhost:8000/api/sensor-data/",
        json=test_data,
        timeout=5
    )
    if response.status_code == 201:
        print("✓ Gửi thành công qua API!")
        print(f"  Response: {response.json()}")
    else:
        print(f"✗ Lỗi: {response.status_code}")
except Exception as e:
    print(f"✗ Lỗi kết nối: {e}")

# Test 2: Đọc dữ liệu mới nhất
print("\n📥 Test 2: Đọc dữ liệu mới nhất...")
try:
    response = requests.get("http://localhost:8000/api/latest/", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print("✓ Đọc dữ liệu thành công!")
        print(f"  Temperature: {data.get('temperature')}°C")
        print(f"  Humidity: {data.get('humidity')}%")
        print(f"  AQI: {data.get('aqi')}")
        print(f"  Status: {data.get('air_quality_status')}")
    else:
        print(f"✗ Lỗi: {response.status_code}")
except Exception as e:
    print(f"✗ Lỗi: {e}")

# Test 3: Đọc dữ liệu lịch sử
print("\n📊 Test 3: Đọc dữ liệu lịch sử...")
try:
    response = requests.get("http://localhost:8000/api/historical/?hours=1", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Có {len(data)} bản ghi trong 1 giờ qua")
    else:
        print(f"✗ Lỗi: {response.status_code}")
except Exception as e:
    print(f"✗ Lỗi: {e}")

# Test 4: Kiểm tra Firebase Console
print("\n🌐 Kiểm tra dữ liệu trên Firebase Console:")
print("   https://console.firebase.google.com/project/aqi-iot-db/database/aqi-iot-db-default-rtdb/data")

print("\n" + "=" * 60)
print("✓ TEST HOÀN TẤT!")
print("=" * 60)
