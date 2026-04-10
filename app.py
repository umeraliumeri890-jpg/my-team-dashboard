import streamlit as st
import requests
import pandas as pd
import time
import os

# --- API & Files ---
URL = "http://51.77.216.195/crapi/lamix/viewstats"
TOKEN = "SVdVRTRSQmiGX4FWYJJzgF-Hi4mHX41TglBhWVtieEOEUHhleGFy"
TEAM_FILE = "Numbers_Export.csv"
LOG_FILE = "otp_history_log.csv" # Ye file OTPs yaad rakhegi

st.set_page_config(page_title="Team OTP Pro", layout="centered")

# --- Functions ---
def load_team_data():
    try:
        df = pd.read_csv(TEAM_FILE)
        df = df[df['Status'].str.contains("Allocated:", na=False)].copy()
        df['Owner'] = df['Status'].str.replace("Allocated:", "").str.strip()
        return df
    except: return pd.DataFrame()

def save_otp_to_file(new_entry):
    # Nayi OTP ko file mein save karna taake reset na ho
    df_new = pd.DataFrame([new_entry])
    if not os.path.isfile(LOG_FILE):
        df_new.to_csv(LOG_FILE, index=False)
    else:
        df_new.to_csv(LOG_FILE, mode='a', header=False, index=False)

def load_otp_history():
    if os.path.exists(LOG_FILE):
        try:
            return pd.read_csv(LOG_FILE).to_dict('records')
        except: return []
    return []

# --- UI ---
st.title("🔥 Team Live OTP (No-Reset)")

team_df = load_team_data()
placeholder = st.empty()

if team_df.empty:
    st.error("Team CSV file missing!")
else:
    # Pehle se saved data load karo
    if 'history' not in st.session_state:
        st.session_state.history = load_otp_history()[::-1] # Reverse for latest first

    while True:
        try:
            r = requests.get(URL, params={"token": TOKEN, "records": 20})
            if r.status_code == 200:
                api_data = r.json().get("data", [])
                team_numbers = team_df['Phone Number'].astype(str).tolist()
                
                # Check for new data
                existing_ids = [str(x.get('id','')) for x in st.session_state.history]
                
                for msg in api_data:
                    num = str(msg.get('num'))
                    msg_id = f"{msg.get('dt')}-{num}"
                    
                    if num in team_numbers and msg_id not in existing_ids:
                        row = team_df[team_df['Phone Number'].astype(str) == num].iloc[0]
                        
                        entry = {
                            "id": msg_id,
                            "owner": row['Owner'].upper(),
                            "range": row['Range'],
                            "app": msg.get('cli'),
                            "otp": msg.get('message'),
                            "num": num,
                            "time": msg.get('dt')
                        }
                        # File aur State dono mein save karo
                        save_otp_to_file(entry)
                        st.session_state.history.insert(0, entry)

                # Display Logic
                with placeholder.container():
                    for item in st.session_state.history[:30]: # Top 30 OTPs
                        st.markdown(f"### 👤 {item['owner']}")
                        st.success(f"**OTP: {item['otp']}**")
                        st.info(f"App: {item['app']} | Range: {item['range']}")
                        st.caption(f"Number: {item['num']} | Time: {item['time']}")
                        st.divider()

            time.sleep(10)
            st.rerun()
        except:
            time.sleep(5)
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
        try:
            return pd.read_csv(LOG_FILE).to_dict('records')
        except: return []
    return []

# --- MAIN UI ---
st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>🔥 PINDIZ PRIVATE MONITOR</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px; color: white;'>Powered by <b>Umer Ali</b></p>", unsafe_allow_html=True)
st.markdown("---")

team_df = load_team_data()

if team_df.empty:
    st.error("Numbers_Export.csv nahi mili ya format sahi nahi hai!")
else:
    # Local memory initialize
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

                # Display Cards
                with placeholder.container():
                    if not st.session_state.history:
                        st.info("Searching for Team OTPs... System is Live.")
                    else:
                        for item in st.session_state.history[:40]: # Show last 40
                            st.markdown(f"""
                            <div class="otp-card">
                                <div class="owner-name">👤 {item['owner']}</div>
                                <div style="color: #e6edf3; margin-bottom: 10px;"><b>RANGE:</b> {item['range']}</div>
                                <div class="otp-code">OTP: {item['otp']}</div>
                                <div style="color: #8b949e; margin-top: 10px;">
                                    <b>APP:</b> {item['app']} | <b>NUM:</b> {item['num']}<br>
                                    <small>🕒 {item['time']}</small>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
            
            # Footer always at bottom of the list
            st.markdown("<div class='footer'>© 2026 | Developed with ❤️ by Umer Ali</div>", unsafe_allow_html=True)
            
            time.sleep(10)
            st.rerun()
        except:
            time.sleep(5)
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
                  
