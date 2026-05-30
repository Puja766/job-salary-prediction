# =============================================================
# SalaryIQ — Know Your Worth
# AI-Powered Salary Prediction Platform
# Run: streamlit run app.py
# =============================================================

import streamlit as st
import pickle
import os
from datetime import datetime

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="SalaryIQ — Know Your Worth",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# USER DATABASE (pickle)
# =========================
USER_FILE = "users.pkl"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "rb") as f:
            return pickle.load(f)
    return {
        "admin": {
            "password": "1234",
            "name": "Admin User",
            "email": "admin@example.com",
            "phone": "",
            "city": "",
            "linkedin": "",
            "bio": "",
            "joined": datetime.now().strftime("%d %b %Y")
        }
    }

def save_users(users):
    with open(USER_FILE, "wb") as f:
        pickle.dump(users, f)

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
if "profile_section" not in st.session_state:
    st.session_state.profile_section = "info"
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "landing"

# =========================
# HELPERS
# =========================
def get_initials(name):
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return parts[0][0].upper()

def get_user_data(username):
    users = st.session_state.users
    u = users.get(username, {})
    if isinstance(u, dict):
        return u
    return {"password": u, "name": username, "email": "", "phone": "",
            "city": "", "linkedin": "", "bio": "", "joined": "2026"}

# =========================
# CAREER DATA
# =========================
SKILLS_BY_ROLE = {
    "Data Scientist":            ["Python","Machine Learning","Deep Learning","SQL","Statistics","TensorFlow","Spark"],
    "Software Engineer":         ["System Design","DSA","Cloud (AWS/GCP)","Docker","Kubernetes","CI/CD","Microservices"],
    "AI Engineer":               ["LLMs","PyTorch","MLOps","Vector Databases","Prompt Engineering","Transformers","CUDA"],
    "Data Analyst":              ["Power BI","Tableau","Advanced SQL","Python","Excel","Statistical Analysis","DAX"],
    "Machine Learning Engineer": ["MLOps","Feature Engineering","Model Deployment","Kubeflow","PyTorch","Scalable ML"],
    "DevOps Engineer":           ["Kubernetes","Terraform","AWS","CI/CD","Monitoring","Docker","Linux"],
    "Cloud Engineer":            ["AWS/Azure/GCP","Terraform","Networking","Security","Serverless","Cost Optimization"],
    "Cybersecurity Analyst":     ["Ethical Hacking","SIEM","Incident Response","Network Security","Compliance","Forensics"],
    "Product Manager":           ["Roadmapping","OKRs","User Research","A/B Testing","SQL","Stakeholder Management"],
    "Business Analyst":          ["Power BI","Process Mapping","SQL","Requirements Gathering","Agile","JIRA"],
    "Frontend Developer":        ["React","TypeScript","Next.js","Tailwind CSS","GraphQL","Web Performance","Testing"],
    "Backend Developer":         ["Node.js","PostgreSQL","Redis","REST APIs","System Design","Docker","Message Queues"],
    "Other":                     ["Communication","Project Management","Data Analysis","Cloud Basics","Agile","Python"],
}
ROADMAP_BY_ROLE = {
    "Data Scientist":            ["Junior Data Analyst","Data Scientist","Senior Data Scientist","Lead / Staff DS","Head of Data Science"],
    "Software Engineer":         ["Junior Developer","Software Engineer","Senior Engineer","Staff Engineer","Principal / VP Eng"],
    "AI Engineer":               ["ML Engineer","AI Engineer","Senior AI Engineer","AI Tech Lead","AI Research Director"],
    "Data Analyst":              ["Junior Analyst","Data Analyst","Senior Analyst","Analytics Manager","Director of Analytics"],
    "Machine Learning Engineer": ["Junior ML Engineer","ML Engineer","Senior ML Engineer","ML Tech Lead","Head of ML"],
    "DevOps Engineer":           ["Junior DevOps","DevOps Engineer","Senior DevOps","Platform Lead","VP Infrastructure"],
    "Cloud Engineer":            ["Cloud Support","Cloud Engineer","Senior Cloud Engineer","Cloud Architect","CTO / VP Cloud"],
    "Cybersecurity Analyst":     ["Security Analyst","Senior Analyst","Security Lead","CISO Director","Chief Security Officer"],
    "Product Manager":           ["Associate PM","Product Manager","Senior PM","Group PM","VP / CPO"],
    "Business Analyst":          ["Junior BA","Business Analyst","Senior BA","BA Manager","Director of Strategy"],
    "Frontend Developer":        ["Junior Frontend","Frontend Developer","Senior Frontend","Frontend Lead","Head of Frontend"],
    "Backend Developer":         ["Junior Backend","Backend Developer","Senior Backend","Backend Lead","Engineering Manager"],
    "Other":                     ["Entry Level","Mid Level","Senior Level","Lead / Manager","Director / VP"],
}
INDUSTRY_TRENDS = {
    "Technology":    {"growth":"22%","outlook":"Excellent","top_pay":"₹1,80,000","demand":"Very High","avg":1400000},
    "Finance":       {"growth":"15%","outlook":"Strong",   "top_pay":"₹1,60,000","demand":"High",     "avg":1300000},
    "Healthcare":    {"growth":"18%","outlook":"Excellent","top_pay":"₹1,40,000","demand":"Very High", "avg":1100000},
    "Consulting":    {"growth":"12%","outlook":"Strong",   "top_pay":"₹1,70,000","demand":"High",     "avg":1350000},
    "Manufacturing": {"growth":"8%", "outlook":"Moderate", "top_pay":"₹1,10,000","demand":"Moderate", "avg":900000},
    "Education":     {"growth":"10%","outlook":"Stable",   "top_pay":"₹90,000",  "demand":"Moderate", "avg":750000},
    "Retail":        {"growth":"7%", "outlook":"Moderate", "top_pay":"₹95,000",  "demand":"Moderate", "avg":800000},
    "Media":         {"growth":"9%", "outlook":"Moderate", "top_pay":"₹1,00,000","demand":"Moderate", "avg":850000},
    "Telecom":       {"growth":"11%","outlook":"Strong",   "top_pay":"₹1,30,000","demand":"High",     "avg":1050000},
    "Government":    {"growth":"6%", "outlook":"Stable",   "top_pay":"₹85,000",  "demand":"Low",      "avg":700000},
    "Other":         {"growth":"10%","outlook":"Moderate", "top_pay":"₹1,00,000","demand":"Moderate", "avg":850000},
}

# =========================
# SALARY PREDICTION ENGINE
# =========================
def predict_salary(job, industry, exp, edu, skills, certs, loc):
    base = {
        "Data Scientist":900000,"Software Engineer":850000,"AI Engineer":1100000,
        "Data Analyst":650000,"Machine Learning Engineer":1000000,"DevOps Engineer":800000,
        "Cloud Engineer":900000,"Cybersecurity Analyst":850000,"Product Manager":1000000,
        "Business Analyst":700000,"Frontend Developer":750000,"Backend Developer":800000,"Other":600000
    }
    salary = base.get(job, 700000)
    salary += exp * 60000
    edu_mult = {"High School":0.85,"Diploma":0.9,"Bachelor's":1.0,"Master's":1.18,"PhD":1.3,"Other":0.95}
    salary *= edu_mult.get(edu, 1.0)
    salary += skills * 18000
    salary += certs * 22000
    ind_mult = {"Technology":1.15,"Finance":1.12,"Healthcare":1.05,"Consulting":1.10,
                "Government":0.82,"Education":0.85,"Telecom":1.02}
    salary *= ind_mult.get(industry, 1.0)
    loc_mult = {"Bangalore":1.15,"Mumbai":1.10,"Delhi/NCR":1.08,"Hyderabad":1.05,
                "Chennai":1.02,"Pune":1.0,"Remote":1.20,"Kolkata":0.92,"Other":0.90}
    salary *= loc_mult.get(loc, 1.0)
    return int(round(salary / 10000) * 10000)

# =========================
# WHATSAPP MESSAGE BUILDER
# =========================
def build_whatsapp_message(job, exp, skills, certs, edu, industry, salary):
    monthly = salary // 12
    level = "Fresher" if exp<=2 else ("Junior" if exp<=5 else ("Mid-Level" if exp<=10 else "Senior"))
    top_skills = SKILLS_BY_ROLE.get(job, SKILLS_BY_ROLE["Other"])[:4]
    roadmap = ROADMAP_BY_ROLE.get(job, ROADMAP_BY_ROLE["Other"])
    trend = INDUSTRY_TRENDS.get(industry, INDUSTRY_TRENDS["Other"])
    cs = 0 if exp<=2 else (1 if exp<=5 else (2 if exp<=10 else (3 if exp<=15 else 4)))
    curr_role = roadmap[cs]
    next_role = roadmap[min(cs+1, len(roadmap)-1)]
    msg = f"""💼 *SalaryIQ — Career Insights Report*
━━━━━━━━━━━━━━━━━━━
👤 *Profile Summary*
• Role: {job}
• Experience: {exp} years ({level})
• Skills: {skills} | Certifications: {certs}
• Education: {edu} | Industry: {industry}

💰 *Salary Prediction*
• Annual: ₹{salary:,}
• Monthly: ₹{monthly:,}

📈 *Career Roadmap*
• Current: {curr_role}
• Next Goal: {next_role}

🛠️ *Top Skills to Learn*
{chr(10).join(f'  ✅ {s}' for s in top_skills)}

🏭 *{industry} Industry Trend*
• Growth: {trend['growth']} YoY
• Job Demand: {trend['demand']}
• Top Pay in Field: {trend['top_pay']}

🚀 *Quick Tips*
• Earn 1–2 certifications → +₹15K–25K/yr
• Add 3–5 skills → +₹20K–35K/yr
• Target remote jobs → 2–4x salary boost
• Always negotiate — ask 15% above offer!

━━━━━━━━━━━━━━━━━━━
_Powered by SalaryIQ AI Platform_ 🤖"""
    return msg

