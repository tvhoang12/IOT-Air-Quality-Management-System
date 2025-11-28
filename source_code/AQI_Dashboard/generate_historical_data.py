#!/usr/bin/env python3
"""
Script tạo dữ liệu lịch sử (bulk insert) vào Firebase để test biểu đồ
Tạo nhiều bản ghi cùng lúc với timestamp khác nhau
"""

import requests
import random
from datetime import datetime, timedelta
import time
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

API_URL = "http://localhost:8000/api/sensor-data/"
DEVICE_ID = "ESP32_TEST_FIREBASE_HISTORICAL"

def generate_historical_data(hours=24, interval_minutes=10):
    """
    Tạo dữ liệu lịch sử
    
    Args:
        hours: Số giờ dữ liệu muốn tạo (mặc định 24h)
        interval_minutes: Khoảng cách giữa các điểm dữ liệu (mặc định 10 phút)
    """
    print(f"Đang tạo dữ liệu lịch sử {hours} giờ với interval {interval_minutes} phút...")
    
    num_records = int((hours * 60) / interval_minutes)
    print(f"Tổng số bản ghi sẽ tạo: {num_records}")
    
    current_time = datetime.now()
    success_count = 0
    
    for i in range(num_records):
        # Tính thời gian cho mỗi điểm dữ liệu (từ quá khứ đến hiện tại)
        timestamp = current_time - timedelta(hours=hours) + timedelta(minutes=i*interval_minutes)
        
        # Tạo pattern biến đổi theo thời gian (mô phỏng thực tế)
        hour_of_day = timestamp.hour
        
        # Buổi sáng (6-12h): AQI tốt
        if 6 <= hour_of_day < 12:
            base_aqi = random.randint(30, 70)
        # Buổi trưa (12-18h): AQI trung bình
        elif 12 <= hour_of_day < 18:
            base_aqi = random.randint(70, 130)
        # Buổi tối (18-22h): AQI cao (giờ cao điểm)
        elif 18 <= hour_of_day < 22:
            base_aqi = random.randint(100, 180)
        # Ban đêm (22-6h): AQI giảm
        else:
            base_aqi = random.randint(40, 90)
        
        # Thêm nhiễu ngẫu nhiên
        aqi = max(10, min(500, base_aqi + random.randint(-15, 15)))
        
        # Tính toán các giá trị cảm biến dựa trên AQI
        gas_level = round((aqi / 300.0) * 400 + random.uniform(-20, 20), 1)
        dust_density = round((aqi / 300.0) * 300 + random.uniform(-15, 15), 1)
        temperature = round(22 + (hour_of_day / 24.0) * 10 + random.uniform(-2, 2), 1)
        humidity = round(60 + random.uniform(-15, 15), 1)
        
        # Xác định status
        if aqi <= 50:
            status = "GOOD"
        elif aqi <= 100:
            status = "MODERATE"
        elif aqi <= 150:
            status = "UNHEALTHY_SENSITIVE"
        elif aqi <= 200:
            status = "UNHEALTHY"
        elif aqi <= 300:
            status = "VERY_UNHEALTHY"
        else:
            status = "HAZARDOUS"
        
        data = {
            "temperature": max(15, min(40, temperature)),
            "humidity": max(30, min(95, humidity)),
            "gas_level": max(50, min(500, gas_level)),
            "dust_density": max(5, min(500, dust_density)),
            "aqi": aqi,
            "air_quality_status": status,
            "device_id": DEVICE_ID
        }
        
        # Gửi dữ liệu
        try:
            response = requests.post(API_URL, json=data, timeout=5)
            if response.status_code == 201:
                success_count += 1
                if (i + 1) % 10 == 0:
                    print(f"✓ Đã tạo {i + 1}/{num_records} bản ghi... (AQI: {aqi})")
            else:
                print(f"✗ Lỗi tại bản ghi {i + 1}: {response.status_code}")
        except Exception as e:
            print(f"✗ Lỗi: {e}")
        
        # Delay nhỏ để không quá tải server
        time.sleep(0.1)
    
    print(f"\n✓ Hoàn thành! Đã tạo {success_count}/{num_records} bản ghi thành công")
    print(f"Truy cập http://localhost:8000 để xem dashboard với dữ liệu đầy đủ!")

if __name__ == "__main__":
    print("=" * 70)
    print("   TẠO DỮ LIỆU LỊCH SỬ CHO DASHBOARD")
    print("=" * 70)
    print("\nChọn khoảng thời gian:")
    print("1. 6 giờ (interval 5 phút)")
    print("2. 12 giờ (interval 10 phút)")
    print("3. 24 giờ (interval 15 phút)")
    print("4. 48 giờ (interval 30 phút)")
    print("5. Tùy chỉnh")
    print()
    
    choice = input("Nhập lựa chọn (1-5) [mặc định: 3]: ").strip() or "3"
    
    if choice == "1":
        generate_historical_data(hours=6, interval_minutes=5)
    elif choice == "2":
        generate_historical_data(hours=12, interval_minutes=10)
    elif choice == "3":
        generate_historical_data(hours=24, interval_minutes=15)
    elif choice == "4":
        generate_historical_data(hours=48, interval_minutes=30)
    elif choice == "5":
        try:
            hours = int(input("Nhập số giờ: "))
            interval = int(input("Nhập interval (phút): "))
            generate_historical_data(hours=hours, interval_minutes=interval)
        except ValueError:
            print("Giá trị không hợp lệ!")
    else:
        generate_historical_data(hours=24, interval_minutes=15)
