#!/usr/bin/env python3
"""
Script tạo dữ liệu ngẫu nhiên và gửi đến Django API để test dashboard
Chạy script này để mô phỏng dữ liệu từ cảm biến
"""

import requests
import random
import time
import json
from datetime import datetime

# Cấu hình
API_URL = "http://localhost:8000/api/sensor-data/"
DEVICE_ID = "ESP32_TEST_001"
SEND_INTERVAL = 5  # Gửi dữ liệu mỗi 5 giây

def generate_sensor_data():
    """
    Tạo dữ liệu cảm biến ngẫu nhiên nhưng có logic
    """
    # Tạo nhiệt độ từ 20-35°C
    temperature = round(random.uniform(20.0, 35.0), 1)
    
    # Tạo độ ẩm từ 40-90%
    humidity = round(random.uniform(40.0, 90.0), 1)
    
    # Tạo mức gas từ 50-400 ppm
    gas_level = round(random.uniform(50.0, 400.0), 1)
    
    # Tạo mật độ bụi từ 10-300 µg/m³
    dust_density = round(random.uniform(10.0, 300.0), 1)
    
    # Tính AQI dựa trên gas và bụi
    gas_aqi = min(int((gas_level / 400.0) * 300), 500)
    dust_aqi = min(int((dust_density / 300.0) * 300), 500)
    aqi = max(gas_aqi, dust_aqi)
    
    # Xác định trạng thái chất lượng không khí
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
    
    return {
        "temperature": temperature,
        "humidity": humidity,
        "gas_level": gas_level,
        "dust_density": dust_density,
        "aqi": aqi,
        "air_quality_status": status,
        "device_id": DEVICE_ID
    }

def send_data(data):
    """
    Gửi dữ liệu đến API
    """
    try:
        response = requests.post(
            API_URL,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 201:
            print(f"✓ [{datetime.now().strftime('%H:%M:%S')}] Gửi thành công - AQI: {data['aqi']} ({data['air_quality_status']})")
            return True
        else:
            print(f"✗ Lỗi: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Không thể kết nối đến server. Đảm bảo Django server đang chạy!")
        return False
    except Exception as e:
        print(f"✗ Lỗi: {e}")
        return False

def generate_scenario_data(scenario="normal"):
    """
    Tạo dữ liệu theo kịch bản cụ thể
    """
    if scenario == "good":
        # Chất lượng không khí tốt
        temperature = round(random.uniform(22.0, 28.0), 1)
        humidity = round(random.uniform(50.0, 70.0), 1)
        gas_level = round(random.uniform(50.0, 100.0), 1)
        dust_density = round(random.uniform(10.0, 35.0), 1)
        aqi = random.randint(20, 50)
        status = "GOOD"
        
    elif scenario == "moderate":
        # Chất lượng không khí trung bình
        temperature = round(random.uniform(25.0, 32.0), 1)
        humidity = round(random.uniform(55.0, 75.0), 1)
        gas_level = round(random.uniform(100.0, 200.0), 1)
        dust_density = round(random.uniform(35.0, 80.0), 1)
        aqi = random.randint(51, 100)
        status = "MODERATE"
        
    elif scenario == "bad":
        # Chất lượng không khí xấu
        temperature = round(random.uniform(28.0, 35.0), 1)
        humidity = round(random.uniform(60.0, 85.0), 1)
        gas_level = round(random.uniform(200.0, 350.0), 1)
        dust_density = round(random.uniform(100.0, 250.0), 1)
        aqi = random.randint(151, 250)
        status = "UNHEALTHY"
        
    else:  # normal - ngẫu nhiên
        return generate_sensor_data()
    
    return {
        "temperature": temperature,
        "humidity": humidity,
        "gas_level": gas_level,
        "dust_density": dust_density,
        "aqi": aqi,
        "air_quality_status": status,
        "device_id": DEVICE_ID
    }

def main():
    """
    Chương trình chính
    """
    print("=" * 60)
    print("   CÔNG CỤ TẠO DỮ LIỆU NGẪU NHIÊN CHO DASHBOARD AQI")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print(f"Device ID: {DEVICE_ID}")
    print(f"Interval: {SEND_INTERVAL} giây")
    print("=" * 60)
    print("\nChọn chế độ:")
    print("1. Ngẫu nhiên (random)")
    print("2. Chất lượng tốt (good)")
    print("3. Chất lượng trung bình (moderate)")
    print("4. Chất lượng xấu (bad)")
    print("5. Tự động chuyển đổi kịch bản (auto)")
    print()
    
    try:
        choice = input("Nhập lựa chọn (1-5) [mặc định: 1]: ").strip() or "1"
        
        mode_map = {
            "1": "normal",
            "2": "good",
            "3": "moderate",
            "4": "bad",
            "5": "auto"
        }
        
        mode = mode_map.get(choice, "normal")
        
        print(f"\n🚀 Bắt đầu gửi dữ liệu ở chế độ: {mode.upper()}")
        print("Nhấn Ctrl+C để dừng\n")
        
        count = 0
        scenario_index = 0
        scenarios = ["good", "moderate", "bad"]
        
        while True:
            count += 1
            
            if mode == "auto":
                # Chuyển đổi kịch bản sau mỗi 5 lần gửi
                current_scenario = scenarios[scenario_index % len(scenarios)]
                if count % 5 == 0:
                    scenario_index += 1
                    print(f"\n➜ Chuyển sang kịch bản: {scenarios[scenario_index % len(scenarios)].upper()}\n")
                data = generate_scenario_data(current_scenario)
            else:
                data = generate_scenario_data(mode)
            
            # Hiển thị dữ liệu
            print(f"#{count} | Temp: {data['temperature']}°C | Hum: {data['humidity']}% | "
                  f"Gas: {data['gas_level']} ppm | Dust: {data['dust_density']} µg/m³")
            
            # Gửi dữ liệu
            send_data(data)
            
            # Chờ trước khi gửi tiếp
            time.sleep(SEND_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n✓ Đã dừng chương trình. Tổng số lần gửi: {}".format(count))
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Lỗi: {e}")

if __name__ == "__main__":
    main()
