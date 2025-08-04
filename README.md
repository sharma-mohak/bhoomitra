# 🌱 Bhoomitra – Smart Compost & Soil Health Monitoring System

**Bhoomitra** (Friend of the Soil) is a low-cost, solar-powered IoT device designed to automate composting and monitor soil health in community spaces. Built using ESP32 and MicroPython, it supports moisture control, temperature sensing, real-time MQTT data streaming, and community dashboards.

---

## 🔧 Features

- ESP32-based IoT controller
- Capacitive moisture sensor + DHT11 for temperature & humidity
- IR heating belt and water pump for automatic compost moisture control
- LCD screen and LED indicators for user feedback
- Solar + battery bank powered (off-grid ready)
- MQTT protocol support for data publishing
- Dashboard compatibility with Grafana and Power BI

---

## 🛠️ Components Used

- ESP32 Dev Board
- Capacitive Soil Moisture Sensor
- DHT11 Temperature/Humidity Sensor
- IR Heating Belt (5V/12V)
- Mini Water Pump (submersible or drip)
- Relay Module (for pump + IR control)
- 16x2 I2C LCD Display
- Solar Panel + Battery + Charge Controller
- Jumper Wires, Breadboard or PCB

---

## 🧠 How It Works

1. Sensors collect real-time compost conditions.
2. If moisture is too high, IR belt is activated to reduce it.
3. If too dry, water pump adds moisture.
4. Data is sent via MQTT to cloud dashboards.
5. LCD shows live status; LEDs blink for alerts.
6. Grafana/Power BI visualizes long-term compost health.

---

## 🚀 Getting Started

### 📁 Folder Structure
/firmware → MicroPython code for ESP32
/hardware → Circuit diagrams and wiring images
/docs → Research, use cases, project brief
/images → Screenshots and visuals

---

### ✅ To Deploy:

1. Flash MicroPython firmware to ESP32 using Thonny or uPyCraft
2. Update Wi-Fi and MQTT broker credentials in `main.py`
3. Connect hardware as per `hardware/wiring_diagram.png`
4. Power device via solar + battery or USB
5. View live data on MQTT broker or linked dashboard

---

## 📊 Visualization

Use Node-RED or Python MQTT client to pipe data into:
- **Grafana**: for real-time community dashboards
- **Power BI**: for detailed compost cycle reports

---

## 🌍 Community & Impact

Bhoomitra is designed for:
- Municipal wards and composting bins
- Schools and SHGs (Soil Circles model)
- Tier 2 & 3 cities with limited tech infrastructure

Supports SDGs: Climate Action, Sustainable Cities, Zero Hunger, Innovation.

---

## 📷 Screenshots & Diagrams

![Bhoomitra Setup](images/bhoomitra-setup.jpg)
![Wiring](hardware/wiring-diagram.png)
![Dashboard](images/grafana-dashboard.png)

---

## 📜 License

MIT License – Free to use, improve, and scale.

---

## 🤝 Contribute

Have ideas, want to join, or replicate Bhoomitra in your city?  
Open an issue or reach out!

---

## 🔗 Useful Links

- [Node-RED MQTT Setup](https://nodered.org/docs/)
- [Grafana MQTT Plugin](https://grafana.com/grafana/plugins/)
- [ESP32 + MQTT MicroPython Docs](https://docs.micropython.org/en/latest/esp32/)


