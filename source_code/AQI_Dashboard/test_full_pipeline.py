import requests
import json
import random
import time

# Cấu hình
SERVER_URL = "http://127.0.0.1:8000/devices/api/webhook/" # Endpoint chính thức cho thiết bị
# SERVER_URL = "http://127.0.0.1:8000/monitor/api/sensor-data/" # Endpoint cũ (nếu muốn test cái này)

# API Key giả lập (Lấy từ database hoặc tạo mới nếu cần)
# Lưu ý: Bạn cần thay API Key này bằng API Key thật của thiết bị bạn đã tạo trên web
API_KEY = "sAwDq4ZWCq1nnXxc9QDPczVp2pAM2qvrpIbDRnEE2x8" 

def send_data(temp, humid, raw_gas, raw_dust, description):
    payload = {
        "temperature": temp,
        "humidity": humid,
        "gas_level": raw_gas,
        "dust_density": raw_dust,
        # Không gửi AQI, để server tự tính
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    print(f"\n--- {description} ---")
    print(f"Sending: Temp={temp}, Humid={humid}, RawDust={raw_dust}, RawGas={raw_gas}")
    
    try:
        response = requests.post(SERVER_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            print("✅ Success!")
            print("Response:", response.json())
            # Nếu server trả về data đã xử lý, ta có thể so sánh ở đây
        else:
            print(f"❌ Failed (Status {response.status_code})")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

# Kịch bản test

# 1. Trời đẹp (Nhiệt độ chuẩn, độ ẩm thấp -> Ít nhiễu)
# AI sẽ giữ nguyên hoặc chỉnh sửa rất ít
send_data(25.0, 40.0, 50.0, 20.0, "Test 1: Good Weather (Low Noise)")

# 2. Trời nồm ẩm (Độ ẩm rất cao -> Gây nhiễu dương cho cảm biến bụi)
# Cảm biến đọc 150 (cao), nhưng thực tế do hơi nước. 
# AI sẽ nhận ra độ ẩm 95% và "trừ" bớt đi -> AQI thấp hơn.
send_data(25.0, 95.0, 50.0, 150.0, "Test 2: High Humidity (Foggy Noise)")

# 3. Ô nhiễm thật (Độ ẩm thấp nhưng bụi cao)
# AI sẽ giữ nguyên mức cao này vì không phải do độ ẩm.
send_data(25.0, 40.0, 50.0, 150.0, "Test 3: Real Pollution (Low Humidity)")
