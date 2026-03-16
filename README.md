## 🌡️ ESP32 IoT Indoor Comfort, Occupancy & Air Quality Telemetry

A MicroPython-based IoT prototype for monitoring indoor environmental conditions, occupancy, and air quality using an ESP32 microcontroller.

The system collects sensor data from multiple environmental sensors and publishes telemetry to ThingsBoard Cloud via the MQTT protocol.

This project demonstrates how low-cost IoT hardware can be used to monitor building environments and stream real-time telemetry to a cloud platform for analytics, visualization, and smart building applications.

## 🧠 System Concept

Modern buildings increasingly rely on distributed IoT sensors to understand indoor conditions.

This prototype measures:

🌡️ Temperature
💧 Relative Humidity
🚶 Occupancy / Motion
🌬️ Indoor Air Quality indicator

The ESP32 processes sensor readings and transmits them to the cloud for dashboard visualization and analysis.

## 🏗️ System Architecture
<img width="2752" height="1536" alt="image" src="https://github.com/user-attachments/assets/a89f7e32-714e-45ce-a34c-01ad9deaaabf" />

1️⃣ Sensors measure environmental conditions
2️⃣ ESP32 processes readings locally
3️⃣ Data is converted to JSON telemetry
4️⃣ MQTT publishes the data to ThingsBoard
5️⃣ ThingsBoard visualizes and stores telemetry

## 🧰 Hardware Components
| Component           | Purpose                       |
| ------------------- | ----------------------------- |
| ESP32               | Microcontroller & IoT gateway |
| DHT22               | Temperature & humidity sensor |
| PIR Sensor          | Motion detection              |
| Gas Sensor (Analog) | Indoor air quality indicator  |

## 🔌 ESP32 Pin Configuration
| Sensor            | ESP32 Pin |
| ----------------- | --------- |
| DHT22 Data        | GPIO15    |
| PIR Motion        | GPIO14    |
| Gas Sensor Analog | GPIO34    |

## 💻 Software Stack
| Layer         | Technology        |
| ------------- | ----------------- |
| Firmware      | MicroPython       |
| Communication | MQTT              |
| IoT Platform  | ThingsBoard Cloud |
| Simulation    | Wokwi ESP32       |

## 🚀 Setup Instructions
1️⃣ Create Device in ThingsBoard

Open ThingsBoard Cloud

Create a new device

Copy the Device Access Token

2️⃣ Update Firmware

Insert the access token in the firmware:
ACCESS_TOKEN = "YOUR_DEVICE_ACCESS_TOKEN"

3️⃣ Run the Prototype

Upload the firmware to:

🔹 ESP32 hardware
or
🔹 Wokwi ESP32 simulator

The device will automatically:

✔ Connect to WiFi
✔ Connect to ThingsBoard via MQTT
✔ Publish telemetry every 10 seconds
✔ Send immediate updates when motion is detected

✨ Features

✔ Environmental monitoring
✔ Occupancy detection
✔ Indoor air quality estimation
✔ Cloud telemetry streaming
✔ MQTT-based communication
✔ Sensor fault tolerance
✔ Automatic reconnection handling
