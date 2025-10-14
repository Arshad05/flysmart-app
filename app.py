import streamlit as st 
import pandas as pd
import json
import random
from datetime import datetime
import requests

# ---------------------------
# APP CONFIG
# ---------------------------
st.set_page_config(
    page_title="FlySmart | Flight Tracker",
    page_icon="✈️",
    layout="centered"
)
# ---------------------------
# BACKGROUND IMAGE (minimal)
# ---------------------------
import base64

def set_background(image_file):
    with open(image_file, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode()
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        [data-testid="stHeader"], [data-testid="stToolbar"] {{
            background: rgba(0, 0, 0, 0);
        }}
        .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6 {{
            color: #ffffff;
            text-shadow: 0 0 6px rgba(0,0,0,0.4);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ---------------------------
# CARD STYLE CONTAINER
# ---------------------------
def card_block(content):
    st.markdown(
        f"""
        <div style='background: rgba(255, 255, 255, 0.75);
                    border-radius: 16px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            {content}
        </div>
        """,
        unsafe_allow_html=True
    )


# Set the background (make sure the file exists)
set_background("background.jpg")

# ---------------------------
# LOAD DATA
# ---------------------------

# Load airline info
with open("airline_info.json", "r") as f:
    airline_data = json.load(f)

# Load flight data from CSV
flights_df = pd.read_csv("flights.csv")

# Create a dictionary for quick lookup
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
# HEADER
# ---------------------------
st.title("✈️ FlySmart: Personal Flight Tracker")
st.caption("Track your flight. Know what matters. Travel stress-free.")
st.markdown("---")

# ---------------------------
# FLIGHT SEARCH
# ---------------------------
st.subheader("🔎 Find Your Flight")
flight_number = st.selectbox(
    "Select or enter your flight number:",
    options=sorted(flights_df["flight_number"].unique()),
    index=None,
    placeholder="Type or select a flight..."
)

# ---------------------------
# MAIN CONTENT
# ---------------------------
if flight_number:
    if flight_number in sample_flights:
        details = sample_flights[flight_number]
        airline_name = details["airline"]

# 1️⃣ Flight Summary
card_block(f"""
<h3>✈️ Flight Summary</h3>
<b>Flight:</b> {flight_number} — {airline_name}<br>
<b>Route:</b> {details['origin']} → {details['destination']}<br>
<b>Departure:</b> {details['departure']}<br>
<b>Status:</b> {details['status']}
""")

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
        except Exception:
            st.warning("Unable to fetch live weather data.")

    else:
        st.error("❌ Flight not found. Please check your flight number and try again.")
else:
    st.info("Enter your flight number above to track your journey.")

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("---")
st.caption("Developed as part of a University Project • Prototype v2.2 • © 2025 FlySmart")


