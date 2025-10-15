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

# ---------------------------
# HELPERS
# ---------------------------
IATA_PATTERN = re.compile(r"\((\w{3})\)")

def extract_airport_code(location: str) -> str:
    m = IATA_PATTERN.search(str(location))
    return m.group(1) if m else ""

# Words that indicate we’ve moved into the airport name (not the city)
AIRPORT_TOKENS = {
    # generic
    "intl", "international", "airport", "airpt", "aeropuerto", "aeroporto",
    "aerodrome", "field", "terminal",
    # common specific names (lowercased)
    "heathrow", "gatwick", "stansted", "luton", "city",
    "jfk", "laguardia", "newark",
    "o'hare", "ohare", "midway", "dulles", "schiphol",
    "charles", "de", "gaulle", "orly",
    "barajas", "el", "prat", "fiumicino", "ciampino",
    "narita", "haneda", "incheon", "changi",
    "zaventem", "songshan", "taoyuan", "suvarnabhumi", "don", "mueang",
    "chhatrapati", "shivaji", "kempegowda", "indira", "gandhi",
    "hartsfield–jackson", "hartsfield-jackson", "hartsfield", "jackson",
    "king", "abdulaziz", "maktoum"
}

def normalize_city(destination: str) -> str:
    """
    Convert strings like:
      'London Heathrow (LHR)' -> 'London'
      'New York JFK' -> 'New York'
      'Dubai Intl (DXB)' -> 'Dubai'
      'Los Angeles LAX' -> 'Los Angeles'
    Always returns a best-effort city name for weather APIs.
    """
    s = str(destination)

    # Remove anything in parentheses, e.g. (LHR)
    s = re.sub(r"\(.*?\)", "", s)

    # Replace hyphens/en-dashes with spaces, collapse spaces
    s = s.replace("–", " ").replace("-", " ")
    s = re.sub(r"\s{2,}", " ", s).strip()

    if not s:
        return ""

    tokens = s.split()

    # If last token looks like an IATA code (3 uppercase letters), drop it
    if tokens and len(tokens[-1]) == 3 and tokens[-1].isupper():
        tokens = tokens[:-1]

    # Build city token-by-token until we hit an airport token
    city_tokens = []
    for t in tokens:
        tl = t.lower()
        if tl in AIRPORT_TOKENS:
            break
        city_tokens.append(t)

    # Fallbacks: if we stripped everything due to tokens, keep the first token(s)
    city = " ".join(city_tokens).strip()
    if not city and tokens:
        # Try first two tokens (handles 'New York', 'Los Angeles', etc.)
        city = " ".join(tokens[:2]).strip()

    return city

# Pre-compute a lookup dict (also stash codes for display)
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
# FLIGHT SEARCH (Cleaner, single-line with IATA codes only in brackets)
# ---------------------------
st.subheader("🔎 Find Your Flight")

flight_options = []
for _, row in flights_df.iterrows():
    o_code = extract_airport_code(row["origin"])
    d_code = extract_airport_code(row["destination"])
    # Only show IATA codes in brackets
    if o_code and d_code:
        display = f"{row['flight_number']} — {row['airline']} ({o_code} → {d_code})"
    else:
        display = f"{row['flight_number']} — {row['airline']}"
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
if flight_number and flight_number in sample_flights:
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

    # 🌤 Live Weather at Destination (Fool-proof city extraction)
    st.subheader("🌤 Live Weather at Destination")

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
st.caption("Developed as part of a University Project • Prototype v3.7 • © 2025 FlySmart")
