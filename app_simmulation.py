!pip install streamlit pyngrok pandas plotly
%%writefile app.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
import time

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="GreenFactory Control Room",
    layout="wide"
)

# Clean dark styling
st.markdown("""
<style>
.block-container {padding-top: 1rem; padding-bottom: 0rem;}
body {background-color: #0e1117; color: white;}
</style>
""", unsafe_allow_html=True)

st.markdown("## 🏭 GreenFactory AI - Industrial Operations Center")

# -------------------------
# Thresholds
# -------------------------
TEMP_LIMIT = 90
VIB_LIMIT = 2.2
CO2_LIMIT = 35
EFF_WARNING = 75
EFF_CRITICAL = 60

# -------------------------
# Initialize 10 Machines
# -------------------------
if "machines" not in st.session_state:
    data = []
    for i in range(1, 11):
        data.append({
            "Machine": f"M{i}",
            "Temp": 70,
            "Vib": 1.0,
            "CO2": 20,
            "Energy": 100,
            "Output": 80,
            "Efficiency": 80,
            "Status": "NORMAL"
        })
    st.session_state.machines = pd.DataFrame(data)

# -------------------------
# Efficiency Formula
# -------------------------
def calculate_efficiency(temp, vib, energy, co2, output):
    base = output / energy
    temp_penalty = max(0, (temp - 75) * 0.5)
    vib_penalty = max(0, (vib - 1.5) * 5)
    carbon_penalty = co2 * 0.3
    eff = 100 * base - temp_penalty - vib_penalty - carbon_penalty
    return max(0, min(eff, 100))

placeholder = st.empty()

while True:

    df = st.session_state.machines

    # Update readings
    for i in range(len(df)):

        if random.random() < 0.85:
            temp = random.uniform(65,80)
            vib = random.uniform(0.5,1.5)
            co2 = random.uniform(15,25)
        else:
            temp = random.uniform(85,100)
            vib = random.uniform(1.8,2.8)
            co2 = random.uniform(30,45)

        energy = random.uniform(90,140)
        output = random.uniform(60,120)

        eff = calculate_efficiency(temp, vib, energy, co2, output)

        df.loc[i,"Temp"] = round(temp,2)
        df.loc[i,"Vib"] = round(vib,2)
        df.loc[i,"CO2"] = round(co2,2)
        df.loc[i,"Energy"] = round(energy,2)
        df.loc[i,"Output"] = round(output,2)
        df.loc[i,"Efficiency"] = round(eff,2)

        if temp > TEMP_LIMIT or vib > VIB_LIMIT or co2 > CO2_LIMIT or eff < EFF_CRITICAL:
            df.loc[i,"Status"] = "CRITICAL"
        elif eff < EFF_WARNING:
            df.loc[i,"Status"] = "WARNING"
        else:
            df.loc[i,"Status"] = "NORMAL"

    with placeholder.container():

        # -------------------------
        # TOP KPI BAR
        # -------------------------
        critical_count = (df["Status"] == "CRITICAL").sum()
        warning_count = (df["Status"] == "WARNING").sum()
        normal_count = (df["Status"] == "NORMAL").sum()

        k1, k2, k3 = st.columns(3)
        k1.metric("🔴 Critical Machines", critical_count)
        k2.metric("🟠 Warning Machines", warning_count)
        k3.metric("🟢 Healthy Machines", normal_count)

        st.markdown("---")

        col1, col2 = st.columns([1.3, 1])

        # -------------------------
        # TABLE WITH HIGHLIGHT
        # -------------------------
        with col1:

            def highlight(row):
                if row["Status"] == "CRITICAL":
                    return ['background-color: #7f1d1d'] * len(row)
                elif row["Status"] == "WARNING":
                    return ['background-color: #78350f'] * len(row)
                else:
                    return [''] * len(row)

            st.dataframe(
                df.style.apply(highlight, axis=1),
                height=420,
                use_container_width=True
            )

        # -------------------------
        # EFFICIENCY GRAPH
        # -------------------------
        with col2:

            colors = []
            for status in df["Status"]:
                if status == "CRITICAL":
                    colors.append("red")
                elif status == "WARNING":
                    colors.append("orange")
                else:
                    colors.append("green")

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=df["Machine"],
                y=df["Efficiency"],
                marker_color=colors,
                text=df["Efficiency"],
                textposition="outside"
            ))

            fig.add_hline(y=EFF_WARNING, line_dash="dash", line_color="orange")
            fig.add_hline(y=EFF_CRITICAL, line_dash="dash", line_color="red")

            fig.update_layout(
                template="plotly_dark",
                height=420,
                margin=dict(l=10, r=10, t=40, b=10),
                title="Machine Efficiency Overview"
            )

            st.plotly_chart(fig, use_container_width=True)

    time.sleep(3)

from pyngrok import ngrok
ngrok.set_auth_token("30TiUFToqhiBM0V1MAlw7UO4mRW_RgXBEMazkJZGyYgz22tj")

from pyngrok import ngrok
ngrok.kill()

!streamlit run app.py &>/dev/null &
public_url = ngrok.connect(8501)
print("🚀 Public URL:", public_url)