# =========================
# CSS INJECTION
# =========================
def inject_css():
    dm = st.session_state.dark_mode
    if dm:
        BG          = "linear-gradient(135deg,#0a0f1e 0%,#0f172a 40%,#1a1040 100%)"
        SIDEBAR_BG  = "#080d1a"
        CARD_BG     = "rgba(15,23,42,0.95)"
        CARD_BORDER = "rgba(99,102,241,0.2)"
        TEXT1       = "#f1f5f9"
        TEXT2       = "#94a3b8"
        TEXT3       = "#64748b"
        ACCENT      = "#6366f1"
        ACCENT2     = "#8b5cf6"
        ACCENT_SOFT = "rgba(99,102,241,0.12)"
        ACCENT_BRD  = "rgba(99,102,241,0.35)"
        INPUT_BG    = "rgba(15,23,42,0.9)"
        NAV_BG      = "rgba(8,13,26,0.98)"
        DIVIDER     = "rgba(99,102,241,0.12)"
        PROFILE_BG  = "linear-gradient(160deg,#312e81,#1e1b4b,#0f0a2e)"
        GLOW        = "0 0 40px rgba(99,102,241,0.15)"
        OPT_BG      = "#0f172a"
        OPT_H       = "rgba(99,102,241,0.2)"
        OPT_C       = "#f1f5f9"
        OPT_CH      = "#a78bfa"
        BTN_INACT   = "rgba(99,102,241,0.08)"
        BTN_BRD     = "rgba(99,102,241,0.25)"
        STEP_BG     = "rgba(15,23,42,0.6)"
        STEP_C      = "#475569"
        STEP_B      = "#1e293b"
        TOGGLE_LBL  = "☀️ Light Mode"
    else:
        BG          = "linear-gradient(135deg,#f0f4ff 0%,#faf5ff 50%,#f8f0ff 100%)"
        SIDEBAR_BG  = "#fafbff"
        CARD_BG     = "#ffffff"
        CARD_BORDER = "#e0e7ff"
        TEXT1       = "#1e1b4b"
        TEXT2       = "#6b7280"
        TEXT3       = "#9ca3af"
        ACCENT      = "#4f46e5"
        ACCENT2     = "#7c3aed"
        ACCENT_SOFT = "#eef2ff"
        ACCENT_BRD  = "#c7d2fe"
        INPUT_BG    = "#f9fafb"
        NAV_BG      = "#ffffff"
        DIVIDER     = "#e0e7ff"
        PROFILE_BG  = "linear-gradient(160deg,#4f46e5,#7c3aed,#6d28d9)"
        GLOW        = "0 4px 24px rgba(79,70,229,0.1)"
        OPT_BG      = "#ffffff"
        OPT_H       = "#eef2ff"
        OPT_C       = "#1e1b4b"
        OPT_CH      = "#4f46e5"
        BTN_INACT   = "#f5f3ff"
        BTN_BRD     = "#c7d2fe"
        STEP_BG     = "#f5f3ff"
        STEP_C      = "#9ca3af"
        STEP_B      = "#d1d5db"
        TOGGLE_LBL  = "🌙 Dark Mode"

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800;900&display=swap');
*,*::before,*::after{{box-sizing:border-box}}
html,body,[class*="css"]{{font-family:'Inter',sans-serif!important}}
#MainMenu,footer{{visibility:hidden!important;display:none!important}}
.block-container{{padding:0!important;max-width:100%!important}}

/* APP BACKGROUND */
.stApp{{background:{BG}!important;transition:all 0.4s ease}}

/* SIDEBAR */
section[data-testid="stSidebar"]{{
  background:{SIDEBAR_BG}!important;
  border-right:1px solid {CARD_BORDER}!important;
  min-width:270px!important;max-width:270px!important
}}
section[data-testid="stSidebar"]>div{{padding:0!important}}
section[data-testid="stSidebar"] *{{color:{TEXT1}!important}}

