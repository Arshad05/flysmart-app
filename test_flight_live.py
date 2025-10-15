import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
from datetime import datetime
import math

# ---------------------------
# APP CONFIG
# ---------------------------
st.set_page_config(
    page_title="FlySmart Live Test",
    page_icon="✈️",
    layout="centered"
)

st.title("✈️ FlySmart (Live Flight Data Test)")
st.caption("Prototype demo — now with live flight search and better error handling.")
st.divider()

# ---------------------------
# 1️⃣ FETCH REAL FLIGHT DATA
# ---------------------------
st.subheader("🛰️ Live Flights from OpenSky Network")

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

        # Clean and filter
        df = df.dropna(subset=["latitude", "longitude"])
        df["callsign"] = df["callsign"].fillna("Unknown").str.strip()
        df = df[df["callsign"] != "Unknown"]

        st.success(f"✅ Loaded {len(df)} active flights worldwide.")

        # ---------------------------
        # 2️⃣ SEARCH FLIGHT
        # ---------------------------
        st.subheader("🔎 Search for a Specific Flight")
        search_query = st.text_input("Enter flight number or callsign (e.g., BAW123, UAE77):").strip().upper()

        if search_query:
            match = df[df["callsign"].str.contains(search_query, case=False, na=False)]
            if not match.empty:
                st.success(f"✅ Found {len(match)} matching flight(s).")

                # Safely extract first flight info
                first_flight = match.iloc[0]

                def safe_value(value, suffix=""):
                    if pd.isna(value) or value is None:
                        return "N/A"
                    if isinstance(value, (int, float)):
                        return f"{round(value)}{suffix}"
                    return str(value)

                st.markdown(
                    f"""
                    **Callsign:** {first_flight['callsign']}  
                    **Country:** {first_flight['origin_country']}  
                    **Altitude:** {safe_value(first_flight['geo_altitude'], ' m')}  
                    **Velocity:** {safe_value(first_flight['velocity'], ' m/s')}  
                    **Position:** ({safe_value(first_flight['latitude'])}, {safe_value(first_flight['longitude'])})
                    """
                )

                # Center map on that flight
                view_state = pdk.ViewState(
                    latitude=first_flight["latitude"],
                    longitude=first_flight["longitude"],
                    zoom=5,
                    pitch=0,
                )

                layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=match,
                    get_position='[longitude, latitude]',
                    get_color='[0, 255, 100, 200]',
                    get_radius=80000,
                    pickable=True,
                )

                st.pydeck_chart(
                    pdk.Deck(
                        map_style="mapbox://styles/mapbox/dark-v10",
                        initial_view_state=view_state,
                        layers=[layer],
                        tooltip={"text": "✈️ {callsign}\nCountry: {origin_country}"}
                    )
                )

            else:
                st.warning("❌ No flights found with that callsign. Showing all flights below.")

        # ---------------------------
        # 3️⃣ GLOBAL MAP (fallback)
        # ---------------------------
        if not search_query or match.empty:
            st.subheader("🌍 All Live Flights")
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position='[longitude, latitude]',
                get_color='[255, 0, 0, 160]',
                get_radius=50000,
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
        st.error("⚠️ No flight data available right now.")

except Exception as e:
    st.error(f"Error fetching data: {e}")

# ---------------------------
# FOOTER
# ---------------------------
st.divider()
st.caption(f"🧭 Prototype v3.2 • Run completed at {datetime.utcnow().strftime('%H:%M:%S UTC')} • Data: OpenSky Network")
