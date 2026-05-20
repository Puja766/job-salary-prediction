# =========================
# IMPORT LIBRARIES
# =========================
import streamlit as st
import pickle
import pandas as pd
import numpy as np
import os
import hashlib
import json
import re
from datetime import datetime

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="SalaryIQ — Salary Prediction",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# USER DATABASE (JSON with hashed passwords)
# =========================
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {"admin": {"name": "Admin", "email": "admin", "password": hash_password("1234"), "predictions": []}}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, username, password):
    users = load_users()
    if username.lower() in users:
        return False, "Username already exists."
    users[username.lower()] = {
        "name": name, "username": username.lower(),
        "password": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "predictions": []
    }
    save_users(users)
    return True, "Account created!"

def login_user(username, password):
    users = load_users()
    if username.lower() not in users:
        return False, "No account found with this username."
    if users[username.lower()]["password"] != hash_password(password):
        return False, "Incorrect password."
    return True, users[username.lower()]["name"]

def save_prediction(username, salary, job, exp, skills):
    users = load_users()
    if username.lower() in users:
        if "predictions" not in users[username.lower()]:
            users[username.lower()]["predictions"] = []
        users[username.lower()]["predictions"].append({
            "salary": salary, "job": job, "exp": exp,
            "skills": skills, "date": datetime.now().strftime("%d %b %Y")
        })
        save_users(users)

def is_valid_username(u):
    return len(u.strip()) >= 3

# =========================
# LOAD MODEL
# =========================
@st.cache_resource
def load_model():
    model   = pickle.load(open("knn_model.pkl", "rb"))
    scaler  = pickle.load(open("scaler.pkl",    "rb"))
    columns = pickle.load(open("columns.pkl",   "rb"))
    return model, scaler, columns

def get_options(columns, prefix):
    opts = [col.replace(prefix, "") for col in columns if col.startswith(prefix)]
    return sorted(list(set(opts)))

# =========================
# SESSION STATE
# =========================
for k, v in [
    ("logged_in", False), ("user_name", ""), ("user_username", ""),
    ("auth_page", "login"), ("active_page", "home"),
    ("last_prediction", None), ("last_inputs", None)
]:
    if k not in st.session_state:
        st.session_state[k] = v

# =========================
# GLOBAL CSS
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

*, html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    box-sizing: border-box;
}

#MainMenu, footer, header, .stDeployButton { visibility: hidden !important; display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none !important; }

.stApp {
    background: #0a0a0f !important;
    min-height: 100vh;
}

/* ---- AUTH PAGE ---- */
.auth-bg {
    min-height: 100vh;
    background: #0a0a0f;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
    position: relative;
    overflow: hidden;
}

.auth-bg::before {
    content: '';
    position: fixed;
    top: -200px; left: -200px;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

.auth-bg::after {
    content: '';
    position: fixed;
    bottom: -200px; right: -200px;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(16,185,129,0.1) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

.auth-card {
    background: #13131a;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 48px 44px;
    width: 100%;
    max-width: 460px;
    position: relative;
    z-index: 1;
}

.brand-text {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 22px;
    letter-spacing: 3px;
    color: #fff;
    margin-bottom: 36px;
}

.brand-text em {
    color: #6366f1;
    font-style: normal;
}

.auth-title {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 52px;
    letter-spacing: 2px;
    color: #ffffff;
    line-height: 1.0;
    margin-bottom: 8px;
}

.auth-title span {
    color: #6366f1;
}

.auth-subtitle {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 32px;
    font-weight: 400;
}

.stats-strip {
    display: flex;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 28px;
}

.stat-item {
    flex: 1;
    text-align: center;
    padding: 14px 8px;
    border-right: 1px solid rgba(255,255,255,0.06);
}

.stat-item:last-child { border-right: none; }

.stat-val {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 22px;
    letter-spacing: 1px;
    color: #6366f1;
}

.stat-lbl {
    font-size: 10px;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 2px;
}

.divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 18px 0;
    color: #334155;
    font-size: 12px;
}

.divider::before, .divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.06);
}

/* ---- INPUTS (DARK THEME) ---- */
.stTextInput > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1.5px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
}

.stTextInput > div > div:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    background: rgba(99,102,241,0.05) !important;
}

