import time
import os
import bme680
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# -----------------------------
# Configuration (via .env)
# -----------------------------
MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

MQTT_BASE_TOPIC = os.getenv("MQTT_BASE_TOPIC", "/sensors/skjulet")

# Recommended default: 60s for environmental monitoring
PUBLISH_INTERVAL_S = int(os.getenv("PUBLISH_INTERVAL_S", "60"))

# Precision control to reduce HA churn
TEMP_DECIMALS = int(os.getenv("TEMP_DECIMALS", "1"))        # e.g. 0.1 C
HUM_DECIMALS = int(os.getenv("HUM_DECIMALS", "1"))          # e.g. 0.1 %
PRESSURE_PA_DECIMALS = int(os.getenv("PRESSURE_PA_DECIMALS", "0"))  # integer Pa
GAS_OHMS_DECIMALS = int(os.getenv("GAS_OHMS_DECIMALS", "0"))        # integer ohms

if not MQTT_HOST:
    raise RuntimeError("MQTT_HOST is not set (check your .env file)")

# -----------------------------
# BME680 sensor setup
# -----------------------------
sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)

sensor.set_temperature_oversample(bme680.OS_16X)
sensor.set_pressure_oversample(bme680.OS_16X)
sensor.set_humidity_oversample(bme680.OS_16X)

sensor.set_filter(bme680.FILTER_SIZE_0)

sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(100)

# -----------------------------
# MQTT setup
# -----------------------------
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.username_pw_set(username=MQTT_USER, password=MQTT_PASSWORD)

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"MQTT connected: reason_code={reason_code}")

def on_disconnect(client, userdata, reason_code, properties=None):
    print(f"MQTT disconnected: reason_code={reason_code}")

mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect

# Reconnect backoff (important for long-running stability)
mqtt_client.reconnect_delay_set(min_delay=1, max_delay=120)

mqtt_client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)

# Start the MQTT network loop so keepalives/reconnects work during sleep()
mqtt_client.loop_start()

def publish(topic: str, value) -> None:
    """Publish a value to MQTT. Logs immediate publish failures."""
    payload = str(value)
    info = mqtt_client.publish(topic=topic, payload=payload, qos=0, retain=False)
    if info.rc != mqtt.MQTT_ERR_SUCCESS:
        print(f"MQTT publish failed rc={info.rc} topic={topic} payload={payload}")

# -----------------------------
# Main loop
# -----------------------------
while True:
    try:
        # get_sensor_data() returns True on success in most bme680 libs
        ok = sensor.get_sensor_data()
        if ok is False:
            print("Sensor read failed; retrying in 5s")
            time.sleep(5)
            continue

        # Read raw values
        temperature = sensor.data.temperature
        humidity = sensor.data.humidity
        pressure_hpa = sensor.data.pressure         # many libs report hPa
        gas_ohms = sensor.data.gas_resistance

        # Normalize units and reduce precision to avoid HA recorder churn
        temperature = round(temperature, TEMP_DECIMALS)
        humidity = round(humidity, HUM_DECIMALS)

        # Convert hPa -> Pa for correct topic naming pressure_pa
        pressure_pa = pressure_hpa * 100.0
        pressure_pa = round(pressure_pa, PRESSURE_PA_DECIMALS)
        if PRESSURE_PA_DECIMALS == 0:
            pressure_pa = int(pressure_pa)

        gas_ohms = round(gas_ohms, GAS_OHMS_DECIMALS)
        if GAS_OHMS_DECIMALS == 0:
            gas_ohms = int(gas_ohms)

        # Publish sensor data to individual MQTT topics
        publish(f"{MQTT_BASE_TOPIC}/temperature_c", temperature)
        publish(f"{MQTT_BASE_TOPIC}/pressure_pa", pressure_pa)
        publish(f"{MQTT_BASE_TOPIC}/humidity_percent", humidity)
        publish(f"{MQTT_BASE_TOPIC}/gas_ohms", gas_ohms)

        # Local logs (journalctl)
        print(f"Temperature: {temperature} C")
        print(f"Pressure: {pressure_pa} Pa")
        print(f"Humidity: {humidity} %")
        print(f"Gas: {gas_ohms} Ohms")

        time.sleep(PUBLISH_INTERVAL_S)

    except Exception as e:
        # Do not exit; recover automatically
        print(f"Loop error: {e!r}; retrying in 10s")
        time.sleep(10)
