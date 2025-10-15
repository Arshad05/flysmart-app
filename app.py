import streamlit as st
import pandas as pd
import json
import random
from datetime import datetime
import requests
import base64
import re

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

# Optional background (only if available)
set_background("background.jpg")

# ---------------------------
# LOAD DATA
# ---------------------------
with open("airline_info.json", "r") as f:
    airline_data = json.load(f)

flights_df = pd.read_csv("flights.csv")

# Helper: Extract airport code in brackets if it exists, otherwise leave blank
def extract_airport_code(location: str):
    match = re.search(r"\((\w{3})\)", location)
    return match.group(1) if match else ""

sample_flights = {
    row["flight_number"]: {
        "airline": row["airline"],
        "origin": row["origin"],
        "destination": row["destination"],
        "departure": row["departure"],
        "status": row["status"],
        "origin_code": extract_airport_code(row["origin"]),
        "dest_code": extract_airport_code(row["destination"])
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
# FLIGHT SEARCH (Cleaner display)
# ---------------------------
st.subheader("🔎 Find Your Flight")

flight_options = []
for _, row in flights_df.iterrows():
    origin_code = extract_airport_code(row["origin"])
    dest_code = extract_airport_code(row["destination"])
    display = f"{row['flight_number']} — {row['airline']}"
    if origin_code and dest_code:
        display += f" ({origin_code} → {dest_code})"
    elif row['origin'] and row['destination']:
        display += f" ({row['origin']} → {row['destination']})"
    flight_options.append(display)

search_selection = st.selectbox(
    "Search or select a flight:",
    options=[""] + flight_options,
    index=0,
    placeholder="Start typing flight number or airline..."
)

flight_number = None
if search_selection:
    flight_number = search_selection.split(" — ")[0].strip()

# ---------------------------
# MAIN CONTENT
# ---------------------------
if flight_number:
    if flight_number in sample_flights:
        details = sample_flights[flight_number]
        airline_name = details["airline"]

        # ✈️ Flight Summary
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

        # ⏰ Countdown to Departure
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

        # 🧳 Airline Information
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

        # 🌍 Simulated Flight Position
        st.subheader("🌍 Current Flight Position (Simulated)")
        lat = random.uniform(-60, 60)
        lon = random.uniform(-150, 150)
        st.map(pd.DataFrame({"latitude": [lat], "longitude": [lon]}))
        st.caption("This position is simulated for demonstration purposes.")
        st.divider()

        # 🌤 Live Weather at Destination (Smarter City Cleanup)
        st.subheader("🌤 Live Weather at Destination")

        raw_city = details["destination"]
        # Remove airport codes and common extra tokens
        city = re.sub(r"\(.*?\)", "", raw_city)  # remove (JFK)
        city = re.sub(r"\b(Intl|International|Airport|Airpt|Aeropuerto|Aeroporto)\b", "", city, flags=re.IGNORECASE)
        city = re.sub(r"\s{2,}", " ", city).strip()

        # Handle cases like “New York JFK”
        tokens = city.split()
        if len(tokens) > 1 and tokens[-1].isupper() and len(tokens[-1]) == 3:
            city = " ".join(tokens[:-1]).strip()

        city = city.replace("-", " ").strip()

        st.caption(f"Fetching live weather for: **{city}**")

        if not city or city.lower() in ["n/a", "-", "unknown"]:
            st.warning("No valid city found for this destination.")
        else:
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
                    st.warning(f"Weather not available for '{city}'.")
            except Exception:
                st.warning("Unable to fetch live weather data.")
    else:
        st.error("❌ Flight not found. Please check your flight number and try again.")
else:
    st.info("Search or select a flight above to view details.")

# ---------------------------
# FOOTER
# ---------------------------
st.divider()
st.caption("Developed as part of a University Project • Prototype v3.6 • © 2025 FlySmart")
