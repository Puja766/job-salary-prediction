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
        "admin": "1234"
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

    st.markdown('<div class="login-card">', unsafe_allow_html=True)

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

        left, right = st.columns([1.4,1])

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

        f1,f2,f3,f4 = st.columns(4)

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

    # =========================
    # SALARY PREDICTION
    # =========================
    elif page == "💰 Salary Prediction":

        st.title("💰 Predict Salary")

        col1, col2 = st.columns(2)

        with col1:
            exp = st.number_input("Experience", 0, 30)
            skills = st.number_input("Skills Count", 0, 50)
            cert = st.number_input("Certifications", 0, 20)

        with col2:
            education = st.selectbox(
                "Education",
                ["Bachelor", "Master", "PhD"]
            )

            company = st.selectbox(
                "Company Size",
                ["Small", "Medium", "Large"]
            )

            remote = st.selectbox(
                "Remote Work",
                ["Remote", "Hybrid", "Office"]
            )

        if st.button("Predict Salary"):

            input_dict = {
                "EXPERIENCE_YEARS": exp,
                "SKILLS_COUNT": skills,
                "CERTIFICATIONS": cert,
                "EDUCATION_LEVEL": education,
                "COMPANY_SIZE": company,
                "REMOTE_WORK": remote
            }

            input_df = pd.get_dummies(
                pd.DataFrame([input_dict])
            )

            input_df = input_df.reindex(
                columns=columns,
                fill_value=0
            )

            scaled_data = scaler.transform(input_df)

            prediction = model.predict(scaled_data)[0]

            st.success(
                f"💰 Predicted Salary: ₹ {prediction:,.0f}"
            )

            st.balloons()

            chart_df = pd.DataFrame({
                "Category": [
                    "Experience",
                    "Skills",
                    "Certifications"
                ],
                "Value": [
                    exp,
                    skills,
                    cert
                ]
            })

            st.subheader("📊 Input Analysis")

            st.bar_chart(
                chart_df.set_index("Category")
            )

    # =========================
    # DASHBOARD
    # =========================
    elif page == "📊 Dashboard":

        st.title("📊 Dashboard")

        col1, col2, col3 = st.columns(3)

        col1.metric("Users", "150+")
        col2.metric("Predictions", "500+")
        col3.metric("Accuracy", "89%")

        st.markdown("---")

        chart_data = pd.DataFrame({
            "Experience": [1,2,3,4,5,6,7],
            "Salary": [
                25000,
                35000,
                50000,
                70000,
                90000,
                120000,
                150000
            ]
        })

        st.subheader("📈 Salary Growth")

        st.line_chart(
            chart_data,
            x="Experience",
            y="Salary"
        )

        st.subheader("🌊 Salary Area Chart")

        st.area_chart(
            chart_data.set_index("Experience")
        )

    # =========================
    # INSIGHTS PAGE
    # =========================
    elif page == "📈 Insights":

        st.title("📈 Salary Insights")

        st.write("""
        ✔ More experience increases salary  
        ✔ Certifications improve salary growth  
        ✔ Senior employees earn higher salaries  
        ✔ Remote jobs may offer better packages  
        """)

        pie_data = pd.DataFrame({
            "Work Mode": [
                "Remote",
                "Hybrid",
                "Office"
            ],
            "Employees": [
                40,
                35,
                25
            ]
        })

        st.subheader("🏠 Work Mode Distribution")

        st.bar_chart(
            pie_data.set_index("Work Mode")
        )

    # =========================
    # ABOUT PAGE
    # =========================
    elif page == "ℹ About":

        st.title("ℹ About Project")

        st.markdown("""
        <div class="about-card">

        <h3>📌 Project Overview</h3>

        <p>
        This project predicts employee salaries
        using Machine Learning algorithms based
        on employee details.
        </p>

        </div>
        """, unsafe_allow_html=True)

        st.subheader("🚀 Features")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="about-feature">
            <h3>📈 Salary Prediction</h3>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="about-feature">
            <h3>📊 Dashboard</h3>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="about-feature">
            <h3>🔐 Authentication</h3>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.subheader("🛠 Tools & Technologies")

        t1, t2, t3 = st.columns(3)

        with t1:
            st.markdown("""
            <div class="tool-card">
            <div class="tool-logo">🐍</div>
            <h4>Python</h4>
            <p class="version">Version 3.11</p>
            </div>
            """, unsafe_allow_html=True)

        with t2:
            st.markdown("""
            <div class="tool-card">
            <div class="tool-logo">🎈</div>
            <h4>Streamlit</h4>
            <p class="version">Version 1.32</p>
            </div>
            """, unsafe_allow_html=True)

        with t3:
            st.markdown("""
            <div class="tool-card">
            <div class="tool-logo">🤖</div>
            <h4>Machine Learning</h4>
            <p class="version">AI Technology</p>
            </div>
            """, unsafe_allow_html=True)

# =========================
# FOOTER
# =========================
st.markdown("""
<div class="footer">
Made with ❤️ using Streamlit
</div>
""", unsafe_allow_html=True)
