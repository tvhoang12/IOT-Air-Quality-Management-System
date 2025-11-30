#include "DHT.h"

#define DHTPIN 2     // Chân DATA nối vào Pin 2
#define DHTTYPE DHT11   // Loại cảm biến DHT11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  Serial.println(F("DHT11 test!"));

  dht.begin();
}

void loop() {
  // Đợi 2 giây giữa các lần đo
  delay(2000);

  // Đọc độ ẩm
  float h = dht.readHumidity();
  // Đọc nhiệt độ C
  float t = dht.readTemperature();

  // Kiểm tra lỗi
  if (isnan(h) || isnan(t)) {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }

  Serial.print(F("Humidity: "));
  Serial.print(h);
  Serial.print(F("%  Temperature: "));
  Serial.print(t);
  Serial.println(F("°C "));
}
