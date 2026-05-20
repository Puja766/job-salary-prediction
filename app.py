# =========================
# IMPORT LIBRARIES
# =========================
import streamlit as st
import pickle
import pandas as pd
import numpy as np
import hashlib
import json
import os
import re
import random
from datetime import datetime

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Salary Prediction App",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# USER DATABASE FUNCTIONS (File 1 style - pickle)
# =========================
USER_FILE = "users.pkl"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "rb") as f:
            return pickle.load(f)
    return {"admin": "1234"}

def save_users(users):
    with open(USER_FILE, "wb") as f:
        pickle.dump(users, f)

# =========================
# LOAD MODEL FILES
# =========================
@st.cache_resource
def load_model():
    model   = pickle.load(open("knn_model.pkl", "rb"))
    scaler  = pickle.load(open("scaler.pkl",    "rb"))
    columns = pickle.load(open("columns.pkl",   "rb"))
    return model, scaler, columns

# =========================
# HELPER: EXTRACT OPTIONS
# =========================
def get_options(columns, prefix):
    opts = [col.replace(prefix, "") for col in columns if col.startswith(prefix)]
    return sorted(list(set(opts)))

# =========================
# CAREER DATA (from File 2)
# =========================
SKILLS_BY_ROLE = {
    "Data Scientist":            ["Python", "Machine Learning", "Deep Learning", "SQL", "Statistics", "TensorFlow", "Spark"],
    "Software Engineer":         ["System Design", "DSA", "Cloud (AWS/GCP)", "Docker", "Kubernetes", "CI/CD", "Microservices"],
    "AI Engineer":               ["LLMs", "PyTorch", "MLOps", "Vector Databases", "Prompt Engineering", "Transformers", "CUDA"],
    "Data Analyst":              ["Power BI", "Tableau", "Advanced SQL", "Python", "Excel", "Statistical Analysis", "DAX"],
    "Machine Learning Engineer": ["MLOps", "Feature Engineering", "Model Deployment", "Kubeflow", "PyTorch", "Scalable ML"],
    "DevOps Engineer":           ["Kubernetes", "Terraform", "AWS", "CI/CD", "Monitoring", "Docker", "Linux"],
    "Cloud Engineer":            ["AWS/Azure/GCP", "Terraform", "Networking", "Security", "Serverless", "Cost Optimization"],
    "Cybersecurity Analyst":     ["Ethical Hacking", "SIEM", "Incident Response", "Network Security", "Compliance", "Forensics"],
    "Product Manager":           ["Roadmapping", "OKRs", "User Research", "A/B Testing", "SQL", "Stakeholder Management"],
    "Business Analyst":          ["Power BI", "Process Mapping", "SQL", "Requirements Gathering", "Agile", "JIRA"],
    "Frontend Developer":        ["React", "TypeScript", "Next.js", "Tailwind CSS", "GraphQL", "Web Performance", "Testing"],
    "Backend Developer":         ["Node.js", "PostgreSQL", "Redis", "REST APIs", "System Design", "Docker", "Message Queues"],
    "Other":                     ["Communication", "Project Management", "Data Analysis", "Cloud Basics", "Agile", "Python"],
}

ROADMAP_BY_ROLE = {
    "Data Scientist":            ["Junior Data Analyst", "Data Scientist", "Senior Data Scientist", "Lead / Staff DS", "Head of Data Science"],
    "Software Engineer":         ["Junior Developer", "Software Engineer", "Senior Engineer", "Staff Engineer", "Principal / VP Eng"],
    "AI Engineer":               ["ML Engineer", "AI Engineer", "Senior AI Engineer", "AI Tech Lead", "AI Research Director"],
    "Data Analyst":              ["Junior Analyst", "Data Analyst", "Senior Analyst", "Analytics Manager", "Director of Analytics"],
    "Machine Learning Engineer": ["Junior ML Engineer", "ML Engineer", "Senior ML Engineer", "ML Tech Lead", "Head of ML"],
    "DevOps Engineer":           ["Junior DevOps", "DevOps Engineer", "Senior DevOps", "Platform Lead", "VP Infrastructure"],
    "Cloud Engineer":            ["Cloud Support", "Cloud Engineer", "Senior Cloud Engineer", "Cloud Architect", "CTO / VP Cloud"],
    "Cybersecurity Analyst":     ["Security Analyst", "Senior Analyst", "Security Lead", "CISO Director", "Chief Security Officer"],
    "Product Manager":           ["Associate PM", "Product Manager", "Senior PM", "Group PM", "VP / CPO"],
    "Business Analyst":          ["Junior BA", "Business Analyst", "Senior BA", "BA Manager", "Director of Strategy"],
    "Frontend Developer":        ["Junior Frontend", "Frontend Developer", "Senior Frontend", "Frontend Lead", "Head of Frontend"],
    "Backend Developer":         ["Junior Backend", "Backend Developer", "Senior Backend", "Backend Lead", "Engineering Manager"],
    "Other":                     ["Entry Level", "Mid Level", "Senior Level", "Lead / Manager", "Director / VP"],
}

INDUSTRY_TRENDS = {
    "Technology":    {"growth": "22%", "outlook": "Excellent", "top_pay": "₹1,80,000", "demand": "Very High"},
    "Finance":       {"growth": "15%", "outlook": "Strong",    "top_pay": "₹1,60,000", "demand": "High"},
    "Healthcare":    {"growth": "18%", "outlook": "Excellent", "top_pay": "₹1,40,000", "demand": "Very High"},
    "Consulting":    {"growth": "12%", "outlook": "Strong",    "top_pay": "₹1,70,000", "demand": "High"},
    "Manufacturing": {"growth": "8%",  "outlook": "Moderate",  "top_pay": "₹1,10,000", "demand": "Moderate"},
    "Education":     {"growth": "10%", "outlook": "Stable",    "top_pay": "₹90,000",   "demand": "Moderate"},
    "Retail":        {"growth": "7%",  "outlook": "Moderate",  "top_pay": "₹95,000",   "demand": "Moderate"},
    "Media":         {"growth": "9%",  "outlook": "Moderate",  "top_pay": "₹1,00,000", "demand": "Moderate"},
    "Telecom":       {"growth": "11%", "outlook": "Strong",    "top_pay": "₹1,30,000", "demand": "High"},
    "Government":    {"growth": "6%",  "outlook": "Stable",    "top_pay": "₹85,000",   "demand": "Low"},
    "Other":         {"growth": "10%", "outlook": "Moderate",  "top_pay": "₹1,00,000", "demand": "Moderate"},
}

