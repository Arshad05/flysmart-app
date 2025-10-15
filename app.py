# ---------------------------
# FLIGHT SEARCH (Smart Unified Dropdown)
# ---------------------------
st.subheader("🔎 Find Your Flight")

# Build list of all flights formatted for easy searching
flight_options = [
    f"{row['flight_number']} — {row['airline']} ({row['origin']} → {row['destination']})"
    for _, row in flights_df.iterrows()
]

# User types or picks from dropdown (filtered automatically)
search_selection = st.selectbox(
    "Search or select a flight:",
    options=[""] + flight_options,  # blank option at start
    index=0,
    placeholder="Start typing flight number or airline..."
)

# Extract flight number if one selected
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

        # ⏰ Countdown
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

        # 🧳 Airline Info
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

        # 🌤 Weather
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
    st.info("Select or search for your flight above to view details.")
