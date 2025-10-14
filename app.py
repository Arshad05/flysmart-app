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
# HEADER
# ---------------------------
st.title("✈️ FlySmart: Your Smart Airline Companion")
st.caption("Helping travellers make informed, stress-free flight decisions.")
st.markdown("---")

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.header("🔍 Select Airline")
selected_airline = st.sidebar.selectbox("Choose an airline:", list(airline_data.keys()))
st.sidebar.info("Select an airline to view details and simulated live flights.")

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

    if search_query:
        result = simulated_flights[simulated_flights["Flight"] == search_query]
        if not result.empty:
            st.success(f"Flight {search_query} found:")
            st.table(result)
            st.map(result.rename(columns={"Latitude": "latitude", "Longitude": "longitude"}))
        else:
            st.warning("❌ Flight not found. Please check the flight number or try again.")
    else:
        # Default view if no search query
        st.dataframe(simulated_flights, use_container_width=True)
        st.map(simulated_flights.rename(columns={"Latitude": "latitude", "Longitude": "longitude"}), size=30)

    st.caption("Note: This is simulated data for demo purposes. Real-time API integration planned for Assessment 002.")

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("---")
st.caption("Developed as part of a University Project • Prototype v1.2 • © 2025 FlySmart")
