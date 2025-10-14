import streamlit as st
import pandas as pd
import json
import random
from datetime import datetime
import requests
import base64
import pydeck as pdk  # For the map

# ---------------------------
# APP CONFIG
# ---------------------------
st.set_page_config(
    page_title="FlySmart | Flight Tracker",
    page_icon="✈️",
    layout="centered"
)

# ---------------------------
# OPTIONAL BACKGROUND IMAGE
# ---------------------------
def set_background(image_file: str):
    try:
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
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        pass

# Apply background (optional)
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
st.divider()

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
        st.subheader("✈️ Flight Summary")
        st.markdown(
            f"""
**Flight:** {flight_number} — {airline_name}  
**Route:** {details['origin']} → {details['destination']}  
**Departure:** {details['departure']}  
**Status:** {details['status']}
            """
        )
        st.divider()

        # 2️⃣ Countdown to Departure
        st.subheader("⏰ Time to Departure")
        dep_time = datetime.strptime(details["departure"], "%Y-%m-%d %H:%M")
        remaining = dep_time - datetime.now()
        if remaining.total_seconds() > 0:
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes = remainder // 60
            st.info(f"{hours} hours and {minutes} minutes remaining until departure.")
        else:
            st.warning("This flight has already departed or is currently in progress.")
        st.divider()

        # 3️⃣ Airline Information
        st.subheader("🧳 Airline Information")
        if airline_name in airline_data:
            info = airline_data[airline_name]
            st.markdown(
                f"""
- **Check-in:** {info['check_in']}
- **Baggage Drop:** {info['baggage_drop']}
- **Boarding:** {info['boarding']}
                """
            )
            st.markdown(f"[Visit {airline_name} Website]({info['contact']})")
        else:
            st.info("No policy data available for this airline.")
        st.divider()

        # 4️⃣ Simulated Flight Position (✈️ flight icon on OpenStreetMap)
        st.subheader("🌍 Current Flight Position (Simulated)")

        lat = random.uniform(-60, 60)
        lon = random.uniform(-150, 150)

        # Define a flight icon
        icon_data = {
            "url": "https://upload.wikimedia.org/wikipedia/commons/e/e0/Plane_icon.svg",
            "width": 128,
            "height": 128,
            "anchorY": 128,
        }

        # Create DataFrame with coordinates and icon
        flight_df = pd.DataFrame(
            [{
                "lat": lat,
                "lon": lon,
                "icon_data": icon_data,
            }]
        )

        # Define icon layer
        icon_layer = pdk.Layer(
            "IconLayer",
            data=flight_df,
            get_icon="icon_data",
            get_size=5,
            get_position='[lon, lat]',
            pickable=True,
        )

        # View settings
        view_state = pdk.ViewState(
            latitude=lat,
            longitude=lon,
            zoom=1.8,
            pitch=0,
        )

        # Add solid background for visibility
        st.markdown(
            """
            <style>
            [data-testid="stDeckGlJsonChart"] {
                background-color: #181818 !important;
                border-radius: 10px;
                padding: 10px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Render visible OpenStreetMap (no token needed)
        st.pydeck_chart(
            pdk.Deck(
                map_style=None,  # ✅ Removes Mapbox dependency
                initial_view_state=view_state,
                layers=[icon_layer],
                tooltip={"text": "✈️ Flight Position"},
            )
        )

        st.divider()

        # 5️⃣ Live Weather at Destination
        st.subheader("🌤 Live Weather at Destination")
        city = details["destination"].split("(")[0].strip()

        try:
            api_key = st.secrets["weather"]["api_key"]
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url, timeout=10)
            data = response.json()
            if data.get("cod") == 200:
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"].title()
                icon = data["weather"][0]["icon"]
                cols = st.columns([1, 4])
                with cols[0]:
                    st.image(f"http://openweathermap.org/img/wn/{icon}.png", width=64)
                with cols[1]:
                    st.success(f"Weather in {city}: **{temp} °C**, {desc}")
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
st.divider()
st.caption("Developed as part of a University Project • Prototype v2.9 • © 2025 FlySmart")
