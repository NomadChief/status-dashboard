import json
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Status Dashboard", layout="centered")

# Set up credentials
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_info(st.secrets["GOOGLE_CREDENTIALS"], scopes=scope)
client = gspread.authorize(creds)

# now open your sheet
sheet = client.open_by_key("1j7fEEf6jw8UcXcGlbgnE5BoxoP58wDRWCLr1XQgi-jM").sheet1

# Read values from the sheet
data = sheet.get_all_records()
if not data or 'Index' not in data[0] or 'Value' not in data[0]:
    st.error("Sheet must have 'Index' and 'Value' headers.")
    st.stop()
index_values = {row['Index']: row['Value'] for row in data}


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

# UI logic
st.title("🧠 Status Dashboard")
new_values = {}
for index in index_values:
   st.markdown(f"**{colorize(index_values[index])} {index}**")
col1, col2 = st.columns([3, 1])
with col1:
    value = st.slider(index, 0, 10, index_values[index], key=index)
with col2:
    st.markdown(f"<div style='text-align:right;'>{describe(index, value)}</div>", unsafe_allow_html=True)

    new_values[index] = value

if st.button("💾 Save"):
    for i, (index, val) in enumerate(new_values.items()):
        sheet.update_cell(i + 2, 2, val)
    st.success("Status updated.")



