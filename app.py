import streamlit as st
import pandas as pd
import json
import random
from datetime import datetime
import requests
import base64
import re
import os

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
# DEBUG: Check asset files
# ---------------------------
st.markdown("### 🧩 Icon Check (temporary)")
for img in ["plane.png", "luggage.png", "weather.png"]:
    path = os.path.join("assets", img)
    st.write(f"{img}: {'✅ Found' if os.path.exists(path) else '❌ Missing'}")
st.divider()

# ---------------------------
# LOAD DATA
# ---------------------------
with open("airline_info.json", "r") as f:
    airline_data = json.load(f)

flights_df = pd.read_csv("flights.csv")

# ---------------------------
# HELPERS
# ---------------------------
IATA_PATTERN = re.compile(r"\((\w{3})\)")

def extract_airport_code(location: str) -> str:
    m = IATA_PATTERN.search(str(location))
    return m.group(1) if m else ""

AIRPORT_TOKENS = {
    "intl", "international", "airport", "aeropuerto", "aeroporto", "field",
    "heathrow", "gatwick", "jfk", "laguardia", "newark", "dulles", "schiphol",
    "charles", "gaulle", "orly", "barajas", "fiumicino", "ciampino",
    "narita", "haneda", "incheon", "changi", "don", "mueang", "maktoum"
}

def normalize_city(destination: str) -> str:
    s = re.sub(r"\(.*?\)", "", str(destination))
    s = re.sub(r"[-–]", " ", s)
    s = re.sub(r"\s{2,}", " ", s).strip()

    tokens = s.split()
    if tokens and len(tokens[-1]) == 3 and tokens[-1].isupper():
        tokens = tokens[:-1]

    city_tokens = []
    for t in tokens:
        if t.lower() in AIRPORT_TOKENS:
            break
        city_tokens.append(t)

    city = " ".join(city_tokens).strip()
    if not city and tokens:
        city = " ".join(tokens[:2]).strip()
    return city

def header_icon(title, icon_path):
    """Reusable section header with small icon."""
    cols = st.columns([0.08, 0.9])
    with cols[0]:
        if os.path.exists(icon_path):
            st.image(icon_path, width=32, use_container_width=False)
        else:
            st.write("🟦")  # fallback marker if icon missing
    with cols[1]:
        st.subheader(title)

# ---------------------------
# FLIGHT DATA DICTIONARY
# ---------------------------
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
st.title("FlySmart Flight Tracker")
st.caption("Professional flight overview and real-time insights for travelers.")
st.divider()

# ---------------------------
# FLIGHT SEARCH
# ---------------------------
header_icon("Find Your Flight", "assets/plane.png")

flight_options = []
for _, row in flights_df.iterrows():
    o_code = extract_airport_code(row["origin"])
    d_code = extract_airport_code(row["destination"])
    if o_code and d_code:
        display = f"{row['flight_number']} — {row['airline']} ({o_code} → {d_code})"
    else:
        display = f"{row['flight_number']} — {row['airline']}"
    flight_options.append(display)

search_selection = st.selectbox(
    "",
    options=[""] + flight_options,
    index=0,
    placeholder="Search by flight number or airline..."
)

flight_number = search_selection.split(" — ")[0].strip() if search_selection else None

# ---------------------------
# MAIN CONTENT
# ---------------------------
if flight_number and flight_number in sample_flights:
    details = sample_flights[flight_number]
    airline_name = details["airline"]

    # ✈️ Flight Summary
    header_icon("Flight Summary", "assets/plane.png")
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
    header_icon("Time to Departure", "assets/clock.png" if os.path.exists("assets/clock.png") else "assets/plane.png")
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
    header_icon("Airline Information", "assets/luggage.png")
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
    header_icon("Current Flight Position (Simulated)", "assets/plane.png")
    lat = random.uniform(-60, 60)
    lon = random.uniform(-150, 150)
    st.map(pd.DataFrame({"latitude": [lat], "longitude": [lon]}))
    st.caption("This position is simulated for demonstration purposes.")
    st.divider()

    # 🌤 Live Weather at Destination
    header_icon("Live Weather at Destination", "assets/weather.png")
    city = normalize_city(details["destination"])
    st.caption(f"Fetching live weather for: **{city or 'Unknown'}**")

    if not city:
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
    st.info("Search or select a flight above to view details.")

# ---------------------------
# FOOTER
# ---------------------------
st.divider()
st.caption("Developed as part of a University Project • Prototype v3.9 • © 2025 FlySmart")
