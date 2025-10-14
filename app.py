import streamlit as st
import pandas as pd
import json
import random
from datetime import datetime, timedelta

# ---------------------------
# APP CONFIG
# ---------------------------
st.set_page_config(
    page_title="FlySmart | Flight Tracker",
    page_icon="✈️",
    layout="centered"
)

# ---------------------------
# LOAD AIRLINE DATA
# ---------------------------
with open("airline_info.json", "r") as f:
    airline_data = json.load(f)

# ---------------------------
# HEADER
# ---------------------------
st.title("✈️ FlySmart: Personal Flight Tracker")
st.caption("Helping travellers track their flight and stay informed at every stage.")
st.markdown("---")

# ---------------------------
# FLIGHT SEARCH SECTION
# ---------------------------
st.subheader("🔎 Find Your Flight")

flight_number = st.text_input("Enter your flight number (e.g. BA102):").strip().upper()

# Mock database of sample flights
sample_flights = {
    "BA102": {"airline": "British Airways", "origin": "London Heathrow (LHR)", "destination": "Dubai (DXB)", "departure": "2025-10-14 21:00", "status": "On Time"},
    "EJ210": {"airline": "EasyJet", "origin": "Paris (CDG)", "destination": "Lisbon (LIS)", "departure": "2025-10-14 19:45", "status": "Delayed"},
    "EM777": {"airline": "Emirates", "origin": "Dubai (DXB)", "destination": "Tokyo (HND)", "departure": "2025-10-15 00:10", "status": "On Time"}
}

if flight_number:
    if flight_number in sample_flights:
        details = sample_flights[flight_number]
        airline_name = details["airline"]
        st.success(f"Flight {flight_number} found!")

        st.markdown(f"### ✈️ {details['airline']}")
        st.write(f"**Route:** {details['origin']} → {details['destination']}")
        st.write(f"**Departure Time:** {details['departure']}")
        st.write(f"**Status:** {details['status']}")

        # ---------------------------
        # AIRLINE INFO SECTION
        # ---------------------------
        st.markdown("---")
        st.subheader("🧳 Airline Information")

        if airline_name in airline_data:
            info = airline_data[airline_name]
            st.write(f"**Check-in:** {info['check_in']}")
            st.write(f"**Baggage Drop:** {info['baggage_drop']}")
            st.write(f"**Boarding:** {info['boarding']}")
            st.markdown(f"[Official Website]({info['contact']})")
        else:
            st.info("No airline policy data available for this carrier.")

        # ---------------------------
        # SIMULATED MAP POSITION
        # ---------------------------
        st.markdown("---")
        st.subheader("🌍 Current Flight Position (Simulated)")
        lat = random.uniform(-60, 60)
        lon = random.uniform(-150, 150)
        st.map(pd.DataFrame({"latitude": [lat], "longitude": [lon]}))

        # ---------------------------
        # COUNTDOWN TIMER
        # ---------------------------
        st.markdown("---")
        st.subheader("⏰ Countdown to Departure")
        dep_time = datetime.strptime(details["departure"], "%Y-%m-%d %H:%M")
        remaining = dep_time - datetime.now()
        if remaining.total_seconds() > 0:
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes = remainder // 60
            st.info(f"🕓 {hours} hours and {minutes} minutes until departure.")
        else:
            st.warning("This flight has already departed or is in progress.")

    else:
        st.error("❌ Flight not found. Please check your flight number and try again.")

else:
    st.info("Enter your flight number above to track your journey.")

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("---")
st.caption("Developed as part of a University Project • Prototype v2.0 • © 2025 FlySmart")
