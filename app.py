import streamlit as st
import pandas as pd
import json
import random

# ---------------------------
# APP CONFIG
# ---------------------------
st.set_page_config(
    page_title="FlySmart | Airline Companion",
    page_icon="✈️",
    layout="wide"
)

# ---------------------------
# LOAD AIRLINE DATA
# ---------------------------
with open("airline_info.json", "r") as f:
    airline_data = json.load(f)

# ---------------------------
# SIDEBAR SETTINGS
# ---------------------------
st.sidebar.header("⚙️ Settings & Airline Selection")

# Theme toggle
theme = st.sidebar.radio("Theme Mode:", ["Light 🌤️", "Dark 🌙"])

# Airline selection
selected_airline = st.sidebar.selectbox("Choose an airline:", list(airline_data.keys()))
st.sidebar.info("Select an airline to view details and simulated live flights.")

# Apply theme color styles
if theme == "Dark 🌙":
    st.markdown("""
        <style>
        body {
            background-color: #0E1117;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)

# ---------------------------
# HEADER
# ---------------------------
st.title("✈️ FlySmart: Your Smart Airline Companion")
st.caption("Helping travellers make informed, stress-free flight decisions.")
st.markdown("---")

# ---------------------------
# TABS LAYOUT
# ---------------------------
tab1, tab2 = st.tabs(["📋 Airline Information", "🌍 Live Flight Map"])

# ---------------------------
# TAB 1: AIRLINE INFO
# ---------------------------
with tab1:
    st.subheader(f"🛫 {selected_airline}")
    info = airline_data[selected_airline]
    st.write(f"**Check-in:** {info['check_in']}")
    st.write(f"**Baggage Drop:** {info['baggage_drop']}")
    st.write(f"**Boarding:** {info['boarding']}")
    st.markdown(f"[Official Website]({info['contact']})")

    st.markdown("---")
    st.success("💡 Tip: Use the Live Flight Map tab to see your airline’s current simulated flights!")

# ---------------------------
# TAB 2: LIVE MAP
# ---------------------------
with tab2:
    st.subheader(f"🌍 Simulated {selected_airline} Flights")

    # Simulate flight data (6 flights)
    destinations = ["New York", "Dubai", "Madrid", "Paris", "Rome", "Berlin", "Lisbon", "Doha", "Istanbul", "Tokyo"]
    num_flights = 6
    simulated_flights = pd.DataFrame({
        "Flight": [f"{selected_airline[:2].upper()}{100 + i}" for i in range(num_flights)],
        "Destination": random.choices(destinations, k=num_flights),
        "Latitude": [random.uniform(-60, 60) for _ in range(num_flights)],
        "Longitude": [random.uniform(-150, 150) for _ in range(num_flights)],
        "Status": random.choices(["On Time", "Delayed", "Cancelled"], [0.7, 0.2, 0.1], k=num_flights)
    })

    # 🔍 Flight Search Input
    search_query = st.text_input("Enter flight number to search (e.g. BA102):").strip().upper()

    # Helper function: colour-code status text
    def color_status(val):
        if val == "On Time":
            color = "green"
        elif val == "Delayed":
            color = "orange"
        else:
            color = "red"
        return f"<span style='color:{color}; font-weight:bold;'>{val}</span>"

    # Search logic
    if search_query:
        result = simulated_flights[simulated_flights["Flight"] == search_query]
        if not result.empty:
            st.success(f"Flight {search_query} found:")
            styled = result.to_html(escape=False, formatters={"Status": color_status})
            st.markdown(styled, unsafe_allow_html=True)
            st.map(result.rename(columns={"Latitude": "latitude", "Longitude": "longitude"}))
        else:
            st.warning("❌ Flight not found. Please check the flight number or try again.")
    else:
        # Default view if no search query
        styled_df = simulated_flights.copy()
        styled_df["Status"] = styled_df["Status"].apply(lambda x: color_status(x))
        st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)
        st.map(simulated_flights.rename(columns={"Latitude": "latitude", "Longitude": "longitude"}), size=30)

    st.caption("Note: This is simulated data for demo purposes. Real-time API integration planned for Assessment 002.")

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("---")
st.caption("Developed as part of a University Project • Prototype v1.3 • © 2025 FlySmart")
