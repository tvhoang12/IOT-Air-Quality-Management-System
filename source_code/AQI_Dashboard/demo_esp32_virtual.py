"""
Script mô phỏng thiết bị ESP32 gửi dữ liệu sensor đến server
- Gửi dữ liệu mỗi 1 PHÚT (60 giây) để cập nhật real-time
- Server tự động lưu vào database mỗi lần nhận được dữ liệu
"""

import requests
import random
import time
from datetime import datetime
import json

# ============ CẤU HÌNH ============
SERVER_URL = "http://localhost:8000/devices/api/webhook/"
API_KEY = "tjmQ51M1dDiUsisrLD3a7reze30z3UI0My20dmyyDxI"  # API Key từ thiết bị ESP32
SECRET_KEY = "4cac78ad23e6e5bd41a4eb86f58c0e820a9c03eb5255b2a2bfec19baa7ec0077"  # Secret Key (không cần dùng cho webhook)

# Thời gian gửi dữ liệu (1 phút = 60 giây)
SEND_INTERVAL = 60  # Gửi mỗi 1 phút

# Giới hạn giá trị sensor (để dữ liệu thực tế hơn)
TEMP_RANGE = (20, 35)      # °C
HUMIDITY_RANGE = (40, 80)   # %
GAS_RANGE = (50, 200)       # ppm
DUST_RANGE = (20, 150)      # µg/m³

# Biến lưu trạng thái dữ liệu trước đó (để tạo xu hướng thay đổi tự nhiên)
previous_data = {
    "temperature": 25.0,
    "humidity": 60.0,
    "gas_level": 100.0,
    "dust_density": 50.0
}


def generate_sensor_data():
    """
    Tạo dữ liệu sensor với xu hướng thay đổi tự nhiên
    (không nhảy vọt, thay đổi từ từ theo thời gian)
    """
    global previous_data
    
    # Thay đổi nhẹ từ giá trị trước đó (±5%)
    temp_change = random.uniform(-2, 2)
    hum_change = random.uniform(-3, 3)
    gas_change = random.uniform(-10, 10)
    dust_change = random.uniform(-8, 8)
    
    # Tính giá trị mới
    temperature = previous_data["temperature"] + temp_change
    humidity = previous_data["humidity"] + hum_change
    gas_level = previous_data["gas_level"] + gas_change
    dust_density = previous_data["dust_density"] + dust_change
    
    # Giới hạn trong phạm vi hợp lý
    temperature = max(TEMP_RANGE[0], min(TEMP_RANGE[1], temperature))
    humidity = max(HUMIDITY_RANGE[0], min(HUMIDITY_RANGE[1], humidity))
    gas_level = max(GAS_RANGE[0], min(GAS_RANGE[1], gas_level))
    dust_density = max(DUST_RANGE[0], min(DUST_RANGE[1], dust_density))
    
    # Làm tròn
    temperature = round(temperature, 1)
    humidity = round(humidity, 1)
    gas_level = round(gas_level, 1)
    dust_density = round(dust_density, 1)
    
    # Lưu lại cho lần sau
    previous_data = {
        "temperature": temperature,
        "humidity": humidity,
        "gas_level": gas_level,
        "dust_density": dust_density
    }
    
    return {
        "temperature": temperature,
        "humidity": humidity,
        "gas_level": gas_level,
        "dust_density": dust_density,
        "ip_address": "192.168.1.100"  # IP ảo
    }


def send_data_to_server(data):
    """Gửi dữ liệu đến server qua HTTP POST"""
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    try:
        response = requests.post(
            SERVER_URL,
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Data sent successfully!")
            print(f"Temperature: {data['temperature']}°C")
            print(f"Humidity: {data['humidity']}%")
            print(f"Gas Level: {data['gas_level']} ppm")
            print(f"Dust Density: {data['dust_density']} µg/m³")
            print(f"Response: {result}")
            print("-" * 50)
            return True
        else:
            print(f"Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"Connection Error: Cannot connect to {SERVER_URL}")
        print("  Make sure Django server is running!")
        return False
    except requests.exceptions.Timeout:
        print("✗ Timeout: Server took too long to respond")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Main loop - gửi dữ liệu định kỳ"""
    print("=" * 60)
    print("ESP32 Virtual Device - 1 Minute Interval")
    print("=" * 60)
    print(f"Server: {SERVER_URL}")
    print(f"API Key: {API_KEY[:20]}...")
    print(f"Send Interval: {SEND_INTERVAL} seconds (1 minute)")
    print(f"Database: Server saves every data received")
    print("=" * 60)
    print("\nPress Ctrl+C to stop\n")
    
    # Kiểm tra API key
    if API_KEY == "YOUR_API_KEY":
        print("⚠️  WARNING: Please update API_KEY in the script!")
        print("   Get API key from: http://localhost:8000/devices/add/")
        return
    
    try:
        count = 0
        success_count = 0
        
        while True:
            count += 1
            print(f"\n[Sending #{count}]")
            
            # Tạo và gửi dữ liệu
            sensor_data = generate_sensor_data()
            if send_data_to_server(sensor_data):
                success_count += 1
            
            # Hiển thị countdown
            print(f"\nWaiting {SEND_INTERVAL} seconds until next send...")
            next_time = datetime.fromtimestamp(time.time() + SEND_INTERVAL)
            print(f"   Next send at: {next_time.strftime('%H:%M:%S')}")
            
            # Đợi trước khi gửi lần tiếp theo
            time.sleep(SEND_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\nStopped by user")
        print(f"Total data sent: {count}")
        print(f"Successful: {success_count}")
        print(f"Failed: {count - success_count}")
        if count > 0:
            print(f"Success rate: {(success_count/count)*100:.1f}%")


if __name__ == "__main__":
    main()
