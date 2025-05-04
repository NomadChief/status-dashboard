import json
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials



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
st.set_page_config(page_title="Status Dashboard", layout="centered")
st.title("🧠 Vox Status")

st.caption("📱 Summary below. Scroll to adjust and save.")

# Section 1: Compact Summary
st.markdown("### Current Status")

for index in index_values:
    val = index_values[index]
    emoji = colorize(val)
    desc = describe(index, val)
    st.markdown(
        f"<div style='font-size:0.9em; padding:2px 0;'><b>{emoji} {index}:</b> {desc}</div>",
        unsafe_allow_html=True,
    )

# Divider
st.markdown("---")

# Section 2: Adjustment Controls
st.markdown("### Adjust Values")
new_values = {}

for index in index_values:
    st.markdown(f"**{index}**")
    val = st.slider(index, 0, 10, index_values[index], key=index)
    new_values[index] = val
    st.markdown(
        f"<span style='font-size:0.8em;'>{colorize(val)} {describe(index, val)}</span>",
        unsafe_allow_html=True,
    )
    st.markdown("<hr style='margin:4px 0;'>", unsafe_allow_html=True)

# Save Button
st.markdown("<br>", unsafe_allow_html=True)
if st.button("💾 Save", use_container_width=True):
    try:
        for i, (index, val) in enumerate(new_values.items()):
            sheet.update_cell(i + 2, 2, val)
        st.success("Status updated.")
    except Exception as e:
        st.error(f"Error updating sheet: {e}")



