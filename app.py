# =========================
# IMPORT LIBRARIES
# =========================
import streamlit as st
import pickle
import pandas as pd
import hashlib
import json
import os
import re
from datetime import datetime

# =========================
# PAGE CONFIG (must be first)
# =========================
st.set_page_config(
    page_title="SalaryIQ — Predict Your Worth",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# LOAD MODEL FILES
# =========================
model   = pickle.load(open("knn_model.pkl", "rb"))
scaler  = pickle.load(open("scaler.pkl",    "rb"))
columns = pickle.load(open("columns.pkl",   "rb"))

# =========================
# HELPER: EXTRACT OPTIONS
# =========================
def get_options(prefix):
    opts = [col.replace(prefix, "") for col in columns if col.startswith(prefix)]
    return sorted(list(set(opts)))

job_options     = ["Other"] + get_options("job_title_")
edu_options     = ["Other"] + get_options("education_level_")
loc_options     = ["Other"] + get_options("location_")
ind_options     = ["Other"] + get_options("industry_")
company_options = ["Other"] + get_options("company_size_")
remote_options  = ["Other"] + get_options("remote_work_")

# =========================
# USER STORAGE  (users.json)
# =========================
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, email, password):
    users = load_users()
    if email.lower() in users:
        return False, "An account with this email already exists."
    users[email.lower()] = {
        "name": name,
        "email": email.lower(),
        "password": hash_password(password),
        "created_at": datetime.now().isoformat()
    }
    save_users(users)
    return True, "Account created successfully!"

def login_user(email, password):
    users = load_users()
    if email.lower() not in users:
        return False, "No account found with this email."
    if users[email.lower()]["password"] != hash_password(password):
        return False, "Incorrect password. Please try again."
    return True, users[email.lower()]["name"]

def is_valid_email(email):
    return re.match(r"^[\w\.\-]+@[\w\.\-]+\.\w{2,}$", email) is not None

# =========================
# SESSION STATE INIT
# =========================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "auth_page" not in st.session_state: st.session_state.auth_page = "login"

# =========================
# GLOBAL STYLES
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Outfit:wght@300;400;500;600&display=swap');

/* ── Base reset ── */
html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
#MainMenu, footer, header, .stDeployButton { visibility: hidden !important; display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none !important; }
.stApp { background: #05050f !important; }

/* =========================================================
   AUTH PAGES
   ========================================================= */
.auth-bg {
    min-height: 100vh;
    background: #05050f;
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
    width: 700px; height: 700px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(79,70,229,0.18) 0%, transparent 65%);
    pointer-events: none; z-index: 0;
}
.auth-bg::after {
    content: '';
    position: fixed;
    bottom: -180px; right: -180px;
    width: 600px; height: 600px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(16,185,129,0.12) 0%, transparent 65%);
    pointer-events: none; z-index: 0;
}

/* Card */
.auth-card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 52px 48px;
    width: 100%; max-width: 480px;
    position: relative; z-index: 1;
    box-shadow: 0 32px 80px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.08);
}

