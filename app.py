import streamlit as st 
import pandas as pd
import json
import random
from datetime import datetime
import requests
import base64

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
        h1, h2, h3, h4, h5, h6, p, .stMarkdown {{
            color: #ffffff !important;
            text-shadow: 0 0 6px rgba(0,0,0,0.4);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ---------------------------
# CARD STYLE CONTAINER (renders HTML correctly)
# ---------------------------
def card_block(content: str):
    html = f"""
    <div style='background: rgba(255, 255, 255, 0.75);
                border-radius: 16px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                color: #000000;'>
        {content}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)  # ✅ This ensures HTML renders properly

# ---------------------------
# BACKGROUND SETUP
# ---------------------------
set_background("background.jpg")

# ---------------------------
# LOAD DATA
# ---------------------------
with open("airline_info.json", "r") as f:
    airline_data = json.load(f)

flights_df = pd.read_csv("flights.csv")

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
        dep_time = datetime.strptime(details["departure"], "%Y-%m-%d %H:%M")
        remaining = dep_time - datetime.now()
        if remaining.total_seconds() > 0:
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes = remainder // 60
            countdown_msg = f"{hours} hours and {minutes} minutes remaining until departure."
        else:
            countdown_msg = "This flight has already departed or is currently in progress."
        card_block(f"<h3>⏰ Time to Departure</h3><p>{countdown_msg}</p>")

        # 3️⃣ Airline Information
        if airline_name in airline_data:
            info = airline_data[airline_name]
            card_block(f"""
            <h3>🧳 Airline Information</h3>
            <b>Check-in:</b> {info['check_in']}<br>
            <b>Baggage Drop:</b> {info['baggage_drop']}<br>
            <b>Boarding:</b> {info['boarding']}<br>
            <a href="{info['contact']}" target="_blank">Visit {airline_name} Website</a>
            """)
        else:
            card_block("<h3>🧳 Airline Information</h3><p>No policy data available for this airline.</p>")

        # 4️⃣ Simulated Flight Position (for presentation visuals)
        lat = random.uniform(-60, 60)
        lon = random.uniform(-150, 150)
        card_block("<h3>🌍 Current Flight Position (Simulated)</h3>")
        st.map(pd.DataFrame({"latitude": [lat], "longitude": [lon]}))

        # 5️⃣ Live Weather at Destination
        city = details["destination"].split("(")[0].strip()
        api_key = st.secrets["weather"]["api_key"]
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

        try:
            response = requests.get(url)
            data = response.json()
            if data.get("cod") == 200:
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"].title()
                icon = data["weather"][0]["icon"]
                card_block(f"""
                <h3>🌤 Live Weather at Destination</h3>
                <img src="http://openweathermap.org/img/wn/{icon}.png" width="80">
                <p><b>Weather in {city}:</b> {temp} °C, {desc}</p>
                """)
            else:
                card_block("<h3>🌤 Live Weather at Destination</h3><p>Weather data not available right now.</p>")
        except Exception:
            card_block("<h3>🌤 Live Weather at Destination</h3><p>Unable to fetch live weather data.</p>")

    else:
        st.error("❌ Flight not found. Please check your flight number and try again.")
else:
    st.info("Enter your flight number above to track your journey.")

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("---")
st.caption("Developed as part of a University Project • Prototype v2.4 • © 2025 FlySmart")
