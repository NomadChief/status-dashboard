import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Set up credentials
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

import json
creds_dict = st.secrets["GOOGLE_CREDENTIALS"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("vox_status_dashboard").sheet1

# Read values from the sheet
data = sheet.get_all_records()
index_values = {row['Index']: row['Value'] for row in data}

# UI logic
st.title("🧠 Vox's Status Dashboard")
new_values = {}
for index in index_values:
    st.subheader(index)
    value = st.slider(index, 0, 10, index_values[index])
    new_values[index] = value

if st.button("💾 Save"):
    for i, (index, val) in enumerate(new_values.items()):
        sheet.update_cell(i + 2, 2, val)
    st.success("Status updated.")

# Helper function
def describe(index, value):
    mood_desc = [
        "Deepest depression", "Very low", "Low", "Subdued", "Flat",
        "Neutral", "Slightly elevated", "High energy", "Very high", "Hypomania", "Full mania"
    ]
    battery_desc = [
        "Non-verbal, withdrawn", "Exhausted", "Overwhelmed", "Wary", "Tired",
        "Functional", "Coping", "Socially available", "Engaged", "Fully charged", "Charismatic"
    ]
    emotion_desc = [
        "Emotionally unsafe", "Raw", "Vulnerable", "Tense", "Guarded",
        "Neutral", "Warm", "Connected", "Engaged", "Open", "Radiant"
    ]
    pain_desc = [
        "No pain", "Minor stubbed toe", "Mild chronic", "Nagging", "Disruptive",
        "Severe", "Drastic limitations", "Barely functioning", "Crippling", "Unbearable", "Max pain"
    ]

    all_desc = {
        "Mood": mood_desc,
        "Autistic Battery": battery_desc,
        "Emotional State": emotion_desc,
        "Physical Pain": pain_desc
    }

    return all_desc[index][value]

# Color scale
def colorize(value):
    if value <= 2:
        return "🔴"
    elif value <= 5:
        return "🟡"
    elif value <= 8:
        return "🟢"
    else:
        return "🔵"

# Sliders and outputs
st.subheader("🔷 Mood Status")
mood = st.slider("Mood Status (0=Depressed, 10=Mania)", 0, 10, 5)
st.write(f"{colorize(mood)} **{describe('Mood', mood)}**")

st.subheader("🔷 Autistic Battery")
battery = st.slider("Autistic Battery (0=Shutdown, 10=Fully Engaged)", 0, 10, 5)
st.write(f"{colorize(battery)} **{describe('Autistic Battery', battery)}**")

st.subheader("🔷 Emotional State")
emotion = st.slider("Emotional State (0=Raw, 10=Safe/Engaged)", 0, 10, 5)
st.write(f"{colorize(emotion)} **{describe('Emotional State', emotion)}**")

st.subheader("🔷 Physical Pain")
pain = st.slider("Physical Pain (0=None, 10=Max)", 0, 10, 3)
st.write(f"{colorize(pain)} **{describe('Physical Pain', pain)}**")

st.markdown("---")
st.caption("🔁 Adjust any time. This dashboard updates in real time.")