/* PROFILE CARD IN SIDEBAR */
.sb-profile-card{{
  background:{PROFILE_BG};padding:28px 20px 18px;text-align:center;
  position:relative;overflow:hidden
}}
.sb-profile-card::before{{
  content:'';position:absolute;top:-30px;right:-30px;
  width:120px;height:120px;border-radius:50%;background:rgba(255,255,255,0.05)
}}
.sb-avatar{{
  width:76px;height:76px;border-radius:50%;
  background:rgba(255,255,255,0.2);margin:0 auto 12px;
  display:flex;align-items:center;justify-content:center;
  font-size:28px;font-weight:800;color:#fff!important;
  border:3px solid rgba(255,255,255,0.5);
  box-shadow:0 4px 20px rgba(0,0,0,0.3);position:relative;z-index:1
}}
.sb-name{{
  font-family:'Plus Jakarta Sans',sans-serif!important;
  font-size:17px;font-weight:800;color:#fff!important;
  position:relative;z-index:1
}}
.sb-email{{font-size:11px;color:rgba(255,255,255,0.65)!important;margin-top:3px;position:relative;z-index:1}}
.sb-since{{font-size:10px;color:rgba(255,255,255,0.45)!important;margin-top:2px;position:relative;z-index:1}}
.sb-stats{{
  display:flex;margin-top:16px;border-top:1px solid rgba(255,255,255,0.12);
  padding-top:14px;position:relative;z-index:1
}}
.sb-stat{{flex:1;text-align:center;border-right:1px solid rgba(255,255,255,0.12)}}
.sb-stat:last-child{{border-right:none}}
.sb-stat-val{{font-family:'Plus Jakarta Sans',sans-serif!important;font-size:16px;font-weight:800;color:#fff!important}}
.sb-stat-lbl{{font-size:9px;color:rgba(255,255,255,0.55)!important;margin-top:2px;text-transform:uppercase;letter-spacing:.5px}}

/* SIDEBAR INNER */
.sb-inner{{padding:12px 14px}}
.sb-section-title{{
  font-size:10px;font-weight:700;color:{TEXT3}!important;
  text-transform:uppercase;letter-spacing:1.2px;margin:14px 0 7px;padding:0 2px
}}
.contact-item{{
  display:flex;align-items:flex-start;gap:10px;
  padding:8px 2px;border-bottom:1px solid {DIVIDER}
}}
.contact-item:last-child{{border-bottom:none}}
.contact-icon{{font-size:14px;width:20px;text-align:center;flex-shrink:0;margin-top:1px}}
.contact-label{{font-size:9px;color:{TEXT3}!important;text-transform:uppercase;letter-spacing:.5px}}
.contact-val{{font-size:12px;color:{TEXT1}!important;font-weight:500;margin-top:1px;word-break:break-all}}

/* SIGN OUT BUTTON */
.signout-wrap .stButton>button{{
  background:rgba(239,68,68,0.08)!important;color:#ef4444!important;
  border:1.5px solid rgba(239,68,68,0.25)!important;
  height:40px!important;font-size:13px!important;font-weight:600!important;
  box-shadow:none!important;border-radius:10px!important
}}
.signout-wrap .stButton>button:hover{{background:rgba(239,68,68,0.18)!important}}

/* THEME TOGGLE BUTTON */
.theme-btn .stButton>button{{
  background:{ACCENT_SOFT}!important;color:{ACCENT}!important;
  border:1.5px solid {ACCENT_BRD}!important;
  height:38px!important;font-size:13px!important;font-weight:600!important;
  box-shadow:none!important;border-radius:9px!important
}}

/* TOP HEADER */
.top-header{{
  background:{NAV_BG};border-bottom:1px solid {CARD_BORDER};
  padding:0 28px;display:flex;align-items:center;
  justify-content:space-between;height:60px;
  box-shadow:{GLOW};position:sticky;top:0;z-index:100
}}
.top-logo{{
  font-family:'Plus Jakarta Sans',sans-serif!important;
  font-size:22px;font-weight:900;color:{TEXT1}!important;
  display:flex;align-items:center;gap:10px;letter-spacing:-0.5px
}}
.top-logo em{{
  background:linear-gradient(135deg,{ACCENT},{ACCENT2});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;font-style:normal
}}
.top-badge{{
  font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;
  background:{ACCENT_SOFT};color:{ACCENT}!important;
  border:1px solid {ACCENT_BRD};letter-spacing:.5px;text-transform:uppercase
}}
.top-right{{display:flex;align-items:center;gap:12px}}
.top-avatar{{
  width:34px;height:34px;border-radius:50%;
  background:linear-gradient(135deg,{ACCENT},{ACCENT2});
  display:flex;align-items:center;justify-content:center;
  font-size:13px;font-weight:700;color:#fff!important;
  box-shadow:0 2px 8px rgba(99,102,241,0.35)
}}
.top-username{{font-size:13px;font-weight:600;color:{TEXT1}!important}}

/* NAV TABS */
.nav-tabs-outer{{
  background:{NAV_BG};border-bottom:1px solid {DIVIDER};padding:6px 20px
}}

/* PAGE WRAPPER */
.page-wrap{{padding:26px 28px 40px;max-width:1120px;margin:0 auto}}
.page-title{{
  font-family:'Plus Jakarta Sans',sans-serif!important;
  font-size:24px;font-weight:900;color:{TEXT1}!important;
  margin-bottom:5px;letter-spacing:-0.3px
}}
.page-sub{{font-size:14px;color:{TEXT2}!important;margin-bottom:22px;line-height:1.6}}

/* CARDS */
.card{{
  background:{CARD_BG};border-radius:18px;border:1px solid {CARD_BORDER};
  padding:22px;box-shadow:{GLOW};margin-bottom:16px;transition:all 0.3s
}}
.card:hover{{box-shadow:0 8px 32px rgba(99,102,241,0.18)}}
.card-title{{
  font-size:10px;font-weight:700;color:{ACCENT}!important;
  text-transform:uppercase;letter-spacing:1.2px;margin-bottom:14px;
  padding-bottom:10px;border-bottom:1px solid {DIVIDER}
}}

/* METRIC CARDS */
.metric-card{{
  background:{CARD_BG};border:1px solid {CARD_BORDER};
  border-radius:14px;padding:16px 14px;box-shadow:{GLOW};transition:all 0.3s
}}
.metric-label{{font-size:10px;color:{TEXT3}!important;font-weight:600;
              margin-bottom:6px;text-transform:uppercase;letter-spacing:.6px}}
.metric-value{{font-size:20px;font-weight:800;color:{TEXT1}!important;
              font-family:'Plus Jakarta Sans',sans-serif!important}}
.metric-sub{{font-size:11px;color:#10b981!important;font-weight:600;margin-top:4px}}

/* RESULT HERO */
.result-hero{{
  background:linear-gradient(135deg,#4338ca,#6d28d9,#7c3aed);
  border-radius:22px;padding:38px 32px;text-align:center;margin-bottom:22px;
  box-shadow:0 16px 48px rgba(99,102,241,0.35),0 4px 16px rgba(0,0,0,0.15);
  position:relative;overflow:hidden
}}
.result-hero::before{{
  content:'';position:absolute;top:-40px;right:-40px;
  width:180px;height:180px;border-radius:50%;background:rgba(255,255,255,0.06)
}}
.result-hero-label{{font-size:11px;color:rgba(255,255,255,0.7)!important;
                   letter-spacing:2px;text-transform:uppercase;position:relative;z-index:1}}
.result-hero-amount{{font-size:58px;font-weight:900;color:#fff!important;
                    margin:10px 0;font-family:'Plus Jakarta Sans',sans-serif!important;
                    position:relative;z-index:1;text-shadow:0 2px 20px rgba(0,0,0,0.2)}}
.result-hero-sub{{font-size:13px;color:rgba(255,255,255,0.65)!important;position:relative;z-index:1}}

/* INSIGHT CARDS */
.insight-card{{
  background:{CARD_BG};border-radius:14px;border:1px solid {CARD_BORDER};
  padding:16px 18px;margin-bottom:10px;display:flex;gap:14px;
  align-items:flex-start;transition:all 0.2s
}}
.insight-card:hover{{border-color:{ACCENT_BRD};box-shadow:0 4px 16px rgba(99,102,241,0.12)}}
.insight-icon{{width:40px;height:40px;border-radius:12px;
              display:flex;align-items:center;justify-content:center;
              font-size:18px;flex-shrink:0}}
.insight-icon-blue  {{background:rgba(99,102,241,0.15)}}
.insight-icon-green {{background:rgba(16,185,129,0.15)}}
.insight-icon-amber {{background:rgba(245,158,11,0.15)}}
.insight-icon-rose  {{background:rgba(244,63,94,0.15)}}
.insight-title{{font-size:14px;font-weight:700;color:{TEXT1}!important;margin-bottom:4px}}
.insight-desc{{font-size:13px;color:{TEXT2}!important;line-height:1.6}}

/* ROADMAP */
.roadmap-step{{display:flex;gap:14px;align-items:flex-start;
              padding:18px 0;border-bottom:1px solid {DIVIDER}}}
.roadmap-step:last-child{{border-bottom:none}}
.step-dot{{width:36px;height:36px;border-radius:50%;
          display:flex;align-items:center;justify-content:center;
          font-size:13px;font-weight:700;flex-shrink:0;margin-top:2px}}
.step-dot-done{{background:{ACCENT};color:#fff}}
.step-dot-curr{{background:linear-gradient(135deg,{ACCENT},{ACCENT2});
               color:#fff;box-shadow:0 0 0 5px {ACCENT_SOFT}}}
.step-dot-next{{background:{STEP_BG};color:{STEP_C}!important;border:2px dashed {STEP_B}}}
.step-title{{font-size:15px;font-weight:700;color:{TEXT1}!important}}
.step-sub{{font-size:12px;color:{TEXT2}!important;margin-top:3px}}
.step-badge{{display:inline-block;font-size:10px;font-weight:700;
            padding:3px 10px;border-radius:99px;margin-top:6px;letter-spacing:.3px}}
.badge-current{{background:{ACCENT_SOFT};color:{ACCENT}!important}}
.badge-done{{background:rgba(16,185,129,0.15);color:#10b981!important}}
.badge-future{{background:rgba(30,41,59,0.4);color:{TEXT3}!important}}

/* COMPARE BARS */
.cbar-wrap{{margin-bottom:14px}}
.cbar-lbl{{display:flex;justify-content:space-between;font-size:13px;margin-bottom:5px}}
.cbar-track{{height:8px;background:rgba(30,41,59,0.8);border-radius:99px;overflow:hidden}}
.cbar-fill{{height:100%;border-radius:99px;
           background:linear-gradient(90deg,{ACCENT},{ACCENT2})}}

/* LEADERBOARD */
.lb-row{{display:flex;align-items:center;gap:14px;padding:14px 16px;
        border-radius:14px;margin-bottom:8px;border:1px solid {CARD_BORDER};
        transition:all 0.2s;background:{CARD_BG}}}
.lb-row:hover{{background:{ACCENT_SOFT};border-color:{ACCENT_BRD};transform:translateX(3px)}}
.lb-row.gold{{background:rgba(245,158,11,0.08);border-color:rgba(245,158,11,0.25)}}
.lb-rank{{font-size:16px;font-weight:800;min-width:28px;color:{TEXT1}!important}}
.lb-name{{flex:1;font-size:13px;font-weight:700;color:{TEXT1}!important}}
.lb-role{{font-size:11px;color:{TEXT2}!important;margin-top:2px}}
.lb-salary{{font-size:16px;font-weight:800;color:{ACCENT}!important;
           font-family:'Plus Jakarta Sans',sans-serif!important}}

/* WHATSAPP */
.wa-card{{background:rgba(37,211,102,0.08);border:1.5px solid rgba(37,211,102,0.25);
         border-radius:16px;padding:20px;margin-top:18px}}
.wa-title{{font-size:14px;font-weight:700;color:#25D366!important;
          margin-bottom:8px;display:flex;align-items:center;gap:8px}}
.wa-desc{{font-size:13px;color:{TEXT2}!important;line-height:1.6;margin-bottom:14px}}
.wa-btn a{{
  display:inline-flex;align-items:center;gap:8px;
  background:linear-gradient(135deg,#25D366,#128C7E);
  color:#fff!important;font-weight:700;font-size:14px;
  padding:12px 24px;border-radius:12px;text-decoration:none;
  box-shadow:0 4px 16px rgba(37,211,102,0.3);transition:all 0.2s
}}

/* HERO (landing) */
.hero-section{{
  background:linear-gradient(135deg,#4338ca,#6d28d9,#7c3aed);
  padding:64px 40px;border-radius:24px;margin-bottom:28px;
  position:relative;overflow:hidden;
  box-shadow:0 16px 48px rgba(99,102,241,0.3)
}}
.hero-section::before{{
  content:'';position:absolute;top:-40px;right:-40px;
  width:200px;height:200px;border-radius:50%;background:rgba(255,255,255,0.05)
}}
.hero-eyebrow{{font-size:12px;font-weight:700;color:rgba(255,255,255,0.7)!important;
              text-transform:uppercase;letter-spacing:2px;margin-bottom:14px}}
.hero-title{{font-family:'Plus Jakarta Sans',sans-serif!important;font-size:42px;
            font-weight:900;color:#fff!important;line-height:1.15;margin-bottom:16px}}
.hero-sub{{font-size:16px;color:rgba(255,255,255,0.75)!important;
          line-height:1.7;margin-bottom:24px;max-width:560px}}
.hero-pill{{background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.3);
           color:#fff!important;padding:7px 18px;border-radius:99px;
           font-size:13px;font-weight:600;display:inline-block;margin:4px}}

/* STAT STRIP */
.stat-strip{{
  background:{CARD_BG};border:1px solid {CARD_BORDER};
  border-radius:16px;display:flex;padding:20px 0;
  margin-bottom:24px;box-shadow:{GLOW}
}}
.stat-strip-item{{flex:1;text-align:center;border-right:1px solid {DIVIDER}}}
.stat-strip-item:last-child{{border-right:none}}
.stat-strip-val{{
  font-family:'Plus Jakarta Sans',sans-serif!important;font-size:24px;font-weight:900;
  background:linear-gradient(135deg,{ACCENT},{ACCENT2});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text
}}
.stat-strip-lbl{{font-size:11px;color:{TEXT2}!important;margin-top:3px;font-weight:500}}

/* FEATURE CARDS */
.feature-card{{
  background:{CARD_BG};border:1px solid {CARD_BORDER};
  padding:26px 20px;border-radius:20px;text-align:center;
  transition:all 0.3s;box-shadow:{GLOW}
}}
.feature-card:hover{{transform:translateY(-5px);
                    box-shadow:0 16px 40px rgba(99,102,241,0.18);
                    border-color:{ACCENT_BRD}}}
.feature-icon{{font-size:36px;margin-bottom:12px}}
.feature-title{{font-family:'Plus Jakarta Sans',sans-serif!important;font-size:15px;
               font-weight:800;color:{TEXT1}!important;margin-bottom:6px}}
.feature-desc{{font-size:13px;color:{TEXT2}!important;line-height:1.5}}

/* PROFILE PAGE */
.profile-hero{{
  background:linear-gradient(135deg,#4338ca,#6d28d9,#7c3aed);
  border-radius:20px;padding:2.5rem;position:relative;overflow:hidden;margin-bottom:20px
}}
.ph-avatar{{width:80px;height:80px;border-radius:50%;
           background:rgba(255,255,255,0.2);border:3px solid rgba(255,255,255,0.5);
           display:flex;align-items:center;justify-content:center;
           font-size:1.8rem;font-weight:900;color:#fff!important}}
.ph-name{{font-family:'Plus Jakarta Sans',sans-serif!important;
         font-size:1.4rem;font-weight:900;color:#fff!important}}
.ph-email{{color:rgba(255,255,255,0.7)!important;font-size:.9rem;margin-top:3px}}

/* INPUTS */
.stTextInput input,.stNumberInput input,.stTextArea textarea{{
  background:{INPUT_BG}!important;border:1.5px solid {CARD_BORDER}!important;
  border-radius:11px!important;color:{TEXT1}!important;font-size:14px!important
}}
.stTextInput input:focus,.stNumberInput input:focus{{
  border-color:{ACCENT}!important;box-shadow:0 0 0 3px {ACCENT_SOFT}!important
}}
.stTextInput label,.stNumberInput label,.stSelectbox label,.stSlider label{{
  color:{TEXT2}!important;font-size:12px!important;font-weight:600!important;
  text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px
}}
.stSelectbox>div>div{{
  background:{INPUT_BG}!important;border:1.5px solid {CARD_BORDER}!important;
  border-radius:11px!important;color:{TEXT1}!important
}}
[data-baseweb="popover"],[data-baseweb="menu"],[role="listbox"]{{
  background:{OPT_BG}!important;border:1px solid {CARD_BORDER}!important;
  border-radius:14px!important;box-shadow:0 8px 32px rgba(0,0,0,0.15)!important
}}
[data-baseweb="menu"] li,[role="option"]{{background:{OPT_BG}!important;color:{OPT_C}!important}}
[data-baseweb="menu"] li:hover,[role="option"]:hover,[role="option"][aria-selected="true"]{{
  background:{OPT_H}!important;color:{OPT_CH}!important
}}

/* MAIN BUTTONS */
.stButton>button{{
  background:linear-gradient(135deg,{ACCENT},{ACCENT2})!important;
  color:#fff!important;border:none!important;border-radius:11px!important;
  height:46px!important;font-size:14px!important;font-weight:700!important;
  box-shadow:0 4px 16px rgba(99,102,241,0.3)!important;
  transition:all 0.2s!important;width:100%!important
}}
.stButton>button:hover{{
  transform:translateY(-1px)!important;
  box-shadow:0 8px 24px rgba(99,102,241,0.45)!important
}}

/* SLIDER */
.stSlider>div>div>div>div{{
  background:linear-gradient(90deg,{ACCENT},{ACCENT2})!important
}}

/* PILL TAGS */
.pill{{display:inline-block;background:{ACCENT_SOFT};color:{ACCENT}!important;
      border-radius:99px;padding:5px 14px;font-size:12px;font-weight:600;
      margin:3px;border:1px solid {ACCENT_BRD}}}

/* FOOTER */
.footer-bar{{text-align:center;color:{TEXT3}!important;padding:24px;
            font-size:12px;border-top:1px solid {DIVIDER};margin-top:20px}}

h1,h2,h3{{font-family:'Plus Jakarta Sans',sans-serif!important;color:{TEXT1}!important}}
p,li{{color:{TEXT2}!important}}
</style>
""", unsafe_allow_html=True)
    return TOGGLE_LBL

# =========================
# SIDEBAR (logged in)
# =========================
def show_sidebar():
    u     = st.session_state.username
    udata = get_user_data(u)
    name  = udata.get("name", u)
    email = udata.get("email", "")
    phone = udata.get("phone", "")
    city  = udata.get("city", "")
    lnkd  = udata.get("linkedin", "")
    bio   = udata.get("bio", "")
    joined= udata.get("joined", "2026")
    initials = get_initials(name)
    pred_count = 1 if st.session_state.last_prediction else 0
    best_salary = st.session_state.last_prediction or 0
    best_fmt = f"₹{best_salary//100000:.0f}L" if best_salary else "—"

    # Profile card
    st.sidebar.markdown(f"""
<div class="sb-profile-card">
  <div class="sb-avatar">{initials}</div>
  <div class="sb-name">{name}</div>
  <div class="sb-email">{email or '—'}</div>
  <div class="sb-since">Member since {joined}</div>
  <div class="sb-stats">
    <div class="sb-stat">
      <div class="sb-stat-val">{pred_count}</div>
      <div class="sb-stat-lbl">Predictions</div>
    </div>
    <div class="sb-stat">
      <div class="sb-stat-val">{best_fmt}</div>
      <div class="sb-stat-lbl">Best Salary</div>
    </div>
    <div class="sb-stat">
      <div class="sb-stat-val">1</div>
      <div class="sb-stat-lbl">Badges</div>
    </div>
  </div>
</div>
<div class="sb-inner">""", unsafe_allow_html=True)

    # Section tabs
    sec = st.session_state.profile_section
    c1, c2, c3 = st.sidebar.columns(3)
    with c1:
        if st.button("Info", key="sb_info"):
            st.session_state.profile_section = "info"; st.rerun()
    with c2:
        if st.button("Edit", key="sb_edit"):
            st.session_state.profile_section = "edit"; st.rerun()
    with c3:
        if st.button("Security", key="sb_sec"):
            st.session_state.profile_section = "security"; st.rerun()

    st.sidebar.markdown(f'<div style="height:1px;background:rgba(99,102,241,0.12);margin:10px 0"></div>', unsafe_allow_html=True)

    # INFO
    if sec == "info":
        st.sidebar.markdown('<div class="sb-section-title">About</div>', unsafe_allow_html=True)
        st.sidebar.markdown(f'<div style="font-size:12px;color:#94a3b8;padding:4px 2px;line-height:1.6">{bio or "No bio added yet."}</div>', unsafe_allow_html=True)
        st.sidebar.markdown('<div class="sb-section-title">Contact</div>', unsafe_allow_html=True)
        for icon, label, val in [
            ("📞","Phone", phone or "—"),
            ("🏙️","City",  city  or "—"),
            ("🔗","LinkedIn", lnkd or "—"),
            ("📧","Email", email or "—")
        ]:
            st.sidebar.markdown(f"""
<div class="contact-item">
  <div class="contact-icon">{icon}</div>
  <div>
    <div class="contact-label">{label}</div>
    <div class="contact-val">{val}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # EDIT
    elif sec == "edit":
        st.sidebar.markdown('<div class="sb-section-title">Edit Profile</div>', unsafe_allow_html=True)
        nn  = st.sidebar.text_input("Full Name",  value=name,  key="en")
        ne  = st.sidebar.text_input("Email",      value=email, key="ee")
        np_ = st.sidebar.text_input("Phone",      value=phone, key="ep")
        nc  = st.sidebar.text_input("City",       value=city,  key="ec")
        nl  = st.sidebar.text_input("LinkedIn",   value=lnkd,  key="el")
        nb  = st.sidebar.text_area( "Bio",        value=bio,   key="eb", height=70)
        if st.sidebar.button("💾 Save Changes", key="save_profile"):
            ud = get_user_data(u)
            ud.update({"name":nn,"email":ne,"phone":np_,"city":nc,"linkedin":nl,"bio":nb})
            st.session_state.users[u] = ud
            save_users(st.session_state.users)
            st.session_state.profile_section = "info"
            st.sidebar.success("Profile saved ✅")
            st.rerun()

    # SECURITY
    elif sec == "security":
        st.sidebar.markdown('<div class="sb-section-title">Change Password</div>', unsafe_allow_html=True)
        op  = st.sidebar.text_input("Current Password", type="password", key="sec_o")
        np1 = st.sidebar.text_input("New Password",     type="password", key="sec_n1")
        np2 = st.sidebar.text_input("Confirm New",      type="password", key="sec_n2")
        if st.sidebar.button("🔒 Update Password", key="upd_pwd"):
            ud = get_user_data(u)
            if ud.get("password") != op:
                st.sidebar.error("Wrong current password")
            elif np1 != np2:
                st.sidebar.error("Passwords don't match")
            elif len(np1) < 6:
                st.sidebar.error("Min 6 characters")
            else:
                ud["password"] = np1
                st.session_state.users[u] = ud
                save_users(st.session_state.users)
                st.sidebar.success("Password updated ✅")

    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # Divider
    st.sidebar.markdown(f'<div style="height:1px;background:rgba(99,102,241,0.12);margin:4px 0"></div>', unsafe_allow_html=True)

    # Theme toggle
    st.sidebar.markdown('<div style="padding:8px 14px 4px"><div class="sb-section-title" style="margin:0 0 8px">🎨 Appearance</div></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="theme-btn" style="padding:0 14px 8px">', unsafe_allow_html=True)
    toggle_lbl = "☀️ Light Mode" if st.session_state.dark_mode else "🌙 Dark Mode"
    if st.sidebar.button(toggle_lbl, key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # Divider
    st.sidebar.markdown(f'<div style="height:1px;background:rgba(99,102,241,0.12);margin:4px 0"></div>', unsafe_allow_html=True)

    # Sign out
    st.sidebar.markdown('<div class="signout-wrap" style="padding:8px 14px 16px">', unsafe_allow_html=True)
    if st.sidebar.button("🚪 Sign Out", key="signout"):
        st.session_state.logged_in    = False
        st.session_state.username     = ""
        st.session_state.last_prediction = None
        st.session_state.active_tab   = "home"
        st.session_state.auth_mode    = "landing"
        st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

# =========================
# TOP BAR + NAV TABS
# =========================
def show_topbar_and_tabs():
    u      = st.session_state.username
    udata  = get_user_data(u)
    name   = udata.get("name", u)
    initials = get_initials(name)

    st.markdown(f"""
<div class="top-header">
  <div class="top-logo">💼 Salary<em>IQ</em> <span class="top-badge">PRO</span></div>
  <div class="top-right">
    <div class="top-avatar">{initials}</div>
    <span class="top-username">{name}</span>
  </div>
</div>""", unsafe_allow_html=True)

    tabs   = ["home","predict","insights","roadmap","dashboard","compare","leaderboard"]
    labels = ["🏠 Home","🔍 Predict","💡 Insights","🗺️ Roadmap","📊 Dashboard","⚖️ Compare","🏆 Leaderboard"]
    active = st.session_state.active_tab
    cols   = st.columns(len(tabs))
    for col, tab, label in zip(cols, tabs, labels):
        with col:
            is_act = tab == active
            st.markdown(f"""<style>
div[data-testid="stHorizontalBlock"] .stButton>button{{
  background:{"linear-gradient(135deg,#6366f1,#8b5cf6)" if is_act else "rgba(99,102,241,0.08)"}!important;
  color:{"#ffffff" if is_act else "#94a3b8"}!important;
  border:1px solid {"#6366f1" if is_act else "rgba(99,102,241,0.25)"}!important;
  height:38px!important;font-size:12px!important;
  font-weight:{"700" if is_act else "500"}!important;
  border-radius:9px!important;
  box-shadow:{"0 4px 12px rgba(99,102,241,0.28)" if is_act else "none"}!important
}}
</style>""", unsafe_allow_html=True)
            if st.button(label, key=f"nav_{tab}"):
                st.session_state.active_tab = tab
                st.rerun()

    st.markdown(f'<div style="height:1px;background:rgba(99,102,241,0.12)"></div>', unsafe_allow_html=True)

# =========================
# ── LANDING PAGE ──
# =========================
def show_landing():
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

    # Hero
    st.markdown("""
<div class="hero-section">
  <div style="position:relative;z-index:1;max-width:640px">
    <div class="hero-eyebrow">💼 AI-Powered Career Intelligence</div>
    <div class="hero-title">Welcome to<br>Salary Prediction App</div>
    <div class="hero-sub">Predict your market salary using Machine Learning based on your experience,
    education, certifications, skills, and industry — instantly.</div>
    <div>
      <span class="hero-pill">✅ 95% Accuracy</span>
      <span class="hero-pill">⚡ Instant Results</span>
      <span class="hero-pill">📱 WhatsApp Insights</span>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    # Stats strip
    st.markdown("""
<div class="stat-strip">
  <div class="stat-strip-item"><div class="stat-strip-val">50K+</div><div class="stat-strip-lbl">Predictions Made</div></div>
  <div class="stat-strip-item"><div class="stat-strip-val">95%</div><div class="stat-strip-lbl">Model Accuracy</div></div>
  <div class="stat-strip-item"><div class="stat-strip-val">120+</div><div class="stat-strip-lbl">Job Roles</div></div>
  <div class="stat-strip-item"><div class="stat-strip-val">10K+</div><div class="stat-strip-lbl">Active Users</div></div>
</div>""", unsafe_allow_html=True)

    # Features
    st.markdown('<div style="font-size:13px;font-weight:700;color:#6366f1;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:16px">✦ Features</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    features = [
        ("🤖","AI Prediction","Predict salary using KNN model trained on 250K+ real salary records."),
        ("📊","Analytics Dashboard","Full dashboard with benchmarks, trends, and skill gap analysis."),
        ("💡","Smart Suggestions","Personalized tips to maximize your earning potential."),
        ("🗺️","Career Roadmap","Step-by-step path from your current role to your dream salary."),
        ("🏆","Leaderboard","See how you rank against top professionals in your field."),
        ("📱","WhatsApp Export","Send your full salary report directly to WhatsApp in one tap."),
    ]
    cols = [c1, c2, c3, c1, c2, c3]
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(f'<div class="feature-card"><div class="feature-icon">{icon}</div><div class="feature-title">{title}</div><div class="feature-desc">{desc}</div></div>', unsafe_allow_html=True)

    # How it works
    st.markdown('<br><div style="font-size:13px;font-weight:700;color:#6366f1;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:16px">🔄 How It Works</div>', unsafe_allow_html=True)
    h1, h2, h3, h4 = st.columns(4)
    steps = [
        ("1️⃣","Create Account","Sign up free in 30 seconds — no credit card required."),
        ("2️⃣","Fill Profile","Enter your experience, skills, education, and job details."),
        ("3️⃣","Get Prediction","Our KNN model instantly calculates your market salary."),
        ("4️⃣","Share & Grow","Export your full insights report to WhatsApp or PDF."),
    ]
    for col, (num, title, desc) in zip([h1, h2, h3, h4], steps):
        with col:
            st.markdown(f'<div class="card" style="text-align:center"><div style="font-size:28px;margin-bottom:10px">{num}</div><div style="font-size:14px;font-weight:700;margin-bottom:6px">{title}</div><div style="font-size:12px;line-height:1.5">{desc}</div></div>', unsafe_allow_html=True)

    # CTA
    st.markdown('<br>', unsafe_allow_html=True)
    cc1, cc2, cc3 = st.columns([2, 1, 2])
    with cc2:
        if st.button("🚀 Get Started Free", key="landing_cta"):
            st.session_state.auth_mode = "signup"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# ── LOGIN PAGE ──
# =========================
def show_login():
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("""
<div class="card">
  <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:26px;font-weight:900;margin-bottom:6px">Welcome back 👋</div>
  <div style="font-size:14px;color:#94a3b8;margin-bottom:24px">Sign in to your career intelligence dashboard</div>
</div>""", unsafe_allow_html=True)

        email = st.text_input("Email Address", placeholder="you@example.com", key="li_email")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="li_pass")
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        if st.button("Sign In →", key="li_btn"):
            users = st.session_state.users
            user = None
            for u_data in users.values():
                if isinstance(u_data, dict):
                    if u_data.get("email") == email and u_data.get("password") == password:
                        user = u_data
                        break
                else:
                    # legacy format: username key with password string
                    pass
            # also try username match
            if not user:
                for uname, u_data in users.items():
                    if isinstance(u_data, dict) and u_data.get("password") == password and uname == email:
                        user = u_data
                        break

            if user:
                uname_key = user.get("username", email)
                # find key in users dict
                for k, v in users.items():
                    if isinstance(v, dict) and v == user:
                        uname_key = k
                        break
                st.session_state.logged_in  = True
                st.session_state.username   = uname_key
                st.session_state.active_tab = "home"
                st.success(f"Welcome {user.get('name', email)} 🎉")
                st.rerun()
            else:
                st.error("Invalid email or password")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Create Account", key="go_signup"):
                st.session_state.auth_mode = "signup"
                st.rerun()
        with c2:
            if st.button("← Back to Home", key="go_landing_from_login"):
                st.session_state.auth_mode = "landing"
                st.rerun()

# =========================
# ── SIGNUP PAGE ──
# =========================
def show_signup():
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("""
<div class="card">
  <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:26px;font-weight:900;margin-bottom:6px">Create Account 🚀</div>
  <div style="font-size:14px;color:#94a3b8;margin-bottom:24px">Join thousands discovering their true market value</div>
</div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            fname = st.text_input("First Name *", placeholder="Pooja", key="su_fn")
        with c2:
            lname = st.text_input("Last Name *",  placeholder="Sharma", key="su_ln")

        email = st.text_input("Email Address *", placeholder="pooja@example.com", key="su_em")

        c3, c4 = st.columns(2)
        with c3:
            username = st.text_input("Username *", placeholder="pooja123", key="su_un")
        with c4:
            city = st.text_input("City", placeholder="Bangalore", key="su_city")

        password  = st.text_input("Password *",         type="password", placeholder="Min. 6 characters", key="su_p1")
        cpassword = st.text_input("Confirm Password *", type="password", placeholder="Repeat password",   key="su_p2")

        if st.button("Create Free Account →", key="su_btn"):
            users = st.session_state.users
            if not all([fname, lname, email, username, password, cpassword]):
                st.warning("Please fill all required fields")
            elif password != cpassword:
                st.warning("Passwords do not match")
            elif len(password) < 6:
                st.warning("Password must be at least 6 characters")
            elif username in users:
                st.warning("Username already taken")
            elif any(isinstance(v, dict) and v.get("email") == email for v in users.values()):
                st.warning("Email already registered")
            else:
                users[username] = {
                    "username": username,
                    "name":     f"{fname} {lname}",
                    "fname":    fname,
                    "lname":    lname,
                    "email":    email,
                    "city":     city or "India",
                    "password": password,
                    "phone":    "",
                    "linkedin": "",
                    "bio":      "",
                    "joined":   datetime.now().strftime("%d %b %Y")
                }
                save_users(users)
                st.session_state.users      = users
                st.session_state.logged_in  = True
                st.session_state.username   = username
                st.session_state.active_tab = "home"
                st.success("Account created! Welcome to SalaryIQ 🎉")
                st.rerun()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Already have account? Sign In", key="go_login"):
                st.session_state.auth_mode = "login"
                st.rerun()
        with c2:
            if st.button("← Back to Home", key="go_landing_from_signup"):
                st.session_state.auth_mode = "landing"
                st.rerun()

# =========================
# ── DASHBOARD TABS ──
# =========================

# --- HOME TAB ---
def show_home_tab():
    u     = st.session_state.username
    udata = get_user_data(u)
    name  = udata.get("name", u)
    email = udata.get("email","")
    initials = get_initials(name)
    pred_count = 1 if st.session_state.last_prediction else 0
    best = f"₹{st.session_state.last_prediction//100000:.0f}L" if st.session_state.last_prediction else "—"

    # Profile hero
    st.markdown(f"""
<div class="profile-hero">
  <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap;position:relative;z-index:1">
    <div class="ph-avatar">{initials}</div>
    <div>
      <div class="ph-name">{name}</div>
      <div class="ph-email">{email}</div>
      <div style="color:rgba(255,255,255,0.5);font-size:.8rem;margin-top:2px">Member since {udata.get('joined','2026')}</div>
    </div>
  </div>
  <div style="display:flex;gap:28px;margin-top:20px;position:relative;z-index:1">
    <div>
      <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.5rem;font-weight:900;color:#fff">{pred_count}</div>
      <div style="font-size:11px;color:rgba(255,255,255,0.6);text-transform:uppercase;letter-spacing:.4px">Predictions</div>
    </div>
    <div>
      <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.5rem;font-weight:900;color:#fff">{best}</div>
      <div style="font-size:11px;color:rgba(255,255,255,0.6);text-transform:uppercase;letter-spacing:.4px">Best Salary</div>
    </div>
    <div>
      <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.5rem;font-weight:900;color:#fff">1</div>
      <div style="font-size:11px;color:rgba(255,255,255,0.6);text-transform:uppercase;letter-spacing:.4px">Badges</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    # Quick action cards
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("🔍","Run Salary Prediction","Get your AI-predicted market salary instantly.","predict"),
        ("🗺️","View Career Roadmap",  "See your full path to higher salary levels.","roadmap"),
        ("🏆","Salary Leaderboard",   "See how you rank against top professionals.","leaderboard"),
        ("⚖️","Compare Roles",        "Compare salaries across different roles.","compare"),
    ]
    for col, (icon, title, desc, tab) in zip([c1,c2,c3,c4], cards):
        with col:
            st.markdown(f'<div class="feature-card" style="cursor:pointer"><div class="feature-icon">{icon}</div><div class="feature-title">{title}</div><div class="feature-desc">{desc}</div></div>', unsafe_allow_html=True)
            if st.button(f"Open →", key=f"home_card_{tab}"):
                st.session_state.active_tab = tab
                st.rerun()

    # Quick tips
    st.markdown("""
<div class="card">
  <div class="card-title">💡 Quick Tips to Boost Your Salary</div>
  <div class="insight-card">
    <div class="insight-icon insight-icon-green">🌍</div>
    <div>
      <div class="insight-title">Target Remote / Global Roles</div>
      <div class="insight-desc">Remote global companies pay 2–4x Indian market rates. Explore Toptal, Turing, and Remote.com.</div>
    </div>
  </div>
  <div class="insight-card">
    <div class="insight-icon insight-icon-amber">💬</div>
    <div>
      <div class="insight-title">Always Negotiate Your Offer</div>
      <div class="insight-desc">60% of professionals never negotiate. Research market rates and ask for 15–20% above the initial offer.</div>
    </div>
  </div>
  <div class="insight-card">
    <div class="insight-icon insight-icon-blue">📜</div>
    <div>
      <div class="insight-title">Earn Certifications</div>
      <div class="insight-desc">AWS, Google Cloud, PMP certifications add ₹10K–₹25K to your annual salary. Many have free study materials.</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

# --- PREDICT TAB ---
def show_predict_tab():
    st.markdown('<div class="page-title">🔍 Salary Prediction</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Fill your professional details to get your AI-predicted market salary.</div>', unsafe_allow_html=True)

    col_form, col_result = st.columns([1, 1], gap="large")

    with col_form:
        st.markdown('<div class="card"><div class="card-title">Your Professional Profile</div>', unsafe_allow_html=True)

        job_roles = ["Data Scientist","Software Engineer","AI Engineer","Data Analyst",
                     "Machine Learning Engineer","DevOps Engineer","Cloud Engineer",
                     "Cybersecurity Analyst","Product Manager","Business Analyst",
                     "Frontend Developer","Backend Developer","Other"]
        industries = ["Technology","Finance","Healthcare","Consulting","Manufacturing",
                      "Education","Retail","Media","Telecom","Government","Other"]
        edu_levels = ["High School","Diploma","Bachelor's","Master's","PhD","Other"]
        locations  = ["Bangalore","Mumbai","Delhi/NCR","Hyderabad","Chennai",
                      "Pune","Kolkata","Remote","Other"]

        c1, c2 = st.columns(2)
        with c1:
            job = st.selectbox("Job Title / Role *", job_roles, key="p_job")
        with c2:
            industry = st.selectbox("Industry *", industries, key="p_ind")

        c3, c4 = st.columns(2)
        with c3:
            exp = st.number_input("Experience (Years) *", min_value=0, max_value=40, value=3, key="p_exp")
        with c4:
            edu = st.selectbox("Education Level *", edu_levels, key="p_edu")

        c5, c6 = st.columns(2)
        with c5:
            skills = st.number_input("Number of Skills", min_value=0, max_value=30, value=6, key="p_skills")
        with c6:
            certs = st.number_input("Certifications", min_value=0, max_value=20, value=1, key="p_certs")

        location = st.selectbox("Location", locations, key="p_loc")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("⚡ Predict My Salary Now", key="predict_btn"):
            salary = predict_salary(job, industry, exp, edu, skills, certs, location)
            st.session_state.last_prediction = salary
            st.session_state.pred_inputs = {
                "job": job, "industry": industry, "exp": exp,
                "edu": edu, "skills": skills, "certs": certs, "loc": location
            }
            st.rerun()

    with col_result:
        if st.session_state.last_prediction:
            salary   = st.session_state.last_prediction
            inp      = st.session_state.get("pred_inputs", {})
            monthly  = salary // 12
            exp_val  = inp.get("exp", 0)
            level    = ("Fresher" if exp_val<=2 else "Junior" if exp_val<=5
                        else "Mid-Level" if exp_val<=10 else "Senior")
            lo = round(salary*0.85/100000)*100000
            hi = round(salary*1.20/100000)*100000
            ind_key  = inp.get("industry","Other")
            trend    = INDUSTRY_TRENDS.get(ind_key, INDUSTRY_TRENDS["Other"])
            avg      = trend["avg"]
            pct_diff = ((salary - avg) / avg * 100)
            market_pos = f"Top {max(10, 50-int(pct_diff))}%" if pct_diff > 0 else f"Below Average"

            st.markdown(f"""
<div class="result-hero">
  <div class="result-hero-label">Predicted Annual Salary</div>
  <div class="result-hero-amount">₹{salary:,}</div>
  <div class="result-hero-sub">≈ ₹{monthly:,} / month</div>
</div>""", unsafe_allow_html=True)

            mc1, mc2 = st.columns(2)
            metrics = [
                ("Seniority Level", level, ""),
                (f"Salary Range", f"₹{lo//100000:.0f}L–₹{hi//100000:.0f}L", ""),
                ("Market Position", market_pos, ""),
                ("Industry Growth", f"+{trend['growth']}/yr", ""),
            ]
            for i, (label, val, sub) in enumerate(metrics):
                with (mc1 if i%2==0 else mc2):
                    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{val}</div></div>', unsafe_allow_html=True)

            # WhatsApp
            import urllib.parse
            wa_msg = build_whatsapp_message(
                inp.get("job",""),inp.get("exp",0),inp.get("skills",0),
                inp.get("certs",0),inp.get("edu",""),inp.get("industry",""),salary
            )
            wa_url = "https://api.whatsapp.com/send?text=" + urllib.parse.quote(wa_msg)
            st.markdown(f"""
<div class="wa-card">
  <div class="wa-title">📱 Share via WhatsApp</div>
  <div class="wa-desc">Send your full salary report with career tips to your WhatsApp.</div>
  <div class="wa-btn"><a href="{wa_url}" target="_blank">💬 Send to WhatsApp →</a></div>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
<div class="card" style="text-align:center;padding:48px 24px">
  <div style="font-size:48px;margin-bottom:16px">🔍</div>
  <div style="font-size:18px;font-weight:700;margin-bottom:8px">Fill the form and predict</div>
  <div style="font-size:14px;color:#94a3b8">Enter your professional details on the left and click Predict to see your market salary.</div>
</div>""", unsafe_allow_html=True)

# --- INSIGHTS TAB ---
def show_insights_tab():
    st.markdown('<div class="page-title">💡 Salary Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Personalized tips to maximize your earning potential.</div>', unsafe_allow_html=True)

    inp = st.session_state.get("pred_inputs", {})
    if not inp:
        st.info("Run a salary prediction first — then personalized insights will appear here.")
        return

    job    = inp.get("job","Other")
    exp    = inp.get("exp",0)
    skills = inp.get("skills",0)
    certs  = inp.get("certs",0)
    edu    = inp.get("edu","")

    tips = []
    if exp < 3:
        tips.append(("blue","🚀","Build a Strong Portfolio","Create 3–5 GitHub projects. At junior levels, real projects matter more than years of experience."))
    if 3 <= exp < 7:
        tips.append(("green","📈","Apply for Senior Roles Now","Senior roles pay 35–50% more. Rewrite your resume highlighting measurable impact."))
    if exp >= 7:
        tips.append(("amber","🏆","Move into Leadership","Lead/Manager roles pay 50–80% more. Your 7+ years positions you perfectly for this leap."))
    if skills < 8:
        tips.append(("rose","🛠️","Expand Your Skill Set","10+ in-demand skills earn 28% more. Focus on cloud, AI tools, or data pipelines."))
    if certs < 2:
        tips.append(("blue","📜","Earn Certifications","AWS, Google Cloud, PMP add ₹10K–₹25K to your annual salary."))
    if edu in ["High School","Diploma","Other"]:
        tips.append(("green","🎓","Upskill with Online Courses","Online Master's or professional diplomas boost salary 15–20% via Coursera or edX."))
    tips.append(("amber","🌍","Target Remote / Global Roles","Remote global companies pay 2–4x Indian market rates. Explore Toptal, Turing, Remote.com."))
    tips.append(("rose","💬","Always Negotiate","60% of professionals never negotiate. Ask 15–20% above the initial offer."))

    for color, icon, title, desc in tips:
        st.markdown(f"""
<div class="insight-card">
  <div class="insight-icon insight-icon-{color}">{icon}</div>
  <div>
    <div class="insight-title">{title}</div>
    <div class="insight-desc">{desc}</div>
  </div>
</div>""", unsafe_allow_html=True)

# --- ROADMAP TAB ---
def show_roadmap_tab():
    st.markdown('<div class="page-title">🗺️ Career Roadmap</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Your step-by-step path to higher salary levels in your field.</div>', unsafe_allow_html=True)

    inp = st.session_state.get("pred_inputs", {})
    job = inp.get("job","Other") if inp else "Other"
    exp = inp.get("exp", 0)     if inp else 0

    steps  = ROADMAP_BY_ROLE.get(job, ROADMAP_BY_ROLE["Other"])
    skills = SKILLS_BY_ROLE.get(job,  SKILLS_BY_ROLE["Other"])
    cs = 0 if exp<=2 else (1 if exp<=5 else (2 if exp<=10 else (3 if exp<=15 else 4)))

    col_rm, col_sk = st.columns([3, 2], gap="large")

    with col_rm:
        st.markdown(f'<div class="card"><div class="card-title">{job} Career Path</div>', unsafe_allow_html=True)
        for i, step in enumerate(steps):
            if i < cs:
                dot_cls  = "step-dot-done"
                badge    = '<span class="step-badge badge-done">✓ Completed</span>'
                sub_text = "Completed"
            elif i == cs:
                dot_cls  = "step-dot-curr"
                badge    = '<span class="step-badge badge-current">● You Are Here</span>'
                sub_text = "Current Level"
            else:
                dot_cls  = "step-dot-next"
                badge    = '<span class="step-badge badge-future">Upcoming</span>'
                sub_text = "Upcoming"
            st.markdown(f"""
<div class="roadmap-step">
  <div class="step-dot {dot_cls}">{i+1}</div>
  <div>
    <div class="step-title">{step}</div>
    <div class="step-sub">{sub_text} · ~{i*3+2}–{i*3+5} years exp</div>
    {badge}
  </div>
</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_sk:
        st.markdown(f'<div class="card"><div class="card-title">Top Skills for {job}</div>', unsafe_allow_html=True)
        pills = " ".join([f'<span class="pill">{s}</span>' for s in skills])
        st.markdown(f'<div style="padding-top:4px">{pills}</div>', unsafe_allow_html=True)

        # Industry trend
        ind_key = inp.get("industry","Other") if inp else "Other"
        trend   = INDUSTRY_TRENDS.get(ind_key, INDUSTRY_TRENDS["Other"])
        st.markdown(f"""
<div style="margin-top:20px">
<div class="card-title">📊 {ind_key} Industry Trend</div>
<div class="metric-card" style="margin-bottom:10px">
  <div class="metric-label">YoY Growth</div>
  <div class="metric-value">{trend['growth']}</div>
</div>
<div class="metric-card" style="margin-bottom:10px">
  <div class="metric-label">Job Demand</div>
  <div class="metric-value">{trend['demand']}</div>
</div>
<div class="metric-card">
  <div class="metric-label">Outlook</div>
  <div class="metric-value">{trend['outlook']}</div>
</div>
</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- DASHBOARD TAB ---
def show_dashboard_tab():
    st.markdown('<div class="page-title">📊 Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Your salary metrics, market position, and industry trends at a glance.</div>', unsafe_allow_html=True)

    if not st.session_state.last_prediction:
        st.info("Run a salary prediction first to see your analytics dashboard.")
        return

    salary  = st.session_state.last_prediction
    inp     = st.session_state.get("pred_inputs", {})
    monthly = salary // 12
    ind_key = inp.get("industry","Other")
    trend   = INDUSTRY_TRENDS.get(ind_key, INDUSTRY_TRENDS["Other"])
    avg     = trend["avg"]
    diff    = ((salary - avg) / avg * 100)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Your Annual Salary</div><div class="metric-value">₹{salary//100000:.0f}L</div><div class="metric-sub">CTC per year</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Monthly Estimate</div><div class="metric-value">₹{monthly:,}</div><div class="metric-sub">per month</div></div>', unsafe_allow_html=True)
    with m3:
        sign = "+" if diff >= 0 else ""
        st.markdown(f'<div class="metric-card"><div class="metric-label">vs Industry Avg</div><div class="metric-value">{sign}{diff:.0f}%</div><div class="metric-sub">Industry avg: ₹{avg//100000:.0f}L</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Industry Growth</div><div class="metric-value">{trend["growth"]}</div><div class="metric-sub">YoY growth rate</div></div>', unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    with d1:
        st.markdown(f"""
<div class="card">
  <div class="card-title">🏭 Industry Outlook — {ind_key}</div>
  <div class="metric-card" style="margin-bottom:10px">
    <div class="metric-label">Market Demand</div>
    <div class="metric-value">{trend['demand']}</div>
  </div>
  <div class="metric-card" style="margin-bottom:10px">
    <div class="metric-label">Industry Outlook</div>
    <div class="metric-value">{trend['outlook']}</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Top Pay in Field</div>
    <div class="metric-value">{trend['top_pay']}</div>
  </div>
</div>""", unsafe_allow_html=True)

    with d2:
        job = inp.get("job","Other")
        steps = ROADMAP_BY_ROLE.get(job, ROADMAP_BY_ROLE["Other"])
        exp_val = inp.get("exp",0)
        cs = 0 if exp_val<=2 else (1 if exp_val<=5 else (2 if exp_val<=10 else (3 if exp_val<=15 else 4)))
        curr_role = steps[cs]
        next_role = steps[min(cs+1,len(steps)-1)]
        st.markdown(f"""
<div class="card">
  <div class="card-title">🗺️ Your Career Status</div>
  <div class="metric-card" style="margin-bottom:10px">
    <div class="metric-label">Current Role Level</div>
    <div class="metric-value" style="font-size:15px">{curr_role}</div>
  </div>
  <div class="metric-card" style="margin-bottom:10px">
    <div class="metric-label">Next Milestone</div>
    <div class="metric-value" style="font-size:15px">{next_role}</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Experience</div>
    <div class="metric-value">{exp_val} yrs</div>
  </div>
</div>""", unsafe_allow_html=True)

# --- COMPARE TAB ---
def show_compare_tab():
    st.markdown('<div class="page-title">⚖️ Role Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">See how your predicted salary compares against similar roles in the market.</div>', unsafe_allow_html=True)

    inp    = st.session_state.get("pred_inputs", {})
    my_job = inp.get("job","Data Scientist") if inp else "Data Scientist"
    my_sal = st.session_state.last_prediction or 0

    compare_roles = {
        "AI Engineer":1400000,"Data Scientist":1200000,"ML Engineer":1300000,
        "Software Engineer":1100000,"Product Manager":1250000,
        "DevOps Engineer":1050000,"Data Analyst":800000,
        "Business Analyst":850000,"Frontend Developer":900000,"Backend Developer":950000
    }

    if my_sal:
        compare_roles[my_job] = my_sal

    sorted_roles = sorted(compare_roles.items(), key=lambda x: x[1], reverse=True)
    max_sal = sorted_roles[0][1]

    st.markdown('<div class="card"><div class="card-title">Salary Benchmark Comparison</div>', unsafe_allow_html=True)
    for role, sal in sorted_roles[:8]:
        pct   = int(sal / max_sal * 100)
        color = "linear-gradient(90deg,#6366f1,#8b5cf6)" if role==my_job else "rgba(99,102,241,0.3)"
        label = f"{role} {'(You)' if role==my_job else ''}"
        st.markdown(f"""
<div class="cbar-wrap">
  <div class="cbar-lbl">
    <span style="font-weight:{'700' if role==my_job else '400'}">{label}</span>
    <span style="font-weight:700">₹{sal//100000:.0f}L</span>
  </div>
  <div class="cbar-track">
    <div class="cbar-fill" style="width:{pct}%;background:{color}"></div>
  </div>
</div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- LEADERBOARD TAB ---
def show_leaderboard_tab():
    st.markdown('<div class="page-title">🏆 Salary Leaderboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Top earners on SalaryIQ — see how you rank against the best.</div>', unsafe_allow_html=True)

    leaderboard = [
        ("🥇","Arjun Mehta",      "AI Engineer · Bangalore",      "gold",   48),
        ("🥈","Priya Kapoor",     "Data Scientist · Mumbai",       "",       42),
        ("🥉","Rohit Singh",      "Cloud Architect · Hyderabad",   "",       38),
        ("4", "Sneha Iyer",       "ML Engineer · Bangalore",       "",       35),
        ("5", "Vikram Nair",      "Backend Developer · Pune",      "",       32),
        ("6", "Kavya Reddy",      "Product Manager · Delhi",       "",       30),
        ("7", "Aditya Kumar",     "DevOps Engineer · Chennai",     "",       28),
        ("8", "Nisha Patel",      "Data Analyst · Bangalore",      "",       25),
    ]

    for rank, name, role, css_cls, sal_l in leaderboard:
        gold_style = "background:rgba(245,158,11,0.08);border-color:rgba(245,158,11,0.25)" if css_cls=="gold" else ""
        st.markdown(f"""
<div class="lb-row" style="{gold_style}">
  <div class="lb-rank">{rank}</div>
  <div style="flex:1">
    <div class="lb-name">{name}</div>
    <div class="lb-role">{role}</div>
  </div>
  <div class="lb-salary">₹{sal_l}L</div>
</div>""", unsafe_allow_html=True)

    # Show current user
    if st.session_state.last_prediction:
        u     = st.session_state.username
        udata = get_user_data(u)
        name  = udata.get("name", u)
        inp   = st.session_state.get("pred_inputs", {})
        job   = inp.get("job","")
        loc   = inp.get("loc","India")
        sal_l = st.session_state.last_prediction // 100000
        st.markdown(f"""
<div class="lb-row" style="border:2px solid rgba(99,102,241,0.5)">
  <div class="lb-rank">★</div>
  <div style="flex:1">
    <div class="lb-name">{name} (You)</div>
    <div class="lb-role">{job} · {loc}</div>
  </div>
  <div class="lb-salary">₹{sal_l}L</div>
</div>""", unsafe_allow_html=True)

# =========================
# MAIN APP ROUTER
# =========================
def main():
    toggle_lbl = inject_css()

    if not st.session_state.logged_in:
        # ── PRE-LOGIN: minimal sidebar ──
        with st.sidebar:
            st.markdown("""
<div style="padding:28px 20px;text-align:center;background:linear-gradient(160deg,#312e81,#1e1b4b,#0f0a2e)">
  <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.4rem;font-weight:900;color:#fff">💼 SalaryIQ</div>
  <div style="font-size:11px;color:rgba(255,255,255,0.5);margin-top:4px">Know Your Worth</div>
</div>
<div style="padding:16px 14px">
  <div style="font-size:12px;color:#64748b;line-height:1.6;margin-bottom:16px">
    AI-Powered Salary Prediction Platform. Discover your true market value instantly.
  </div>
</div>""", unsafe_allow_html=True)

            st.markdown('<div class="sb-section-title" style="padding:0 14px">✦ Features</div>', unsafe_allow_html=True)
            for feat in ["🎯 95% Accurate ML Model","⚡ Instant Predictions","🗺️ Career Roadmap",
                         "📊 Analytics Dashboard","🏆 Salary Leaderboard","📱 WhatsApp Export"]:
                st.markdown(f'<div style="padding:6px 14px;font-size:13px;color:#94a3b8">  {feat}</div>', unsafe_allow_html=True)

            st.markdown('<div style="height:1px;background:rgba(99,102,241,0.12);margin:12px 0"></div>', unsafe_allow_html=True)
            st.markdown('<div style="padding:0 14px 8px"><div class="sb-section-title" style="margin:0 0 8px">🎨 Appearance</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="theme-btn" style="padding:0 14px 8px">', unsafe_allow_html=True)
            if st.button(toggle_lbl, key="theme_pre"):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Route to landing / login / signup ──
        mode = st.session_state.auth_mode

        if mode == "landing":
            # Show top nav for landing
            st.markdown(f"""
<div style="background:rgba(8,13,26,0.98);border-bottom:1px solid rgba(99,102,241,0.2);
     height:60px;display:flex;align-items:center;justify-content:space-between;padding:0 28px;
     position:sticky;top:0;z-index:100">
  <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:22px;font-weight:900;
       color:#f1f5f9;display:flex;align-items:center;gap:10px">
    💼 Salary<span style="background:linear-gradient(135deg,#6366f1,#8b5cf6);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">IQ</span>
    <span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;
         background:rgba(99,102,241,0.12);color:#6366f1;border:1px solid rgba(99,102,241,0.35);
         text-transform:uppercase;letter-spacing:.5px">PRO</span>
  </div>
</div>""", unsafe_allow_html=True)
            c1, c2, c3 = st.columns([6,1,1])
            with c2:
                if st.button("Sign In",   key="nav_login"):
                    st.session_state.auth_mode = "login";  st.rerun()
            with c3:
                if st.button("Sign Up",   key="nav_signup"):
                    st.session_state.auth_mode = "signup"; st.rerun()

            st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
            show_landing()
            st.markdown('</div>', unsafe_allow_html=True)

        elif mode == "login":
            st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
            show_login()
            st.markdown('</div>', unsafe_allow_html=True)

        elif mode == "signup":
            st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
            show_signup()
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        # ── POST-LOGIN: full sidebar + dashboard ──
        with st.sidebar:
            show_sidebar()

        show_topbar_and_tabs()

        st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
        tab = st.session_state.active_tab
        if tab == "home":        show_home_tab()
        elif tab == "predict":   show_predict_tab()
        elif tab == "insights":  show_insights_tab()
        elif tab == "roadmap":   show_roadmap_tab()
        elif tab == "dashboard": show_dashboard_tab()
        elif tab == "compare":   show_compare_tab()
        elif tab == "leaderboard": show_leaderboard_tab()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="footer-bar">© 2026 SalaryIQ · AI-Powered Career Intelligence Platform · Know Your Worth</div>', unsafe_allow_html=True)

# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()
