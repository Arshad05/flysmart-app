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
# BACKGROUND IMAGE (optional)
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
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        pass

set_background("background.jpg")

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

def section_header(title, icon=None):
    """Header with optional small icon."""
    cols = st.columns([0.08, 0.92])
    with cols[0]:
        if icon and os.path.exists(icon):
            st.image(icon, width=30)
    with cols[1]:
        st.subheader(title)

def card(content):
    """Soft white translucent card for section grouping."""
    st.markdown(
        f"""
        <div style="background-color: rgba(255,255,255,0.8);
                    padding: 1rem 1.5rem;
                    border-radius: 12px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                    margin-bottom: 1.2rem;">
            {content}
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------
# DATA DICTIONARY
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
cols = st.columns([0.15, 0.85])
with cols[0]:
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=70)
with cols[1]:
    st.markdown("<h1 style='margin-bottom:0;'>FlySmart Flight Tracker</h1>", unsafe_allow_html=True)
    st.caption("Track your flight with clarity and confidence.")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------
# STYLING FOR SEARCH
# ---------------------------
st.markdown(
    """
    <style>
    div[data-testid="stSelectbox"] {
        text-align: center;
        width: 70%;
        margin-left: auto;
        margin-right: auto;
        padding: 0.8rem 0;
    }
    label {
        display: flex;
        justify-content: center;
        font-size: 1.1rem;
        font-weight: 600;
        color: #333;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# FLIGHT SEARCH
# ---------------------------
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
    "Find Your Flight",
    options=[""] + flight_options,
    index=0,
    placeholder="Search by flight number or airline..."
)

flight_number = search_selection.split(" — ")[0].strip() if search_selection else None
st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------
# MAIN CONTENT
# ---------------------------
if flight_number and flight_number in sample_flights:
    details = sample_flights[flight_number]
    airline_name = details["airline"]

    # ✈️ FLIGHT SUMMARY
    status_color = {
        "On Time": "green",
        "Boarding": "orange",
        "Delayed": "red",
        "Cancelled": "gray"
    }.get(details["status"], "blue")

    card(f"""
    <h3>Flight Summary</h3>
    <b>Flight:</b> {flight_number} — {airline_name}<br>
    <b>Route:</b> {details['origin']} → {details['destination']}<br>
    <b>Departure:</b> {details['departure']}<br>
    <b>Status:</b> <span style="color:{status_color}">{details['status']}</span>
    """)

    # ⏰ TIME TO DEPARTURE
    dep_time = datetime.strptime(details["departure"], "%Y-%m-%d %H:%M")
    remaining = dep_time - datetime.now()
    with st.container():
        section_header("Time to Departure", "assets/departures.png")
        if remaining.total_seconds() > 0:
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes = remainder // 60
            st.info(f"{hours} hours and {minutes} minutes remaining until departure.")
            st.progress(min((hours / 12), 1))  # simple progress bar toward departure
        else:
            st.warning("This flight has already departed or is currently in progress.")

    # 🌍 FLIGHT MAP
    with st.container():
        st.subheader("Current Flight Position (Simulated)")
        lat = random.uniform(-60, 60)
        lon = random.uniform(-150, 150)
        st.map(pd.DataFrame({"latitude": [lat], "longitude": [lon]}))
        st.caption("This position is simulated for demonstration purposes.")

    # 🧳 AIRLINE INFORMATION
    with st.container():
        section_header("Airline Information", "assets/luggage.png")
        if airline_name in airline_data:
            info = airline_data[airline_name]
            card(f"""
            - **Check-in:** {info['check_in']}  
            - **Baggage Drop:** {info['baggage_drop']}  
            - **Boarding:** {info['boarding']}  
            [Visit {airline_name} Website]({info['contact']})
            """)
        else:
            st.info("No policy data available for this airline.")

    # 🌤 LIVE WEATHER
    with st.container():
        section_header("Live Weather at Destination", "assets/weather.png")
        city = normalize_city(details["destination"])
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
                    # Add weather emoji
                    if "rain" in desc.lower():
                        emoji = "🌧️"
                    elif "cloud" in desc.lower():
                        emoji = "☁️"
                    elif "clear" in desc.lower():
                        emoji = "☀️"
                    else:
                        emoji = "🌤️"
                    cols = st.columns([1, 4])
                    with cols[0]:
                        st.image(f"http://openweathermap.org/img/wn/{icon}.png", width=64)
                    with cols[1]:
                        st.success(f"{emoji} Weather in {city}: **{temp}°C**, {desc}")
                else:
                    st.warning(f"Weather not available for '{city}'.")
            except Exception:
                st.warning("Unable to fetch live weather data.")
else:
    st.info("Search or select a flight above to view details.")

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("---")
st.caption("Developed as part of a University Project • Prototype v4.4 • © 2025 FlySmart")
