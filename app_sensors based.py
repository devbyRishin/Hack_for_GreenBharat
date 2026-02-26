import pathway as pw
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import Adafruit_DHT
import serial
import RPi.GPIO as GPIO
import time
from threading import Thread

# ----------------------------
# SENSOR CONFIGURATION
# ----------------------------

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

ser = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)

VIB_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(VIB_PIN, GPIO.IN)

# ----------------------------
# THRESHOLDS
# ----------------------------

TEMP_LIMIT = 85
CO2_LIMIT = 800
EFF_WARNING = 75
EFF_CRITICAL = 60

# ----------------------------
# SENSOR FUNCTIONS
# ----------------------------

def read_temperature():
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    return temperature if temperature else 0

def read_vibration():
    return GPIO.input(VIB_PIN)

def read_co2():
    ser.write(b'\xff\x01\x86\x00\x00\x00\x00\x00\x79')
    data = ser.read(9)
    if len(data) == 9:
        return data[2] * 256 + data[3]
    return 0

def read_energy():
    return 120  # Replace with ADC logic

# ----------------------------
# PATHWAY STREAM SOURCE
# ----------------------------

class MachineSchema(pw.Schema):
    timestamp: float
    temperature: float
    co2: int
    vibration: int
    energy: float
    output: float

def sensor_stream():
    while True:
        temp = read_temperature()
        co2 = read_co2()
        vibration = read_vibration()
        energy = read_energy()
        output = 100 - (vibration * 10)

        yield {
            "timestamp": time.time(),
            "temperature": temp,
            "co2": co2,
            "vibration": vibration,
            "energy": energy,
            "output": output
        }

        time.sleep(5)

table = pw.io.python.read(sensor_stream, schema=MachineSchema)

# ----------------------------
# REAL-TIME EFFICIENCY CALCULATION
# ----------------------------

def calculate_efficiency(temp, co2, vibration, energy, output):
    base = output / energy if energy > 0 else 0
    temp_penalty = max(0, (temp - 70) * 0.5)
    vib_penalty = vibration * 10
    carbon_penalty = co2 * 0.02
    eff = 100 * base - temp_penalty - vib_penalty - carbon_penalty
    return max(0, min(eff, 100))

processed = table.with_columns(
    efficiency=pw.apply(
        calculate_efficiency,
        pw.this.temperature,
        pw.this.co2,
        pw.this.vibration,
        pw.this.energy,
        pw.this.output
    )
)

processed = processed.with_columns(
    status=pw.apply(
        lambda temp, co2, eff:
            "CRITICAL" if temp > TEMP_LIMIT or co2 > CO2_LIMIT or eff < EFF_CRITICAL
            else "WARNING" if eff < EFF_WARNING
            else "NORMAL",
        pw.this.temperature,
        pw.this.co2,
        pw.this.efficiency
    )
)

# ----------------------------
# STREAMLIT DASHBOARD
# ----------------------------

st.set_page_config(layout="wide")
st.title("🏭 GreenFactory AI - Pathway Powered Live System")

placeholder = st.empty()

def run_pathway():
    pw.run()

Thread(target=run_pathway, daemon=True).start()

while True:
    df = processed.to_pandas()

    if not df.empty:
        latest = df.iloc[-1]

        with placeholder.container():

            col1, col2 = st.columns([1,1])

            with col1:
                st.metric("Temperature", round(latest.temperature,2))
                st.metric("CO2 (ppm)", latest.co2)
                st.metric("Efficiency (%)", round(latest.efficiency,2))
                st.metric("Status", latest.status)

            with col2:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=latest.efficiency,
                    title={'text': "Machine Efficiency"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'steps': [
                            {'range': [0, 60], 'color': "red"},
                            {'range': [60, 75], 'color': "orange"},
                            {'range': [75, 100], 'color': "green"}
                        ]
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)

    time.sleep(5)