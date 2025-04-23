import time
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import random
import datetime
import matplotlib.pyplot as plt

# Must be first
st.set_page_config(layout="centered", page_title="Fish Farm Monitoring", initial_sidebar_state="auto")

# Auto-refresh every 60 seconds
st_autorefresh(interval=60 * 1000, key="refresh")

# App Title
st.title("🌊 Fish Farm Monitoring Dashboard")
st.markdown("Real-time monitoring of temperature, pH, and dissolved oxygen across all tanks.")

# Constants
TANKS = {
    "Grower Tanks": [f"Grower Tank {i+1}" for i in range(4)],
    "Nursery Tanks": [f"Nursery Tank {i+1}" for i in range(4)]
}
IDEAL_RANGES = {
    "Temperature (°C)": (28, 31),
    "pH": (7.0, 8.0),
    "DO (mg/L)": (7.0, 8.0)
}

# Session state initialization
if "data" not in st.session_state:
    st.session_state.data = {tank: {
        "Temperature (°C)": [],
        "pH": [],
        "DO (mg/L)": [],
        "Time": []
    } for t in TANKS.values() for tank in t}
    st.session_state.last_update = time.time()

# Simulate a new reading
def simulate_sensor_data():
    for tank_group in TANKS.values():
        for tank in tank_group:
            st.session_state.data[tank]["Temperature (°C)"].append(round(random.uniform(26, 33), 2))
            st.session_state.data[tank]["pH"].append(round(random.uniform(6.5, 8.5), 2))
            st.session_state.data[tank]["DO (mg/L)"].append(round(random.uniform(6.5, 8.5), 2))
            st.session_state.data[tank]["Time"].append(datetime.datetime.now())

# Alert logic
def get_alerts():
    alerts = []
    for tank, readings in st.session_state.data.items():
        for metric, (low, high) in IDEAL_RANGES.items():
            if readings[metric]:
                latest = readings[metric][-1]
                if latest < low or latest > high:
                    alerts.append(f"🚨 {tank}: {metric} is {latest} (Ideal: {low}-{high})")
    return alerts

# Automatic update every minute
if time.time() - st.session_state.last_update > 60:
    simulate_sensor_data()
    st.session_state.last_update = time.time()

# Manual update button
if st.button("🔁 Update Sensor Data"):
    simulate_sensor_data()
    st.session_state.last_update = time.time()

# Show alerts
alerts = get_alerts()
if alerts:
    st.error("⚠️ Alerts Detected:")
    for alert in alerts:
        st.markdown(f"- {alert}")
else:
    st.success("✅ All readings are within safe limits.")

# Tank selection
tank_selected = st.selectbox("Select a Tank to View Details", [tank for t in TANKS.values() for tank in t])

# Plotting graphs
for metric in ["Temperature (°C)", "pH", "DO (mg/L)"]:
    st.subheader(f"📊 {metric} for {tank_selected}")
    
    times = st.session_state.data[tank_selected]["Time"]
    values = st.session_state.data[tank_selected][metric]

    if times:
        total_points = len(times)
        default_points = 5

        # Only show slider if there's more data than default view
        if total_points > default_points:
            num_points = st.slider(
                f"Select number of data points to display for {metric}",
                min_value=default_points,
                max_value=total_points,
                value=default_points,
                key=f"slider_{metric}"
            )
        else:
            num_points = total_points

        times_to_show = times[-num_points:]
        values_to_show = values[-num_points:]

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(times_to_show, values_to_show, marker='o', color='blue', label=metric)

        # Ideal range highlight
        low, high = IDEAL_RANGES[metric]
        ax.axhspan(low, high, color='green', alpha=0.2, label='Ideal Range')

        # Align ticks with times
        ax.set_xticks(times_to_show)
        ax.set_xticklabels([t.strftime('%H:%M:%S') for t in times_to_show], rotation=45, ha='right')

        # Label each point with the value
        for i in range(len(values_to_show)):
            value_label = str(values_to_show[i])
            ax.annotate(value_label, (times_to_show[i], values_to_show[i]),
                        textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8, color='black')

        ax.set_xlabel("Time")
        ax.set_ylabel(metric)
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)


        st.markdown(f"**Latest {metric}:** {values_to_show[-1]} at {times_to_show[-1].strftime('%H:%M:%S')}")
    else:
        st.info("No data yet. Please update.")
