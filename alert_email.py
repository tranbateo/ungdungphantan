import requests
import yagmail
from influxdb_client import InfluxDBClient
from datetime import datetime

# --- Cấu hình ---
OPENWEATHER_API_KEY = "5e77ff472346abf13ef5c5e458845c45"
CITY = "Hanoi"
EMAIL_SENDER = "22010012@st.phenikaa-uni.edu.vn"
EMAIL_PASSWORD = "Cap24052004@"
EMAIL_RECEIVER = "tailangtund@gmail.comcom"

# InfluxDB cấu hình
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "8h3t28Bpdb98wbr2yIqJ3BSkdGfLvTs4-atNDRfU7Mu-C_1v4t3MoRihvnxUP6VKeWakIFKXXZ35h3xNvHDJuA=="
INFLUXDB_ORG = "btl"
INFLUXDB_BUCKET = "udpt"

def get_latest_weather():
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    query_api = client.query_api()
    
    query = f'''
    from(bucket:"{INFLUXDB_BUCKET}")
      |> range(start: -10m)
      |> filter(fn: (r) => r._measurement == "weather")
      |> last()
    '''
    tables = query_api.query(query)

    weather = {}
    for table in tables:
        for record in table.records:
            weather[record.get_field()] = record.get_value()

    return weather

def check_and_send_alert(weather):
    temp = weather.get("temperature", 0)
    humidity = weather.get("humidity", 0)
    wind = weather.get("wind_speed", 0)

    alerts = []
    if temp > 35:
        alerts.append(f"Nhiệt độ cao: {temp}°C")
    if humidity > 90:
        alerts.append(f"Độ ẩm cao: {humidity}%")
    if wind > 10:
        alerts.append(f"Gió mạnh: {wind} m/s")

    if alerts:
        subject = "🌡️ CẢNH BÁO THỜI TIẾT"
        body = "\n".join(alerts)
        yag = yagmail.SMTP(EMAIL_SENDER, EMAIL_PASSWORD)
        yag.send(to=EMAIL_RECEIVER, subject=subject, contents=body)
        print("✅ Đã gửi email cảnh báo:")
        print(body)
    else:
        print("✅ Không có điều kiện cảnh báo nào.")

if __name__ == "__main__":
    try:
        data = get_latest_weather()
        check_and_send_alert(data)
    except Exception as e:
        print("❌ Lỗi:", e)
