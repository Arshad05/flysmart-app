
import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
from datetime import datetime

# ---------------------------
# APP CONFIG
# ---------------------------
st.set_page_config(
    page_title="FlySmart Live Test",
    page_icon="✈️",
    layout="centered"
)

st.title("✈️ FlySmart (Live Data Test)")
st.caption("Prototype test for Assessment 002 — exploring real-time flight data & paths.")
st.divider()

# ---------------------------
# 1️⃣ FETCH REAL FLIGHT DATA (OpenSky Network API)
# ---------------------------
st.subheader("🛰️ Live Flights from OpenSky API")

try:
    url = "https://opensky-network.org/api/states/all"
    response = requests.get(url, timeout=10)
    data = response.json()

    if "states" in data:
        flights = data["states"]
        df = pd.DataFrame(flights, columns=[
            "icao24", "callsign", "origin_country", "time_position",
            "last_contact", "longitude", "latitude", "baro_altitude",
            "on_ground", "velocity", "heading", "vertical_rate",
            "sensors", "geo_altitude", "squawk", "spi", "position_source"
        ])

        # Drop flights without position data
        df = df.dropna(subset=["latitude", "longitude"])

        # Clean up callsigns
        df["callsign"] = df["callsign"].fillna("Unknown").str.strip()

        st.success(f"✅ Loaded {len(df)} live flights worldwide.")
        st.dataframe(df[["callsign", "origin_country", "latitude", "longitude"]].head(10))

        # ---------------------------
        # 2️⃣ VISUALIZE FLIGHTS ON MAP
        # ---------------------------
        st.subheader("🌍 Live Global Flight Positions")

        # Map using PyDeck ScatterplotLayer
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position='[longitude, latitude]',
            get_color='[255, 0, 0, 160]',
            get_radius=60000,
            pickable=True,
        )

        view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1.5)
        st.pydeck_chart(
            pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v9",
                initial_view_state=view_state,
                layers=[layer],
                tooltip={"text": "✈️ {callsign}\nCountry: {origin_country}"}
            )
        )

    else:
        st.error("⚠️ No flight data available from OpenSky right now.")

except Exception as e:
    st.error(f"Error fetching data: {e}")

st.divider()

# ---------------------------
# 3️⃣ FLIGHT PATH TEST (Example Route)
# ---------------------------
st.subheader("🛫 Sample Route Path (London → Dubai)")

# Example coordinates
origin = {"city": "London", "lat": 51.4700, "lon": -0.4543}  # Heathrow
destination = {"city": "Dubai", "lat": 25.2532, "lon": 55.3657}  # DXB

path_df = pd.DataFrame([
    {"lon": origin["lon"], "lat": origin["lat"], "city": origin["city"]},
    {"lon": destination["lon"], "lat": destination["lat"], "city": destination["city"]}
])

# Line Layer for the route
line_layer = pdk.Layer(
    "LineLayer",
    data=path_df,
    get_source_position='[lon, lat]',
    get_target_position='[lon, lat]',
    get_color='[0, 150, 255, 200]',
    get_width=4,
)

# Marker Layer for airports
airport_layer = pdk.Layer(
    "ScatterplotLayer",
    data=path_df,
    get_position='[lon, lat]',
    get_color='[0, 255, 100, 255]',
    get_radius=80000,
    pickable=True,
)

# Combine route + markers
view_state = pdk.ViewState(latitude=35, longitude=20, zoom=2)
st.pydeck_chart(
    pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v10",
        initial_view_state=view_state,
        layers=[line_layer, airport_layer],
        tooltip={"text": "{city}"}
    )
)

st.caption("🧭 Example visualization of a flight path between London and Dubai.")
st.divider()

# ---------------------------
# 4️⃣ SUMMARY
# ---------------------------
st.info("✅ This sandbox demonstrates live flight data and a sample route path. Not part of Assessment 001.")
st.caption(f"Run completed at {datetime.utcnow().strftime('%H:%M:%S UTC')} • OpenSky API test mode")