# =========================
# CUSTOM CSS (File 1 style for auth/home + File 2 style for app pages)
# =========================
st.markdown("""
<style>

/* ===== FILE 1 STYLES (Auth + Home) ===== */

/* Main Background */
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b, #334155);
    color: white;
}

/* Navbar */
.navbar {
    background: linear-gradient(90deg, #06b6d4, #3b82f6);
    padding: 15px;
    border-radius: 15px;
    text-align: center;
    font-size: 28px;
    font-weight: bold;
    color: white;
    margin-bottom: 20px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
}

/* Titles */
h1, h2, h3 {
    color: #f8fafc !important;
    text-align: center;
}

/* Text */
p, li, label, div {
    color: #f1f5f9 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #06b6d4, #2563eb);
    color: white;
    border-radius: 12px;
    border: none;
    height: 50px;
    width: 100%;
    font-size: 18px;
    font-weight: bold;
    transition: 0.3s;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #ec4899, #8b5cf6);
    transform: scale(1.02);
}

/* Inputs */
.stTextInput input,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 10px;
    border: 2px solid #38bdf8;
    background-color: #f8fafc;
    color: black !important;
}

/* Login Card */
.login-card {
    background-color: rgba(30,41,59,0.9);
    padding: 20px;
    border-radius: 20px;
    margin-top: 20px;
    box-shadow: 0px 5px 15px rgba(0,0,0,0.5);
}

/* Metrics */
[data-testid="metric-container"] {
    background-color: #1e293b;
    border: 1px solid #38bdf8;
    padding: 20px;
    border-radius: 15px;
}

/* Footer */
.footer {
    text-align: center;
    color: white;
    padding: 20px;
    margin-top: 30px;
}

/* Home Cards */
.feature-card {
    background: rgba(255,255,255,0.08);
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    backdrop-filter: blur(10px);
    transition: 0.3s;
    border: 1px solid rgba(255,255,255,0.1);
}

.feature-card:hover {
    transform: translateY(-5px);
}

/* Stats Card */
.stats-card {
    background: rgba(255,255,255,0.05);
    padding: 30px;
    border-radius: 20px;
    text-align: center;
}

/* About Cards */
.about-card {
    background: linear-gradient(135deg, #1e1e2f, #2d2d44);
    padding:20px;
    border-radius:15px;
    margin-bottom:20px;
}

.about-feature {
    background:#26273b;
    padding:15px;
    border-radius:12px;
    text-align:center;
}

/* Tool Cards */
.tool-card {
    background:#20232a;
    padding:15px;
    border-radius:12px;
    text-align:center;
    transition:0.3s;
}

.tool-card:hover {
    transform:translateY(-5px);
}

.tool-logo {
    font-size:40px;
}

.version {
    color:#00ff99;
}

/* ===== FILE 2 STYLES (App Pages) ===== */

/* PAGE */
.page-wrap { padding: 28px 36px; max-width: 1200px; margin: 0 auto; }
.page-title { font-size: 24px; font-weight: 800; color: #f8fafc !important; margin-bottom: 4px; }
.page-sub { font-size: 14px; color: #94a3b8 !important; margin-bottom: 24px; }

/* CARDS */
.card {
    background: rgba(30,41,59,0.85);
    border-radius: 16px;
    border: 1px solid rgba(56,189,248,0.2);
    padding: 22px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    margin-bottom: 16px;
}
.card-title { font-size: 11px; font-weight: 700; color: #38bdf8 !important; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px; }

/* METRICS */
.metric-card {
    background: rgba(15,23,42,0.8);
    border: 1px solid rgba(56,189,248,0.25);
    border-radius: 14px;
    padding: 18px 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}
.metric-label { font-size: 12px; color: #94a3b8 !important; font-weight: 500; margin-bottom: 6px; }
.metric-value { font-size: 22px; font-weight: 800; color: #f8fafc !important; }
.metric-sub { font-size: 12px; color: #10b981 !important; font-weight: 500; margin-top: 4px; }

/* RESULT HERO */
.result-hero {
    background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
    border-radius: 20px;
    padding: 36px 32px;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(6,182,212,0.3);
}
.result-hero-label { font-size: 12px; color: rgba(255,255,255,0.8) !important; letter-spacing: 1.5px; text-transform: uppercase; }
.result-hero-amount { font-size: 56px; font-weight: 800; color: #fff !important; margin: 8px 0; }
.result-hero-sub { font-size: 13px; color: rgba(255,255,255,0.7) !important; }

/* INSIGHTS */
.insight-card {
    background: rgba(15,23,42,0.7);
    border-radius: 12px;
    border: 1px solid rgba(56,189,248,0.15);
    padding: 18px;
    margin-bottom: 10px;
    display: flex;
    gap: 14px;
    align-items: flex-start;
}
.insight-icon {
    width: 38px; height: 38px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; flex-shrink: 0;
}
.insight-icon-blue  { background: rgba(99,102,241,0.2); }
.insight-icon-green { background: rgba(16,185,129,0.2); }
.insight-icon-amber { background: rgba(245,158,11,0.2); }
.insight-icon-rose  { background: rgba(244,63,94,0.2); }
.insight-title { font-size: 14px; font-weight: 600; color: #f8fafc !important; margin-bottom: 4px; }
.insight-desc  { font-size: 13px; color: #94a3b8 !important; line-height: 1.5; }

/* ROADMAP */
.roadmap-step {
    display: flex; gap: 16px; align-items: flex-start;
    padding: 18px 0; border-bottom: 1px solid rgba(56,189,248,0.1);
}
.roadmap-step:last-child { border-bottom: none; }
.step-dot {
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700; flex-shrink: 0; margin-top: 2px;
}
.step-dot-done { background: #06b6d4; color: #fff; }
.step-dot-curr { background: linear-gradient(135deg, #06b6d4, #3b82f6); color: #fff; box-shadow: 0 0 0 4px rgba(6,182,212,0.25); }
.step-dot-next { background: rgba(30,41,59,0.8); color: #64748b !important; border: 2px dashed #334155; }
.step-title { font-size: 15px; font-weight: 600; color: #f8fafc !important; }
.step-sub   { font-size: 13px; color: #94a3b8 !important; margin-top: 3px; }
.step-badge { display: inline-block; font-size: 11px; font-weight: 600; padding: 2px 10px; border-radius: 99px; margin-top: 6px; }
.badge-current { background: rgba(6,182,212,0.2); color: #38bdf8 !important; }
.badge-done    { background: rgba(16,185,129,0.2); color: #10b981 !important; }
.badge-future  { background: rgba(30,41,59,0.5); color: #64748b !important; }

/* LEADERBOARD */
.lb-row {
    display: flex; align-items: center; gap: 14px; padding: 14px 16px;
    border-radius: 12px; margin-bottom: 8px;
    background: rgba(15,23,42,0.6);
    border: 1px solid rgba(56,189,248,0.1);
    transition: all 0.15s;
}
.lb-row:hover { background: rgba(6,182,212,0.1); border-color: rgba(6,182,212,0.3); }
.lb-row.gold   { background: rgba(245,158,11,0.1); border-color: rgba(245,158,11,0.3); }
.lb-row.silver { background: rgba(148,163,184,0.1); border-color: rgba(148,163,184,0.3); }
.lb-row.bronze { background: rgba(180,83,9,0.1); border-color: rgba(180,83,9,0.3); }
.lb-rank  { font-size:16px; font-weight:800; min-width:28px; color: #f8fafc !important; }
.lb-name  { flex:1; font-size:14px; font-weight:600; color:#f8fafc !important; }
.lb-role  { font-size:12px; color:#94a3b8 !important; }
.lb-salary{ font-size:16px; font-weight:800; color:#38bdf8 !important; }

/* COMPARE BARS */
.compare-bar-wrap { margin-bottom: 14px; }
.compare-bar-label { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 5px; }
.compare-bar-track { height: 8px; background: rgba(30,41,59,0.8); border-radius: 99px; overflow: hidden; }
.compare-bar-fill  { height: 100%; border-radius: 99px; }

/* MISC */
.trend-up   { color: #10b981 !important; font-weight: 600; font-size: 13px; }
.pw-track   { height: 4px; background: #334155; border-radius: 99px; overflow: hidden; margin-bottom: 6px; }
.pw-bar     { height: 100%; border-radius: 99px; transition: width .3s, background .3s; }

/* NAV TABS */
.nav-tab-area {
    background: rgba(15,23,42,0.9);
    border-bottom: 1px solid rgba(56,189,248,0.2);
    padding: 0 20px 8px 20px;
}

/* Top Nav Bar */
.top-nav {
    background: linear-gradient(90deg, #06b6d4, #3b82f6);
    padding: 0 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 56px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
    margin-bottom: 0;
}
.nav-brand { font-size: 20px; font-weight: 800; color: white !important; }
.nav-user { display: flex; align-items: center; gap: 10px; }
.nav-avatar {
    width: 34px; height: 34px; border-radius: 50%;
    background: rgba(255,255,255,0.3);
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700; color: #fff !important;
}
.nav-name { font-size: 13px; font-weight: 500; color: rgba(255,255,255,0.9) !important; }

/* Signout button override */
.signout-btn > button {
    background: rgba(239,68,68,0.15) !important;
    color: #fca5a5 !important;
    border: 1.5px solid rgba(239,68,68,0.3) !important;
    box-shadow: none !important;
    font-size: 13px !important;
    height: 40px !important;
}
.signout-btn > button:hover {
    background: rgba(239,68,68,0.25) !important;
}

/* Selectbox dropdown */
[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
}
[data-baseweb="menu"] li, [role="option"] {
    background: #1e293b !important;
    color: #f1f5f9 !important;
    font-size: 14px !important;
}
[data-baseweb="menu"] li:hover, [role="option"]:hover, [role="option"][aria-selected="true"] {
    background: rgba(6,182,212,0.15) !important;
    color: #38bdf8 !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# NAVBAR (File 1 style)
# =========================
st.markdown(
    '<div class="navbar">💼 Salary Prediction System</div>',
    unsafe_allow_html=True
)

# =========================
# SESSION STATE
# =========================
if "users" not in st.session_state:
    st.session_state.users = load_users()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "home"

if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None

if "last_inputs" not in st.session_state:
    st.session_state.last_inputs = None

# =========================
# LOGIN FUNCTION (File 1)
# =========================
def login():
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.subheader("🔐 Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in st.session_state.users and \
           st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.active_tab = "home"
            st.success(f"Welcome {username} 🎉")
            st.rerun()
        else:
            st.error("Invalid Username or Password")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# SIGNUP FUNCTION (File 1)
# =========================
def signup():
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.subheader("📝 Create Account")
    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")
    confirm_pass = st.text_input("Confirm Password", type="password")
    if st.button("Create Account"):
        if new_user in st.session_state.users:
            st.warning("Username already exists")
        elif new_pass != confirm_pass:
            st.warning("Passwords do not match")
        else:
            st.session_state.users[new_user] = new_pass
            save_users(st.session_state.users)
            st.success("Account Created Successfully ✅")
            st.info("Now login anytime")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# AUTH PAGE (File 1)
# =========================
if not st.session_state.logged_in:
    menu = st.sidebar.radio("Menu", ["Login", "Sign Up"])
    if menu == "Login":
        login()
    else:
        signup()

# =========================
# MAIN APP
# =========================
else:
    # Load model
    try:
        model, scaler, columns = load_model()
        job_options     = ["Other"] + get_options(columns, "job_title_")
        edu_options     = ["Other"] + get_options(columns, "education_level_")
        loc_options     = ["Other"] + get_options(columns, "location_")
        ind_options     = ["Other"] + get_options(columns, "industry_")
        company_options = ["Other"] + get_options(columns, "company_size_")
        remote_options  = ["Other"] + get_options(columns, "remote_work_")
        model_loaded = True
    except:
        model_loaded = False

    # ===== TOP NAV BAR =====
    initials = st.session_state.username[:2].upper()
    st.markdown(f"""
    <div class="top-nav">
        <div class="nav-brand">💼 Salary Prediction System</div>
        <div class="nav-user">
            <div class="nav-avatar">{initials}</div>
            <span class="nav-name">{st.session_state.username}</span>
        </div>
    </div>""", unsafe_allow_html=True)

    # ===== SIDEBAR NAV =====
    st.sidebar.title("📌 Navigation")
    page = st.sidebar.radio(
        "Go To",
        [
            "🏠 Home",
            "💰 Salary Prediction",
            "💡 Insights",
            "🗺️ Roadmap",
            "📊 Dashboard",
            "⚖️ Compare",
            "🏆 Leaderboard",
        ]
    )
    st.sidebar.success(f"Logged in as {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.last_prediction = None
        st.session_state.last_inputs = None
        st.rerun()

    # ===========================
    # HOME PAGE (File 1)
    # ===========================
    if page == "🏠 Home":
        st.title("Welcome to Salary Prediction App")

        left, right = st.columns([1.4, 1])
        with left:
            st.markdown("""
            <div class="about-card">
            <h1>💼 Salary Prediction Platform</h1>
            <p>
            Predict employee salary using Machine Learning
            based on experience, education, certifications
            and skills.
            </p>
            </div>
            """, unsafe_allow_html=True)
        with right:
            st.image(
                "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a",
                use_container_width=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        f1, f2, f3, f4 = st.columns(4)
        with f1:
            st.markdown("""
            <div class="feature-card">
            <h3>🎯 Accurate</h3>
            <p>Highly accurate salary prediction</p>
            </div>
            """, unsafe_allow_html=True)
        with f2:
            st.markdown("""
            <div class="feature-card">
            <h3>⚡ Fast</h3>
            <p>Instant AI prediction system</p>
            </div>
            """, unsafe_allow_html=True)
        with f3:
            st.markdown("""
            <div class="feature-card">
            <h3>📊 Analytics</h3>
            <p>Interactive dashboard & charts</p>
            </div>
            """, unsafe_allow_html=True)
        with f4:
            st.markdown("""
            <div class="feature-card">
            <h3>🔒 Secure</h3>
            <p>Safe and secure user system</p>
            </div>
            """, unsafe_allow_html=True)

    # ===========================
    # SALARY PREDICTION (File 2)
    # ===========================
    elif page == "💰 Salary Prediction":
        st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
        st.markdown('<div class="page-title">💰 Salary Prediction</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-sub">Fill in your profile — our KNN model will estimate your market salary instantly.</div>', unsafe_allow_html=True)

        if not model_loaded:
            st.error("Model files not found. Please ensure knn_model.pkl, scaler.pkl, columns.pkl are present.")
        else:
            col1, col2 = st.columns(2, gap="large")
            with col1:
                st.markdown('<div class="card"><div class="card-title">📊 Experience & Skills</div>', unsafe_allow_html=True)
                exp    = st.number_input("Years of Experience", 0, 30, key="exp")
                skills = st.number_input("Number of Skills",    1, 50, key="skills")
                cert   = st.number_input("Certifications",      0, 20, key="cert")
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="card"><div class="card-title">🎓 Education & Role</div>', unsafe_allow_html=True)
                job = st.selectbox("Job Role",        job_options if job_options else ["Other"], key="job")
                edu = st.selectbox("Education Level", edu_options if edu_options else ["Other"], key="edu")
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="card"><div class="card-title">🏢 Company & Location</div>', unsafe_allow_html=True)
                loc     = st.selectbox("Location",     loc_options     if loc_options     else ["Other"], key="loc")
                ind     = st.selectbox("Industry",     ind_options     if ind_options     else ["Other"], key="ind")
                company = st.selectbox("Company Size", company_options if company_options else ["Other"], key="company")
                remote  = st.selectbox("Remote Work",  remote_options  if remote_options  else ["Other"], key="remote")
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("""
                <div class="card" style="background:linear-gradient(135deg,rgba(6,182,212,0.1),rgba(59,130,246,0.1));border-color:rgba(6,182,212,0.3);">
                    <div class="card-title" style="color:#38bdf8;">✨ What you'll get</div>
                    <div style="font-size:13px;color:#94a3b8;line-height:1.8;margin:0;">
                        💰 &nbsp;<strong style="color:#f1f5f9;">Instant salary prediction</strong><br>
                        💡 &nbsp;<strong style="color:#f1f5f9;">Personalised growth tips</strong><br>
                        🗺️ &nbsp;<strong style="color:#f1f5f9;">Step-by-step career roadmap</strong><br>
                        📈 &nbsp;<strong style="color:#f1f5f9;">Industry trends & benchmarks</strong><br>
                        ⚖️ &nbsp;<strong style="color:#f1f5f9;">Compare vs market salaries</strong>
                    </div>
                </div>""", unsafe_allow_html=True)

            if st.button("🔍  Predict My Salary", key="predict_btn"):
                input_dict = {
                    "experience_years": exp, "skills_count": skills, "certifications": cert,
                    "job_title": job, "education_level": edu, "location": loc,
                    "industry": ind, "company_size": company, "remote_work": remote,
                }
                df = pd.DataFrame([input_dict])
                df["exp_squared"]    = df["experience_years"] ** 2
                df["skill_per_exp"]  = df["skills_count"] / (df["experience_years"] + 1)
                df["cert_per_skill"] = df["certifications"]  / (df["skills_count"] + 1)
                df["seniority"]      = pd.cut(df["experience_years"], bins=[0,2,5,10,20], labels=["Fresher","Junior","Mid","Senior"])
                df = pd.get_dummies(df)
                df = df.reindex(columns=columns, fill_value=0)
                num_cols = ["experience_years","skills_count","certifications","exp_squared","skill_per_exp","cert_per_skill"]
                existing_num_cols = [c for c in num_cols if c in df.columns]
                if existing_num_cols:
                    df[existing_num_cols] = scaler.transform(df[existing_num_cols])

                salary = int(model.predict(df)[0])
                st.session_state.last_prediction = salary
                st.session_state.last_inputs     = input_dict

                salary_fmt = f"₹{salary:,}"
                monthly    = f"₹{salary//12:,}"

                st.markdown(f"""
                <div class="result-hero">
                    <div class="result-hero-label">Your Estimated Annual Salary</div>
                    <div class="result-hero-amount">{salary_fmt}</div>
                    <div class="result-hero-sub">≈ {monthly} / month &nbsp;·&nbsp; Powered by K-Nearest Neighbors</div>
                </div>""", unsafe_allow_html=True)

                seniority  = "Fresher" if exp<=2 else ("Junior" if exp<=5 else ("Mid-Level" if exp<=10 else "Senior"))
                potential  = f"₹{int(salary*1.35):,}"
                percentile = min(95, max(30, int(30 + (salary/220000)*65)))
                m1,m2,m3,m4 = st.columns(4)
                with m1: st.markdown(f'<div class="metric-card"><div class="metric-label">Seniority Level</div><div class="metric-value" style="font-size:17px;">{seniority}</div></div>', unsafe_allow_html=True)
                with m2: st.markdown(f'<div class="metric-card"><div class="metric-label">Monthly Salary</div><div class="metric-value" style="font-size:17px;">{monthly}</div></div>', unsafe_allow_html=True)
                with m3: st.markdown(f'<div class="metric-card"><div class="metric-label">Growth Potential</div><div class="metric-value" style="font-size:17px;">{potential}</div><div class="metric-sub">↑ in 2–3 years</div></div>', unsafe_allow_html=True)
                with m4: st.markdown(f'<div class="metric-card"><div class="metric-label">Market Percentile</div><div class="metric-value" style="font-size:17px;">{percentile}th</div></div>', unsafe_allow_html=True)

                st.markdown("""
                <div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:12px;padding:14px 20px;margin-top:8px;">
                    <span style="font-size:14px;color:#10b981;font-weight:600;">✅ Prediction complete!</span>
                    <span style="font-size:13px;color:#94a3b8;"> &nbsp;·&nbsp; Now explore <strong style="color:#f1f5f9;">Insights</strong>, <strong style="color:#f1f5f9;">Roadmap</strong>, and <strong style="color:#f1f5f9;">Compare</strong> in the sidebar.</span>
                </div>""", unsafe_allow_html=True)

                st.balloons()

                chart_df = pd.DataFrame({
                    "Category": ["Experience", "Skills", "Certifications"],
                    "Value": [exp, skills, cert]
                })
                st.subheader("📊 Input Analysis")
                st.bar_chart(chart_df.set_index("Category"))

        st.markdown('</div>', unsafe_allow_html=True)

    # ===========================
    # INSIGHTS (File 2)
    # ===========================
    elif page == "💡 Insights":
        st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
        st.markdown('<div class="page-title">💡 Career Insights</div>', unsafe_allow_html=True)

        if not st.session_state.last_prediction:
            st.markdown('<div style="text-align:center;padding:60px;"><div style="font-size:48px;">💡</div><div style="font-size:18px;font-weight:600;color:#f8fafc;margin-top:12px;">Run a prediction first</div><div style="font-size:14px;color:#94a3b8;margin-top:8px;">Go to Salary Prediction tab to get started.</div></div>', unsafe_allow_html=True)
        else:
            inp    = st.session_state.last_inputs
            salary = st.session_state.last_prediction
            job    = inp["job_title"]; exp = inp["experience_years"]
            skills_c = inp["skills_count"]; cert = inp["certifications"]
            edu    = inp["education_level"]; ind = inp["industry"]

            # Salary boost tips
            def salary_boost_tips(job, exp, skills, cert, edu):
                tips = []
                if exp < 3:
                    tips.append(("🚀", "Build a strong portfolio", "Create 3–5 GitHub projects demonstrating real skills. At junior levels, projects matter more than years of experience.", "blue"))
                if 3 <= exp < 7:
                    tips.append(("📈", "Apply for senior roles now", "With your experience, senior roles pay 35–50% more. Rewrite your resume to highlight impact and outcomes.", "green"))
                if exp >= 7:
                    tips.append(("🏆", "Move into leadership", "7+ years of experience puts you in prime position for Lead/Manager roles — which pay 50–80% more.", "amber"))
                if skills < 8:
                    tips.append(("🛠️", "Expand your skill set", "Professionals with 10+ in-demand skills earn 28% more on average. Focus on cloud, data, or AI tools.", "rose"))
                if cert < 2:
                    tips.append(("📜", "Earn certifications", "AWS, Google Cloud, and PMP certifications add ₹10,000–₹25,000 to your annual salary.", "blue"))
                if edu in ["High School", "Diploma", "Other"]:
                    tips.append(("🎓", "Upskill with online courses", "Online Master's degrees or professional diplomas can boost salary by 15–20%.", "green"))
                tips.append(("🌍", "Target remote / global roles", "Remote roles at global companies pay 2–4x Indian market rates. Explore Toptal, Turing, and Remote.com.", "amber"))
                tips.append(("💬", "Negotiate your salary", "60% of professionals never negotiate. Research market rates then ask for 15–20% above the offer.", "rose"))
                return tips

            icon_map = {"blue":"insight-icon-blue","green":"insight-icon-green","amber":"insight-icon-amber","rose":"insight-icon-rose"}
            st.markdown('<div class="card"><div class="card-title">🚀 How to Increase Your Salary</div>', unsafe_allow_html=True)
            for icon, title, desc, color in salary_boost_tips(job, exp, skills_c, cert, edu):
                st.markdown(f"""
                <div class="insight-card">
                    <div class="insight-icon {icon_map[color]}">{icon}</div>
                    <div><div class="insight-title">{title}</div><div class="insight-desc">{desc}</div></div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            col_a, col_b = st.columns(2, gap="large")
            with col_a:
                top_skills    = SKILLS_BY_ROLE.get(job, SKILLS_BY_ROLE["Other"])[:6]
                salary_boosts = ["+₹8K–15K","+₹10K–20K","+₹6K–12K","+₹12K–25K","+₹5K–10K","+₹15K–30K"]
                st.markdown('<div class="card"><div class="card-title">🛠️ Top Skills to Learn Next</div>', unsafe_allow_html=True)
                for i, (sk, boost) in enumerate(zip(top_skills, salary_boosts)):
                    pct = 90 - i*10
                    st.markdown(f"""
                    <div class="compare-bar-wrap">
                        <div class="compare-bar-label">
                            <span style="font-size:13px;font-weight:500;color:#f1f5f9;">{sk}</span>
                            <span class="trend-up">{boost}/yr</span>
                        </div>
                        <div class="compare-bar-track">
                            <div class="compare-bar-fill" style="width:{pct}%;background:linear-gradient(90deg,#06b6d4,#3b82f6);"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_b:
                trend = INDUSTRY_TRENDS.get(ind, INDUSTRY_TRENDS["Other"])
                st.markdown('<div class="card"><div class="card-title">📈 Industry Salary Trends</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px;">
                    <div class="metric-card"><div class="metric-label">Industry Growth</div><div class="metric-value">{trend['growth']}</div><div class="metric-sub">↑ YoY</div></div>
                    <div class="metric-card"><div class="metric-label">Job Demand</div><div class="metric-value" style="font-size:16px;">{trend['demand']}</div></div>
                    <div class="metric-card"><div class="metric-label">Top Pay</div><div class="metric-value" style="font-size:16px;">{trend['top_pay']}</div></div>
                    <div class="metric-card"><div class="metric-label">Outlook</div><div class="metric-value" style="font-size:16px;">{trend['outlook']}</div></div>
                </div>
                <div style="background:rgba(6,182,212,0.1);border-radius:10px;padding:14px 16px;border:1px solid rgba(6,182,212,0.2);">
                    <div style="font-size:13px;color:#38bdf8;font-weight:600;">💡 {ind} sector insight</div>
                    <div style="font-size:13px;color:#94a3b8;margin-top:6px;line-height:1.5;">
                        Growing at <strong style="color:#f1f5f9;">{trend['growth']}</strong> annually with <strong style="color:#f1f5f9;">{trend['demand'].lower()}</strong> talent demand.
                        Top earners make <strong style="color:#f1f5f9;">{trend['top_pay']}</strong>. Now is an excellent time to upskill and negotiate confidently.
                    </div>
                </div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # What-If Simulator
            st.markdown('<div class="card"><div class="card-title">⚡ What-If Salary Simulator</div>', unsafe_allow_html=True)
            st.markdown('<p style="font-size:13px;color:#94a3b8;margin-bottom:16px;">Drag the sliders to see how improving one factor changes your salary.</p>', unsafe_allow_html=True)
            s1,s2,s3 = st.columns(3)
            with s1:
                extra_exp = st.slider("+ Years Experience", 0, 10, 2, key="sim_exp")
                sim_e = int(salary * (1 + extra_exp * 0.055))
                st.markdown(f'<div class="metric-card"><div class="metric-label">+{extra_exp} years experience</div><div class="metric-value">₹{sim_e:,}</div><div class="metric-sub trend-up">+₹{sim_e-salary:,}</div></div>', unsafe_allow_html=True)
            with s2:
                extra_sk = st.slider("+ Skills Added", 0, 10, 3, key="sim_skills")
                sim_s = int(salary * (1 + extra_sk * 0.028))
                st.markdown(f'<div class="metric-card"><div class="metric-label">+{extra_sk} skills</div><div class="metric-value">₹{sim_s:,}</div><div class="metric-sub trend-up">+₹{sim_s-salary:,}</div></div>', unsafe_allow_html=True)
            with s3:
                extra_c = st.slider("+ Certifications", 0, 5, 1, key="sim_cert")
                sim_c = int(salary * (1 + extra_c * 0.04))
                st.markdown(f'<div class="metric-card"><div class="metric-label">+{extra_c} certifications</div><div class="metric-value">₹{sim_c:,}</div><div class="metric-sub trend-up">+₹{sim_c-salary:,}</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ===========================
    # ROADMAP (File 2)
    # ===========================
    elif page == "🗺️ Roadmap":
        st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
        st.markdown('<div class="page-title">🗺️ Career Roadmap</div>', unsafe_allow_html=True)

        if not st.session_state.last_inputs:
            st.markdown('<div style="text-align:center;padding:60px;"><div style="font-size:48px;">🗺️</div><div style="font-size:18px;font-weight:600;color:#f8fafc;margin-top:12px;">Run a prediction first</div></div>', unsafe_allow_html=True)
        else:
            inp   = st.session_state.last_inputs
            job   = inp["job_title"]; exp = inp["experience_years"]
            steps = ROADMAP_BY_ROLE.get(job, ROADMAP_BY_ROLE["Other"])
            current_step = 0 if exp<=2 else (1 if exp<=5 else (2 if exp<=10 else (3 if exp<=15 else 4)))

            col_r, col_i = st.columns([3, 2], gap="large")
            with col_r:
                salary_ranges = ["₹40K–70K","₹70K–1.1L","₹1.1L–1.6L","₹1.6L–2.0L","₹2.0L+"]
                exp_ranges    = ["0–2 yrs","2–5 yrs","5–10 yrs","10–15 yrs","15+ yrs"]
                st.markdown(f'<div class="card"><div class="card-title">🗺️ Your Career Path — {job}</div>', unsafe_allow_html=True)
                for i, step in enumerate(steps):
                    if i < current_step:
                        dot = "step-dot-done"; badge = "badge-done"; btxt = "✓ Completed"
                    elif i == current_step:
                        dot = "step-dot-curr"; badge = "badge-current"; btxt = "📍 You are here"
                    else:
                        dot = "step-dot-next"; badge = "badge-future"; btxt = f"Next · {exp_ranges[i]}"
                    st.markdown(f"""
                    <div class="roadmap-step">
                        <div class="step-dot {dot}">{i+1}</div>
                        <div>
                            <div class="step-title">{step}</div>
                            <div class="step-sub">{exp_ranges[i]} &nbsp;·&nbsp; {salary_ranges[i]}</div>
                            <span class="step-badge {badge}">{btxt}</span>
                        </div>
                    </div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_i:
                curr = steps[current_step]
                nxt  = steps[min(current_step+1, len(steps)-1)]
                sk   = SKILLS_BY_ROLE.get(job, SKILLS_BY_ROLE["Other"])[:4]
                st.markdown(f"""
                <div class="card" style="background:linear-gradient(135deg,rgba(6,182,212,0.1),rgba(59,130,246,0.1));border-color:rgba(6,182,212,0.3);margin-bottom:12px;">
                    <div class="card-title" style="color:#38bdf8;">🎯 Your Next Goal</div>
                    <div style="font-size:19px;font-weight:700;color:#f8fafc;margin-bottom:8px;">{nxt}</div>
                    <div style="font-size:13px;color:#94a3b8;line-height:1.6;">
                        Currently at <strong style="color:#f1f5f9;">{curr}</strong>. Build 1–2 impactful projects,
                        master the skills below, and apply for senior roles to make the leap.
                    </div>
                </div>""", unsafe_allow_html=True)
                st.markdown('<div class="card"><div class="card-title">🛠️ Skills for Next Level</div>', unsafe_allow_html=True)
                for s in sk:
                    st.markdown(f'<span style="display:inline-block;background:rgba(6,182,212,0.15);color:#38bdf8;border-radius:99px;padding:5px 14px;font-size:13px;font-weight:500;margin:4px;border:1px solid rgba(6,182,212,0.3);">{s}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">📅 Estimated Timeline</div>
                    <div style="font-size:13px;color:#94a3b8;line-height:2.0;">
                        🟣 &nbsp;<strong style="color:#f1f5f9;">Now:</strong> {steps[current_step]}<br>
                        🟢 &nbsp;<strong style="color:#f1f5f9;">1–2 yrs:</strong> {steps[min(current_step+1,len(steps)-1)]}<br>
                        🔵 &nbsp;<strong style="color:#f1f5f9;">3–5 yrs:</strong> {steps[min(current_step+2,len(steps)-1)]}<br>
                        ⭐ &nbsp;<strong style="color:#f1f5f9;">5–8 yrs:</strong> {steps[-1]}
                    </div>
                </div>""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ===========================
    # DASHBOARD (File 2 style, File 1 data)
    # ===========================
    elif page == "📊 Dashboard":
        st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
        st.markdown('<div class="page-title">📊 Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-sub">Platform statistics and salary growth trends.</div>', unsafe_allow_html=True)

        m1,m2,m3 = st.columns(3)
        with m1: st.markdown('<div class="metric-card"><div class="metric-label">Total Users</div><div class="metric-value">150+</div></div>', unsafe_allow_html=True)
        with m2: st.markdown('<div class="metric-card"><div class="metric-label">Predictions Made</div><div class="metric-value">500+</div></div>', unsafe_allow_html=True)
        with m3: st.markdown('<div class="metric-card"><div class="metric-label">Model Accuracy</div><div class="metric-value">89%</div><div class="metric-sub">↑ KNN Model</div></div>', unsafe_allow_html=True)

        st.markdown("---")

        chart_data = pd.DataFrame({
            "Experience": [1,2,3,4,5,6,7],
            "Salary": [25000, 35000, 50000, 70000, 90000, 120000, 150000]
        })

        st.subheader("📈 Salary Growth by Experience")
        st.line_chart(chart_data, x="Experience", y="Salary")

        st.subheader("🌊 Salary Area Chart")
        st.area_chart(chart_data.set_index("Experience"))

        st.markdown('</div>', unsafe_allow_html=True)

    # ===========================
    # COMPARE (File 2)
    # ===========================
    elif page == "⚖️ Compare":
        st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
        st.markdown('<div class="page-title">⚖️ Compare Yourself</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-sub">See how your predicted salary stacks up against market benchmarks.</div>', unsafe_allow_html=True)

        if not st.session_state.last_prediction:
            st.markdown('<div style="text-align:center;padding:60px;"><div style="font-size:48px;">⚖️</div><div style="font-size:18px;font-weight:600;color:#f8fafc;margin-top:12px;">Run a prediction first</div></div>', unsafe_allow_html=True)
        else:
            salary = st.session_state.last_prediction
            inp    = st.session_state.last_inputs
            job    = inp["job_title"]
            base   = max(40000, salary - random.randint(10000,20000))
            top25  = int(salary * 1.22); top10 = int(salary * 1.48); top5 = int(salary * 1.75)
            max_v  = top5

            benchmarks = [
                ("Entry Level (0–2 yrs)",  int(base * 0.6),  "#334155"),
                ("Mid Level (3–6 yrs)",    int(base * 0.85), "#0ea5e9"),
                ("Your Salary",            salary,            "#06b6d4"),
                ("Top 25% in your role",   top25,             "#3b82f6"),
                ("Top 10% in your role",   top10,             "#6366f1"),
                ("Top 5% — Elite earner",  top5,              "#8b5cf6"),
            ]

            col1, col2 = st.columns([3, 2], gap="large")
            with col1:
                st.markdown(f'<div class="card"><div class="card-title">📊 Salary Benchmarks — {job}</div>', unsafe_allow_html=True)
                for label, val, color in benchmarks:
                    pct    = int((val / max_v) * 100)
                    is_you = label == "Your Salary"
                    st.markdown(f"""
                    <div class="compare-bar-wrap" style="{'background:rgba(6,182,212,0.1);border-radius:8px;padding:8px 10px;border:1px solid rgba(6,182,212,0.3);' if is_you else ''}">
                        <div class="compare-bar-label">
                            <span style="font-size:13px;font-weight:{'700' if is_you else '500'};color:{'#38bdf8' if is_you else '#f1f5f9'};">{'📍 ' if is_you else ''}{label}</span>
                            <span style="font-size:13px;font-weight:600;color:{'#38bdf8' if is_you else '#f1f5f9'};">₹{val:,}</span>
                        </div>
                        <div class="compare-bar-track"><div class="compare-bar-fill" style="width:{pct}%;background:{color};"></div></div>
                    </div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                pct_rank = min(95, max(25, int(30 + (salary/top5)*65)))
                gap      = max(0, top10 - salary)
                st.markdown(f"""
                <div class="card" style="text-align:center;margin-bottom:12px;">
                    <div class="card-title">🎯 Your Market Position</div>
                    <div style="font-size:52px;font-weight:800;color:#38bdf8;">{pct_rank}th</div>
                    <div style="font-size:14px;color:#94a3b8;">percentile in your field</div>
                    <div style="font-size:13px;color:#94a3b8;margin-top:12px;line-height:1.6;">
                        You earn more than <strong style="color:#f1f5f9;">{pct_rank}%</strong> of professionals in similar roles.
                        {'Focus on top skills to break into the top 10%.' if pct_rank < 90 else '🎉 You are among the elite earners!'}
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">💰 Gap to Top 10%</div>
                    <div style="font-size:24px;font-weight:800;color:#38bdf8;">{'Already there! 🎉' if gap==0 else f'₹{gap:,}'}</div>
                    <div style="font-size:13px;color:#94a3b8;margin-top:6px;line-height:1.5;">
                        {'You have already cracked the top 10% — excellent work!' if gap==0 else 'Add 2–3 high-demand skills and pursue senior roles to close this gap within 1–2 years.'}
                    </div>
                </div>""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ===========================
    # LEADERBOARD (File 2)
    # ===========================
    elif page == "🏆 Leaderboard":
        st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
        st.markdown('<div class="page-title">🏆 Leaderboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-sub">Top predicted salaries across all users (based on session predictions).</div>', unsafe_allow_html=True)

        # For pickle-based user system, build leaderboard from session
        # Show current user's best if available
        if st.session_state.last_prediction:
            salary = st.session_state.last_prediction
            job    = st.session_state.last_inputs.get("job_title","Professional") if st.session_state.last_inputs else "Professional"
            exp    = st.session_state.last_inputs.get("experience_years",0) if st.session_state.last_inputs else 0

            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(6,182,212,0.1),rgba(59,130,246,0.1));border:1px solid rgba(6,182,212,0.3);
                        border-radius:14px;padding:18px 24px;margin-bottom:20px;
                        display:flex;align-items:center;justify-content:space-between;">
                <div>
                    <div style="font-size:11px;color:#38bdf8;font-weight:700;text-transform:uppercase;letter-spacing:.8px;">Your Best Prediction</div>
                    <div style="font-size:22px;font-weight:800;color:#f8fafc;">{st.session_state.username} &nbsp;<span style="font-size:14px;color:#94a3b8;font-weight:400;">{job} · {exp} yrs exp</span></div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:11px;color:#38bdf8;font-weight:700;text-transform:uppercase;">Predicted Salary</div>
                    <div style="font-size:22px;font-weight:800;color:#38bdf8;">₹{salary:,}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        # Example leaderboard
        sample_lb = [
            {"name": "Rahul S.", "job": "AI Engineer",      "exp": 8,  "salary": 195000},
            {"name": "Priya M.", "job": "Data Scientist",   "exp": 6,  "salary": 175000},
            {"name": "Arjun K.", "job": "Cloud Engineer",   "exp": 10, "salary": 168000},
            {"name": "Sneha R.", "job": "Software Engineer","exp": 7,  "salary": 155000},
            {"name": "Vikram T.","job": "DevOps Engineer",  "exp": 9,  "salary": 148000},
        ]
        medals  = ["🥇","🥈","🥉"]
        row_cls = ["gold","silver","bronze"]

        st.markdown('<div class="card"><div class="card-title">🏆 Top Earners</div>', unsafe_allow_html=True)
        for i, entry in enumerate(sample_lb):
            medal = medals[i] if i<3 else f"#{i+1}"
            rcls  = row_cls[i] if i<3 else ""
            st.markdown(f"""
            <div class="lb-row {rcls}">
                <div class="lb-rank">{medal}</div>
                <div style="flex:1;">
                    <div class="lb-name">{entry['name']}</div>
                    <div class="lb-role">{entry['job']} &nbsp;·&nbsp; {entry['exp']} yrs exp</div>
                </div>
                <div class="lb-salary">₹{entry['salary']:,}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# FOOTER
# =========================
st.markdown("""
<div class="footer">
Made with ❤️ using Streamlit
</div>
""", unsafe_allow_html=True)