/* Logo */
.auth-logo {
    font-family: 'Syne', sans-serif !important;
    font-size: 22px; font-weight: 800;
    color: #fff; letter-spacing: -0.3px;
    margin-bottom: 36px;
    display: flex; align-items: center; gap: 10px;
}
.auth-logo-dot { color: #4f46e5; }

/* Heading */
.auth-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 36px; font-weight: 800;
    color: #ffffff; letter-spacing: -1px;
    line-height: 1.1; margin-bottom: 8px;
}
.auth-title span {
    background: linear-gradient(135deg, #818cf8 0%, #10b981 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.auth-subtitle {
    font-size: 15px; color: rgba(255,255,255,0.45);
    margin-bottom: 36px; font-weight: 400;
}

/* Stats strip */
.auth-stats {
    display: flex; gap: 24px;
    margin-bottom: 36px; padding: 20px 0;
    border-top: 1px solid rgba(255,255,255,0.06);
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.stat-item { flex: 1; text-align: center; }
.stat-value {
    font-family: 'Syne', sans-serif !important;
    font-size: 22px; font-weight: 800;
    background: linear-gradient(135deg, #818cf8, #10b981);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.stat-label {
    font-size: 11px; color: rgba(255,255,255,0.35);
    margin-top: 2px; text-transform: uppercase; letter-spacing: 0.8px;
}

/* Divider */
.auth-divider {
    text-align: center; color: rgba(255,255,255,0.25);
    font-size: 13px; margin: 20px 0; position: relative;
}
.auth-divider::before, .auth-divider::after {
    content: ''; position: absolute; top: 50%;
    width: calc(50% - 28px); height: 1px;
    background: rgba(255,255,255,0.08);
}
.auth-divider::before { left: 0; }
.auth-divider::after  { right: 0; }

/* =========================================================
   TEXT INPUTS
   ========================================================= */
.stTextInput > div > div {
    background: #0d0d20 !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 12px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 15px !important;
    transition: border-color 0.2s;
}
.stTextInput > div > div:focus-within {
    border-color: rgba(79,70,229,0.8) !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.18) !important;
}
.stTextInput input,
.stTextInput > div > div > input {
    background: #0d0d20 !important;
    background-color: #0d0d20 !important;
    -webkit-box-shadow: 0 0 0px 1000px #0d0d20 inset !important;
    box-shadow: 0 0 0px 1000px #0d0d20 inset !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 15px !important;
    caret-color: #818cf8 !important;
    border: none !important;
    outline: none !important;
}
.stTextInput input:-webkit-autofill,
.stTextInput input:-webkit-autofill:hover,
.stTextInput input:-webkit-autofill:focus,
.stTextInput input:-webkit-autofill:active {
    -webkit-box-shadow: 0 0 0px 1000px #0d0d20 inset !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #818cf8 !important;
}
.stTextInput input::placeholder { color: rgba(255,255,255,0.30) !important; }

/* =========================================================
   NUMBER INPUTS  —  dark box + white text
   ========================================================= */
.stNumberInput > div {
    background: transparent !important;
}
.stNumberInput > div > div {
    background: #0d0d20 !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 12px !important;
}
.stNumberInput input,
.stNumberInput > div > div > input,
input[type="number"] {
    background: #0d0d20 !important;
    background-color: #0d0d20 !important;
    -webkit-box-shadow: 0 0 0px 1000px #0d0d20 inset !important;
    box-shadow: 0 0 0px 1000px #0d0d20 inset !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 15px !important;
    caret-color: #818cf8 !important;
    border: none !important;
    outline: none !important;
}
.stNumberInput input:-webkit-autofill,
.stNumberInput input:-webkit-autofill:hover,
.stNumberInput input:-webkit-autofill:focus,
.stNumberInput input:-webkit-autofill:active {
    -webkit-box-shadow: 0 0 0px 1000px #0d0d20 inset !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #818cf8 !important;
}
.stNumberInput > div > div:focus-within {
    border-color: rgba(79,70,229,0.8) !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.18) !important;
}
.stNumberInput button {
    background: transparent !important;
    color: rgba(255,255,255,0.5) !important;
    border: none !important;
}
.stNumberInput button:hover {
    background: rgba(255,255,255,0.08) !important;
    color: #fff !important;
}

/* =========================================================
   SELECTBOX  —  closed / trigger state
   ========================================================= */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 12px !important;
    color: #fff !important;
    font-family: 'Outfit', sans-serif !important;
}
.stSelectbox > div > div:focus-within {
    border-color: rgba(79,70,229,0.6) !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.15) !important;
}

/* Selected value text */
.stSelectbox [data-baseweb="select"] > div,
.stSelectbox [data-baseweb="select"] > div > div,
.stSelectbox [data-baseweb="select"] span {
    color: #ffffff !important;
    background: transparent !important;
    font-family: 'Outfit', sans-serif !important;
}

/* =========================================================
   SELECTBOX  —  open dropdown panel & options
   ========================================================= */
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="menu"],
ul[data-baseweb="menu"],
[role="listbox"] {
    background: #13132b !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    box-shadow: 0 16px 48px rgba(0,0,0,0.7) !important;
}

