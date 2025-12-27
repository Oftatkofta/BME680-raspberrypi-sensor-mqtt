# BME680 Raspberry Pi MQTT Sensor

A Python script that reads environmental data from a BME680 sensor on a Raspberry Pi and publishes the measurements to MQTT for integration with Home Assistant or other MQTT-compatible systems. Works well even on an old Raspberry pi 1B.

## Features

- **Multi-sensor readings**: Temperature, pressure, humidity, and gas resistance
- **MQTT integration**: Publishes sensor data to individual MQTT topics
- **Home Assistant compatible**: Easy integration with Home Assistant
- **Configurable**: Environment variables for MQTT settings
- **High precision**: Uses maximum oversampling (16X) for accurate readings

## Hardware Requirements

- Raspberry Pi (any model with I2C support)
- BME680 sensor module
- I2C connection between Raspberry Pi and BME680

## Software Requirements

- Python 3.6+ (I use 3.13.5)
- BME680 Python library (pimoroni)
- paho-mqtt
- python-dotenv

## Installation

1. **Clone or download this repository**

2. **Set up the virtual environment:**

The script runs in a virtual environment located at `~/.virtualenvs/pimoroni/`. If you don't have this virtual environment set up yet:

```bash
# Create the virtual environment (if it doesn't exist)
python3 -m venv ~/.virtualenvs/pimoroni

# Activate the virtual environment
source ~/.virtualenvs/pimoroni/bin/activate
```

3. **Install dependencies in the virtual environment:**

```bash
pip install paho-mqtt bme680 python-dotenv
```

Or install specific versions:

```bash
pip install paho-mqtt==2.1.0 bme680==2.0.0 python-dotenv
```

4. **Enable I2C on your Raspberry Pi:**

```bash
sudo raspi-config
```

Navigate to `Interfacing Options` → `I2C` → `Enable`

5. **Create a `.env` file** in the project root directory:

```env
MQTT_USER=your_mqtt_username
MQTT_PASSWORD=your_mqtt_password
MQTT_HOST=homeassistant.local
MQTT_PORT=1883
```

**Note:** The `.env` file is already in `.gitignore` to keep your credentials secure.

## Sensor Configuration

The script is configured with:
- **Oversampling**: 16X for temperature, pressure, and humidity (maximum precision)
- **Filter**: Size 0 (no filtering)
- **Gas heater**: 320°C for 100ms
- **Update interval**: 60 seconds

You can modify these settings in `bme680-sensor-mqtt.py` if needed.

## Usage

Run the script using the Python interpreter from the virtual environment:

```bash
~/.virtualenvs/pimoroni/bin/python3 bme680-sensor-mqtt.py
```

Or activate the virtual environment first:

```bash
source ~/.virtualenvs/pimoroni/bin/activate
python3 bme680-sensor-mqtt.py
```

The script will:
1. Initialize the BME680 sensor
2. Connect to the MQTT broker
3. Continuously read and publish sensor data every 60 seconds

## MQTT Topics

The script publishes sensor data to the following MQTT topics:

| Topic | Description | Unit | Example |
|-------|-------------|------|---------|
| `/sensors/skjulet/temperature_c` | Temperature | Celsius | `22.5` |
| `/sensors/skjulet/pressure_pa` | Atmospheric pressure | Pascal | `101325` |
| `/sensors/skjulet/humidity_percent` | Relative humidity | Percentage | `45.2` |
| `/sensors/skjulet/gas_ohms` | Gas resistance | Ohms | `125000` |

**Note:** You can change the base topic (`/sensors/skjulet`) by modifying the `mqtt_base_topic` variable in the script.

## Running as a Service

To run the script automatically on boot, create a systemd service:

1. Create a service file:

```bash
sudo nano /etc/systemd/system/bme680-sensor.service
```
or copy the one in the repository.

2. Add the following content (adjust paths as needed):

```ini
[Unit]
Description=BME680 MQTT Sensor
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/BME680-raspberrypi-sensor-mqtt
ExecStart=/home/pi/.virtualenvs/pimoroni/bin/python3 /home/pi/BME680-raspberrypi-sensor-mqtt/bme680-sensor-mqtt.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Note:** The `ExecStart` path uses the Python interpreter from the virtual environment at `~/.virtualenvs/pimoroni/bin/python3`. Adjust the user path (`/home/pi`) if your setup differs.

3. Enable and start the service:

```bash
sudo systemctl enable bme680-sensor.service
sudo systemctl start bme680-sensor.service
```

4. Check status:

```bash
sudo systemctl status bme680-sensor.service
```


## Dependencies

- [pimoroni/bme680-python](https://github.com/pimoroni/bme680-python) - BME680 sensor library
- [paho-mqtt](https://github.com/eclipse/paho.mqtt.python) - MQTT client library
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Environment variable management

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

Jens Eriksson
