# ---------------------------
# FLIGHT SEARCH (Improved)
# ---------------------------
st.subheader("🔎 Find Your Flight")

# Initialize variable
flight_number = None

# Search input
search_query = st.text_input(
    "Enter your flight number or airline (e.g. BA102 or Emirates):",
    placeholder="Start typing to search..."
).strip().upper()

# Filter logic for top 5 results
filtered_flights = flights_df[
    flights_df["flight_number"].str.contains(search_query, case=False, na=False) |
    flights_df["airline"].str.contains(search_query, case=False, na=False)
] if search_query else pd.DataFrame()

if not search_query:
    st.info("Type a flight number or airline to view details.")
elif filtered_flights.empty:
    st.warning("❌ No flights found. Try another query.")
else:
    top_matches = filtered_flights.head(5)
    flight_number = st.selectbox(
        "Select your flight from the matches below:",
        options=top_matches["flight_number"].tolist(),
        format_func=lambda x: f"{x} — {sample_flights[x]['airline']} ({sample_flights[x]['origin']} → {sample_flights[x]['destination']})",
        index=0,
    )
    st.success(f"✅ Showing details for flight **{flight_number}**")

# ---------------------------
# MAIN CONTENT (cleaned up)
# ---------------------------
if flight_number:  # only runs if valid flight selected
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
    st.info("Type a flight number above to begin tracking.")
