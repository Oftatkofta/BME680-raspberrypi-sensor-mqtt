import bme680 as bme680
import paho.mqtt.client as mqtt
import time
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the BME680 sensor
sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)

# Set the temperature, pressure, and humidity oversampling values to maximum (16X)
sensor.set_temperature_oversample(bme680.OS_16X)
sensor.set_pressure_oversample(bme680.OS_16X)
sensor.set_humidity_oversample(bme680.OS_16X)

# Set the filter
sensor.set_filter(bme680.FILTER_SIZE_0)

# Set the gas sensor heater temperature
sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(50)

# setup mqtt client with the mqtt-user on Home Assistant and password from the .env file
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_host = os.getenv("MQTT_HOST")
mqtt_port = int(os.getenv("MQTT_PORT", 1883))  # Default to 1883 if not set
mqtt_topic = os.getenv("MQTT_TOPIC")
mqtt_client.username_pw_set(username=os.getenv("MQTT_USER"), password=os.getenv("MQTT_PASSWORD"))
mqtt_client.connect(mqtt_host, mqtt_port, 60)

while True:
    sensor.get_sensor_data()
    temperature = sensor.data.temperature
    pressure = sensor.data.pressure
    humidity = sensor.data.humidity
    gas = sensor.data.gas_resistance

    # Publish sensor data to MQTT
    mqtt_client.publish(topic=mqtt_topic, payload=json.dumps({
        "temperature": temperature,
        "pressure": pressure,
        "humidity": humidity,
        "gas": gas
    }))

    print(f"Temperature: {temperature} C")
    print(f"Pressure: {pressure} Pa")
    print(f"Humidity: {humidity} %")
    print(f"Gas: {gas} Ohms")
    time.sleep(5)

