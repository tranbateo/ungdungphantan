from flask import Flask, render_template, jsonify
from influxdb_client import InfluxDBClient
from datetime import datetime, timedelta, timezone

import pytz  

app = Flask(__name__)

INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "8h3t28Bpdb98wbr2yIqJ3BSkdGfLvTs4-atNDRfU7Mu-C_1v4t3MoRihvnxUP6VKeWakIFKXXZ35h3xNvHDJuA=="
INFLUXDB_ORG = "btl"
INFLUXDB_BUCKET = "udpt"

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/weather-data")
def get_weather_data():
    query_api = client.query_api()
    query = f'''
    from(bucket:"{INFLUXDB_BUCKET}")
      |> range(start: -1h)
      |> filter(fn: (r) => r._measurement == "weather")
      |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity" )
    '''
    tables = query_api.query(query)
    
    data = {"temperature": [], "humidity": [], "timestamps": []}

    vietnam_tz = pytz.timezone("Asia/Ho_Chi_Minh") 

    for table in tables:
        for record in table.records:
            utc_time = record.get_time()
            local_time = utc_time.astimezone(vietnam_tz)  
            ts = local_time.strftime("%H:%M")

            field = record.get_field()
            value = record.get_value()

            if ts not in data["timestamps"]:
                data["timestamps"].append(ts)

            data[field].append(value)

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