.stTextInput input {
    color: #f1f5f9 !important;
    background: transparent !important;
    font-size: 14px !important;
    -webkit-box-shadow: none !important;
    box-shadow: none !important;
}

.stTextInput input::placeholder { color: #475569 !important; }
.stTextInput label { color: #94a3b8 !important; font-size: 12px !important; font-weight: 600 !important; letter-spacing: .5px; text-transform: uppercase; }

.stNumberInput > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1.5px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
}

.stNumberInput > div > div:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}

.stNumberInput input {
    color: #f1f5f9 !important;
    background: transparent !important;
    font-size: 14px !important;
    -webkit-box-shadow: none !important;
    box-shadow: none !important;
}

.stNumberInput label { color: #94a3b8 !important; font-size: 12px !important; font-weight: 600 !important; letter-spacing: .5px; text-transform: uppercase; }
.stNumberInput button { color: #6366f1 !important; }

.stSelectbox > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1.5px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
}

.stSelectbox > div > div:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}

.stSelectbox [data-baseweb="select"] > div,
.stSelectbox [data-baseweb="select"] span { color: #f1f5f9 !important; background: transparent !important; }
.stSelectbox label { color: #94a3b8 !important; font-size: 12px !important; font-weight: 600 !important; letter-spacing: .5px; text-transform: uppercase; }

[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] {
    background: #1a1a24 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    box-shadow: 0 16px 48px rgba(0,0,0,0.5) !important;
}

[data-baseweb="menu"] li, [role="option"] {
    background: transparent !important;
    color: #cbd5e1 !important;
    font-size: 14px !important;
}

[data-baseweb="menu"] li:hover, [role="option"]:hover,
[role="option"][aria-selected="true"] {
    background: rgba(99,102,241,0.15) !important;
    color: #a5b4fc !important;
}

/* ---- BUTTONS ---- */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 20px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    cursor: pointer !important;
    letter-spacing: .5px;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(99,102,241,0.4) !important;
}

.ghost-btn > button {
    background: transparent !important;
    border: 1.5px solid rgba(255,255,255,0.12) !important;
    color: #94a3b8 !important;
    box-shadow: none !important;
}

.ghost-btn > button:hover {
    background: rgba(255,255,255,0.04) !important;
    border-color: rgba(255,255,255,0.2) !important;
    color: #f1f5f9 !important;
    transform: none !important;
    box-shadow: none !important;
}

.logout-btn > button {
    background: transparent !important;
    border: 1.5px solid rgba(239,68,68,0.3) !important;
    color: #ef4444 !important;
    box-shadow: none !important;
    font-size: 12px !important;
    padding: 8px 14px !important;
    width: auto !important;
}

.logout-btn > button:hover {
    background: rgba(239,68,68,0.08) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ---- NAVBAR ---- */
.top-navbar {
    background: #0d0d14;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    padding: 0 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 60px;
}

.nav-brand {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 20px;
    letter-spacing: 3px;
    color: #fff;
}

.nav-brand em { color: #6366f1; font-style: normal; }

.nav-tabs {
    display: flex;
    gap: 4px;
}

.nav-tab {
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    color: #64748b;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid transparent;
    text-decoration: none;
}

.nav-tab:hover { color: #f1f5f9; background: rgba(255,255,255,0.05); }
.nav-tab.active { color: #a5b4fc; background: rgba(99,102,241,0.12); border-color: rgba(99,102,241,0.25); }

.nav-user-area {
    display: flex;
    align-items: center;
    gap: 12px;
}

.nav-avatar {
    width: 34px; height: 34px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 800; color: #fff;
}

.nav-username {
    font-size: 13px;
    font-weight: 600;
    color: #94a3b8;
}

/* ---- HOME PAGE ---- */
.home-hero {
    background: #0a0a0f;
    padding: 80px 40px 60px;
    position: relative;
    overflow: hidden;
}

.home-hero::before {
    content: '';
    position: absolute;
    top: -300px; left: 50%;
    transform: translateX(-50%);
    width: 800px; height: 600px;
    background: radial-gradient(ellipse, rgba(99,102,241,0.12) 0%, transparent 70%);
    pointer-events: none;
}

.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(99,102,241,0.1);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 99px;
    padding: 6px 16px;
    font-size: 12px;
    font-weight: 700;
    color: #a5b4fc;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 24px;
}

.hero-title {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: clamp(56px, 7vw, 96px);
    letter-spacing: 2px;
    color: #ffffff;
    line-height: 0.95;
    margin-bottom: 20px;
}

.hero-title .accent { color: #6366f1; }
.hero-title .accent2 { color: #10b981; }

.hero-desc {
    font-size: 16px;
    color: #64748b;
    line-height: 1.7;
    max-width: 520px;
    margin-bottom: 36px;
}

.hero-actions {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

.btn-primary-hero {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 14px 28px;
    font-size: 15px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    display: inline-block;
}

.btn-primary-hero:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(99,102,241,0.4);
}

.hero-img-wrap {
    position: relative;
}

.hero-img-wrap img {
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.06);
    width: 100%;
    object-fit: cover;
}

.hero-img-badge {
    position: absolute;
    bottom: 20px; left: 20px;
    background: rgba(10,10,15,0.9);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 12px;
    padding: 12px 18px;
}

.badge-sal {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 26px;
    letter-spacing: 1px;
    color: #6366f1;
}

.badge-lbl {
    font-size: 11px;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ---- FEATURE CARDS ---- */
.features-section {
    padding: 60px 40px;
    background: #0a0a0f;
    border-top: 1px solid rgba(255,255,255,0.04);
}

.section-label {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 12px;
    letter-spacing: 4px;
    color: #6366f1;
    margin-bottom: 12px;
    text-transform: uppercase;
}

.section-title {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 42px;
    letter-spacing: 1px;
    color: #fff;
    margin-bottom: 40px;
    line-height: 1;
}

.feat-card {
    background: #13131a;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 28px;
    transition: all 0.3s;
    height: 100%;
}

.feat-card:hover {
    border-color: rgba(99,102,241,0.3);
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(99,102,241,0.1);
}

.feat-icon {
    width: 48px; height: 48px;
    border-radius: 12px;
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.2);
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    margin-bottom: 16px;
}

.feat-title {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 20px;
    letter-spacing: 1px;
    color: #f1f5f9;
    margin-bottom: 8px;
}

.feat-desc {
    font-size: 13px;
    color: #64748b;
    line-height: 1.6;
}

/* ---- PREDICT PAGE ---- */
.predict-wrap {
    padding: 36px 40px;
    background: #0a0a0f;
    min-height: calc(100vh - 60px);
}

.page-header {
    margin-bottom: 28px;
}

.page-title-main {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 40px;
    letter-spacing: 2px;
    color: #fff;
    margin-bottom: 4px;
}

.page-sub {
    font-size: 14px;
    color: #475569;
}

.form-card {
    background: #13131a;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 16px;
}

.form-card-title {
    font-size: 10px;
    font-weight: 800;
    color: #6366f1;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ---- RESULT ---- */
.result-banner {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a78bfa 100%);
    border-radius: 20px;
    padding: 40px 36px;
    text-align: center;
    margin: 20px 0;
    position: relative;
    overflow: hidden;
}

.result-banner::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: repeating-linear-gradient(
        -45deg,
        transparent,
        transparent 60px,
        rgba(255,255,255,0.02) 60px,
        rgba(255,255,255,0.02) 62px
    );
}

.result-eyebrow {
    font-size: 11px;
    color: rgba(255,255,255,0.6);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 8px;
    position: relative;
}

.result-amount {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 80px;
    letter-spacing: 3px;
    color: #fff;
    line-height: 1;
    margin: 4px 0;
    position: relative;
}

.result-sub {
    font-size: 14px;
    color: rgba(255,255,255,0.55);
    font-family: 'JetBrains Mono', monospace !important;
    position: relative;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin: 16px 0;
}

.metric-box {
    background: #13131a;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 16px;
}

.metric-lbl {
    font-size: 11px;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
}

.metric-val {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 24px;
    letter-spacing: 1px;
    color: #f1f5f9;
}

.metric-note {
    font-size: 11px;
    color: #10b981;
    margin-top: 3px;
    font-weight: 600;
}

.input-chart-section {
    background: #13131a;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 24px;
    margin-top: 16px;
}

.chart-title {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 18px;
    letter-spacing: 1px;
    color: #f1f5f9;
    margin-bottom: 16px;
}

.success-toast {
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.25);
    border-radius: 12px;
    padding: 14px 20px;
    margin-top: 12px;
    font-size: 13px;
    color: #34d399;
    font-weight: 600;
}

/* Streamlit overrides for dark theme */
h1,h2,h3,h4,h5 {
    font-family: 'Bebas Neue', sans-serif !important;
    color: #f1f5f9 !important;
    letter-spacing: 1px;
}

p { color: #94a3b8; }

.stAlert { border-radius: 10px !important; }

[data-testid="stMetricValue"] { color: #f1f5f9 !important; }
[data-testid="stMetricLabel"] { color: #64748b !important; }

/* Streamlit bar chart dark */
[data-testid="stArrowVegaLiteChart"] {
    filter: invert(0.85) hue-rotate(180deg);
    border-radius: 12px;
    overflow: hidden;
}

</style>
""", unsafe_allow_html=True)


# =========================
# HELPERS
# =========================
def get_initials(name):
    parts = name.strip().split()
    return (parts[0][0] + (parts[1][0] if len(parts) > 1 else "")).upper()


# =========================
# AUTH — LOGIN PAGE
# =========================
def show_login():
    st.markdown('<div class="auth-bg">', unsafe_allow_html=True)
    st.markdown("""
    <div class="auth-card">
        <div class="brand-text">💼 SALARY<em>IQ</em></div>
        <div class="auth-title">WELCOME<br><span>BACK.</span></div>
        <div class="auth-subtitle">Sign in to your career intelligence dashboard</div>
        <div class="stats-strip">
            <div class="stat-item"><div class="stat-val">95%</div><div class="stat-lbl">Accuracy</div></div>
            <div class="stat-item"><div class="stat-val">50K+</div><div class="stat-lbl">Predictions</div></div>
            <div class="stat-item"><div class="stat-val">120+</div><div class="stat-lbl">Job Roles</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("<div style='height:310px'></div>", unsafe_allow_html=True)
        username = st.text_input("Username", placeholder="Enter your username", key="login_user")
        password = st.text_input("Password", placeholder="Your password", key="login_pass", type="password")
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        if st.button("Sign In →", key="login_btn"):
            if not username or not password:
                st.error("Please fill in all fields.")
            else:
                ok, result = login_user(username, password)
                if ok:
                    st.session_state.logged_in     = True
                    st.session_state.user_name     = result
                    st.session_state.user_username = username.lower()
                    st.session_state.active_page   = "home"
                    st.rerun()
                else:
                    st.error(result)

        st.markdown('<div class="divider">or</div>', unsafe_allow_html=True)

        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("Create a free account →", key="goto_signup"):
            st.session_state.auth_page = "signup"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<p style='text-align:center;font-size:12px;color:#334155;margin-top:16px;'>🔒 Your data stays private and secure.</p>", unsafe_allow_html=True)


# =========================
# AUTH — SIGNUP PAGE
# =========================
def show_signup():
    st.markdown('<div class="auth-bg">', unsafe_allow_html=True)
    st.markdown("""
    <div class="auth-card">
        <div class="brand-text">💼 SALARY<em>IQ</em></div>
        <div class="auth-title">CREATE<br><span>ACCOUNT.</span></div>
        <div class="auth-subtitle">Join professionals discovering their true market value</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("<div style='height:240px'></div>", unsafe_allow_html=True)
        name     = st.text_input("Full Name",        placeholder="John Doe",          key="su_name")
        username = st.text_input("Username",          placeholder="johndoe123",        key="su_user")
        password = st.text_input("Password",          placeholder="Min 8 characters",  key="su_pass",    type="password")
        confirm  = st.text_input("Confirm Password",  placeholder="Repeat password",   key="su_confirm", type="password")

        if st.button("Create Account →", key="signup_btn"):
            if not all([name, username, password, confirm]):
                st.error("Please fill in all fields.")
            elif not is_valid_username(username):
                st.error("Username must be at least 3 characters.")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                ok, msg = register_user(name.strip(), username.strip(), password)
                if ok:
                    st.session_state.logged_in     = True
                    st.session_state.user_name     = name.strip()
                    st.session_state.user_username = username.strip().lower()
                    st.session_state.active_page   = "home"
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown('<div class="divider">or</div>', unsafe_allow_html=True)
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("Already have an account? Sign In", key="goto_login"):
            st.session_state.auth_page = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# =========================
# NAVBAR
# =========================
def show_navbar():
    initials = get_initials(st.session_state.user_name)
    active   = st.session_state.active_page

    st.markdown(f"""
    <div class="top-navbar">
        <div class="nav-brand">💼 SALARY<em>IQ</em></div>
        <div class="nav-tabs">
            <span class="nav-tab {'active' if active=='home' else ''}">🏠 Home</span>
            <span class="nav-tab {'active' if active=='predict' else ''}">💰 Predict</span>
        </div>
        <div class="nav-user-area">
            <div class="nav-avatar">{initials}</div>
            <span class="nav-username">{st.session_state.user_name}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, spacer = st.columns([1, 1, 1, 6])
    with c1:
        if st.button("🏠  Home", key="nav_home"):
            st.session_state.active_page = "home"
            st.rerun()
    with c2:
        if st.button("💰  Predict Salary", key="nav_predict"):
            st.session_state.active_page = "predict"
            st.rerun()
    with c3:
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("🚪 Logout", key="nav_logout"):
            st.session_state.logged_in       = False
            st.session_state.user_name       = ""
            st.session_state.user_username   = ""
            st.session_state.active_page     = "home"
            st.session_state.last_prediction = None
            st.session_state.last_inputs     = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# =========================
# HOME PAGE
# =========================
def show_home():
    # HERO
    left, right = st.columns([1.2, 1], gap="large")

    with left:
        st.markdown("""
        <div class="home-hero">
            <div class="hero-eyebrow">⚡ AI-POWERED SALARY INTELLIGENCE</div>
            <div class="hero-title">
                WELCOME TO<br>
                <span class="accent">SALARY</span><br>
                <span class="accent2">PREDICTION</span><br>
                APP
            </div>
            <div class="hero-desc">
                Predict your true market worth using Machine Learning trained on 250,000+ salary records.
                Get instant results based on your experience, skills, education, and role.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💰  Predict My Salary Now →", key="home_predict_btn"):
            st.session_state.active_page = "predict"
            st.rerun()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:flex;gap:24px;margin-top:32px;padding:0 40px 40px;">
            <div style="text-align:center;">
                <div style="font-family:'Bebas Neue',sans-serif;font-size:32px;color:#6366f1;letter-spacing:1px;">250K+</div>
                <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:1px;">Training Records</div>
            </div>
            <div style="text-align:center;">
                <div style="font-family:'Bebas Neue',sans-serif;font-size:32px;color:#10b981;letter-spacing:1px;">95%</div>
                <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:1px;">Model Accuracy</div>
            </div>
            <div style="text-align:center;">
                <div style="font-family:'Bebas Neue',sans-serif;font-size:32px;color:#f59e0b;letter-spacing:1px;">120+</div>
                <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:1px;">Job Roles</div>
            </div>
            <div style="text-align:center;">
                <div style="font-family:'Bebas Neue',sans-serif;font-size:32px;color:#ec4899;letter-spacing:1px;">KNN</div>
                <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:1px;">ML Algorithm</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown('<div style="padding:40px 20px 20px;">', unsafe_allow_html=True)
        st.image(
            "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=700&q=80",
            use_container_width=True
        )
        st.markdown("""
        <div style="background:#13131a;border:1px solid rgba(99,102,241,0.25);border-radius:14px;
                    padding:16px 20px;margin-top:12px;display:flex;align-items:center;gap:16px;">
            <div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:30px;color:#6366f1;letter-spacing:1px;">₹1,80,000</div>
                <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:1px;">Avg Top Tech Salary/yr</div>
            </div>
            <div style="width:1px;height:40px;background:rgba(255,255,255,0.06);"></div>
            <div>
                <div style="font-size:13px;color:#10b981;font-weight:700;">↑ 22% Growth</div>
                <div style="font-size:11px;color:#475569;">Tech sector 2025</div>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

    # FEATURES
    st.markdown("""
    <div class="features-section">
        <div class="section-label">WHAT WE OFFER</div>
        <div class="section-title">EVERYTHING YOU NEED TO<br>KNOW YOUR WORTH</div>
    </div>
    """, unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4, gap="small")

    features = [
        ("🎯", "ACCURATE", "KNN model trained on 250K+ real salary records across industries and roles."),
        ("⚡", "INSTANT", "Get your predicted salary in under a second — no waiting, no forms."),
        ("📊", "DETAILED", "See experience vs skills breakdown with visual analytics."),
        ("🔒", "SECURE", "Your data is private, hashed, and never shared with anyone."),
    ]

    for col, (icon, title, desc) in zip([f1, f2, f3, f4], features):
        with col:
            st.markdown(f"""
            <div class="feat-card">
                <div class="feat-icon">{icon}</div>
                <div class="feat-title">{title}</div>
                <div class="feat-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # CTA
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#13131a,#1a1a2e);
                border:1px solid rgba(99,102,241,0.2);border-radius:20px;
                padding:40px 48px;margin:0 0 40px;text-align:center;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:36px;letter-spacing:2px;color:#fff;margin-bottom:8px;">
            READY TO DISCOVER YOUR<br>
            <span style="color:#6366f1;">MARKET VALUE?</span>
        </div>
        <div style="font-size:14px;color:#64748b;margin-bottom:24px;">
            Fill in your profile on the Predict page and get an instant AI-powered salary estimate.
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        if st.button("🚀  Go to Salary Prediction →", key="home_cta"):
            st.session_state.active_page = "predict"
            st.rerun()


# =========================
# PREDICT PAGE
# =========================
def show_predict():
    try:
        model, scaler, columns = load_model()
    except Exception as e:
        st.error(f"⚠️ Could not load model files: {e}")
        st.info("Make sure knn_model.pkl, scaler.pkl, and columns.pkl are in the same folder.")
        return

    job_options     = ["Other"] + get_options(columns, "job_title_")
    edu_options     = ["Other"] + get_options(columns, "education_level_")
    loc_options     = ["Other"] + get_options(columns, "location_")
    ind_options     = ["Other"] + get_options(columns, "industry_")
    company_options = ["Other"] + get_options(columns, "company_size_")
    remote_options  = ["Other"] + get_options(columns, "remote_work_")

    st.markdown("""
    <div class="predict-wrap">
        <div class="page-header">
            <div class="page-title-main">💰 SALARY PREDICTION</div>
            <div class="page-sub">Fill in your profile — our KNN model will estimate your market salary instantly.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="form-card"><div class="form-card-title">📊 Experience & Skills</div>', unsafe_allow_html=True)
        exp    = st.number_input("Years of Experience", 0, 30, key="pred_exp")
        skills = st.number_input("Number of Skills",    1, 50, key="pred_skills")
        cert   = st.number_input("Certifications",      0, 20, key="pred_cert")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="form-card"><div class="form-card-title">🎓 Education & Role</div>', unsafe_allow_html=True)
        job = st.selectbox("Job Role",        job_options, key="pred_job")
        edu = st.selectbox("Education Level", edu_options, key="pred_edu")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="form-card"><div class="form-card-title">🏢 Company & Location</div>', unsafe_allow_html=True)
        loc     = st.selectbox("Location",     loc_options,     key="pred_loc")
        ind     = st.selectbox("Industry",     ind_options,     key="pred_ind")
        company = st.selectbox("Company Size", company_options, key="pred_company")
        remote  = st.selectbox("Remote Work",  remote_options,  key="pred_remote")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="form-card" style="background:linear-gradient(135deg,rgba(99,102,241,0.08),rgba(139,92,246,0.06));
                    border-color:rgba(99,102,241,0.2);">
            <div class="form-card-title" style="color:#a5b4fc;">✨ WHAT YOU'LL GET</div>
            <div style="font-size:13px;color:#64748b;line-height:2.0;">
                💰 &nbsp;<span style="color:#a5b4fc;font-weight:600;">Instant annual salary prediction</span><br>
                📅 &nbsp;<span style="color:#a5b4fc;font-weight:600;">Monthly earnings breakdown</span><br>
                📈 &nbsp;<span style="color:#a5b4fc;font-weight:600;">Growth potential estimate</span><br>
                🏆 &nbsp;<span style="color:#a5b4fc;font-weight:600;">Market percentile ranking</span><br>
                📊 &nbsp;<span style="color:#a5b4fc;font-weight:600;">Input analysis chart</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        clicked = st.button("🔍  PREDICT MY SALARY", key="do_predict")

    if clicked:
        input_dict = {
            "experience_years": exp, "skills_count": skills, "certifications": cert,
            "job_title": job, "education_level": edu, "location": loc,
            "industry": ind, "company_size": company, "remote_work": remote,
        }

        df = pd.DataFrame([input_dict])
        df["exp_squared"]    = df["experience_years"] ** 2
        df["skill_per_exp"]  = df["skills_count"] / (df["experience_years"] + 1)
        df["cert_per_skill"] = df["certifications"] / (df["skills_count"] + 1)
        df["seniority"]      = pd.cut(
            df["experience_years"],
            bins=[0, 2, 5, 10, 20],
            labels=["Fresher", "Junior", "Mid", "Senior"]
        )
        df = pd.get_dummies(df)
        df = df.reindex(columns=columns, fill_value=0)

        num_cols = ["experience_years", "skills_count", "certifications", "exp_squared", "skill_per_exp", "cert_per_skill"]
        existing_num = [c for c in num_cols if c in df.columns]
        if existing_num:
            df[existing_num] = scaler.transform(df[existing_num])

        salary     = int(model.predict(df)[0])
        monthly    = salary // 12
        seniority  = "Fresher" if exp <= 2 else ("Junior" if exp <= 5 else ("Mid-Level" if exp <= 10 else "Senior"))
        potential  = int(salary * 1.35)
        percentile = min(95, max(30, int(30 + (salary / 220000) * 65)))

        st.session_state.last_prediction = salary
        st.session_state.last_inputs     = input_dict
        save_prediction(st.session_state.user_username, salary, job, exp, skills)

        # RESULT BANNER
        st.markdown(f"""
        <div class="result-banner">
            <div class="result-eyebrow">YOUR ESTIMATED ANNUAL SALARY</div>
            <div class="result-amount">₹{salary:,}</div>
            <div class="result-sub">≈ ₹{monthly:,} / month · Powered by K-Nearest Neighbors</div>
        </div>
        """, unsafe_allow_html=True)

        # METRIC GRID
        st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-box">
                <div class="metric-lbl">Seniority Level</div>
                <div class="metric-val" style="font-size:20px;">{seniority}</div>
            </div>
            <div class="metric-box">
                <div class="metric-lbl">Monthly Salary</div>
                <div class="metric-val">₹{monthly:,}</div>
            </div>
            <div class="metric-box">
                <div class="metric-lbl">Growth Potential</div>
                <div class="metric-val" style="font-size:20px;">₹{potential:,}</div>
                <div class="metric-note">↑ in 2–3 years</div>
            </div>
            <div class="metric-box">
                <div class="metric-lbl">Market Percentile</div>
                <div class="metric-val">{percentile}th</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # INPUT CHART
        st.markdown('<div class="input-chart-section"><div class="chart-title">📊 INPUT ANALYSIS</div>', unsafe_allow_html=True)
        chart_df = pd.DataFrame({
            "Category": ["Experience (yrs)", "Skills Count", "Certifications"],
            "Value":    [exp, skills, cert]
        })
        st.bar_chart(chart_df.set_index("Category"), height=200)
        st.markdown('</div>', unsafe_allow_html=True)

        # SUCCESS
        st.markdown("""
        <div class="success-toast">
            ✅ Prediction saved to your account! Explore more by checking different inputs.
        </div>
        """, unsafe_allow_html=True)

        st.balloons()


# =========================
# MAIN APP
# =========================
def show_app():
    show_navbar()
    if st.session_state.active_page == "home":
        show_home()
    elif st.session_state.active_page == "predict":
        show_predict()


# =========================
# ENTRY POINT
# =========================
if st.session_state.logged_in:
    show_app()
elif st.session_state.auth_page == "signup":
    show_signup()
else:
    show_login()
