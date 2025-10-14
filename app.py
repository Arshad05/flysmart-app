import streamlit as st
import pandas as pd
import json
import random

# ---------------------------
# APP CONFIG
# ---------------------------
st.set_page_config(
    page_title="FlySmart | Airline Companion",
    page_icon="✈️",
    layout="wide"
)

# ---------------------------
# LOAD AIRLINE DATA
# ---------------------------
with open("airline_info.json", "r") as f:
    airline_data = json.load(f)

# ---------------------------
# SIDEBAR SETTINGS
# ---------------------------
st.sidebar.header("⚙️ Settings & Airline Selection")

# NOTE: Streamlit can't switch themes programmatically at runtime.
# We provide a working "High-contrast (dark) mode" that injects CSS.
dark_mode = st.sidebar.toggle("High-contrast (dark) mode)", value=False)

# Airline selection
selected_airline = st.sidebar.selectbox("Choose an airline:", list(airline_data.keys()))
st.sidebar.info("Select an airline to view details and simulated live flights.")

# Apply high-contrast CSS if toggled
if dark_mode:
    st.markdown(
        """
        <style>
            /* App background & text */
            [data-testid="stAppViewContainer"] {
                background-color: #0E1117;
                color: #E6E6E6;
            }
            [data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
            /* Markdown/text colours */
            .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, span {
                color: #E6E6E6 !important;
            }
            /* Dataframe headers and cells */
            .stDataFrame, .stTable {
                color: #E6E6E6 !important;
            }
            /* Tabs underline and label colour */
            button[role="tab"] > div > p {
                color: #E6E6E6 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------
# HEADER
# ---------------------------
st.title("✈️ FlySmart: Your Smart Airline Companion")
st.caption("Helping travellers make informed, stress-free flight decisions.")
st.markdown("---")

# ---------------------------
# TABS LAYOUT
# ---------------------------
tab1, tab2 = st.tabs(["📋 Airline Information", "🌍 Live Flight Map"])

# ---------------------------
# TAB 1: AIRLINE INFO
# ---------------------------
with tab1:
    st.subheader(f"🛫 {selected_airline}")
