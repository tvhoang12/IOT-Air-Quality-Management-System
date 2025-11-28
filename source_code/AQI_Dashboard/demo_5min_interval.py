#!/usr/bin/env python3
"""
Demo script: Gửi dữ liệu mỗi 5 giây, lưu database mỗi 5 phút
"""

import requests
import time
from datetime import datetime
import random

API_URL = "http://localhost:8000/api/sensor-data/"
DEVICE_ID = "ESP32_DEMO_5MIN"

def generate_data():
    """Tạo dữ liệu mẫu"""
    temp = round(random.uniform(22.0, 32.0), 1)
    humidity = round(random.uniform(50.0, 80.0), 1)
    gas = round(random.uniform(100.0, 300.0), 1)
    dust = round(random.uniform(30.0, 150.0), 1)
    aqi = random.randint(50, 180)
    
    if aqi <= 50:
        status = "GOOD"
    elif aqi <= 100:
        status = "MODERATE"
    else:
        status = "UNHEALTHY"
    
    return {
        "temperature": temp,
        "humidity": humidity,
        "gas_level": gas,
        "dust_density": dust,
        "aqi": aqi,
        "air_quality_status": status,
        "device_id": DEVICE_ID
    }

print("=" * 70)
print("  DEMO: CẬP NHẬT MỖI 5 GIÂY - LƯU DATABASE MỖI 5 PHÚT")
print("=" * 70)
print(f"⏰ Gửi dữ liệu: mỗi 5 giây")
print(f"💾 Lưu database: mỗi 5 phút (60 lần gửi = 1 lần lưu)")
print(f"🔄 Dashboard cập nhật: mỗi 5 giây (real-time)")
print(f"📊 Biểu đồ hiển thị: chỉ dữ liệu trong database (mỗi 5 phút)")
print("=" * 70)
print("\nBắt đầu gửi dữ liệu... (Ctrl+C để dừng)\n")

count = 0
db_save_count = 0

try:
    while True:
        count += 1
        data = generate_data()
        
        try:
            response = requests.post(API_URL, json=data, timeout=5)
            
            if response.status_code == 201:
                result = response.json()
                saved = result.get('saved_to_database', False)
                
                if saved:
                    db_save_count += 1
                    print(f"✓ [{datetime.now().strftime('%H:%M:%S')}] #{count:3d} | AQI: {data['aqi']:3d} | 💾 SAVED TO DATABASE (#{db_save_count})")
                else:
                    print(f"  [{datetime.now().strftime('%H:%M:%S')}] #{count:3d} | AQI: {data['aqi']:3d} | ⚡ Cached (Dashboard real-time)")
            else:
                print(f"✗ Lỗi: {response.status_code}")
        
        except Exception as e:
            print(f"✗ Lỗi kết nối: {e}")
        
        time.sleep(5)  # Gửi mỗi 5 giây

except KeyboardInterrupt:
    print(f"\n\n{'=' * 70}")
    print(f"  📊 THỐNG KÊ")
    print(f"{'=' * 70}")
    print(f"  Tổng số lần gửi: {count}")
    print(f"  Số lần lưu database: {db_save_count}")
    print(f"  Tỷ lệ: {count}/{db_save_count} = {count/db_save_count if db_save_count > 0 else 0:.0f} lần gửi / 1 lần lưu")
    print(f"{'=' * 70}")
    print("\n✓ Đã dừng script!")
