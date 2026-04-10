import streamlit as st
import requests
import pandas as pd
import time

# --- API Details ---
URL = "http://51.77.216.195/crapi/lamix/viewstats"
TOKEN = "SVdVRTRSQmiGX4FWYJJzgF-Hi4mHX41TglBhWVtieEOEUHhleGFy"
CSV_FILE = "Numbers_Export.csv"

st.set_page_config(page_title="Team OTP Live", layout="centered")

# Custom UI Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stAlert { border-radius: 10px; border: 1px solid #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

def load_team_data():
    try:
        df = pd.read_csv(CSV_FILE)
        df = df[df['Status'].str.contains("Allocated:", na=False)].copy()
        df['Owner'] = df['Status'].str.replace("Allocated:", "").str.strip()
        return df
    except: return pd.DataFrame()

st.title("🚀 Team Live OTP Dashboard")
st.write("Live data refresh every 10 seconds")

team_df = load_team_data()
placeholder = st.empty()

if team_df.empty:
    st.error("CSV file format error or file missing!")
else:
    while True:
        try:
            r = requests.get(URL, params={"token": TOKEN, "records": 30})
            if r.status_code == 200:
                api_data = r.json().get("data", [])
                team_numbers = team_df['Phone Number'].astype(str).tolist()
                
                with placeholder.container():
                    found = False
                    for msg in api_data:
                        num = str(msg.get('num'))
                        if num in team_numbers:
                            found = True
                            row = team_df[team_df['Phone Number'].astype(str) == num].iloc[0]
                            
                            # Team Member Card
                            with st.container():
                                st.markdown(f"### 👤 {row['Owner'].upper()}")
                                st.code(f"OTP: {msg.get('message')}", language="text")
                                st.info(f"App: {msg.get('cli')} | Range: {row['Range']}")
                                st.caption(f"Number: {num} | Time: {msg.get('dt')}")
                                st.divider()
                    
                    if not found:
                        st.info("Searching for team OTPs... No live data found yet.")
            
            time.sleep(10)
            st.rerun()
        except:
            time.sleep(5)
            
