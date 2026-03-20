import json
import math
import random
import time
from datetime import datetime
import paho.mqtt.client as mqtt

# ==============================
# ThingsBoard settings
# ==============================
TB_HOST = "thingsboard.cloud"
TB_PORT = 1883
ACCESS_TOKEN = "6mP5x6kL7VIOQPSLLGxk"  # replace with your device access token
TOPIC = "v1/devices/me/telemetry"

# ==============================
# Model settings
# ==============================
DEVICE_NAME = "sense01"
PUBLISH_EVERY_SEC = 10
OCCUPANCY_HOLD_SEC = 10 * 60   # 10 minutes

# Initial states
last_motion_ts = 0
iaq_raw = 900.0
temperature = 23.0
humidity = 48.0

def hour_profile(hour_float: float) -> float:
    """
    Returns occupancy tendency 0..1 depending on time of day.
    """
    if 0 <= hour_float < 6:
        return 0.03
    elif 6 <= hour_float < 8:
        return 0.15
    elif 8 <= hour_float < 12:
        return 0.70
    elif 12 <= hour_float < 13:
        return 0.35
    elif 13 <= hour_float < 17:
        return 0.75
    elif 17 <= hour_float < 21:
        return 0.25
    else:
        return 0.08

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def simulate_step():
    global last_motion_ts, iaq_raw, temperature, humidity

    now = datetime.now()
    hour_float = now.hour + now.minute / 60.0 + now.second / 3600.0
    occ_bias = hour_profile(hour_float)

    # ---- Motion event generation ----
    # Bursty motion during occupied hours
    motion = 1 if random.random() < (0.08 + 0.25 * occ_bias) else 0

    if motion == 1:
        last_motion_ts = time.time()

    # Hold occupancy for 10 min after last motion
    occupied = 1 if (time.time() - last_motion_ts) < OCCUPANCY_HOLD_SEC else 0

    # ---- Temperature model ----
    # Daily sinusoidal variation + small noise + occupancy gain
    daily_temp = 22.5 + 1.8 * math.sin((hour_float - 6) / 24 * 2 * math.pi)
    occ_temp_gain = 0.6 if occupied else 0.0
    target_temp = daily_temp + occ_temp_gain

    # smooth response
    temperature += 0.15 * (target_temp - temperature) + random.uniform(-0.05, 0.05)
    temperature = clamp(temperature, 20.0, 28.5)

    # ---- Humidity model ----
    # Slight inverse relationship to temp + noise
    target_humidity = 50.0 - 0.8 * (temperature - 23.0) + random.uniform(-0.4, 0.4)
    humidity += 0.12 * (target_humidity - humidity)
    humidity = clamp(humidity, 35.0, 65.0)

    # ---- IAQ model ----
    # rises when occupied, decays when unoccupied
    if occupied:
        iaq_raw += random.uniform(20, 55)
    else:
        iaq_raw -= random.uniform(15, 35)

    # occasional spikes for cooking/poor ventilation event
    if random.random() < 0.01:
        iaq_raw += random.uniform(250, 700)

    # smooth and clamp
    iaq_raw = clamp(iaq_raw, 300, 3200)
    iaq_index = int(iaq_raw * 100 / 4095)

    payload = {
        "dev": DEVICE_NAME,
        "t_c": round(temperature, 2),
        "rh_pct": round(humidity, 2),
        "motion": motion,
        "occupied": occupied,
        "iaq_raw": int(iaq_raw),
        "iaq_index": iaq_index
    }

    return payload

def main():
    client = mqtt.Client()
    client.username_pw_set(ACCESS_TOKEN)
    client.connect(TB_HOST, TB_PORT, 60)
    client.loop_start()

    print("Sending realistic synthetic telemetry to ThingsBoard...")

    try:
        while True:
            payload = simulate_step()
            client.publish(TOPIC, json.dumps(payload))
            print(datetime.now().strftime("%H:%M:%S"), payload)
            time.sleep(PUBLISH_EVERY_SEC)
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()