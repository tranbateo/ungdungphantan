import time
import requests
from influxdb_client import InfluxDBClient, Point, WritePrecision
from datetime import datetime

# --- Thông tin cấu hình ---
API_KEY = "5e77ff472346abf13ef5c5e458845c45"
CITY = "Hanoi"
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "8h3t28Bpdb98wbr2yIqJ3BSkdGfLvTs4-atNDRfU7Mu-C_1v4t3MoRihvnxUP6VKeWakIFKXXZ35h3xNvHDJuA=="
ORG = "btl"
BUCKET = "udpt"

def fetch_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Lỗi API ({response.status_code}): {response.text}")
    
    data = response.json()
    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    pressure = data["main"]["pressure"]
    wind_speed = data["wind"]["speed"]
    return temp, humidity, pressure, wind_speed

def write_to_influx(temp, humidity, pressure, wind_speed):
    with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=ORG) as client:
        write_api = client.write_api()
        point = (
            Point("weather")
            .field("temperature", temp)
            .field("humidity", humidity)
            .field("pressure", pressure)
            .field("wind_speed", wind_speed)
            .time(time.time_ns(), WritePrecision.NS)
        )
        write_api.write(bucket=BUCKET, record=point)
        print(f"✅ {datetime.now()} - Ghi: {temp}°C | {humidity}% | {pressure} hPa | {wind_speed} m/s")

if __name__ == "__main__":
    while True:
        try:
            temp, humidity, pressure, wind_speed = fetch_weather()
            write_to_influx(temp, humidity, pressure, wind_speed)
        except Exception as e:
            print(f"❌ {datetime.now()} - Lỗi: {e}")
        time.sleep(300)  # Lặp lại mỗi 5 phút
