import streamlit as st
import pandas as pd
import hashlib
import sqlite3
import random
import pyotp
import qrcode
import os
import json
import time
from datetime import datetime
from math import radians, sin, cos, asin, sqrt

# ================= 1. CONFIGURATION & STATE INIT =================
st.set_page_config(
    page_title="JeevSetu | Bridging Lives",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Session State Initialization ---
if "page" not in st.session_state: st.session_state.page = "home"
if "history" not in st.session_state: st.session_state.history = [] 
if "user" not in st.session_state: st.session_state.user = None
if "guest_mode" not in st.session_state: st.session_state.guest_mode = False
if "auth_role" not in st.session_state: st.session_state.auth_role = None
if "logs" not in st.session_state: st.session_state.logs = [] 

# ================= 2. ENHANCED STYLING (CSS) =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* ANIMATED BACKGROUND */
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    .stApp {
        background: linear-gradient(-45deg, #fff1f2, #fdf2f8, #f0f9ff, #ffffff);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #1e293b;
    }

    /* GLOBAL RESETS */
    h1, h2, h3, h4, h5, h6 { font-weight: 800 !important; color: #0f172a; letter-spacing: -0.5px; }
    p, div, label { color: #475569; }
    
    /* HIDE DEFAULT STREAMLIT ELEMENTS */
    #MainMenu, footer, header {visibility: hidden;}
    div[data-testid="stToolbar"] {visibility: hidden;}
    div[data-testid="stDecoration"] {display: none;}
    
    /* REDUCE TOP PADDING FOR HEADER */
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }

    /* ================= HEADER STYLES ================= */
    .custom-header {
        position: fixed;
        top: 0; left: 0; right: 0;
        height: 70px;
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(226, 232, 240, 0.6);
        z-index: 99999;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 40px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    }
    .header-logo {
        font-size: 1.5rem;
        font-weight: 800;
        color: #e11d48;
        display: flex; align-items: center; gap: 10px;
    }
    .header-right {
        display: flex; align-items: center; gap: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        color: #64748b;
    }

    /* ================= FOOTER STYLES ================= */
    .custom-footer {
        margin-top: 50px;
        padding: 40px 0;
        background: #0f172a;
        color: #94a3b8;
        border-top: 1px solid #1e293b;
        text-align: center;
        border-radius: 20px 20px 0 0;
    }
    .footer-links {
        display: flex; justify-content: center; gap: 30px;
        margin-bottom: 20px;
        font-size: 0.9rem;
    }
    .footer-links a { text-decoration: none; color: #cbd5e1; transition: 0.3s; }
    .footer-links a:hover { color: #e11d48; }
    .footer-copy { font-size: 0.8rem; opacity: 0.6; }

    /* ================= COMPONENT STYLES ================= */
    
    /* CARDS */
    .feature-card {
        background: rgba(255, 255, 255, 0.7);
        padding: 30px; 
        border-radius: 24px;
        box-shadow: 0 10px 30px -5px rgba(0,0,0,0.05);
        text-align: center; 
        margin-bottom: 20px; 
        border: 1px solid rgba(255, 255, 255, 0.8);
        transition: all 0.3s ease;
    }
    .feature-card:hover { 
        transform: translateY(-8px); 
        box-shadow: 0 20px 50px -12px rgba(225, 29, 72, 0.15);
        border-color: #fecaca;
        background: white;
    }
    .card-img { 
        width: 100%; height: 160px; object-fit: cover; 
        border-radius: 16px; margin-bottom: 20px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    /* --- FIXED INPUT & DROPDOWN VISIBILITY (CRITICAL FIX) --- */
    
    /* 1. Force Text Color in Input Boxes */
    input[type="text"], input[type="password"], input[type="number"], .stTextInput input {
        color: #1e293b !important;
        background-color: #ffffff !important;
        -webkit-text-fill-color: #1e293b !important; /* Forces color in Webkit browsers */
        caret-color: #e11d48 !important; /* Pink cursor */
    }

    /* 2. Force Text Color in Select Box (The box you see before clicking) */
    .stSelectbox div[data-baseweb="select"] div {
        color: #1e293b !important;
        -webkit-text-fill-color: #1e293b !important;
    }

    /* 3. Force Dropdown Menu Items (The list that pops up) */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #ffffff !important;
    }
    li[role="option"] {
        color: #1e293b !important;
        background-color: #ffffff !important;
    }
    
    /* 4. Highlighted/Selected Option in Menu */
    li[role="option"][aria-selected="true"] {
        background-color: #fff1f2 !important;
        color: #e11d48 !important;
        font-weight: bold !important;
    }

    /* 5. General Input Container Styling */
    .stTextInput div[data-baseweb="base-input"], .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
    }

    /* 6. Placeholders and Labels */
    ::placeholder { color: #94a3b8 !important; opacity: 1; }
    .stTextInput label, .stSelectbox label { color: #475569 !important; font-weight: 600; }

    /* BUTTONS */
    div.stButton > button { 
        width: 100%; border-radius: 10px; font-weight: 600; 
        padding: 0.6rem 1.2rem; transition: all 0.2s ease; border: none;
    }
    div.stButton > button[kind="primary"] { 
        background: linear-gradient(135deg, #e11d48 0%, #be123c 100%); 
        color: white; 
        box-shadow: 0 4px 15px rgba(225, 29, 72, 0.3);
    }
    div.stButton > button[kind="primary"]:hover { 
        transform: scale(1.02); box-shadow: 0 6px 20px rgba(225, 29, 72, 0.4);
    }
    div.stButton > button[kind="secondary"] { 
        background: white; border: 1px solid #cbd5e1; color: #334155; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    div.stButton > button[kind="secondary"]:hover {
        background: #f8fafc; border-color: #94a3b8;
    }
    
    /* SOS & TABS */
    .sos-header {
        background: #fef2f2; border-left: 6px solid #ef4444; 
        padding: 20px; border-radius: 12px; margin-bottom: 25px; color: #991b1b;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent; border-radius: 8px;
        color: #64748b; font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #fff1f2 !important; color: #e11d48 !important;
    }
</style>
""", unsafe_allow_html=True)

# ================= 3. UTILITIES & DB =================

class SecurityService:
    @staticmethod
    def hash_password(password, salt=None):
        if not salt: salt = os.urandom(16).hex()
        return hashlib.sha256((salt + password).encode()).hexdigest(), salt

class DatabaseService:
    DB_NAME = "jeevsetu_v9_ui.db" 
    def __init__(self): self._init_tables()
    def _get_conn(self): return sqlite3.connect(self.DB_NAME)
    def _init_tables(self):
        conn = self._get_conn(); c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY, password_hash TEXT, salt TEXT, name TEXT, role TEXT, 
            age INTEGER, blood TEXT, totp_secret TEXT, reg_no TEXT, area TEXT, 
            created_at TEXT, weight INTEGER, medical_history TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS donors (
            id TEXT PRIMARY KEY, hospital TEXT, organ TEXT, blood_type TEXT, 
            lat REAL, lon REAL, hla_json TEXT, contact TEXT, harvest_time TEXT
        )''')
        
        c.execute("SELECT count(*) FROM donors")
        if c.fetchone()[0] == 0:
            seed_data = [
                ('D-101', 'Apollo Hospital', 'Kidney', 'A+', 28.6139, 77.2090, json.dumps({"A": [2], "B": [7], "DR": [4]}), '9876543210', datetime.now().isoformat()),
                ('D-102', 'Max Healthcare', 'Liver', 'O-', 28.5355, 77.3910, json.dumps({"A": [1], "B": [8], "DR": [7]}), '8876543210', datetime.now().isoformat()),
                ('D-103', 'Fortis Mumbai', 'Heart', 'B+', 19.0760, 72.8777, json.dumps({"A": [3], "B": [44], "DR": [7]}), '7776543210', datetime.now().isoformat()),
                ('D-104', 'AIIMS Delhi', 'Lungs', 'AB+', 28.5659, 77.2111, json.dumps({"A": [2], "B": [12]}), '9998887776', datetime.now().isoformat()),
                ('D-105', 'Narayana Health', 'Kidney', 'O+', 12.9716, 77.5946, json.dumps({"A": [5], "B": [9]}), '8887776665', datetime.now().isoformat())
            ]
            c.executemany("INSERT INTO donors VALUES (?,?,?,?,?,?,?,?,?)", seed_data)
            conn.commit()
        conn.close()

    def execute(self, query, params=(), fetch_one=False, fetch_all=False):
        conn = self._get_conn(); c = conn.cursor()
        try:
            c.execute(query, params)
            if fetch_one: return c.fetchone()
            if fetch_all: return c.fetchall()
            conn.commit()
        except Exception as e: st.error(f"DB Error: {e}")
        finally: conn.close()

class MLService:
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        return R * 2 * asin(sqrt(a))

    @staticmethod
    def calculate_compatibility(donor_row, patient_dict):
        d_blood = donor_row[3]
        if d_blood != 'O-' and d_blood != patient_dict['blood_type']:
            if d_blood != patient_dict['blood_type']: return 0, 0 
        
        try:
            d_hla = json.loads(donor_row[6])
            p_hla = patient_dict['hla']
            matches = 0
            matches += len(set(d_hla.get('A',[])).intersection(p_hla.get('A',[])))
            matches += len(set(d_hla.get('B',[])).intersection(p_hla.get('B',[])))
            hla_score = (matches / 6) * 60
        except: hla_score = 10 
            
        dist = MLService.haversine(patient_dict['lat'], patient_dict['lon'], donor_row[4], donor_row[5])
        if dist > 3000: return 0, dist
        
        dist_score = max(0, 40 * (1 - (dist / 3000)))
        return min(round(hla_score + dist_score, 1), 100), int(dist)

db = DatabaseService()
CITIES = {"New Delhi": (28.6139, 77.2090), "Mumbai": (19.0760, 72.8777), "Pune": (18.5204, 73.8567), "Bangalore": (12.9716, 77.5946)}
ORGAN_LIMITS = {"Heart": 4, "Lungs": 6, "Liver": 12, "Kidney": 36, "Pancreas": 12}

# ================= 4. NAVIGATION & UI COMPONENTS =================

def navigate(target_page):
    if st.session_state.page != target_page:
        st.session_state.history.append(st.session_state.page)
    st.session_state.page = target_page
    st.rerun()

def go_back():
    if st.session_state.history:
        previous_page = st.session_state.history.pop()
        st.session_state.page = previous_page
        st.rerun()
    else:
        st.session_state.page = "home"
        st.rerun()

def get_user_location():
    if st.session_state.user and 'area' in st.session_state.user:
        return CITIES.get(st.session_state.user['area'], CITIES["New Delhi"])
    return CITIES["New Delhi"]

# --- HEADER ---
def render_header():
    user_display = ""
    if st.session_state.user:
        user_display = f"👤 {st.session_state.user['name']}"
    elif st.session_state.guest_mode:
        user_display = "👀 Guest View"
    else:
        user_display = "Please Login"

    st.markdown(f"""
    <div class="custom-header">
        <div class="header-logo">
            <span>❤️</span> JeevSetu
        </div>
        <div class="header-right">
            <span>{user_display}</span>
        </div>
    </div>
    <div style="margin-top: 80px;"></div>
    """, unsafe_allow_html=True)
    
    if st.session_state.user or st.session_state.guest_mode:
        c1, c2 = st.columns([9, 1])
        with c2:
            if st.session_state.user:
                if st.button("Logout", key="hdr_logout", type="secondary"): 
                    st.session_state.user = None
                    st.session_state.history = []
                    st.session_state.logs = []
                    navigate("auth")
            elif st.session_state.guest_mode:
                if st.button("Exit", key="hdr_exit", type="secondary"):
                    st.session_state.guest_mode = False
                    st.session_state.history = []
                    navigate("home")

# --- FOOTER ---
def render_footer():
    st.markdown("""
    <div class="custom-footer">
        <div class="footer-links">
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
            <a href="#">Hospital Guidelines</a>
            <a href="#">Support</a>
        </div>
        <div class="footer-copy">
            &copy; 2024 JeevSetu National Bio-Registry. <br>
            Connecting donors and patients with AI technology.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================= 5. PAGE LOGIC =================

def home_page():
    render_header()
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 50px; padding-top:20px;">
        <h1 style="font-size: 3.5rem; margin-bottom: 15px; background: -webkit-linear-gradient(#e11d48, #9f1239); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Bridging Lives, Instantly.</h1>
        <p style="font-size: 1.25rem; max-width: 650px; margin: 0 auto; line-height: 1.6;">
            The advanced AI-powered network connecting organ donors with patients in real-time. Secure, fast, and lifesaving.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="feature-card">
            <img src="https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=500" class="card-img">
            <h3>For Donors</h3>
            <p style="font-size:0.95rem;">Register your pledge securely and leave a legacy of life.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Register Now", use_container_width=True): st.session_state.auth_role = "User"; navigate("auth")
    
    with c2:
        st.markdown("""
        <div class="feature-card">
            <img src="https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=500" class="card-img">
            <h3>For Hospitals</h3>
            <p style="font-size:0.95rem;">Access the national database and find matches instantly.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Hospital Login", use_container_width=True): st.session_state.auth_role = "Hospital"; navigate("auth")
    
    with c3:
        st.markdown("""
        <div class="feature-card" style="border: 2px solid #fecaca; background: rgba(254, 242, 242, 0.8);">
            <img src="https://images.unsplash.com/photo-1516738901171-8eb4fc13bd20?w=500" class="card-img">
            <h3 style="color:#b91c1c;">Emergency SOS</h3>
            <p style="font-size:0.95rem;">Broadcast urgent organ requirements to the network.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Activate SOS", type="primary", use_container_width=True): navigate("sos")

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    xc1, xc2, xc3 = st.columns([1,2,1])
    with xc2:
        if st.button("👀 Continue as Guest (View Availability Only)", type="secondary"):
            st.session_state.guest_mode = True
            st.session_state.user = None
            navigate("search")
            
    render_footer()

def auth_page():
    render_header()
    
    st.markdown("<br>", unsafe_allow_html=True)
    if not st.session_state.auth_role: st.session_state.auth_role = "User"
    role = st.session_state.auth_role
    
    if st.button("← Back"): go_back()

    st.markdown(f"""
    <div style="max-width: 550px; margin: 0 auto; background: rgba(255,255,255,0.7); backdrop-filter: blur(10px); padding: 40px; border-radius: 24px; border: 1px solid white; box-shadow: 0 20px 50px rgba(0,0,0,0.05);">
        <h2 style='text-align:center; margin-bottom:20px;'>{role} Portal</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            st.write("")
            l_email = st.text_input("Email Address", key="l_email", placeholder="name@example.com")
            l_pass = st.text_input("Password", type="password", key="l_pass", placeholder="••••••••")
            st.write("")
            if st.button("Sign In", type="primary"):
                user = db.execute("SELECT * FROM users WHERE email=?", (l_email,), fetch_one=True)
                if user and SecurityService.hash_password(l_pass, user[2])[0] == user[1]:
                    st.session_state.user = {"email":user[0], "name":user[3], "role":user[4], "area":user[9]}
                    st.session_state.guest_mode = False
                    st.session_state.history = []
                    navigate("dashboard" if user[4] == "User" else "hospital_dashboard")
                else:
                    st.error("Invalid credentials.")

        with tab2:
            st.write("")
            name_label = "Full Name" if role == "User" else "Hospital Name"
            r_name = st.text_input(name_label, placeholder="Enter Name")
            r_email = st.text_input("Email", key="r_email", placeholder="name@example.com")
            r_pass = st.text_input("Password", type="password", key="r_pass", placeholder="Create a strong password")
            
            c_loc, c_bld = st.columns(2)
            with c_loc: r_loc = st.selectbox("Location", list(CITIES.keys()))
            with c_bld:
                if role == "User":
                    r_blood = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                else:
                    r_blood = "N/A"
                    st.info("Hospital Acct")
            
            st.markdown("---")
            st.caption("📷 **Two-Factor Auth:** Scan in Google Authenticator")
            
            if 'temp_secret' not in st.session_state: st.session_state.temp_secret = pyotp.random_base32()
            
            if r_email:
                uri = pyotp.totp.TOTP(st.session_state.temp_secret).provisioning_uri(r_email, issuer_name="JeevSetu")
                st.image(qrcode.make(uri).get_image(), width=150)
                
            otp_code = st.text_input("Verification Code", max_chars=6, placeholder="000 000")
            
            if st.button("Verify & Create Account", type="primary"):
                if pyotp.TOTP(st.session_state.temp_secret).verify(otp_code):
                    h, s = SecurityService.hash_password(r_pass)
                    db.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                            (r_email, h, s, r_name, role, 25, r_blood, st.session_state.temp_secret, "REG-001", r_loc, datetime.now().isoformat(), 0, ""))
                    
                    if role == "Hospital":
                        st.session_state.logs.append({"Time": datetime.now(), "Event": "Hospital Registered"})
                    
                    st.success("✅ Account Created! Please Login.")
                else:
                    st.error("❌ Invalid Code. Scan QR again.")

    render_footer()

def dashboard():
    render_header()
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%); padding: 30px; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); margin-bottom: 30px; border: 1px solid #e2e8f0;'>
        <h2 style='margin:0; color: #0f172a;'>Welcome back, {st.session_state.user['name']} 👋</h2>
        <p style='margin:5px 0 0 0; color: #64748b;'>Patient ID: {random.randint(10000,99999)} | Location: {st.session_state.user['area']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div style="background:#f0fdf4; border:1px solid #bbf7d0; padding:25px; border-radius:16px; margin-bottom:20px;">
            <h3 style="color:#166534; margin:0 0 10px 0;">Health Profile Active</h3>
            <p style="font-size:0.95rem; color:#15803d; margin-bottom:20px;">Your metrics are being monitored by the central registry AI.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔍 Find a Donor Match", type="primary"): navigate("search")
    with c2:
        st.markdown("""
        <div style="background:#fff7ed; border:1px solid #fed7aa; padding:25px; border-radius:16px; margin-bottom:20px;">
            <h3 style="color:#9a3412; margin:0 0 10px 0;">Upcoming Appointments</h3>
            <p style="font-size:0.95rem; color:#c2410c; margin-bottom:20px;">No appointments scheduled for this week.</p>
        </div>
        """, unsafe_allow_html=True)
        
    render_footer()

def search_page():
    render_header()
    is_guest = st.session_state.get('guest_mode', False)
    
    st.markdown("<h2 style='text-align:center; margin-bottom:30px;'>🧬 Organ Search Engine</h2>", unsafe_allow_html=True)
    
    if is_guest:
        st.warning("👀 GUEST MODE: You can view availability, but you must Login to Contact donors.")

    with st.container():
        st.markdown("<div style='background:rgba(255,255,255,0.7); padding:30px; border-radius:20px; box-shadow:0 10px 30px rgba(0,0,0,0.05); border:1px solid white;'>", unsafe_allow_html=True)
        with st.form("search_form"):
            st.write("### Patient Parameters")
            c1, c2 = st.columns(2)
            s_organ = c1.selectbox("Required Organ", list(ORGAN_LIMITS.keys()))
            s_blood = c2.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            st.write("")
            submitted = st.form_submit_button("Run AI Matching Algorithm", type="primary")
        st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        u_loc = get_user_location()
        patient = {
            "organ": s_organ, "blood_type": s_blood, 
            "lat": u_loc[0], "lon": u_loc[1],
            "hla": {"A": [2], "B": [7], "DR": [4]}
        }
        
        with st.spinner("Analyzing genetic compatibility and logistics..."):
            time.sleep(1) # UX Pause
            raw = db.execute("SELECT * FROM donors WHERE organ=?", (s_organ,), fetch_all=True)
            matches = []
            for d in raw:
                score, dist = MLService.calculate_compatibility(d, patient)
                if score > 0:
                    matches.append({"id":d[0], "hosp":d[1], "score":score, "dist":dist, "lat":d[4], "lon":d[5], "blood":d[3]})
            
            matches = sorted(matches, key=lambda x: x['score'], reverse=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if matches:
            st.success(f"✅ Analysis Complete: {len(matches)} potential matches found.")
            
            # Map Section
            map_df = pd.DataFrame(matches)
            map_df['color'] = "#e11d48"
            st.map(map_df, latitude='lat', longitude='lon', color='color', size=20, use_container_width=True)
            
            for m in matches:
                # Custom Card for Match
                with st.container():
                    st.markdown(f"""
                    <div style="background:white; padding:20px; border-radius:15px; border-left: 5px solid #e11d48; margin-bottom:15px; box-shadow:0 4px 10px rgba(0,0,0,0.05);">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <h4 style="margin:0;">{m['hosp']}</h4>
                                <p style="margin:0; font-size:0.9rem;">Distance: <b>{m['dist']} km</b> | Blood: <b>{m['blood']}</b></p>
                            </div>
                            <div style="text-align:right;">
                                <h2 style="margin:0; color:#e11d48;">{m['score']}%</h2>
                                <span style="font-size:0.8rem; color:#64748b;">MATCH SCORE</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c_act1, c_act2, c_act3 = st.columns([1,2,1])
                    with c_act2:
                        if is_guest:
                            if st.button(f"🔒 Login to Contact {m['id']}", key=m['id']):
                                st.session_state.guest_mode = False
                                st.session_state.auth_role = "User"
                                navigate("auth")
                        else:
                            if st.button(f"Request Connection ({m['id']})", key=m['id'], type="primary"):
                                st.toast("✅ Request Sent to Transplant Coordinator!", icon="📩")
        else:
            st.error("No compatible matches found at this time.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back"): go_back()
    
    render_footer()

def sos_page():
    render_header()
    st.markdown("""
    <div class="sos-header">
        <h2 style="margin-bottom:5px;">🚨 LIVE SOS FEED</h2>
        <p style="color:#b91c1c; margin:0;">Real-time emergency organ availability broadcasts. Time is critical.</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns([4, 1])
    with c1:
        q = st.text_input("Filter Organs/Blood", placeholder="Type 'Heart' or 'O+'...")
    with c2:
        st.write("")
        st.write("")
        search_btn = st.button("Search", type="primary")

    if q:
        donors = db.execute("SELECT * FROM donors WHERE organ LIKE ? OR blood_type LIKE ?", (f"%{q}%", f"%{q}%"), fetch_all=True)
    else:
        donors = db.execute("SELECT * FROM donors LIMIT 20", fetch_all=True)

    if not donors:
        # --- NEW LOGIC FOR BROADCAST ---
        st.warning(f"⚠️ Organ Not Found: No active SOS signals match '{q}'")
        
        st.markdown(f"""
        <div style="background:white; padding:25px; border-radius:15px; text-align:center; border: 1px dashed #ef4444; margin-top:20px;">
            <h3 style="color:#ef4444;">Broadcast Emergency Requirement?</h3>
            <p>We can alert all registered donors and hospitals about this specific need.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_space, col_btn, col_space2 = st.columns([1,2,1])
        with col_btn:
            if st.button(f"📢 Broadcast Alert for {q}", type="primary", key="broadcast_btn"):
                # Simulation of fetching users and sending emails
                all_users = db.execute("SELECT email, name FROM users", fetch_all=True)
                count = len(all_users)
                
                if count == 0:
                    st.error("No users registered in database to alert.")
                else:
                    my_bar = st.progress(0, text="Initializing Secure Broadcast...")
                    for percent_complete in range(100):
                        time.sleep(0.01) # Simulate network delay
                        my_bar.progress(percent_complete + 1, text=f"Sending encrypted alerts to {count} users...")
                    
                    # Log the event
                    st.session_state.logs.append({
                        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                        "Event": f"SOS Broadcast: {q} required. Alerted {count} users."
                    })
                    
                    st.success(f"✅ Alert Successfully Sent to {count} Registered Users & Hospitals!")
                    st.caption("Emails and SMS have been queued via the notification gateway.")
        # -------------------------------
    else:
        for d in donors:
            with st.expander(f"🔴 {d[3]} {d[2]} - {d[1]} (View Details)"):
                mc1, mc2 = st.columns([1, 1])
                with mc1:
                    st.markdown(f"""
                    <div style="background:#fff1f2; padding:15px; border-radius:10px;">
                        <b>Donor ID:</b> {d[0]}<br>
                        <b>Contact:</b> {d[7]}<br>
                        <b>Logged:</b> {d[8][:16]}
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")
                    if st.button(f"📞 Call Coordinator {d[0]}", key=f"sos_{d[0]}"): st.toast(f"Dialing {d[7]}...")
                with mc2:
                    m_df = pd.DataFrame({'lat': [d[4]], 'lon': [d[5]], 'color': ['#ef4444']})
                    st.map(m_df, latitude='lat', longitude='lon', color='color', zoom=11, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back"): go_back()
    
    render_footer()

def hospital_dashboard():
    render_header()
    
    st.markdown(f"""
    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;'>
        <h3>🏥 Hospital Operations Center</h3>
        <span style='background:#e2e8f0; padding:5px 15px; border-radius:20px; font-size:0.9rem; font-weight:600; color:#475569;'>{st.session_state.user['name']}</span>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Inventory", "📂 Upload Data", "🕒 Activity Logs"])
    
    with tab1:
        st.info("Manage your current organ inventory and active donors.")
        inv_data = db.execute("SELECT organ, blood_type, count(*) FROM donors GROUP BY organ, blood_type", fetch_all=True)
        if inv_data:
            df_inv = pd.DataFrame(inv_data, columns=["Organ", "Blood", "Count"])
            st.dataframe(df_inv, use_container_width=True, hide_index=True)
        else:
            st.write("No active inventory.")

    with tab2:
        st.markdown("<div style='background:white; padding:20px; border-radius:15px; border:1px dashed #cbd5e1;'>", unsafe_allow_html=True)
        st.write("**Batch Upload Donor Records**")
        uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])
        if uploaded_file is not None:
            st.success(f"File '{uploaded_file.name}' uploaded successfully!")
            with st.spinner("Encrypting and syncing with registry..."):
                time.sleep(1.5)
                log_entry = {"Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Event": f"Uploaded {uploaded_file.name}"}
                st.session_state.logs.append(log_entry)
                st.success("Database updated.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.write("**System Audit Logs**")
        if not st.session_state.logs:
            st.caption("No activity recorded yet.")
        else:
            log_df = pd.DataFrame(st.session_state.logs)
            st.dataframe(log_df, use_container_width=True, hide_index=True)

    render_footer()

# ================= 6. ROUTER =================
if st.session_state.page == "home": home_page()
elif st.session_state.page == "auth": auth_page()
elif st.session_state.page == "dashboard": dashboard()
elif st.session_state.page == "search": search_page()
elif st.session_state.page == "sos": sos_page()
elif st.session_state.page == "hospital_dashboard": hospital_dashboard()