/* Every option row */
[data-baseweb="menu"] li,
[data-baseweb="menu"] [role="option"],
[role="listbox"] li,
[role="option"] {
    background: #13132b !important;
    color: #e2e2f0 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 14px !important;
}

/* Hovered / selected option */
[data-baseweb="menu"] li:hover,
[data-baseweb="menu"] [role="option"]:hover,
[role="option"]:hover,
[data-baseweb="menu"] li[aria-selected="true"],
[role="option"][aria-selected="true"] {
    background: rgba(79,70,229,0.28) !important;
    color: #ffffff !important;
}

/* =========================================================
   ALL FORM LABELS
   ========================================================= */
.stSelectbox label,
.stNumberInput label,
.stTextInput label {
    color: rgba(255,255,255,0.55) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}

/* =========================================================
   BUTTONS
   ========================================================= */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 24px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    letter-spacing: 0.2px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px rgba(79,70,229,0.35) !important;
    margin-top: 4px !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 28px rgba(79,70,229,0.45) !important;
    background: linear-gradient(135deg, #5b52f0 0%, #8b47f5 100%) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* =========================================================
   PASSWORD STRENGTH BAR
   ========================================================= */
.pw-strength-wrap {
    height: 4px;
    background: rgba(255,255,255,0.08);
    border-radius: 99px; overflow: hidden;
}
.pw-strength-bar {
    height: 100%; border-radius: 99px;
    transition: width 0.3s, background 0.3s;
}

/* =========================================================
   MAIN APP  —  header
   ========================================================= */
.app-header {
    background: rgba(255,255,255,0.03);
    border-bottom: 1px solid rgba(255,255,255,0.07);
    padding: 16px 40px;
    display: flex; align-items: center; justify-content: space-between;
}
.app-logo-text {
    font-family: 'Syne', sans-serif !important;
    font-size: 20px; font-weight: 800; color: #fff;
}
.app-logo-text span { color: #818cf8; }
.app-user-chip {
    background: rgba(79,70,229,0.15);
    border: 1px solid rgba(79,70,229,0.3);
    border-radius: 99px; padding: 6px 16px;
    font-size: 13px; color: #a5b4fc; font-weight: 500;
}

/* =========================================================
   MAIN APP  —  headings & text
   ========================================================= */
h1 {
    font-family: 'Syne', sans-serif !important;
    color: #fff !important;
    font-size: 32px !important;
    font-weight: 800 !important;
    letter-spacing: -0.8px !important;
}
h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: rgba(255,255,255,0.85) !important;
    font-weight: 700 !important;
}
p, li, div { color: rgba(255,255,255,0.75); }

/* =========================================================
   MAIN APP  —  section cards
   ========================================================= */
.section-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 28px 24px;
    margin-bottom: 16px;
}
.section-card-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 13px; font-weight: 700;
    color: #818cf8;
    text-transform: uppercase; letter-spacing: 1.2px;
    margin-bottom: 16px;
}

/* =========================================================
   MAIN APP  —  prediction result card
   ========================================================= */
