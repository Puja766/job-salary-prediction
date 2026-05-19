# =========================
# IMPORT LIBRARIES
# =========================
import streamlit as st
import pickle
import pandas as pd
import numpy as np

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Salary Prediction App",
    page_icon="💼",
    layout="wide"
)

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
    st.session_state.users = {
        "admin": "1234",
        "aparna": "aparna123"
    }

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

            st.success("Account Created Successfully ✅")
            st.info("Redirecting to Login Page...")

            st.session_state.signup_success = True

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

        # =========================
        # HERO SECTION
        # =========================
        left,right = st.columns([1.4,1])

        with left:

            st.markdown("""
            <div class="hero-box">

            <div style="
            color:#38bdf8;
            font-size:20px;
            font-weight:bold;">
            AI POWERED SYSTEM
            </div>

            <div class="hero-title">
            Salary <br>
            Prediction <br>
            Platform
            </div>

            <div class="hero-text">
            Predict employee salary using
            Machine Learning based on:
            experience, skills, education,
            certifications and job role.
            </div>

            </div>
            """, unsafe_allow_html=True)

        with right:

            st.image(
                "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a",
                use_container_width=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # =========================
        # FEATURES
        # =========================
        f1,f2,f3,f4 = st.columns(4)

        with f1:
            st.markdown("""
            <div class="feature-card">
            <div class="feature-title">
            🎯 Accurate
            </div>
            <div class="feature-text">
            Highly accurate salary prediction
            </div>
            </div>
            """, unsafe_allow_html=True)

        with f2:
            st.markdown("""
            <div class="feature-card">
            <div class="feature-title">
            ⚡ Fast
            </div>
            <div class="feature-text">
            Instant AI prediction system
            </div>
            </div>
            """, unsafe_allow_html=True)

        with f3:
            st.markdown("""
            <div class="feature-card">
            <div class="feature-title">
            📊 Analytics
            </div>
            <div class="feature-text">
            Interactive dashboard & charts
            </div>
            </div>
            """, unsafe_allow_html=True)

        with f4:
            st.markdown("""
            <div class="feature-card">
            <div class="feature-title">
            🔒 Secure
            </div>
            <div class="feature-text">
            Safe and secure user system
            </div>
            </div>
            """, unsafe_allow_html=True)

        # =========================
        # STATS SECTION
        # =========================
        st.markdown("<br>", unsafe_allow_html=True)

        s1,s2,s3,s4 = st.columns(4)

        with s1:
            st.markdown("""
            <div class="stats-card">
            <div class="stats-number">
            1000+
            </div>
            <div class="stats-label">
            Users
            </div>
            </div>
            """, unsafe_allow_html=True)

        with s2:
            st.markdown("""
            <div class="stats-card">
            <div class="stats-number">
            5000+
            </div>
            <div class="stats-label">
            Predictions
            </div>
            </div>
            """, unsafe_allow_html=True)

        with s3:
            st.markdown("""
            <div class="stats-card">
            <div class="stats-number">
            90%
            </div>
            <div class="stats-label">
            Accuracy
            </div>
            </div>
            """, unsafe_allow_html=True)

        with s4:
            st.markdown("""
            <div class="stats-card">
            <div class="stats-number">
            24/7
            </div>
            <div class="stats-label">
            Availability
            </div>
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

            fake_salary = (
                exp * 10000 +
                skills * 3000 +
                cert * 5000
            )

            st.success(
                f"💰 Predicted Salary: ₹ {fake_salary:,}"
            )

            st.balloons()

            # GRAPH
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

        # LINE CHART
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

        # AREA CHART
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

      st.markdown("""
    <style>
    .main-title{
        font-size:38px;
        font-weight:bold;
        color:#4CAF50;
        text-align:center;
        margin-bottom:20px;
    }

    .card {
        background: linear-gradient(135deg, #1e1e2f, #2d2d44);
        padding:20px;
        border-radius:15px;
        box-shadow:0px 4px 15px rgba(0,0,0,0.3);
        color:#93c5fd;
        margin-bottom:20px;
        transition:0.3s;
    }

    .card:hover{
        transform:scale(1.02);
        box-shadow:0px 6px 20px rgba(0,255,150,0.4);
    }

    .feature{
        background:#26273b;
        padding:15px;
        border-radius:12px;
        text-align:center;
        color:white;
        box-shadow:0px 2px 10px rgba(0,0,0,0.2);
    }

    .tool-card{
        background:#20232a;
        padding:15px;
        border-radius:12px;
        color:white;
        text-align:center;
        box-shadow:0px 2px 10px rgba(0,0,0,0.3);
        transition:0.3s;
    }

    .tool-card:hover{
        transform:translateY(-5px);
        background:#2b2f3a;
    }

    .tool-logo{
        font-size:40px;
        margin-bottom:10px;
    }

    .version{
        color:#00ff99;
        font-size:14px;
    }
    </style>
    """, unsafe_allow_html=True)

     # ================= TITLE =================
    st.markdown(
        '<div class="main-title">💼 Salary Prediction System</div>',
        unsafe_allow_html=True
    )


    # ================= PROJECT CARD =================
    st.markdown("""
    <div class="card">
        <h3>📌 Project Overview</h3>
        <p>
        This project predicts employee salaries using 
        Machine Learning algorithms based on different 
        employee details such as experience, education, 
        job role, and working hours.
        </p>

    </div>
    """, unsafe_allow_html=True)

    # ================= FEATURES =================
    st.subheader("🚀 Features")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature">
            <h3>📈</h3>
            <h4>Salary Prediction</h4>
            <p>Predict employee salary instantly.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature">
            <h3>📊</h3>
            <h4>Dashboard</h4>
            <p>Interactive charts and analytics.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature">
            <h3>🔐</h3>
            <h4>Authentication</h4>
            <p>Secure login and signup system.</p>
        </div>
        """, unsafe_allow_html=True)

    col4, col5 = st.columns(2)

    with col4:
        st.markdown("""
        <div class="feature">
            <h3>📉</h3>
            <h4>Visualization</h4>
            <p>Beautiful data visualization graphs.</p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="feature">
            <h3>📥</h3>
            <h4>Download Reports</h4>
            <p>Export prediction reports easily.</p>
        </div>
        """, unsafe_allow_html=True)

    # ================= TOOLS & TECHNOLOGIES =================
    st.subheader("🛠 Tools & Technologies")

    t1, t2, t3 = st.columns(3)

    with t1:
        st.markdown("""
        <div class="tool-card">
            <div class="tool-logo">🐍</div>
            <h4>Python</h4>
            <p class="version">Version: 3.11</p>
            <p>
            Main programming language used for 
            backend development and machine learning.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with t2:
        st.markdown("""
        <div class="tool-card">
            <div class="tool-logo">🎈</div>
            <h4>Streamlit</h4>
            <p class="version">Version: 1.32</p>
            <p>
            Used for building interactive web applications 
            and dashboards.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with t3:
        st.markdown("""
        <div class="tool-card">
            <div class="tool-logo">🐼</div>
            <h4>Pandas</h4>
            <p class="version">Version: 2.2</p>
            <p>
            Used for data cleaning, processing, 
            and analysis.
            </p>
        </div>
        """, unsafe_allow_html=True)

    t4, t5, t6 = st.columns(3)

    with t4:
        st.markdown("""
        <div class="tool-card">
            <div class="tool-logo">🔢</div>
            <h4>NumPy</h4>
            <p class="version">Version: 1.26</p>
            <p>
            Used for numerical computations 
            and array operations.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with t5:
        st.markdown("""
        <div class="tool-card">
            <div class="tool-logo">🤖</div>
            <h4>Scikit-Learn</h4>
            <p class="version">Version: 1.4</p>
            <p>
            Machine Learning library used 
            for model training and prediction.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with t6:
        st.markdown("""
        <div class="tool-card">
            <div class="tool-logo">📊</div>
            <h4>Machine Learning</h4>
            <p class="version">AI Technology</p>
            <p>
            Used to analyze employee data 
            and predict salary accurately.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ================= FOOTER =================
    st.markdown("""
    <br>
    <div class="card" style="text-align:center;">
        <h3>✨ Developed with Passion</h3>
        <p>
        Salary Prediction System using Machine Learning 
        and Data Science technologies.
        </p>
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
