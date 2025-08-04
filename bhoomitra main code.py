import network
import time
import machine
from machine import Pin, ADC, I2C
import dht
import ssd1306
import ubinascii
import ujson
from umqtt.simple import MQTTClient

# ---- Wi-Fi Credentials ----
WIFI_SSID = 'your_SSID'
WIFI_PASSWORD = 'your_PASSWORD'

# ---- MQTT Configuration ----
MQTT_BROKER = '192.168.1.100'   # Your Mosquitto or HiveMQ broker IP
MQTT_PORT = 1883
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
TOPIC_PUB = b"bhoomitra/sensor"
TOPIC_ALERT = b"bhoomitra/alerts"
TOPIC_EVENT = b"bhoomitra/events"  # ✅ New Topic for Events

# ---- Thresholds ----
MOISTURE_DRY_THRESHOLD = 2000
MOISTURE_WET_THRESHOLD = 3000
BATTERY_LOW_VOLTAGE = 3.3
TEMP_HIGH = 50
TEMP_LOW = 15

# ---- GPIO Assignments ----
DHT_PIN = 14
MOISTURE_PIN = 34
BATTERY_ADC_PIN = 35
PUMP_PIN = 26
HEATER_PIN = 27
I2C_SCL = 22
I2C_SDA = 21
WATER_SENSOR_PIN = 33
BUZZER_PIN = 25

# ---- Set Up Components ----
dht_sensor = dht.DHT11(Pin(DHT_PIN))
moisture_adc = ADC(Pin(MOISTURE_PIN))
moisture_adc.atten(ADC.ATTN_11DB)
battery_adc = ADC(Pin(BATTERY_ADC_PIN))
battery_adc.atten(ADC.ATTN_11DB)

pump = Pin(PUMP_PIN, Pin.OUT)
heater = Pin(HEATER_PIN, Pin.OUT)
water_sensor = Pin(WATER_SENSOR_PIN, Pin.IN, Pin.PULL_UP)  # Float switch: 0 = empty, 1 = OK
buzzer = Pin(BUZZER_PIN, Pin.OUT)
i2c = I2C(scl=Pin(I2C_SCL), sda=Pin(I2C_SDA))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# ---- Compost Ready Tracking ----
compost_ready_counter = 0
COMPOST_READY_THRESHOLD = 5  # 5 consecutive healthy readings

# ---- Wi-Fi Connect ----
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    timeout = 0
    while not wlan.isconnected() and timeout < 10:
        time.sleep(1)
        timeout += 1
    return wlan.isconnected()

# ---- Get Battery Voltage ----
def get_battery_voltage():
    v = battery_adc.read()
    voltage = (v / 4095.0) * 3.3 * 2  # Adjust based on voltage divider
    return round(voltage, 2)

# ---- Publish Sensor Data (JSON format) ----
def publish_data(mqttc, temp, hum, moist, battery):
    payload = ujson.dumps({
        "temperature": temp,
        "humidity": hum,
        "moisture": moist,
        "battery": battery
    })
    mqttc.publish(TOPIC_PUB, payload)
    print("📤 Published sensor data:", payload)

# ---- Publish Alerts ----
def publish_alert(mqttc, message):
    mqttc.publish(TOPIC_ALERT, message)
    print("‼️ ALERT Published:", message)
    buzzer.value(1)
    time.sleep(1)
    buzzer.value(0)

# ✅ Publish Events to InfluxDB via MQTT
def publish_event(mqttc, event_name):
    payload = ujson.dumps({
        "event": event_name,
        "status": 1
    })
    mqttc.publish(TOPIC_EVENT, payload)
    print("📦 Event Published:", payload)

# ---- Update OLED Display ----
def update_display(temp, hum, moist, batt):
    oled.fill(0)
    oled.text("Bhoomitra", 25, 0)
    oled.text("T:{}C H:{}%".format(temp, hum), 0, 15)
    oled.text("Moist: {}".format(moist), 0, 30)
    oled.text("Batt: {:.2f}V".format(batt), 0, 45)
    oled.show()

# ---- Sensor Monitoring and Logic ----
def monitor(mqttc):
    global compost_ready_counter

    dht_sensor.measure()
    temp = dht_sensor.temperature()
    hum = dht_sensor.humidity()
    moist = moisture_adc.read()
    battery = get_battery_voltage()
    water_ok = water_sensor.value()  # 0 = empty

    print("🌡 Temp: {}C, 💧 Hum: {}%, 🪴 Moist: {}, 🔋 Battery: {}V, 🚰 Water_OK: {}".format(temp, hum, moist, battery, water_ok))

    # ---- Compost Control Logic ----
    if moist < MOISTURE_DRY_THRESHOLD:
        pump.value(1)
        heater.value(0)
    elif moist > MOISTURE_WET_THRESHOLD:
        pump.value(0)
        heater.value(1)
    else:
        pump.value(0)
        heater.value(0)

    # ---- Alerts ----
    if battery < BATTERY_LOW_VOLTAGE:
        publish_alert(mqttc, b'Battery low: %.2fV' % battery)

    if temp > TEMP_HIGH or temp < TEMP_LOW:
        publish_alert(mqttc, b'Abnormal temperature: %dC' % temp)

    if moist < MOISTURE_DRY_THRESHOLD:
        publish_alert(mqttc, b'Compost too dry!')

    if moist > MOISTURE_WET_THRESHOLD:
        publish_alert(mqttc, b'Compost too wet!')

    if water_ok == 0:
        publish_alert(mqttc, b'Water tank is empty!')

    # ---- Compost Readiness Detection ----
    if 2000 <= moist <= 3000 and 20 <= temp <= 45:
        compost_ready_counter += 1
        print("✅ Compost in optimal condition. Counter:", compost_ready_counter)
    else:
        compost_ready_counter = 0  # Reset if any condition fails

    if compost_ready_counter >= COMPOST_READY_THRESHOLD:
        publish_alert(mqttc, b'✅ Compost is ready for use!')
        publish_event(mqttc, "compost_ready")  # ✅ Publish to Grafana/Influx
        compost_ready_counter = 0  # Reset after firing

        # Show message on OLED
        oled.fill(0)
        oled.text("🌿 COMPOST READY!", 0, 25)
        oled.show()
        time.sleep(3)
        update_display(temp, hum, moist, battery)

    # ---- Update Display + Publish Sensor Data ----
    update_display(temp, hum, moist, battery)
    publish_data(mqttc, temp, hum, moist, battery)

# ---- Main Loop ----
def main():
    connected = connect_wifi()
    if not connected:
        print("Wi-Fi connection failed.")
        return

    mqttc = MQTTClient(client_id=CLIENT_ID.decode(),
                       server=MQTT_BROKER,
                       port=MQTT_PORT,
                       keepalive=60)

    try:
        mqttc.connect()
        print("✅ MQTT connected to broker:", MQTT_BROKER)

        while True:
            monitor(mqttc)  # Run main monitor
            time.sleep(60)

    except Exception as e:
        print("MQTT Error:", e)
    finally:
        mqttc.disconnect()

main()
