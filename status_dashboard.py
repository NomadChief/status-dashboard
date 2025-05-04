import json
import gspread
import streamlit as st
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from streamlit_autorefresh import st_autorefresh
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials


# ----------------------------
# 🛠️ Config and Setup
# ----------------------------

st.set_page_config(page_title="Status Dashboard", layout="centered")
autorefresh_enabled = st.sidebar.checkbox("🔄 Auto-refresh every 2 min", value=True)
if autorefresh_enabled:
    st_autorefresh(interval=120_000, key="refresh_dashboard")

SHEET_ID = "1j7fEEf6jw8UcXcGlbgnE5BoxoP58wDRWCLr1XQgi-jM"
TIMEZONE = ZoneInfo("America/Chicago")
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


# ----------------------------
# 🔐 Authentication and APIs
# ----------------------------

def load_credentials():
    return Credentials.from_service_account_info(
        st.secrets["GOOGLE_CREDENTIALS"], scopes=SCOPES
    )

creds = load_credentials()
client = gspread.authorize(creds)
drive_service = build("drive", "v3", credentials=creds)


# ----------------------------
# 🕒 Timestamp Utility
# ----------------------------

def get_last_modified_str(file_id):
    metadata = drive_service.files().get(fileId=file_id, fields="modifiedTime").execute()
    raw_time = metadata.get("modifiedTime", "")
    dt_utc = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
    dt_cst = dt_utc.astimezone(TIMEZONE)
    delta = datetime.now(TIMEZONE) - dt_cst

    if delta < timedelta(minutes=1):
        time_ago = "(just now)"
    elif delta < timedelta(hours=1):
        time_ago = f"({int(delta.total_seconds() // 60)} min ago)"
    elif delta < timedelta(days=1):
        time_ago = f"({int(delta.total_seconds() // 3600)} hrs ago)"
    else:
        time_ago = f"({delta.days} days ago)"

    return dt_cst.strftime("%A, %b %d %I:%M %p CST") + f" {time_ago}"


# ----------------------------
# 🧠 Sheet Loading & Parsing
# ----------------------------

def load_status_data(sheet):
    records = sheet.get_all_records()
    if not records or 'Index' not in records[0] or 'Value' not in records[0]:
        st.error("Sheet must have 'Index' and 'Value' headers.")
        st.stop()
    return {row['Index']: row['Value'] for row in records}


# ----------------------------
# 🎨 UI Helpers
# ----------------------------

def colorize(value, index):
    if index == "Physical Pain":
        return "🟢" if value <= 2 else "🟡" if value <= 5 else "🟠" if value <= 8 else "🔴"
    elif index == "Mood":
        return "🟣" if value <= 1 else "🔵" if value <= 3 else "🟢" if value <= 5 else "🟡" if value <= 7 else "🟠" if value <= 9 else "🔴"
    else:
        return "🔴" if value <= 2 else "🟡" if value <= 5 else "🟢" if value <= 8 else "🔵"

def describe(index, value):
    descriptions = {
        "Mood": [
            "Deepest depression", "Very low", "Low", "Subdued", "Flat",
            "Neutral", "Slightly elevated", "High energy", "Very high", "Hypomania", "Full mania"
        ],
        "Autistic Battery": [
            "Non-verbal, withdrawn", "Exhausted", "Overwhelmed", "Wary", "Tired",
            "Functional", "Coping", "Socially available", "Engaged", "Fully charged", "Charismatic"
        ],
        "Emotional State": [
            "Emotionally unsafe", "Raw", "Vulnerable", "Tense", "Guarded",
            "Neutral", "Warm", "Connected", "Engaged", "Open", "Radiant"
        ],
        "Physical Pain": [
            "No pain", "Minor stubbed toe", "Mild chronic", "Nagging", "Disruptive",
            "Severe", "Drastic limitations", "Barely functioning", "Crippling", "Unbearable", "Max pain"
        ]
    }
    return descriptions.get(index, ["Unknown"] * 11)[value]


# ----------------------------
# 📊 UI Rendering
# ----------------------------

def render_status_summary(data):
    st.markdown("### Current Status")
    for index, val in data.items():
        emoji = colorize(val, index)
        desc = describe(index, val)
        st.markdown(f"<div style='font-size:0.9em; padding:2px 0;'><b>{emoji} {index}:</b> {desc}</div>", unsafe_allow_html=True)

def render_adjustment_controls(data):
    st.markdown("### Adjust Values")
    updated = {}
    for index, default_val in data.items():
        st.markdown(f"**{index}**")
        val = st.slider(index, 0, 10, default_val, key=index)
        updated[index] = val
        st.markdown(f"<span style='font-size:0.8em;'>{colorize(val, index)} {describe(index, val)}</span>", unsafe_allow_html=True)
        st.markdown("<hr style='margin:4px 0;'>", unsafe_allow_html=True)
    return updated


# ----------------------------
# 🚀 Main Logic
# ----------------------------

st.title("🧠 Status")
st.caption(f"📱 Summary below (Last updated: {get_last_modified_str(SHEET_ID)})")

sheet = client.open_by_key(SHEET_ID).sheet1
index_values = load_status_data(sheet)

render_status_summary(index_values)
st.markdown("---")
new_values = render_adjustment_controls(index_values)

st.markdown("<br>", unsafe_allow_html=True)
if st.button("💾 Save", use_container_width=True):
    try:
        for i, (index, val) in enumerate(new_values.items()):
            sheet.update_cell(i + 2, 2, val)
        
        #Append History
        history_sheet = client.open_by_key(SHEET_ID).worksheet("History")
        now_str = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        history_row = [now_str] + [new_values.get(field, "") for field in ["Mood", "Autistic Battery", "Emotional State", "Physical Pain"]]
        history_sheet.append_row(history_row)
        
        st.success("Status updated.")
    except Exception as e:
        st.error(f"Error updating sheet: {e}")
