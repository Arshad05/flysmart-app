import streamlit as st
import pandas as pd
import json
import random
from datetime import datetime

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
st.caption("Track your flight. Know what matters. Travel stress-free.")
st.markdown("---")

# ---------------------------
# FLIGHT SEARCH
# ---------------------------
flight_number = st.selectbox(
    "Select or enter your flight number:",
    options=sorted(flights_df["flight_number"].unique()),
    index=None,
    placeholder="Type or select a flight..."
)


# Mock flight database (for demonstration)
# Load flight data from CSV
flights_df = pd.read_csv("flights.csv")

# Create a dictionary for easy lookup
sample_flights = {
    row["flight_number"]: {
        "airline": row["airline"],
        "origin": row["origin"],
        "destination": row["destination"],
        "departure": row["departure"],
        "status": row["status"]
    }
    for _, row in flights_df.iterrows()
}


# ---------------------------
# MAIN CONTENT
# ---------------------------
if flight_number:
    if flight_number in sample_flights:
        details = sample_flights[flight_number]
        airline_name = details["airline"]

        # 1️⃣ Flight Summary
        st.markdown("### ✈️ Flight Summary")
        st.markdown(f"""
        **Flight:** {flight_number} — {airline_name}  
        **Route:** {details['origin']} → {details['destination']}  
        **Departure:** {details['departure']}  
        **Status:** {details['status']}
        """)
        st.markdown("---")

        # 2️⃣ Countdown to Departure
        st.markdown("### ⏰ Time to Departure")
        dep_time = datetime.strptime(details["departure"], "%Y-%m-%d %H:%M")
        remaining = dep_time - datetime.now()
        if remaining.total_seconds() > 0:
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes = remainder // 60
            st.info(f"{hours} hours and {minutes} minutes remaining until departure.")
        else:
            st.warning("This flight has already departed or is currently in progress.")
        st.markdown("---")

        # 3️⃣ Airline Information
        st.markdown("### 🧳 Airline Information")
        if airline_name in airline_data:
            info = airline_data[airline_name]
            st.write(f"**Check-in:** {info['check_in']}")
            st.write(f"**Baggage Drop:** {info['baggage_drop']}")
            st.write(f"**Boarding:** {info['boarding']}")
            st.markdown(f"[Visit {airline_name} Website]({info['contact']})")
        else:
            st.info("No policy data available for this airline.")
        st.markdown("---")

        # 4️⃣ Simulated Flight Position (for presentation visuals)
        st.markdown("### 🌍 Current Flight Position (Simulated)")
        lat = random.uniform(-60, 60)
        lon = random.uniform(-150, 150)
        st.map(pd.DataFrame({"latitude": [lat], "longitude": [lon]}))

        # 5️⃣ Live Weather at Destination
        st.markdown("---")
        st.markdown("### 🌤 Live Weather at Destination")

        import requests
        city = details["destination"].split("(")[0].strip()  # extract city name
        api_key = st.secrets["weather"]["api_key"]
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

        try:
            response = requests.get(url)
            data = response.json()
            if data.get("cod") == 200:
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"].title()
                icon = data["weather"][0]["icon"]
                st.image(f"http://openweathermap.org/img/wn/{icon}.png", width=80)
                st.success(f"Weather in {city}: {temp} °C, {desc}")
            else:
                st.warning("Weather data not available right now.")
        except Exception as e:
            st.warning("Unable to fetch live weather data.")


# ---------------------------
# FOOTER
# ---------------------------
st.markdown("---")
st.caption("Developed as part of a University Project • Prototype v2.1 • © 2025 FlySmart")





