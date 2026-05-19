import streamlit as st
import numpy as np
import pandas as pd
import requests

import os

# FastAPI Backend Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")
if not BACKEND_URL.startswith("http"):
    if "localhost" in BACKEND_URL or "127.0.0.1" in BACKEND_URL:
        BACKEND_URL = f"http://{BACKEND_URL}"
    else:
        if ":" in BACKEND_URL:
            BACKEND_URL = f"http://{BACKEND_URL}"
        else:
            # Render internal private host connects via port 8000 (exposed in Dockerfile)
            BACKEND_URL = f"http://{BACKEND_URL}:8000"

if not BACKEND_URL.endswith("/api/v1"):
    BACKEND_URL = f"{BACKEND_URL.rstrip('/')}/api/v1"

# Page configuration
st.set_page_config(
    page_title="Laptop Price Predictor Pro",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Sleek Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main-title {
        background: linear-gradient(135deg, #FF4B4B 0%, #FF8F8F 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #888888;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .card {
        background-color: #1E1E1E;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        margin-bottom: 1.5rem;
        border: 1px solid #333;
    }
    
    .success-text {
        font-weight: 600;
        font-size: 1.8rem;
        color: #2ECC71;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #FF4B4B;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "username" not in st.session_state:
    st.session_state.username = None

# Reference categories from reference dataframe
# In case backend is offline, we have local fallbacks for categories
CATEGORIES = {
    'Company': ['Apple', 'HP', 'Acer', 'Asus', 'Dell', 'Lenovo', 'Chuwi', 'MSI',
               'Microsoft', 'Toshiba', 'Huawei', 'Xiaomi', 'Vero', 'Razer',
               'Mediacom', 'Samsung', 'Google', 'Fujitsu', 'LG'],
    'TypeName': ['Ultrabook', 'Notebook', 'Netbook', 'Gaming', '2 in 1 Convertible', 'Workstation'],
    'Cpu brand': ['Intel Core i5', 'Intel Core i7', 'AMD Processor', 'Intel Core i3', 'Other Intel Processor'],
    'Gpu brand': ['Intel', 'AMD', 'Nvidia'],
    'OS': ['Mac', 'Windows', 'Others/No OS/Linux']
}

# --- Sidebar / Authentication ---
with st.sidebar:
    st.markdown("## 💻 Predictor Center")
    if st.session_state.access_token:
        st.success(f"Logged in as: **{st.session_state.username}** 👤")
        if st.button("Logout 🚪", use_container_width=True):
            st.session_state.access_token = None
            st.session_state.username = None
            st.rerun()
    else:
        st.info("Please log in or sign up to access predictions.")

# Main app display
st.markdown("<h1 class='main-title'>Laptop Price Predictor Pro</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Production-grade ML engine powered by an optimized XGBoost & LightGBM Voting Ensemble</p>", unsafe_allow_html=True)

# --- Authentication Screen ---
if not st.session_state.access_token:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        tab_login, tab_signup = st.tabs(["🔑 Login", "📝 Sign Up"])
        
        # --- LOGIN TAB ---
        with tab_login:
            st.markdown("### Access Your Account")
            login_user = st.text_input("Username", key="login_user_input")
            login_pass = st.text_input("Password", type="password", key="login_pass_input")
            
            if st.button("Log In", use_container_width=True):
                if not login_user or not login_pass:
                    st.error("Please fill in both fields.")
                else:
                    try:
                        resp = requests.post(
                            f"{BACKEND_URL}/auth/login",
                            json={"username": login_user, "password": login_pass},
                            timeout=5
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            st.session_state.access_token = data["access_token"]
                            st.session_state.username = login_user
                            st.success("Successfully logged in!")
                            st.rerun()
                        else:
                            st.error(f"Login failed: {resp.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Could not connect to FastAPI backend: {e}")
                        
        # --- SIGNUP TAB ---
        with tab_signup:
            st.markdown("### Create an Account")
            signup_user = st.text_input("Choose Username", key="signup_user_input")
            signup_pass = st.text_input("Choose Password", type="password", key="signup_pass_input")
            
            if st.button("Sign Up", use_container_width=True):
                if not signup_user or not signup_pass:
                    st.error("Please fill in both fields.")
                elif len(signup_user) < 3 or len(signup_pass) < 4:
                    st.error("Username must be >= 3 chars, Password >= 4 chars.")
                else:
                    try:
                        resp = requests.post(
                            f"{BACKEND_URL}/auth/signup",
                            json={"username": signup_user, "password": signup_pass},
                            timeout=5
                        )
                        if resp.status_code == 201:
                            st.success("Registration successful! You can now log in using the Login tab.")
                        else:
                            st.error(f"Sign up failed: {resp.json().get('detail', 'Username already taken')}")
                    except Exception as e:
                        st.error(f"Could not connect to FastAPI backend: {e}")

# --- Predictor Screen (Authenticated) ---
else:
    # 3-column split to group matching feature types
    col_sys, col_specs, col_perf = st.columns(3)
    
    with col_sys:
        st.subheader("🖥️ Brand & Model")
        Company = st.selectbox('Brand', CATEGORIES['Company'])
        Type = st.selectbox('Type', CATEGORIES['TypeName'])
        OS = st.selectbox('Operating System', CATEGORIES['OS'])
        
    with col_specs:
        st.subheader("⚙️ Memory & Storage")
        Ram = st.selectbox('RAM (in GB)', [2, 4, 6, 8, 12, 16, 24, 32, 64], index=3)
        Weight = st.number_input('Weight (in KG)', min_value=0.5, max_value=5.0, value=2.0, step=0.1)
        HDD = st.selectbox('HDD Size (in GB)', [0, 128, 256, 512, 1024, 2048])
        SSD = st.selectbox('SSD Size (in GB)', [0, 8, 128, 256, 512, 1024], index=3)
        
    with col_perf:
        st.subheader("⚡ Processor & Display")
        Cpu = st.selectbox('CPU Brand', CATEGORIES['Cpu brand'])
        Cpu_Speed = st.slider('CPU Speed (in GHz)', min_value=0.8, max_value=4.5, value=2.5, step=0.1)
        Gpu = st.selectbox('GPU Brand', CATEGORIES['Gpu brand'])
        
        # Display Specs
        Touchscreen = st.selectbox('Touchscreen Display', ['No', 'Yes'])
        Ips = st.selectbox('IPS Panel Display', ['No', 'Yes'])
        Screen_size = st.number_input('Screen Size (in Inches)', min_value=10.0, max_value=20.0, value=15.6, step=0.1)
        resolution = st.selectbox('Screen Resolution', [
            '1920x1080', '1366x768', '1600x900', '3840x2160', 
            '3200x1800', '2880x1800', '2560x1600', '2560x1440', '2304x1440'
        ])
        
    st.markdown("---")
    
    # Predict trigger
    if st.button('🔮 Predict Price via API', use_container_width=True):
        # Prepare API Request Payload
        payload = {
            "Company": Company,
            "TypeName": Type,
            "Ram": Ram,
            "Weight": Weight,
            "Touchscreen": Touchscreen,
            "Ips": Ips,
            "Screen_size": Screen_size,
            "Resolution": resolution,
            "Cpu_brand": Cpu,
            "Cpu_Speed": Cpu_Speed,
            "HDD": HDD,
            "SSD": SSD,
            "Gpu_brand": Gpu,
            "OS": OS
        }
        
        # Call Backend API
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        with st.spinner("Quering production prediction engine via secured API..."):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/predict",
                    json=payload,
                    headers=headers,
                    timeout=10
                )
                
                if resp.status_code == 200:
                    result = resp.json()
                    price = result["predicted_price"]
                    
                    # Premium Price display Card
                    st.markdown(f"""
                    <div style="background-color: #121212; padding: 2rem; border-radius: 12px; border: 2px solid #FF4B4B; text-align: center; margin-top: 1.5rem;">
                        <p style="font-size: 1.1rem; color: #888; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 0.5rem;">Estimated Market Price</p>
                        <h2 style="font-size: 3.5rem; font-weight: 700; color: #FF4B4B; margin: 0;">₹ {price:,}</h2>
                        <p style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Predicted with 91.68% accuracy using optimal XGBoost + LightGBM ensemble</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                elif resp.status_code in [401, 403]:
                    st.error("Authentication expired or invalid. Please log in again.")
                    st.session_state.access_token = None
                    st.session_state.username = None
                    st.rerun()
                else:
                    st.error(f"Prediction failed (Status {resp.status_code}): {resp.json().get('detail', 'Unknown API Error')}")
                    
            except Exception as e:
                st.error(f"Failed to communicate with prediction API backend: {e}")
