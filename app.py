import streamlit as st
import pandas as pd
import json
import random

# ---------------------------
# APP CONFIG
# ---------------------------
st.set_page_config(
    page_title="FlySmart | Airline Assistant",
    page_icon="✈️",
    layout="centered"
)

# ---------------------------
# LOAD DATA
# ---------------------------
with open("airline_info.json", "r") as f:
    airline_data = json.load(f)

# ---------------------------
# HEADER
# ---------------------------
st.title("✈️ FlySmart: Your Smart Airline Companion")
st.write("A digital tool to help travellers make informed, stress-free flight decisions.")

st.markdown("---")

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.header("🔍 Find Airline Info")
selected_airline = st.sidebar.selectbox("Select Airline", list(airline_data.keys()))
st.sidebar.info("Select an airline to view its important travel details below.")

# ---------------------------
# DISPLAY AIRLINE DETAILS
# ---------------------------
if selected_airline:
    info = airline_data[selected_airline]
    st.subheader(f"🛫 {selected_airline}")
    st.write(f"**Check-in:** {info['check_in']}")
    st.write(f"**Baggage Drop:** {info['baggage_drop']}")
    st.write(f"**Boarding:** {info['boarding']}")
    st.markdown(f"[Official Website]({info['contact']})")

# ---------------------------
# SIMULATED FLIGHT DATA (STATIC FOR DEMO)
# ---------------------------
st.markdown("---")
st.subheader("🌍 Live Flight Overview (Simulated Data)")

# Create fake flight data
flights = pd.DataFrame({
    "Flight": [f"{selected_airline[:2].upper()}{i}" for i in range(101, 106)],
    "Status": random.choices(["On Time", "Delayed", "Cancelled"], weights=[0.7, 0.2, 0.1], k=5),
    "Gate": [random.randint(1, 50) for _ in range(5)],
    "Destination": random.choices(
        ["New York", "Dubai", "Madrid", "Paris", "Rome", "Berlin", "Lisbon"], k=5)
})

st.dataframe(flights, use_container_width=True)

st.caption("Note: Flight data shown is simulated. Real-time tracking will be integrated in future versions.")
