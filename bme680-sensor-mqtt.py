import bme680 as bme680
import paho.mqtt.client as mqtt
import time

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

sensor.get_sensor_data()
temperature = sensor.data.temperature
pressure = sensor.data.pressure
humidity = sensor.data.humidity
gas = sensor.data.gas_resistance

print(f"Temperature: {temperature} C")
print(f"Pressure: {pressure} Pa")
print(f"Humidity: {humidity} %")
print(f"Gas: {gas} Ohms")

while True:
    sensor.get_sensor_data()
    temperature = sensor.data.temperature
    pressure = sensor.data.pressure
    humidity = sensor.data.humidity
    gas = sensor.data.gas_resistance

    print(f"Temperature: {temperature} C")
    print(f"Pressure: {pressure} Pa")
    print(f"Humidity: {humidity} %")
    print(f"Gas: {gas} Ohms")
    time.sleep(5)

