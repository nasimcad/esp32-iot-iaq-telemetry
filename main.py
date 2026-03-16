"""
MicroPython IoT "Indoor Comfort + Occupancy + IAQ" Telemetry
for Wokwi ESP32 -> ThingsBoard Cloud (MQTT)

What it does:
- Reads 3 sensors:
  - DHT22 (temperature, humidity)
  - PIR (motion -> occupied)
  - Gas sensor (analog -> iaq_raw + scaled iaq_index)
- Publishes JSON telemetry to ThingsBoard Cloud over MQTT

ThingsBoard settings you need:
- Create a device in ThingsBoard Cloud
- Copy the device Access Token
- Paste it into ACCESS_TOKEN below
"""

import network
import time
from machine import Pin, unique_id, ADC
import dht
import ujson
import ubinascii
from umqtt.simple import MQTTClient

# -----------------------------
# WiFi (Wokwi)
# -----------------------------
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""

# -----------------------------
# ThingsBoard Cloud MQTT
# -----------------------------
MQTT_CLIENT_ID = b"sense01-" + ubinascii.hexlify(unique_id())

# IMPORTANT: Replace with your real token
ACCESS_TOKEN = "YOUR_DEVICE_ACCESS_TOKEN"

MQTT_BROKER   = "thingsboard.cloud"
MQTT_PORT     = 1883  # informational; umqtt.simple uses default for broker string
MQTT_TOPIC_TELE = "v1/devices/me/telemetry"

# ThingsBoard uses Access Token as MQTT username
MQTT_USER     = ACCESS_TOKEN
MQTT_PASSWORD = ""

# -----------------------------
# Sensors (match your diagram.json)
# -----------------------------
# DHT22 data pin -> GPIO15
dht_sensor = dht.DHT22(Pin(15))

# PIR OUT -> GPIO14
pir = Pin(14, Pin.IN, Pin.PULL_DOWN)

# Gas sensor analog output -> GPIO34 (ADC)
gas_adc = ADC(Pin(34))
gas_adc.atten(ADC.ATTN_11DB)      # 0..~3.3V range
gas_adc.width(ADC.WIDTH_12BIT)    # 0..4095

# -----------------------------
# Connectivity helpers
# -----------------------------
def wifi_connect():
  """
  Establish a WiFi connection to a specified network.
  
  This function activates the WiFi station interface and connects to a 
  network using predefined SSID and password credentials (WIFI_SSID and 
  WIFI_PASS). It polls the connection status with visual feedback via 
  console output, displaying dots while waiting for the connection to 
  establish. Once successfully connected, it prints a confirmation message.
  
  Returns:
    network.WLAN: An active WLAN station interface object that is 
            connected to the specified WiFi network.
  
  Note:
    - Requires 'network' module (MicroPython)
    - Requires 'time' module for sleep functionality
    - WIFI_SSID and WIFI_PASS must be defined globally
    - Blocks execution until connection is established
  """
  print("Connecting to WiFi", end="")
  sta_if = network.WLAN(network.STA_IF)
  sta_if.active(True)
  sta_if.connect(WIFI_SSID, WIFI_PASS)
  while not sta_if.isconnected():
    print(".", end="")
    time.sleep(0.1)
  print(" Connected!")
  return sta_if

def mqtt_connect():
  print("Connecting to ThingsBoard... ", end="")
  c = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD, keepalive=60)
  c.connect()
  print("Connected!")
  return c

# -----------------------------
# Start connections
# -----------------------------
sta_if = wifi_connect()
client = mqtt_connect()

# -----------------------------
# Publish logic
# -----------------------------
PUBLISH_INTERVAL_MS = 10000  # publish every 10 seconds
last_pub = time.ticks_ms()

prev_motion = pir.value()

while True:
  # Ensure WiFi stays connected (rarely needed in Wokwi, but good practice)
  if not sta_if.isconnected():
    sta_if = wifi_connect()

  try:
    # Read DHT22
    dht_sensor.measure()
    temp = dht_sensor.temperature()
    hum  = dht_sensor.humidity()
  except Exception as e:
    print("DHT read error:", e)
    time.sleep(1)
    continue

  # Read PIR
  motion = pir.value()
  occupied = 1 if motion else 0

  # Read Gas sensor (ADC)
  iaq_raw = gas_adc.read()                 # 0..4095
  iaq_index = int(iaq_raw * 100 / 4095)    # 0..100 (simple demo scaling)

  # Build telemetry payload (ThingsBoard accepts plain JSON key-values)
  payload = ujson.dumps({
    "dev": "sense01",
    "t_c": temp,
    "rh_pct": hum,
    "motion": motion,
    "occupied": occupied,
    "iaq_raw": iaq_raw,
    "iaq_index": iaq_index
  })

  now = time.ticks_ms()
  periodic_due = time.ticks_diff(now, last_pub) >= PUBLISH_INTERVAL_MS
  motion_changed = (motion != prev_motion)

  # Publish periodically OR immediately if motion changes
  if periodic_due or motion_changed:
    try:
      client.publish(MQTT_TOPIC_TELE, payload)
      print("Published:", payload)
      last_pub = now
      prev_motion = motion
    except Exception as e:
      print("MQTT publish error:", e)
      # Attempt reconnect
      try:
        client = mqtt_connect()
      except Exception as e2:
        print("Reconnect failed:", e2)

  time.sleep(1)