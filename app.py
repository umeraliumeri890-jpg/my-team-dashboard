import streamlit as st
import requests
import pandas as pd
import time
import os

# --- CONFIGURATION ---
URL = "http://51.77.216.195/crapi/lamix/viewstats"
TOKEN = "SVdVRTRSQmiGX4FWYJJzgF-Hi4mHX41TglBhWVtieEOEUHhleGFy"
TEAM_FILE = "Numbers_Export.csv"
LOG_FILE = "otp_history_log.csv"

st.set_page_config(page_title="UMER ALI - LIVE OTP", layout="centered")

# --- STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .otp-card {
        border: 2px solid #ff4b4b;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        background-color: #161b22;
    }
    .owner-name { color: #ff4b4b; font-size: 20px; font-weight: bold; }
    .otp-code { color: #00ff00; font-size: 22px; font-weight: bold; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# --- LOGIC ---
def load_team_data():
    if os.path.exists(TEAM_FILE):
        try:
            df = pd.read_csv(TEAM_FILE)
            df = df[df['Status'].str.contains("Allocated:", na=False)].copy()
            df['Owner'] = df['Status'].str.replace("Allocated:", "").str.strip()
            return df
        except: pass
    return pd.DataFrame()

def save_to_log(entry):
    df_new = pd.DataFrame([entry])
    if not os.path.isfile(LOG_FILE):
        df_new.to_csv(LOG_FILE, index=False)
    else:
        df_new.to_csv(LOG_FILE, mode='a', header=False, index=False)

def get_history():
    if os.path.exists(LOG_FILE):
        try: return pd.read_csv(LOG_FILE).to_dict('records')
        except: return []
    return []

# --- UI ---
st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>🔥 PINDIZ PRIVATE MONITOR</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Powered by <b>Umer Ali</b></p>", unsafe_allow_html=True)
st.markdown("---")

team_df = load_team_data()

if team_df.empty:
    st.error("Numbers_Export.csv missing or format error!")
else:
    if 'history' not in st.session_state:
        st.session_state.history = get_history()[::-1]

    placeholder = st.empty()

    while True:
        try:
            r = requests.get(URL, params={"token": TOKEN, "records": 25})
            if r.status_code == 200:
                api_data = r.json().get("data", [])
                team_nums = team_df['Phone Number'].astype(str).tolist()
                existing_ids = [str(x.get('id','')) for x in st.session_state.history]
                
                for msg in api_data:
                    num = str(msg.get('num'))
                    m_id = f"{msg.get('dt')}-{num}"
                    
                    if num in team_nums and m_id not in existing_ids:
                        row = team_df[team_df['Phone Number'].astype(str) == num].iloc[0]
                        entry = {
                            "id": m_id,
                            "owner": row['Owner'].upper(),
                            "range": row['Range'],
                            "app": msg.get('cli'),
                            "otp": msg.get('message'),
                            "num": num,
                            "time": msg.get('dt')
                        }
                        save_to_log(entry)
                        st.session_state.history.insert(0, entry)

                with placeholder.container():
                    if not st.session_state.history:
                        st.info("Searching for OTPs... System Live")
                    else:
                        for item in st.session_state.history[:40]:
                            st.markdown(f"""
                            <div class="otp-card">
                                <div class="owner-name">👤 {item['owner']}</div>
                                <div style="color:white;"><b>RANGE:</b> {item['range']}</div>
                                <div class="otp-code">OTP: {item['otp']}</div>
                                <div style="color:#8b949e; font-size:12px;">
                                    App: {item['app']} | Num: {item['num']} | {item['time']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
            
            time.sleep(10)
            st.rerun()
        except:
            time.sleep(5)
            
