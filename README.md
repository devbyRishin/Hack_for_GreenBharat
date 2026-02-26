# Hack_for_GreenBharat
GreenFactory AI

Real-Time Industrial Sustainability Monitoring System
1. Project Overview

GreenFactory AI is a real-time industrial monitoring system that:

Reads live machine sensor data

Streams data using Pathway

Calculates sustainability efficiency

Detects anomalies

Displays real-time dashboard using Streamlit

Two implementations are included:

app_simmulation.py → Simulation-based system

app_sensors based.py → Real sensor-based system
2. Technology Stack
Hardware

Raspberry Pi 4

DHT22

MH-Z19B

SW-420

ACS712

Software

Python 3.x

Pathway

Streamlit

Pandas

Plotly

RPi.GPIO

Adafruit_DHT

pyserial
Sensors → Raspberry Pi → Pathway Stream Engine → Processing Layer → Alert Logic → Streamlit Dashboard
Data Flow

Sensors collect temperature, CO₂, vibration, and energy data.

Raspberry Pi reads sensors via GPIO and UART.

Data is streamed into Pathway using pw.io.python.read().

Pathway performs:

Efficiency calculation

Status classification (Normal / Warning / Critical)

Streamlit displays real-time metrics and alerts
4. Efficiency Calculation Logic
base = output / energy

Efficiency =
    (base × 100)
    - temperature penalty
    - vibration penalty
    - carbon penalty
    Thresholds

Efficiency < 60 → CRITICAL

60–75 → WARNING

75 → NORMAL
5. Pathway Processing Layer
Schema Definition
class MachineSchema(pw.Schema):
    timestamp: float
    temperature: float
    co2: int
    vibration: int
    energy: float
    output: float
    Real-Time Processing

with_columns() used for transformation

pw.apply() used for efficiency calculation

Status derived from threshold logic

pw.run() executes streaming engine
6. Simulation Version (app.py)

Generates synthetic data for 10 machines

Simulates failure conditions

Displays:

KPI summary

Status-highlighted table

Efficiency graph

Used for demo without hardware

Run:streamlit run app.py
7. Sensor-Based Version (app_sensors based.py)

Requirements:

Sensors connected properly

UART enabled for CO₂ sensor

GPIO enabled

Run:streamlit run greenfactory_pathway.py
access : http://<raspberry-pi-ip>:8501
8. Project Structure
GreenFactory-AI/
│
├── app_simmulation.py
├── app_sensirs based.py
└── README.md
9. Scalability

The system supports:

Multi-machine monitoring

Edge deployment on Raspberry Pi

Real-time stream processing

Cloud extension capability
10. Limitations

Energy sensor requires ADC calibration

CO₂ sensor requires calibration

Industrial-grade vibration may require accelerometer upgrade
