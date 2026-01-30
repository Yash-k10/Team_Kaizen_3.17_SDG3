import streamlit as st
from math import radians, sin, cos, asin, sqrt

# ================= PAGE CONFIG =================
st.set_page_config(page_title="OrganMatch", layout="wide")

# ================= STYLES =================
st.markdown("""
<style>
.stApp { background:#f8fafc; font-family:'Segoe UI',Arial;}

h1,h2,h3 { color:#0f172a; }

.card {
    background:white; padding:18px; border-radius:14px;
    box-shadow:0 8px 25px rgba(0,0,0,0.06);
    margin-bottom:16px;
}

.primary button {
    background:#2563eb !important; color:white !important;
    border-radius:10px; padding:12px 24px; font-weight:600;
}
.success button {
    background:#16a34a !important; color:white !important;
    border-radius:10px; padding:10px 20px;
}
.danger button {
    background:#dc2626 !important; color:white !important;
    border-radius:10px; padding:14px 28px; font-size:18px;
}

.back button {
    background:#64748b !important; color:white !important;
    border-radius:6px; padding:6px 16px;
}

.organ-card img {
    width:100%; border-radius:10px;
}

.footer {
    position:fixed; bottom:0; width:100%;
    background:#0f172a; color:white;
    text-align:center; padding:8px;
}
footer {visibility:hidden;}
</style>

<div class="footer">© 2026 Team Kizen</div>
""", unsafe_allow_html=True)

# ================= UTIL =================
def haversine(lat1, lon1, lat2, lon2):
    try:
        lat1, lon1, lat2, lon2 = map(float,[lat1,lon1,lat2,lon2])
    except:
        return 9999
    R=6371
    dlat=radians(lat2-lat1)
    dlon=radians(lon2-lon1)
    a=sin(dlat/2)**2+cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return R*2*asin(sqrt(a))

def back(target="landing"):
    st.markdown("<div class='back'>", unsafe_allow_html=True)
    if st.button("⬅ Back"):
        st.session_state.page=target
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ================= SESSION =================
if "page" not in st.session_state:
    st.session_state.page="landing"

if "db" not in st.session_state:
    st.session_state.db={
        "users":[],
        "admins":[{"email":"admin@org","pwd":"admin"}],
        "donors":[
            {"name":"Apollo Hospital","organ":"Kidney","lat":21.1458,"lon":79.0882},
            {"name":"AIIMS Nagpur","organ":"Heart","lat":21.1230,"lon":79.0510}
        ]
    }

# ================= PAGES =================
def landing():
    st.title("🫀 jeevSetu")
    st.subheader("AI-Powered Organ Donation Platform")

    c1,c2=st.columns(2)
    with c1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("New User")
        st.markdown("<div class='primary'>", unsafe_allow_html=True)
        if st.button("Register"):
            st.session_state.page="register"
        st.markdown("</div></div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Login")
        st.markdown("<div class='success'>", unsafe_allow_html=True)
        if st.button("Login"):
            st.session_state.page="login"
        st.markdown("</div></div>", unsafe_allow_html=True)

def register():
    back()
    st.header("👤 Register User")

    with st.form("reg"):
        email=st.text_input("Email")
        pwd=st.text_input("Password",type="password")
        if st.form_submit_button("Create Account"):
            st.session_state.db["users"].append({"email":email,"pwd":pwd})
            st.success("Registered successfully")
            st.session_state.page="login"
            st.rerun()

def login():
    back()
    st.header("🔐 Login")

    role=st.selectbox("Login As",["User","Admin","Hospitality"])
    email=st.text_input("Email")
    pwd=st.text_input("Password",type="password")

    if st.button("Login",type="primary"):
        if role=="User" and any(u for u in st.session_state.db["users"] if u["email"]==email):
            st.session_state.page="dashboard"

        elif role=="Admin" and any(a for a in st.session_state.db["admins"] if a["email"]==email and a["pwd"]==pwd):
            st.session_state.page="admin_dashboard"

        elif role=="Hospitality":
            st.session_state.hospital=email
            st.session_state.page="hospital_dashboard"

        else:
            st.error("Invalid credentials")

        st.rerun()

def dashboard():
    st.title("📊 User Dashboard")
    search=st.text_input("🔍 Search organ or hospital")

    st.subheader("Available Organs")
    o1,o2,o3,o4=st.columns(4)
    organs=[
        ("Kidney","https://i.imgur.com/Y9p7H0E.png"),
        ("Heart","https://i.imgur.com/5L2mG3J.png"),
        ("Liver","https://i.imgur.com/Y6YxY5F.png"),
        ("Lung","https://i.imgur.com/j9QZz1K.png")
    ]
    for col,(name,img) in zip([o1,o2,o3,o4],organs):
        with col:
            st.markdown("<div class='card organ-card'>", unsafe_allow_html=True)
            st.image(img)
            st.markdown(f"### {name}")
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='danger'>", unsafe_allow_html=True)
    if st.button("🚨 EMERGENCY SOS"):
        st.session_state.page="sos"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def sos():
    back("dashboard")
    st.header("🚨 SOS Emergency")

    with st.form("sos"):
        organ=st.selectbox("Select Organ",["Kidney","Heart","Liver","Lung"])
        lat=st.text_input("Your Latitude")
        lon=st.text_input("Your Longitude")

        if st.form_submit_button("Find Nearest Facility"):
            found=False
            for d in st.session_state.db["donors"]:
                if d["organ"]==organ:
                    dist=haversine(lat,lon,d["lat"],d["lon"])
                    st.success(f"{d['name']} — {round(dist,2)} km away")
                    st.link_button("📍 Open in Google Maps",
                        f"https://www.google.com/maps/search/?api=1&query={d['lat']},{d['lon']}")
                    found=True
            if not found:
                st.warning("No matching facilities found")

def admin_dashboard():
    back()
    st.title("🛠 Admin Dashboard")
    st.metric("Total Users",len(st.session_state.db["users"]))
    st.metric("Total Donors",len(st.session_state.db["donors"]))

    st.subheader("Registered Donors")
    for d in st.session_state.db["donors"]:
        st.info(f"{d['name']} — {d['organ']}")

def hospital_dashboard():
    back()
    st.title("🏥 Hospital Dashboard")

    with st.form("add_donor"):
        name=st.text_input("Hospital Name")
        organ=st.selectbox("Organ",["Kidney","Heart","Liver","Lung"])
        lat=st.text_input("Latitude")
        lon=st.text_input("Longitude")

        if st.form_submit_button("Add Availability"):
            st.session_state.db["donors"].append({
                "name":name,"organ":organ,"lat":lat,"lon":lon
            })
            st.success("Added successfully")

# ================= ROUTER =================
{
    "landing":landing,
    "register":register,
    "login":login,
    "dashboard":dashboard,
    "sos":sos,
    "admin_dashboard":admin_dashboard,
    "hospital_dashboard":hospital_dashboard
}.get(st.session_state.page,landing)()