.result-card {
    background: linear-gradient(135deg, rgba(79,70,229,0.2), rgba(16,185,129,0.12));
    border: 1px solid rgba(79,70,229,0.3);
    border-radius: 20px; padding: 32px;
    text-align: center; margin-top: 24px;
}
.result-amount {
    font-family: 'Syne', sans-serif !important;
    font-size: 52px; font-weight: 800;
    background: linear-gradient(135deg, #818cf8 0%, #10b981 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.result-label {
    font-size: 14px; color: rgba(255,255,255,0.45);
    margin-top: 4px; letter-spacing: 1px; text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)


# =========================
# ── LOGIN PAGE ──
# =========================
def show_login():
    st.markdown("""
    <div class="auth-bg">
      <div class="auth-card">
        <div class="auth-logo">💼 <span>Salary<span class="auth-logo-dot">IQ</span></span></div>
        <div class="auth-title">Welcome<br><span>back.</span></div>
        <div class="auth-subtitle">Sign in to access your salary predictor</div>
        <div class="auth-stats">
          <div class="stat-item">
            <div class="stat-value">95%</div>
            <div class="stat-label">Accuracy</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">50K+</div>
            <div class="stat-label">Predictions</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">120+</div>
            <div class="stat-label">Job Roles</div>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<div style='height:340px'></div>", unsafe_allow_html=True)

        email    = st.text_input("Email address", placeholder="you@example.com",     key="login_email")
        password = st.text_input("Password",      placeholder="Enter your password", key="login_password", type="password")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("Sign In →", key="login_btn"):
            if not email or not password:
                st.error("Please fill in all fields.")
            elif not is_valid_email(email):
                st.error("Please enter a valid email address.")
            else:
                ok, result = login_user(email, password)
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.user_name = result
                    st.rerun()
                else:
                    st.error(result)

        st.markdown('<div class="auth-divider">or</div>', unsafe_allow_html=True)

        if st.button("Sign Up — Create an Account", key="goto_signup"):
            st.session_state.auth_page = "signup"
            st.rerun()

        st.markdown("""
        <div style="margin-top:16px; text-align:center; font-size:12px;
                    color:rgba(255,255,255,0.25);">
            🔒 Your data is stored securely and never shared.
        </div>
        """, unsafe_allow_html=True)


# =========================
# ── SIGN UP PAGE ──
# =========================
def show_signup():
    st.markdown("""
    <div class="auth-bg">
      <div class="auth-card">
        <div class="auth-logo">💼 <span>Salary<span class="auth-logo-dot">IQ</span></span></div>
        <div class="auth-title">Sign<br><span>Up.</span></div>
        <div class="auth-subtitle">Join thousands discovering their market value</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<div style='height:270px'></div>", unsafe_allow_html=True)

        name     = st.text_input("Full Name",        placeholder="John Doe",             key="signup_name")
        email    = st.text_input("Email Address",    placeholder="you@example.com",      key="signup_email")
        password = st.text_input("Password",         placeholder="Min. 8 characters",    key="signup_password", type="password")
        confirm  = st.text_input("Confirm Password", placeholder="Repeat your password", key="signup_confirm",  type="password")

        # Live password strength bar
        if password:
            strength = 0
            hints = []
            if len(password) >= 8:                    strength += 1
            else:                                     hints.append("8+ characters")
            if re.search(r"[A-Z]", password):         strength += 1
            else:                                     hints.append("uppercase letter")
            if re.search(r"\d", password):            strength += 1
            else:                                     hints.append("a number")
            if re.search(r"[^A-Za-z0-9]", password): strength += 1
            else:                                     hints.append("special character")

            bar_colors = ["#ef4444", "#f97316", "#eab308", "#10b981"]
            bar_labels = ["Weak", "Fair", "Good", "Strong"]
            bar_widths = [25, 50, 75, 100]
            idx        = min(strength - 1, 3) if strength > 0 else 0
            hint_text  = "" if strength == 4 else " — add " + ", ".join(hints[:2])

            st.markdown(f"""
            <div style='margin-top:-6px; margin-bottom:14px;'>
              <div class='pw-strength-wrap'>
                <div class='pw-strength-bar'
                     style='width:{bar_widths[idx]}%; background:{bar_colors[idx]};'></div>
              </div>
              <div style='font-size:12px; color:{bar_colors[idx]};
                          margin-top:5px; font-weight:500;'>
                {bar_labels[idx]} password{hint_text}
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("Sign Up →", key="signup_btn"):
            if not all([name, email, password, confirm]):
                st.error("Please fill in all fields.")
            elif not is_valid_email(email):
                st.error("Please enter a valid email address.")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                ok, msg = register_user(name.strip(), email.strip(), password)
                if ok:
                    # Auto-login straight into the app after sign up
                    st.session_state.logged_in = True
                    st.session_state.user_name = name.strip()
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown('<div class="auth-divider">or</div>', unsafe_allow_html=True)

        if st.button("Already have an account? Sign In", key="goto_login"):
            st.session_state.auth_page = "login"
            st.rerun()


# =========================
# ── MAIN PREDICTION APP ──
# =========================
def show_app():
    # Header
    st.markdown(f"""
    <div class="app-header">
        <div class="app-logo-text">Salary<span>IQ</span></div>
        <div class="app-user-chip">👤 {st.session_state.user_name}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding: 32px 40px;'>", unsafe_allow_html=True)
    st.markdown("""
    <h1 style='margin-bottom:4px;'>💼 Salary Prediction</h1>
    <p style='color:rgba(255,255,255,0.4); font-size:15px; margin-bottom:32px;'>
        Fill in your profile and we'll predict your market salary using KNN.
    </p>
    """, unsafe_allow_html=True)

    # Two-column input form
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("<div class='section-card'><div class='section-card-title'>📊 Experience & Skills</div>", unsafe_allow_html=True)
        exp    = st.number_input("Experience (years)", 0, 30, key="exp")
        skills = st.number_input("Skills Count",       0, 50, key="skills")
        cert   = st.number_input("Certifications",     0, 20, key="cert")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-card'><div class='section-card-title'>🎓 Education & Role</div>", unsafe_allow_html=True)
        job = st.selectbox("Job Role",  job_options, key="job")
        edu = st.selectbox("Education", edu_options, key="edu")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='section-card'><div class='section-card-title'>🏢 Company & Location</div>", unsafe_allow_html=True)
        loc     = st.selectbox("Location",     loc_options,     key="loc")
        ind     = st.selectbox("Industry",     ind_options,     key="ind")
        company = st.selectbox("Company Size", company_options, key="company")
        remote  = st.selectbox("Remote Work",  remote_options,  key="remote")
        st.markdown("</div>", unsafe_allow_html=True)

    # Predict button
    st.markdown("<div style='max-width:320px; margin: 0 auto;'>", unsafe_allow_html=True)
    predict_clicked = st.button("🔍 Predict My Salary", key="predict_btn")
    st.markdown("</div>", unsafe_allow_html=True)

    if predict_clicked:
        input_dict = {
            "experience_years": exp,
            "skills_count":     skills,
            "certifications":   cert,
            "job_title":        job,
            "education_level":  edu,
            "location":         loc,
            "industry":         ind,
            "company_size":     company,
            "remote_work":      remote,
        }
        input_df = pd.DataFrame([input_dict])

        # Feature Engineering
        input_df["exp_squared"]    = input_df["experience_years"] ** 2
        input_df["skill_per_exp"]  = input_df["skills_count"] / (input_df["experience_years"] + 1)
        input_df["cert_per_skill"] = input_df["certifications"] / (input_df["skills_count"] + 1)
        input_df["seniority"]      = pd.cut(
            input_df["experience_years"],
            bins=[0, 2, 5, 10, 20],
            labels=["Fresher", "Junior", "Mid", "Senior"]
        )

        # Dummies + Align
        input_df = pd.get_dummies(input_df)
        input_df = input_df.reindex(columns=columns, fill_value=0)

        # Scale
        num_cols = ["experience_years", "skills_count", "certifications",
                    "exp_squared", "skill_per_exp", "cert_per_skill"]
        input_df[num_cols] = scaler.transform(input_df[num_cols])

        # Predict
        prediction = model.predict(input_df)
        salary     = int(prediction[0])
        salary_fmt = f"₹{salary:,}"

        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Estimated Annual Salary</div>
            <div class="result-amount">{salary_fmt}</div>
            <div style='color:rgba(255,255,255,0.35); font-size:13px; margin-top:12px;'>
                Predicted using K-Nearest Neighbors &middot; Based on your inputs
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.ballons()

    # Sign Out
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    _, _, right_col = st.columns([3, 1, 1])
    with right_col:
        if st.button("Sign Out", key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.user_name = ""
            st.session_state.auth_page = "login"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# ── ROUTER ──
# =========================
if st.session_state.logged_in:
    show_app()
elif st.session_state.auth_page == "signup":
    show_signup()
else:
    show_login()
