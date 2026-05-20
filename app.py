# =========================
# IMPORT LIBRARIES
# =========================
import streamlit as st
import pickle
import pandas as pd
import numpy as np
import os

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Salary Prediction App",
    page_icon="💼",
    layout="wide"
)

# =========================
# USER DATABASE FUNCTIONS
# =========================
USER_FILE = "users.pkl"

def load_users():

    if os.path.exists(USER_FILE):

        with open(USER_FILE, "rb") as f:
            return pickle.load(f)

    return {
        "admin": "1234",
        "aparna": "aparna123"
    }

def save_users(users):

    with open(USER_FILE, "wb") as f:
        pickle.dump(users, f)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>

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

/* Text Visibility */
p, li, label, div {
    color: #f1f5f9 !important;
    font-size: 16px;
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

/* Cards */
.card {
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

</style>
""", unsafe_allow_html=True)

# =========================
# NAVBAR
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

# =========================
# LOGIN FUNCTION
# =========================
def login():

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("🔐 Login Page")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username in st.session_state.users and \
           st.session_state.users[username] == password:

            st.session_state.logged_in = True
            st.session_state.username = username

            st.success(f"Welcome {username} 🎉")
            st.rerun()

        else:
            st.error("Invalid Username or Password")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# SIGNUP FUNCTION
# =========================
def signup():

    st.markdown('<div class="card">', unsafe_allow_html=True)

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

            # SAVE USERS PERMANENTLY
            save_users(st.session_state.users)

            st.success("Account Created Successfully ✅")
            st.info("Now you can login anytime")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# AUTH PAGE
# =========================
if not st.session_state.logged_in:

    menu = st.sidebar.radio(
        "Menu",
        ["Login", "Sign Up"]
    )

    if menu == "Login":
        login()

    else:
        signup()

# =========================
# MAIN APP
# =========================
else:

    # =========================
    # SIDEBAR
    # =========================
    st.sidebar.title("📌 Navigation")

    page = st.sidebar.radio(
        "Go To",
        [
            "🏠 Home",
            "💰 Salary Prediction",
            "📊 Dashboard",
            "📈 Insights",
            "ℹ About"
        ]
    )

    st.sidebar.success(
        f"Logged in as {st.session_state.username}"
    )

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.rerun()

    # =========================
    # LOAD MODEL
    # =========================
    model = pickle.load(open("knn_model.pkl", "rb"))
    scaler = pickle.load(open("scaler.pkl", "rb"))
    columns = pickle.load(open("columns.pkl", "rb"))

    # =========================
    # HOME PAGE
    # =========================
    if page == "🏠 Home":

        st.title("Welcome to Salary Prediction App")
      # =========================
        # HOME PAGE CSS
        # =========================
        st.markdown("""
        <style>

        .hero-box{
            background: linear-gradient(
            135deg,
            #0f172a,
            #1e3a8a,
            #2563eb
            );

            padding:50px;
            border-radius:30px;
            box-shadow:0px 10px 30px rgba(0,0,0,0.5);
        }

        .hero-title{
            font-size:65px;
            font-weight:800;
            color:white;
            line-height:1.1;
        }

        .hero-text{
            font-size:20px;
            color:#dbeafe;
            margin-top:20px;
        }

        .feature-card{
            background:rgba(255,255,255,0.08);
            padding:25px;
            border-radius:20px;
            text-align:center;
            backdrop-filter: blur(10px);
            transition:0.3s;
            border:1px solid rgba(255,255,255,0.1);
        }

        .feature-card:hover{
            transform:translateY(-5px);
        }

        .feature-title{
            color:white;
            font-size:22px;
            font-weight:bold;
        }

        .feature-text{
            color:#cbd5e1;
            margin-top:10px;
        }

        .stats-card{
            background:rgba(255,255,255,0.05);
            padding:30px;
            border-radius:20px;
            text-align:center;
            margin-top:20px;
        }

        .stats-number{
            font-size:40px;
            color:#38bdf8;
            font-weight:bold;
        }

        .stats-label{
            color:white;
            font-size:18px;
        }

        </style>
        """, unsafe_allow_html=True)

        # YOUR REMAINING CODE SAME AS BEFORE
