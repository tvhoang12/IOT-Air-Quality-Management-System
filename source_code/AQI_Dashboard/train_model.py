import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

# 1. Cấu hình
NUM_SAMPLES = 15000
MODEL_PATH = 'sensor_calibration_model.pkl'

print(f"Generating {NUM_SAMPLES} synthetic data samples...")

# 2. Sinh dữ liệu giả lập (Synthetic Data Generation)
np.random.seed(42)

# Các biến đầu vào ngẫu nhiên
# Nhiệt độ: 10 - 45 độ C
temperature = np.random.uniform(10, 45, NUM_SAMPLES)
# Độ ẩm: 20 - 95%
humidity = np.random.uniform(20, 95, NUM_SAMPLES)

# Giá trị thực (Ground Truth) - Giả sử đây là giá trị chuẩn từ trạm quan trắc
# Bụi PM2.5 thực tế: 0 - 500 µg/m3
true_pm25 = np.random.exponential(scale=30, size=NUM_SAMPLES) 
true_pm25 = np.clip(true_pm25, 0, 500) # Giới hạn max

# Gas thực tế: 10 - 1000 ppm
true_gas = np.random.exponential(scale=100, size=NUM_SAMPLES)
true_gas = np.clip(true_gas, 10, 1000)

# 3. Mô phỏng Nhiễu (Noise Simulation)
# Giả lập đặc tính cảm biến giá rẻ: Sai số tăng khi độ ẩm cao

# --- Bụi (GP2Y10) ---
# Độ ẩm > 70% gây sai số dương (do hơi nước ngưng tụ bị nhận nhầm là bụi)
dust_noise_factor = np.where(humidity > 70, (humidity - 70) * 1.5, 0) 
# Cộng thêm nhiễu ngẫu nhiên
random_noise_dust = np.random.normal(0, 5, NUM_SAMPLES)
# Giá trị đo được (Raw Data) = Giá trị thực + Nhiễu độ ẩm + Nhiễu ngẫu nhiên
raw_dust = true_pm25 + dust_noise_factor + random_noise_dust
raw_dust = np.clip(raw_dust, 0, None) # Không âm

# --- Gas (MQ-135) ---
# Nhạy cảm với nhiệt độ và độ ẩm
# Giả sử: Nhiệt độ cao làm tăng điện trở -> đọc thấp hơn thực tế
# Độ ẩm cao làm giảm điện trở -> đọc cao hơn thực tế
gas_temp_effect = (temperature - 25) * 2 # Lệch so với chuẩn 25 độ
gas_humid_effect = (humidity - 50) * 1.5 # Lệch so với chuẩn 50%
random_noise_gas = np.random.normal(0, 10, NUM_SAMPLES)

raw_gas = true_gas - gas_temp_effect + gas_humid_effect + random_noise_gas
raw_gas = np.clip(raw_gas, 10, None)

# 4. Đóng gói dữ liệu
# Input cho model: Raw Dust, Raw Gas, Temp, Humidity
X = pd.DataFrame({
    'raw_dust': raw_dust,
    'raw_gas': raw_gas,
    'temperature': temperature,
    'humidity': humidity
})

# Output mong muốn: True PM2.5, True Gas
y = pd.DataFrame({
    'corrected_dust': true_pm25,
    'corrected_gas': true_gas
})

# 5. Huấn luyện Model
print("Training Random Forest Regressor...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Random Forest với 100 cây
model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# 6. Đánh giá
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\nModel Performance:")
print(f"Mean Squared Error: {mse:.2f}")
print(f"R2 Score: {r2:.4f}")

# 7. Lưu Model
joblib.dump(model, MODEL_PATH)
print(f"\nModel saved to {MODEL_PATH}")

# 8. Test thử một trường hợp cụ thể
print("\n--- Test Case: High Humidity (Foggy) ---")
test_input = pd.DataFrame({
    'raw_dust': [150.0],    # Đọc được 150 (cao do sương mù)
    'raw_gas': [200.0],
    'temperature': [25.0],
    'humidity': [90.0]      # Độ ẩm rất cao
})
predicted = model.predict(test_input)
print(f"Input Raw Dust: {test_input['raw_dust'][0]}")
print(f"Input Humidity: {test_input['humidity'][0]}%")
print(f"AI Corrected Dust: {predicted[0][0]:.2f} (Should be lower than 150)")
