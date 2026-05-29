# =========================
# IMPORT LIBRARIES
# =========================
import streamlit as st
import pickle
import pandas as pd
import numpy as np
import os
import random
import urllib.parse
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
# USER DATABASE
# =========================
USER_FILE = "users.pkl"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "rb") as f:
            return pickle.load(f)
    return {"admin": {"password": "1234", "name": "Admin User", "email": "admin@example.com",
                      "phone": "", "city": "", "linkedin": "", "bio": "", "joined": "20 May 2026"}}

def save_users(users):
    with open(USER_FILE, "wb") as f:
        pickle.dump(users, f)

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
    "Technology":    {"growth":"22%","outlook":"Excellent","top_pay":"₹1,80,000","demand":"Very High"},
    "Finance":       {"growth":"15%","outlook":"Strong",   "top_pay":"₹1,60,000","demand":"High"},
    "Healthcare":    {"growth":"18%","outlook":"Excellent","top_pay":"₹1,40,000","demand":"Very High"},
    "Consulting":    {"growth":"12%","outlook":"Strong",   "top_pay":"₹1,70,000","demand":"High"},
    "Manufacturing": {"growth":"8%", "outlook":"Moderate", "top_pay":"₹1,10,000","demand":"Moderate"},
    "Education":     {"growth":"10%","outlook":"Stable",   "top_pay":"₹90,000",  "demand":"Moderate"},
    "Retail":        {"growth":"7%", "outlook":"Moderate", "top_pay":"₹95,000",  "demand":"Moderate"},
    "Media":         {"growth":"9%", "outlook":"Moderate", "top_pay":"₹1,00,000","demand":"Moderate"},
    "Telecom":       {"growth":"11%","outlook":"Strong",   "top_pay":"₹1,30,000","demand":"High"},
    "Government":    {"growth":"6%", "outlook":"Stable",   "top_pay":"₹85,000",  "demand":"Low"},
    "Other":         {"growth":"10%","outlook":"Moderate", "top_pay":"₹1,00,000","demand":"Moderate"},
}

# =========================
# SESSION STATE
# =========================
defaults = {
    "logged_in": False, "username": "", "active_tab": "predict",
    "last_prediction": None, "last_inputs": None,
    "dark_mode": True, "profile_section": "info", "edit_mode": False,
    "show_public_home": True, "sidebar_collapsed": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v
if "users" not in st.session_state:
    st.session_state.users = load_users()

# =========================
# THEME VARIABLES
# =========================
dm = st.session_state.dark_mode
if dm:
    BG            = "linear-gradient(135deg,#020D12 0%,#041520 40%,#062030 100%)"
    SIDEBAR_BG    = "#020D12"
    CARD_BG       = "rgba(6,21,32,0.95)"
    CARD_BG2      = "rgba(7,25,38,0.9)"
    CARD_BORDER   = "rgba(34,211,238,0.2)"
    CARD_BORDER2  = "rgba(14,165,201,0.15)"
    TEXT1         = "#ECFEFF"
    TEXT2         = "#67E8F9"
    TEXT3         = "#0E7490"
    ACCENT        = "#22D3EE"
    ACCENT2       = "#0891B2"
    ACCENT3       = "#67E8F9"
    ACCENT_SOFT   = "rgba(34,211,238,0.1)"
    ACCENT_BORDER = "rgba(34,211,238,0.35)"
    INPUT_BG      = "rgba(6,21,32,0.9)"
    NAV_BG        = "rgba(2,13,18,0.98)"
    DIVIDER       = "rgba(34,211,238,0.12)"
    PROFILE_BG    = "linear-gradient(160deg,#0C2B3A,#0E4563,#0C2B3A)"
    HERO_BG       = "linear-gradient(135deg,#0C2B3A,#0E4563,#155E75)"
    BTN_INACTIVE  = "rgba(34,211,238,0.08)"
    BTN_BORDER    = "rgba(34,211,238,0.25)"
    OPT_BG        = "#041520"
    OPT_H         = "rgba(34,211,238,0.15)"
    OPT_C         = "#ECFEFF"
    OPT_CH        = "#22D3EE"
    METRIC_BG     = "rgba(2,13,18,0.9)"
    BAR_TRACK     = "rgba(7,25,38,0.8)"
    TOGGLE_LBL    = "☀️ Light Mode"
    SUCCESS_BG    = "rgba(16,185,129,0.1)"
    SUCCESS_B     = "rgba(16,185,129,0.3)"
    LB_GOLD       = "rgba(245,158,11,0.1)"
    LB_SILVER     = "rgba(34,211,238,0.06)"
    LB_BRONZE     = "rgba(14,116,144,0.1)"
    STEP_NEXT_BG  = "rgba(6,21,32,0.6)"
    STEP_NEXT_C   = "#0E7490"
    STEP_NEXT_B   = "#0C2B3A"
    GLOW          = "0 0 40px rgba(34,211,238,0.12)"
    WA_BG         = "rgba(37,211,102,0.12)"
    WA_BORDER     = "rgba(37,211,102,0.3)"
    WA_COLOR      = "#25D366"
else:
    BG            = "linear-gradient(135deg,#ECFEFF 0%,#CFFAFE 50%,#E0F7FA 100%)"
    SIDEBAR_BG    = "#F0FDFF"
    CARD_BG       = "#FFFFFF"
    CARD_BG2      = "#F0FDFF"
    CARD_BORDER   = "#A5F3FC"
    CARD_BORDER2  = "#CFFAFE"
    TEXT1         = "#164E63"
    TEXT2         = "#0E7490"
    TEXT3         = "#67E8F9"
    ACCENT        = "#0891B2"
    ACCENT2       = "#0E7490"
    ACCENT3       = "#155E75"
    ACCENT_SOFT   = "#ECFEFF"
    ACCENT_BORDER = "#A5F3FC"
    INPUT_BG      = "#F0FDFF"
    NAV_BG        = "#FFFFFF"
    DIVIDER       = "#CFFAFE"
    PROFILE_BG    = "linear-gradient(160deg,#164E63,#0E7490,#0891B2)"
    HERO_BG       = "linear-gradient(135deg,#164E63,#155E75,#0E7490)"
    BTN_INACTIVE  = "#ECFEFF"
    BTN_BORDER    = "#A5F3FC"
    OPT_BG        = "#FFFFFF"
    OPT_H         = "#ECFEFF"
    OPT_C         = "#164E63"
    OPT_CH        = "#0891B2"
    METRIC_BG     = "#F0FDFF"
    BAR_TRACK     = "#CFFAFE"
    TOGGLE_LBL    = "🌙 Dark Mode"
    SUCCESS_BG    = "#F0FDF4"
    SUCCESS_B     = "#BBF7D0"
    LB_GOLD       = "#FEFCE8"
    LB_SILVER     = "#F0FDFF"
    LB_BRONZE     = "#ECFEFF"
    STEP_NEXT_BG  = "#ECFEFF"
    STEP_NEXT_C   = "#67E8F9"
    STEP_NEXT_B   = "#A5F3FC"
    GLOW          = "0 4px 24px rgba(8,145,178,0.1)"
    WA_BG         = "rgba(37,211,102,0.08)"
    WA_BORDER     = "rgba(37,211,102,0.25)"
    WA_COLOR      = "#16a34a"

# =========================
# INJECT CSS
# =========================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800;900&display=swap');
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
html,body,[class*="css"]{{font-family:'Inter',sans-serif!important;}}
#MainMenu,footer{{visibility:hidden!important;display:none!important;}}

/* ── Streamlit root containers ── */
.stApp{{background:{BG}!important;transition:all 0.4s ease;}}
.stApp>div{{background:transparent!important;}}

/* Remove ALL default block padding so our custom layout takes over */
.block-container{{
  padding:0!important;
  max-width:100%!important;
}}

/* Streamlit v1.x main column wrapper — prevent it sitting under sticky nav */
[data-testid="stAppViewContainer"]{{
  padding-top:0!important;
}}
[data-testid="stAppViewBlockContainer"],
[data-testid="stMainBlockContainer"]{{
  padding-top:0!important;
  padding-left:0!important;
  padding-right:0!important;
  max-width:100%!important;
}}

/* The actual scrollable content area: push it down by navbar height (60px) + a little breathing room */
section.main > div.block-container,
div[data-testid="stVerticalBlock"] > div:first-child{{
  padding-top:0!important;
}}

/* Ensure the sticky header sits above everything */
.top-header{{
  position:sticky!important;
  top:0!important;
  z-index:999!important;
}}

/* Content wrapper offset — compensates for 60px sticky navbar */
.page-wrap{{
  padding-top:20px!important;
}}

div {{color:#38BDF8!important;font-size:16px;}}

section[data-testid="stSidebar"]{{
  background:{SIDEBAR_BG}!important;
  border-right:1px solid {CARD_BORDER}!important;
  min-width:270px!important; max-width:270px!important;
  transition:all 0.3s;
}}
section[data-testid="stSidebar"]>div{{padding:0!important;}}
section[data-testid="stSidebar"] *{{color:{TEXT1}!important;}}

/* Collapsed sidebar narrow mode */
{"section[data-testid='stSidebar']{min-width:80px!important;max-width:80px!important;}" if st.session_state.get("sidebar_collapsed") else ""}

.profile-card{{
  background:{PROFILE_BG};padding:28px 20px 18px;text-align:center;
  position:relative;overflow:hidden;
}}
.profile-card::before{{
  content:'';position:absolute;top:-30px;right:-30px;
  width:120px;height:120px;border-radius:50%;
  background:rgba(255,255,255,0.05);
}}
.profile-card::after{{
  content:'';position:absolute;bottom:-20px;left:-20px;
  width:80px;height:80px;border-radius:50%;
  background:rgba(255,255,255,0.04);
}}
.profile-avatar{{
  width:76px;height:76px;border-radius:50%;
  background:rgba(255,255,255,0.2);
  margin:0 auto 12px;display:flex;align-items:center;justify-content:center;
  font-size:28px;font-weight:800;color:#fff!important;
  border:3px solid rgba(255,255,255,0.5);
  box-shadow:0 4px 20px rgba(0,0,0,0.3);
  position:relative;z-index:1;
}}
.profile-name{{
  font-family:'Plus Jakarta Sans',sans-serif!important;
  font-size:17px;font-weight:800;color:#fff!important;
  position:relative;z-index:1;
}}
.profile-email{{font-size:11px;color:rgba(255,255,255,0.65)!important;margin-top:3px;position:relative;z-index:1;}}
.profile-since{{font-size:10px;color:rgba(255,255,255,0.45)!important;margin-top:2px;position:relative;z-index:1;}}
.profile-stats{{
  display:flex;margin-top:16px;border-top:1px solid rgba(255,255,255,0.12);
  padding-top:14px;position:relative;z-index:1;
}}
.profile-stat{{flex:1;text-align:center;border-right:1px solid rgba(255,255,255,0.12);}}
.profile-stat:last-child{{border-right:none;}}
.profile-stat-val{{font-family:'Plus Jakarta Sans',sans-serif!important;font-size:16px;font-weight:800;color:#fff!important;}}
.profile-stat-lbl{{font-size:9px;color:rgba(255,255,255,0.55)!important;margin-top:2px;text-transform:uppercase;letter-spacing:.5px;}}

.sidebar-inner{{padding:12px 14px;}}
.sb-section-title{{
  font-size:10px;font-weight:700;color:{TEXT3}!important;
  text-transform:uppercase;letter-spacing:1.2px;
  margin:14px 0 7px;padding:0 2px;
}}
.contact-item{{
  display:flex;align-items:flex-start;gap:10px;
  padding:8px 2px;border-bottom:1px solid {DIVIDER};
}}
.contact-item:last-child{{border-bottom:none;}}
.contact-icon{{font-size:14px;width:20px;text-align:center;flex-shrink:0;margin-top:1px;}}
.contact-label{{font-size:9px;color:{TEXT3}!important;text-transform:uppercase;letter-spacing:.5px;}}
.contact-val{{font-size:12px;color:{TEXT1}!important;font-weight:500;margin-top:1px;word-break:break-all;}}

.signout-wrap{{padding:8px 14px 16px;}}
.signout-wrap .stButton>button{{
  background:rgba(239,68,68,0.08)!important;color:#ef4444!important;
  border:1.5px solid rgba(239,68,68,0.25)!important;
  height:40px!important;font-size:13px!important;font-weight:600!important;
  box-shadow:none!important;border-radius:10px!important;
}}
.signout-wrap .stButton>button:hover{{background:rgba(239,68,68,0.18)!important;}}

.theme-sb .stButton>button{{
  background:{ACCENT_SOFT}!important;color:{ACCENT}!important;
  border:1.5px solid {ACCENT_BORDER}!important;
  height:38px!important;font-size:13px!important;font-weight:600!important;
  box-shadow:none!important;border-radius:9px!important;
}}

.top-header{{
  background:{NAV_BG};border-bottom:1px solid {CARD_BORDER};
  padding:0 28px;display:flex;align-items:center;justify-content:space-between;
  height:60px;box-shadow:{GLOW};
  position:sticky;top:0;z-index:999;
  width:100%;box-sizing:border-box;
}}
.top-logo{{
  font-family:'Plus Jakarta Sans',sans-serif!important;
  font-size:22px;font-weight:900;color:{TEXT1}!important;
  display:flex;align-items:center;gap:10px;letter-spacing:-0.5px;
}}
.top-logo em{{
  background:linear-gradient(135deg,{ACCENT},{ACCENT2});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;font-style:normal;
}}
.top-badge{{
  font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;
  background:{ACCENT_SOFT};color:{ACCENT}!important;
  border:1px solid {ACCENT_BORDER};letter-spacing:.5px;text-transform:uppercase;
}}
.top-right{{display:flex;align-items:center;gap:12px;}}
.top-avatar{{
  width:34px;height:34px;border-radius:50%;
  background:linear-gradient(135deg,{ACCENT},{ACCENT2});
  display:flex;align-items:center;justify-content:center;
  font-size:13px;font-weight:700;color:#fff!important;
  box-shadow:0 2px 8px rgba(99,102,241,0.35);
}}
.top-username{{font-size:13px;font-weight:600;color:{TEXT1}!important;}}

.page-wrap{{
  padding:24px 28px 40px;
  max-width:1120px;
  margin:0 auto;
}}

/* ── Responsive: mobile ── */
@media(max-width:768px){{
  .top-header{{padding:0 14px;height:54px;}}
  .page-wrap{{padding:16px 14px 32px;}}
  .result-hero-amount{{font-size:38px!important;}}
  .stat-strip{{flex-wrap:wrap;}}
  .stat-strip-item{{min-width:50%;border-bottom:1px solid {DIVIDER};}}
}}
.page-title{{
  font-family:'Plus Jakarta Sans',sans-serif!important;
  font-size:24px;font-weight:900;color:{TEXT1}!important;
  margin-bottom:5px;letter-spacing:-0.3px;
}}
.page-sub{{font-size:14px;color:{TEXT2}!important;margin-bottom:22px;line-height:1.6;}}

.section-heading{{
  font-family:'Plus Jakarta Sans',sans-serif!important;
  font-size:13px;font-weight:700;color:{ACCENT}!important;
  text-transform:uppercase;letter-spacing:1.2px;margin-bottom:14px;
  display:flex;align-items:center;gap:6px;
}}

.card{{
  background:{CARD_BG};border-radius:18px;
  border:1px solid {CARD_BORDER};padding:22px;
  box-shadow:{GLOW};margin-bottom:16px;
  transition:all 0.3s;
}}
.card:hover{{box-shadow:0 8px 32px rgba(99,102,241,0.18);}}
.card-title{{
  font-size:10px;font-weight:700;color:{ACCENT}!important;
  text-transform:uppercase;letter-spacing:1.2px;margin-bottom:14px;
  padding-bottom:10px;border-bottom:1px solid {DIVIDER};
}}

.metric-card{{
  background:{METRIC_BG};border:1px solid {CARD_BORDER};
  border-radius:14px;padding:16px 14px;
  box-shadow:{GLOW};transition:all 0.3s;
}}
.metric-label{{font-size:10px;color:{TEXT3}!important;font-weight:600;margin-bottom:6px;text-transform:uppercase;letter-spacing:.6px;}}
.metric-value{{font-size:20px;font-weight:800;color:{TEXT1}!important;font-family:'Plus Jakarta Sans',sans-serif!important;}}
.metric-sub{{font-size:11px;color:#10b981!important;font-weight:600;margin-top:4px;}}

.result-hero{{
  background:{HERO_BG};border-radius:22px;
  padding:38px 32px;text-align:center;margin-bottom:22px;
  box-shadow:0 16px 48px rgba(99,102,241,0.35),0 4px 16px rgba(0,0,0,0.15);
  position:relative;overflow:hidden;
}}
.result-hero::before{{
  content:'';position:absolute;top:-40px;right:-40px;
  width:180px;height:180px;border-radius:50%;
  background:rgba(255,255,255,0.06);
}}
.result-hero::after{{
  content:'';position:absolute;bottom:-30px;left:-30px;
  width:120px;height:120px;border-radius:50%;
  background:rgba(255,255,255,0.04);
}}
.result-hero-label{{font-size:11px;color:rgba(255,255,255,0.7)!important;letter-spacing:2px;text-transform:uppercase;position:relative;z-index:1;}}
.result-hero-amount{{font-size:58px;font-weight:900;color:#fff!important;margin:10px 0;font-family:'Plus Jakarta Sans',sans-serif!important;position:relative;z-index:1;text-shadow:0 2px 20px rgba(0,0,0,0.2);}}
.result-hero-sub{{font-size:13px;color:rgba(255,255,255,0.65)!important;position:relative;z-index:1;}}

.insight-card{{
  background:{CARD_BG};border-radius:14px;border:1px solid {CARD_BORDER};
  padding:16px 18px;margin-bottom:10px;display:flex;gap:14px;align-items:flex-start;
  transition:all 0.2s;
}}
.insight-card:hover{{border-color:{ACCENT_BORDER};box-shadow:0 4px 16px rgba(99,102,241,0.12);}}
.insight-icon{{width:40px;height:40px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;}}
.insight-icon-blue  {{background:{'rgba(99,102,241,0.15)' if dm else '#eef2ff'};}}
.insight-icon-green {{background:{'rgba(16,185,129,0.15)' if dm else '#f0fdf4'};}}
.insight-icon-amber {{background:{'rgba(245,158,11,0.15)'  if dm else '#fffbeb'};}}
.insight-icon-rose  {{background:{'rgba(244,63,94,0.15)'   if dm else '#fff1f2'};}}
.insight-title{{font-size:14px;font-weight:700;color:{TEXT1}!important;margin-bottom:4px;}}
.insight-desc{{font-size:13px;color:{TEXT2}!important;line-height:1.6;}}

.roadmap-step{{display:flex;gap:14px;align-items:flex-start;padding:18px 0;border-bottom:1px solid {DIVIDER};}}
.roadmap-step:last-child{{border-bottom:none;}}
.step-dot{{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;flex-shrink:0;margin-top:2px;}}
.step-dot-done{{background:{ACCENT};color:#fff;}}
.step-dot-curr{{background:linear-gradient(135deg,{ACCENT},{ACCENT2});color:#fff;box-shadow:0 0 0 5px {ACCENT_SOFT};}}
.step-dot-next{{background:{STEP_NEXT_BG};color:{STEP_NEXT_C}!important;border:2px dashed {STEP_NEXT_B};}}
.step-title{{font-size:15px;font-weight:700;color:{TEXT1}!important;}}
.step-sub{{font-size:12px;color:{TEXT2}!important;margin-top:3px;}}
.step-badge{{display:inline-block;font-size:10px;font-weight:700;padding:3px 10px;border-radius:99px;margin-top:6px;letter-spacing:.3px;}}
.badge-current{{background:{ACCENT_SOFT};color:{ACCENT}!important;}}
.badge-done{{background:{'rgba(16,185,129,0.15)' if dm else '#dcfce7'};color:#10b981!important;}}
.badge-future{{background:{'rgba(30,41,59,0.4)' if dm else '#f1f5f9'};color:{TEXT3}!important;}}

.compare-bar-wrap{{margin-bottom:14px;}}
.compare-bar-label{{display:flex;justify-content:space-between;font-size:13px;margin-bottom:5px;}}
.compare-bar-track{{height:8px;background:{BAR_TRACK};border-radius:99px;overflow:hidden;}}
.compare-bar-fill{{height:100%;border-radius:99px;}}

.lb-row{{display:flex;align-items:center;gap:14px;padding:14px 16px;border-radius:14px;margin-bottom:8px;border:1px solid {CARD_BORDER};transition:all 0.2s;background:{CARD_BG};}}
.lb-row:hover{{background:{ACCENT_SOFT};border-color:{ACCENT_BORDER};transform:translateX(3px);}}
.lb-row.gold  {{background:{LB_GOLD};border-color:{'rgba(245,158,11,0.3)' if dm else '#fde68a'};}}
.lb-row.silver{{background:{LB_SILVER};}}
.lb-row.bronze{{background:{LB_BRONZE};border-color:{'rgba(180,83,9,0.3)' if dm else '#fed7aa'};}}
.lb-rank{{font-size:16px;font-weight:800;min-width:28px;color:{TEXT1}!important;}}
.lb-name{{flex:1;font-size:13px;font-weight:700;color:{TEXT1}!important;}}
.lb-role{{font-size:11px;color:{TEXT2}!important;margin-top:2px;}}
.lb-salary{{font-size:16px;font-weight:800;color:{ACCENT}!important;font-family:'Plus Jakarta Sans',sans-serif!important;}}

.wa-card{{
  background:{WA_BG};border:1.5px solid {WA_BORDER};
  border-radius:16px;padding:20px;margin-top:18px;
}}
.wa-title{{font-size:14px;font-weight:700;color:{WA_COLOR}!important;margin-bottom:8px;display:flex;align-items:center;gap:8px;}}
.wa-desc{{font-size:13px;color:{TEXT2}!important;line-height:1.6;margin-bottom:14px;}}
.wa-btn a{{
  display:inline-flex;align-items:center;gap:8px;
  background:linear-gradient(135deg,#25D366,#128C7E);
  color:#fff!important;font-weight:700;font-size:14px;
  padding:12px 24px;border-radius:12px;text-decoration:none;
  box-shadow:0 4px 16px rgba(37,211,102,0.3);transition:all 0.2s;
}}
.wa-btn a:hover{{box-shadow:0 6px 24px rgba(37,211,102,0.45);transform:translateY(-1px);}}

.feature-card{{
  background:{CARD_BG};border:1px solid {CARD_BORDER};
  padding:26px 20px;border-radius:20px;text-align:center;
  transition:all 0.3s;box-shadow:{GLOW};
}}
.feature-card:hover{{transform:translateY(-5px);box-shadow:0 16px 40px rgba(99,102,241,0.18);border-color:{ACCENT_BORDER};}}
.feature-icon{{font-size:36px;margin-bottom:12px;}}
.feature-title{{font-family:'Plus Jakarta Sans',sans-serif!important;font-size:15px;font-weight:800;color:{TEXT1}!important;margin-bottom:6px;}}
.feature-desc{{font-size:13px;color:{TEXT2}!important;line-height:1.5;}}

.stat-strip{{
  background:{CARD_BG};border:1px solid {CARD_BORDER};border-radius:16px;
  display:flex;padding:20px 0;margin-bottom:24px;box-shadow:{GLOW};
}}
.stat-strip-item{{flex:1;text-align:center;border-right:1px solid {DIVIDER};}}
.stat-strip-item:last-child{{border-right:none;}}
.stat-strip-val{{font-family:'Plus Jakarta Sans',sans-serif!important;font-size:24px;font-weight:900;background:linear-gradient(135deg,{ACCENT},{ACCENT2});-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}}
.stat-strip-lbl{{font-size:11px;color:{TEXT2}!important;margin-top:3px;font-weight:500;}}

.login-card{{
  background:{CARD_BG};border:1px solid {CARD_BORDER};
  padding:32px;border-radius:22px;box-shadow:{GLOW};
}}
.login-heading{{font-family:'Plus Jakarta Sans',sans-serif!important;font-size:26px;font-weight:900;color:{TEXT1}!important;margin-bottom:6px;}}
.login-sub{{font-size:14px;color:{TEXT2}!important;margin-bottom:24px;}}

.footer{{text-align:center;color:{TEXT3}!important;padding:24px;font-size:12px;border-top:1px solid {DIVIDER};margin-top:20px;}}

.trend-up{{color:#10b981!important;font-weight:700;font-size:12px;}}
.pill{{display:inline-block;background:{ACCENT_SOFT};color:{ACCENT}!important;border-radius:99px;padding:5px 14px;font-size:12px;font-weight:600;margin:3px;border:1px solid {ACCENT_BORDER};}}
h1,h2,h3{{font-family:'Plus Jakarta Sans',sans-serif!important;color:{TEXT1}!important;}}
p,li{{color:{TEXT2}!important;}}

.stTextInput input,.stNumberInput input{{
  background:{INPUT_BG}!important;border:1.5px solid {CARD_BORDER}!important;
  border-radius:11px!important;color:#38BDF8!important;font-size:14px!important;padding:10px 14px!important;
}}
.stTextInput input:focus,.stNumberInput input:focus{{border-color:{ACCENT}!important;box-shadow:0 0 0 3px {ACCENT_SOFT}!important;}}
.stTextInput label,.stNumberInput label,.stSelectbox label{{color:{TEXT2}!important;font-size:12px!important;font-weight:600!important;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px;}}
.stTextInput textarea{{background:{INPUT_BG}!important;border:1.5px solid {CARD_BORDER}!important;border-radius:11px!important;color:{TEXT1}!important;font-size:14px!important;}}
.stSelectbox>div>div{{background:{INPUT_BG}!important;border:1.5px solid {CARD_BORDER}!important;border-radius:11px!important;}}
[data-baseweb="popover"],[data-baseweb="menu"],[role="listbox"]{{background:{OPT_BG}!important;border:1px solid {CARD_BORDER}!important;border-radius:14px!important;box-shadow:0 8px 32px rgba(0,0,0,0.15)!important;}}
[data-baseweb="menu"] li,[role="option"]{{background:{OPT_BG}!important;color:{OPT_C}!important;font-size:14px!important;}}
[data-baseweb="menu"] li:hover,[role="option"]:hover,[role="option"][aria-selected="true"]{{background:{OPT_H}!important;color:{OPT_CH}!important;}}

.stButton>button{{
  background:linear-gradient(135deg,{ACCENT},{ACCENT2})!important;
  display:flex!important;justify-content:center!important;align-items:center!important;
  color:#fff!important;border:none!important;border-radius:11px!important;
  height:46px!important;font-size:14px!important;font-weight:700!important;
  box-shadow:0 4px 16px rgba(99,102,241,0.3)!important;transition:all 0.2s!important;
  width:100%!important;letter-spacing:.2px;
}}
.stButton>button:hover{{transform:translateY(-1px)!important;box-shadow:0 8px 24px rgba(99,102,241,0.45)!important;}}

.stSlider>div>div>div>div{{background:linear-gradient(90deg,{ACCENT},{ACCENT2})!important;}}

/* Public home Login button special style */
.login-cta .stButton>button{{
  background:linear-gradient(135deg,{ACCENT},{ACCENT2})!important;
  font-size:16px!important;height:54px!important;
  box-shadow:0 8px 24px rgba(99,102,241,0.4)!important;
  border-radius:14px!important;
}}
</style>
""", unsafe_allow_html=True)

# =========================
# HELPERS
# =========================
def get_initials(name):
    parts = name.strip().split()
    return (parts[0][0] + (parts[1][0] if len(parts) > 1 else "")).upper()

def get_user_data(username):
    users = st.session_state.users
    u = users.get(username)
    if isinstance(u, dict):
        return u
    return {"password": u, "name": username, "email": "", "phone": "", "city": "", "linkedin": "", "bio": "", "joined": "2026"}

def salary_boost_tips(job, exp, skills, cert, edu):
    tips = []
    if exp < 3:    tips.append(("🚀","Build a strong portfolio","Create 3–5 GitHub projects. At junior levels, real projects matter more than years of experience.","blue"))
    if 3<=exp<7:   tips.append(("📈","Apply for senior roles now","Senior roles pay 35–50% more. Rewrite your resume highlighting impact and measurable outcomes.","green"))
    if exp >= 7:   tips.append(("🏆","Move into leadership","Lead/Manager roles pay 50–80% more. Your 7+ years positions you perfectly for this leap.","amber"))
    if skills < 8: tips.append(("🛠️","Expand your skill set","10+ in-demand skills earn 28% more. Focus on cloud, data pipelines, or AI tools in your domain.","rose"))
    if cert < 2:   tips.append(("📜","Earn certifications","AWS, Google Cloud, PMP add ₹10K–₹25K to your annual salary. Many offer free study materials.","blue"))
    if edu in ["High School","Diploma","Other"]: tips.append(("🎓","Upskill with online courses","Online Master's or professional diplomas can boost salary by 15–20% via Coursera or edX.","green"))
    tips.append(("🌍","Target remote / global roles","Remote global companies pay 2–4x Indian market rates. Explore Toptal, Turing, and Remote.com.","amber"))
    tips.append(("💬","Negotiate your offer","60% of professionals never negotiate. Research market rates and ask for 15–20% above the offer.","rose"))
    return tips

def build_whatsapp_message(inp, salary):
    job=inp.get("job_title","N/A"); exp=inp.get("experience_years",0)
    skills=inp.get("skills_count",0); cert=inp.get("certifications",0)
    edu=inp.get("education_level","N/A"); ind=inp.get("industry","N/A")
    monthly = salary // 12
    sen = "Fresher" if exp<=2 else ("Junior" if exp<=5 else ("Mid-Level" if exp<=10 else "Senior"))
    top_skills = SKILLS_BY_ROLE.get(job, SKILLS_BY_ROLE["Other"])[:4]
    roadmap    = ROADMAP_BY_ROLE.get(job, ROADMAP_BY_ROLE["Other"])
    trend      = INDUSTRY_TRENDS.get(ind, INDUSTRY_TRENDS["Other"])
    cs         = 0 if exp<=2 else (1 if exp<=5 else (2 if exp<=10 else (3 if exp<=15 else 4)))
    curr_role  = roadmap[cs]
    next_role  = roadmap[min(cs+1, len(roadmap)-1)]

    msg = f"""💼 *SalaryIQ — Career Insights Report*
━━━━━━━━━━━━━━━━━━━
👤 *Profile Summary*
• Role: {job}
• Experience: {exp} years ({sen})
• Skills: {skills}
• Certifications: {cert}
• Education: {edu}
• Industry: {ind}

💰 *Salary Prediction*
• Annual: ₹{salary:,}
• Monthly: ₹{monthly:,}

📈 *Career Roadmap*
• Current: {curr_role}
• Next Goal: {next_role}

🛠️ *Top Skills to Learn*
{chr(10).join(f"  ✅ {s}" for s in top_skills)}

🏭 *{ind} Industry Trend*
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
# LOGIN PAGE
# =========================
def show_login():
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="login-heading">Welcome back 👋</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="login-sub">Sign in to your career intelligence dashboard</div>', unsafe_allow_html=True)
    u = st.text_input("Username", placeholder="Enter your username", key="li_u")
    p = st.text_input("Password", type="password", placeholder="Enter your password", key="li_p")
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    if st.button("Sign In →", key="li_btn"):
        users = st.session_state.users
        udata = get_user_data(u) if u in users else None
        if udata and udata.get("password") == p:
            st.session_state.logged_in  = True
            st.session_state.username   = u
            st.session_state.active_tab = "predict"   # ← lands on Predict tab
            st.session_state.show_public_home = False
            st.success(f"Welcome {udata.get('name', u)} 🎉")
            st.rerun()
        else:
            st.error("Invalid username or password")
    st.markdown('</div>', unsafe_allow_html=True)

def show_signup():
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="login-heading">Create account 🚀</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="login-sub">Join thousands discovering their true market value</div>', unsafe_allow_html=True)
    name  = st.text_input("Full Name",        placeholder="John Doe",          key="su_name")
    email = st.text_input("Email",            placeholder="you@example.com",   key="su_email")
    u     = st.text_input("Username",         placeholder="Choose a username", key="su_u")
    p     = st.text_input("Password",         type="password", placeholder="Min. 6 characters", key="su_p")
    cp    = st.text_input("Confirm Password", type="password", placeholder="Repeat password",   key="su_cp")
    if st.button("Create Account →", key="su_btn"):
        if u in st.session_state.users: st.warning("Username already exists")
        elif p != cp: st.warning("Passwords do not match")
        elif len(p) < 6: st.warning("Password must be at least 6 characters")
        elif not u: st.warning("Please fill all fields")
        else:
            st.session_state.users[u] = {"password":p,"name":name or u,"email":email,
                "phone":"","city":"","linkedin":"","bio":"","joined":datetime.now().strftime("%d %b %Y")}
            save_users(st.session_state.users)
            st.success("Account created! Please login ✅")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# SIDEBAR (logged-in only)
# =========================
def show_sidebar():
    u     = st.session_state.username
    udata = get_user_data(u)
    name  = udata.get("name", u)
    email = udata.get("email","")
    phone = udata.get("phone","")
    city  = udata.get("city","")
    lnkd  = udata.get("linkedin","")
    bio   = udata.get("bio","")
    joined= udata.get("joined","2026")
    initials = get_initials(name)
    pred_count = 1 if st.session_state.last_prediction else 0
    best_salary = st.session_state.last_prediction or 0
    best_fmt = f"₹{best_salary//1000}K" if best_salary else "—"
    pic_data = udata.get("profile_pic","")

    # Collapse/Expand toggle button at the very top
    collapsed = st.session_state.get("sidebar_collapsed", False)
    toggle_arrow = "»" if collapsed else "«"
    st.sidebar.markdown(f"""
    <style>
    .collapse-btn-wrap {{text-align:right;padding:8px 10px 0px;}}
    .collapse-btn-wrap button {{background:transparent!important;border:1px solid {CARD_BORDER}!important;
      color:{TEXT2}!important;border-radius:8px!important;font-size:16px!important;font-weight:700!important;
      width:36px!important;height:36px!important;min-height:36px!important;padding:0!important;cursor:pointer;
      box-shadow:none!important;}}
    </style>
    """, unsafe_allow_html=True)
    if st.sidebar.button(toggle_arrow, key="sb_collapse_btn"):
        st.session_state.sidebar_collapsed = not collapsed
        st.rerun()

    if collapsed:
        # Minimized sidebar: show only avatar and expand arrow hint
        if pic_data:
            st.sidebar.markdown(f'<div style="text-align:center;padding:10px 0;"><img src="{pic_data}" style="width:52px;height:52px;border-radius:50%;object-fit:cover;border:3px solid rgba(255,255,255,0.5);"/></div>', unsafe_allow_html=True)
        else:
            st.sidebar.markdown(f'<div style="text-align:center;padding:10px 0;"><div style="width:52px;height:52px;border-radius:50%;background:rgba(255,255,255,0.2);margin:0 auto;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:800;color:#fff;border:3px solid rgba(255,255,255,0.5);">{initials}</div></div>', unsafe_allow_html=True)
        return  # Don't render rest of sidebar when collapsed

    # Profile card with optional photo
    if pic_data:
        avatar_html = f'<img src="{pic_data}" style="width:76px;height:76px;border-radius:50%;object-fit:cover;border:3px solid rgba(255,255,255,0.5);box-shadow:0 4px 20px rgba(0,0,0,0.3);position:relative;z-index:1;"/>'
    else:
        avatar_html = f'<div class="profile-avatar">{initials}</div>'

    st.sidebar.markdown(f"""
    <div class="profile-card">
      {avatar_html}
      <div class="profile-name">{name}</div>
      <div class="profile-email">{email or '—'}</div>
      <div class="profile-since">Member since {joined}</div>
      <div class="profile-stats">
        <div class="profile-stat"><div class="profile-stat-val">{pred_count}</div><div class="profile-stat-lbl">Predictions</div></div>
        <div class="profile-stat"><div class="profile-stat-val">{best_fmt}</div><div class="profile-stat-lbl">Best Salary</div></div>
        <div class="profile-stat"><div class="profile-stat-val">1</div><div class="profile-stat-lbl">Badges</div></div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.sidebar.markdown('<div class="sidebar-inner">', unsafe_allow_html=True)

    sec = st.session_state.profile_section
    c1, c2, c3 = st.sidebar.columns([1, 1, 1.5], gap="small")
    with c1:
        if st.button("Info",     key="sb_info", use_container_width=True):
            st.session_state.profile_section="info"; st.rerun()
    with c2:
        if st.button("Edit",     key="sb_edit", use_container_width=True):
            st.session_state.profile_section="edit"; st.rerun()
    with c3:
        if st.button("Security", key="sb_sec",  use_container_width=True):
            st.session_state.profile_section="security"; st.rerun()

    st.sidebar.markdown(f'<div style="height:1px;background:{DIVIDER};margin:10px 0;"></div>', unsafe_allow_html=True)

    if sec == "info":
        st.sidebar.markdown(f'<div class="sb-section-title">About</div>', unsafe_allow_html=True)
        st.sidebar.markdown(f'<div style="font-size:12px;color:{TEXT2};padding:4px 2px;line-height:1.6;">{bio or "No bio added yet."}</div>', unsafe_allow_html=True)
        st.sidebar.markdown(f'<div class="sb-section-title">Contact</div>', unsafe_allow_html=True)
        for icon,label,val in [("📞","Phone",phone or "—"),("🏙️","City",city or "—"),("🔗","LinkedIn",lnkd or "—"),("📧","Email",email or "—")]:
            st.sidebar.markdown(f'<div class="contact-item"><div class="contact-icon">{icon}</div><div><div class="contact-label">{label}</div><div class="contact-val">{val}</div></div></div>', unsafe_allow_html=True)

    elif sec == "edit":
        st.sidebar.markdown(f'<div class="sb-section-title">Edit Profile</div>', unsafe_allow_html=True)
        # Profile picture upload
        st.sidebar.markdown(f'<div style="font-size:11px;color:{TEXT2};font-weight:600;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px;">Profile Picture</div>', unsafe_allow_html=True)
        uploaded_pic = st.sidebar.file_uploader("Upload Photo", type=["png","jpg","jpeg","webp"], key="pic_upload", label_visibility="collapsed")
        if uploaded_pic is not None:
            import base64
            pic_bytes = uploaded_pic.read()
            pic_b64 = base64.b64encode(pic_bytes).decode()
            mime = uploaded_pic.type
            pic_data_url = f"data:{mime};base64,{pic_b64}"
            ud = get_user_data(u)
            ud["profile_pic"] = pic_data_url
            st.session_state.users[u] = ud
            save_users(st.session_state.users)
            st.sidebar.success("Photo updated ✅")
            st.rerun()
        if pic_data:
            if st.sidebar.button("🗑️ Remove Photo", key="rm_pic"):
                ud = get_user_data(u)
                ud["profile_pic"] = ""
                st.session_state.users[u] = ud
                save_users(st.session_state.users)
                st.rerun()
        nn  = st.sidebar.text_input("Full Name",  value=name,  key="en")
        ne  = st.sidebar.text_input("Email",      value=email, key="ee")
        np_ = st.sidebar.text_input("Phone",      value=phone, key="ep")
        nc  = st.sidebar.text_input("City",       value=city,  key="ec")
        nl  = st.sidebar.text_input("LinkedIn",   value=lnkd,  key="el")
        nb  = st.sidebar.text_area("Bio",         value=bio,   key="eb", height=70)
        if st.sidebar.button("💾 Save", key="save_p"):
            ud = get_user_data(u); ud.update({"name":nn,"email":ne,"phone":np_,"city":nc,"linkedin":nl,"bio":nb})
            st.session_state.users[u]=ud; save_users(st.session_state.users)
            st.session_state.profile_section="info"; st.sidebar.success("Saved ✅"); st.rerun()

    elif sec == "security":
        st.sidebar.markdown(f'<div class="sb-section-title">Change Password</div>', unsafe_allow_html=True)
        op  = st.sidebar.text_input("Current Password", type="password", key="sec_o")
        np1 = st.sidebar.text_input("New Password",     type="password", key="sec_n1")
        np2 = st.sidebar.text_input("Confirm New",      type="password", key="sec_n2")
        if st.sidebar.button("🔒 Update", key="upd_pwd"):
            ud = get_user_data(u)
            if ud["password"] != op: st.sidebar.error("Wrong current password")
            elif np1 != np2:         st.sidebar.error("Passwords don't match")
            elif len(np1) < 6:       st.sidebar.error("Min 6 characters")
            else:
                ud["password"]=np1; st.session_state.users[u]=ud; save_users(st.session_state.users)
                st.sidebar.success("Password updated ✅")

    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<div style="height:1px;background:{DIVIDER};margin:4px 0;"></div>', unsafe_allow_html=True)

    st.sidebar.markdown(f'<div style="padding:8px 14px 4px;"><div class="sb-section-title" style="margin:0 0 8px;">🎨 Appearance</div></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="theme-sb" style="padding:0 14px 8px;">', unsafe_allow_html=True)
    if st.sidebar.button(TOGGLE_LBL, key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode; st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    st.sidebar.markdown(f'<div style="height:1px;background:{DIVIDER};margin:4px 0;"></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="signout-wrap">', unsafe_allow_html=True)
    if st.sidebar.button("🚪 Sign Out", key="signout"):
        st.session_state.logged_in        = False
        st.session_state.show_public_home = True
        st.session_state.last_prediction  = None
        st.session_state.last_inputs      = None
        st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

# =========================
# TOP BAR + NAV TABS
# ── "Home" tab removed from the logged-in nav ──
# =========================
def show_topbar():
    u = st.session_state.username
    udata = get_user_data(u)
    name = udata.get("name", u)
    initials = get_initials(name)
    st.markdown(f"""
    <div class="top-header">
      <div class="top-logo">💼 Salary<em>IQ</em> <span class="top-badge">PRO</span></div>
      <div class="top-right">
        <div class="top-user" style="display:flex;align-items:center;gap:8px;">
          <div class="top-avatar">{initials}</div>
          <span class="top-username">{name}</span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Home removed; starts directly at Predict ──
    tabs   = ["predict","insights","roadmap","dashboard","compare","leaderboard"]
    labels = ["🔍 Predict","💡 Insights","🗺️ Roadmap","📊 Dashboard","⚖️ Compare","🏆 Leaderboard"]
    active = st.session_state.active_tab
    cols   = st.columns(len(tabs))
    for i,(col,tab,label) in enumerate(zip(cols,tabs,labels)):
        with col:
            is_act = tab == active
            st.markdown(f"""<style>
            div[data-testid="stHorizontalBlock"]>div:nth-child({i+1}) .stButton>button{{
              background:{'linear-gradient(135deg,' + ACCENT + ',' + ACCENT2 + ')' if is_act else BTN_INACTIVE}!important;
              color:{'#ffffff' if is_act else TEXT2}!important;
              border:1px solid {ACCENT if is_act else BTN_BORDER}!important;
              height:38px!important;font-size:12px!important;font-weight:{'700' if is_act else '500'}!important;
              border-radius:9px!important;
              box-shadow:{'0 4px 12px rgba(99,102,241,0.28)' if is_act else 'none'}!important;
            }}
            </style>""", unsafe_allow_html=True)
            if st.button(label, key=f"nav_{tab}"):
                st.session_state.active_tab=tab; st.rerun()
    st.markdown(f'<div style="height:1px;background:{DIVIDER};"></div>', unsafe_allow_html=True)

# =========================
# HOME PAGE  (public landing only)
# =========================
def show_home():
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:{HERO_BG};border-radius:24px;padding:48px 40px;margin-bottom:28px;
                position:relative;overflow:hidden;box-shadow:0 16px 48px rgba(99,102,241,0.3);">
      <div style="position:absolute;top:-40px;right:-40px;width:200px;height:200px;border-radius:50%;background:rgba(255,255,255,0.05);"></div>
      <div style="position:absolute;bottom:-30px;left:200px;width:150px;height:150px;border-radius:50%;background:rgba(255,255,255,0.04);"></div>
      <div style="position:relative;z-index:1;max-width:600px;">
        <div style="font-size:12px;font-weight:700;color:rgba(255,255,255,0.7);text-transform:uppercase;letter-spacing:2px;margin-bottom:14px;">💼 AI-Powered Career Intelligence</div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:38px;font-weight:900;color:#fff;line-height:1.15;margin-bottom:16px;">
          Welcome to<br><em style="font-style:normal;opacity:0.9;">Salary Prediction App</em>
        </div>
        <div style="font-size:15px;color:rgba(255,255,255,0.75);line-height:1.7;margin-bottom:24px;">
          Predict your market salary using Machine Learning based on your experience,<br>education, certifications, skills, and industry — instantly.
        </div>
        <div style="display:flex;gap:12px;flex-wrap:wrap;">
          <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.3);color:#fff!important;padding:8px 18px;border-radius:99px;font-size:13px;font-weight:600;">✅ 95% Accuracy</span>
          <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.3);color:#fff!important;padding:8px 18px;border-radius:99px;font-size:13px;font-weight:600;">⚡ Instant Results</span>
          <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.3);color:#fff!important;padding:8px 18px;border-radius:99px;font-size:13px;font-weight:600;">📱 WhatsApp Insights</span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat-strip">
      <div class="stat-strip-item"><div class="stat-strip-val">50K+</div><div class="stat-strip-lbl">Predictions Made</div></div>
      <div class="stat-strip-item"><div class="stat-strip-val">95%</div><div class="stat-strip-lbl">Model Accuracy</div></div>
      <div class="stat-strip-item"><div class="stat-strip-val">120+</div><div class="stat-strip-lbl">Job Roles</div></div>
      <div class="stat-strip-item"><div class="stat-strip-val">10K+</div><div class="stat-strip-lbl">Active Users</div></div>
    </div>""", unsafe_allow_html=True)

    f1,f2,f3,f4 = st.columns(4)
    cards = [("🎯","Accurate","KNN model trained on 250K+ real salary records across industries."),
             ("⚡","Instant","Get your salary prediction in under 1 second — no waiting."),
             ("📊","Full Analytics","Dashboard, roadmap, benchmarks and industry trend reports."),
             ("📱","WhatsApp Send","Export your full career insights report directly to WhatsApp.")]
    for col,(icon,title,desc) in zip([f1,f2,f3,f4],cards):
        with col:
            st.markdown(f'<div class="feature-card"><div class="feature-icon">{icon}</div><div class="feature-title">{title}</div><div class="feature-desc">{desc}</div></div>', unsafe_allow_html=True)

    st.markdown(f'<br><div class="section-heading">🔄 How It Works</div>', unsafe_allow_html=True)
    h1,h2,h3,h4 = st.columns(4)
    steps = [("1️⃣","Fill Profile","Enter your experience, skills, education, and job details"),
             ("2️⃣","Run Prediction","Our KNN model instantly calculates your market salary"),
             ("3️⃣","Get Insights","See career roadmap, benchmarks, and growth tips"),
             ("4️⃣","Share via WhatsApp","Send your full report to yourself on WhatsApp")]
    for col,(num,title,desc) in zip([h1,h2,h3,h4],steps):
        with col:
            st.markdown(f'<div class="card" style="text-align:center;padding:20px;"><div style="font-size:28px;margin-bottom:10px;">{num}</div><div style="font-size:14px;font-weight:700;color:{TEXT1};margin-bottom:6px;">{title}</div><div style="font-size:12px;color:{TEXT2};line-height:1.5;">{desc}</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# PREDICT PAGE
# =========================
def show_predict(model, scaler, columns):
    jo = ["Other"]+get_options(columns,"job_title_")
    eo = ["Other"]+get_options(columns,"education_level_")
    lo = ["Other"]+get_options(columns,"location_")
    io = ["Other"]+get_options(columns,"industry_")
    co = ["Other"]+get_options(columns,"company_size_")
    ro = ["Other"]+get_options(columns,"remote_work_")

    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="page-title">🔍 Salary Prediction</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">Fill in your details — our KNN model trained on 250,000+ records will estimate your market salary instantly.</div>', unsafe_allow_html=True)

    col1,col2 = st.columns(2,gap="large")
    with col1:
        st.markdown(f'<div class="card"><div class="card-title">📊 Experience & Skills</div>', unsafe_allow_html=True)
        exp    = st.number_input("Years of Experience",0,30,key="exp")
        skills = st.number_input("Number of Skills",  0,50, key="skills")
        cert   = st.number_input("Certifications",    0,20, key="cert")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card"><div class="card-title">🎓 Education & Role</div>', unsafe_allow_html=True)
        job = st.selectbox("Job Role",        jo, key="job")
        edu = st.selectbox("Education Level", eo, key="edu")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="card"><div class="card-title">🏢 Company & Location</div>', unsafe_allow_html=True)
        loc     = st.selectbox("Location",     lo, key="loc")
        ind     = st.selectbox("Industry",     io, key="ind")
        company = st.selectbox("Company Size", co, key="company")
        remote  = st.selectbox("Remote Work",  ro, key="remote")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card" style="background:{ACCENT_SOFT};border-color:{ACCENT_BORDER};">
          <div class="card-title">✨ What You'll Get</div>
          <div style="font-size:13px;color:{TEXT2};line-height:2;">
            💰 <strong style="color:{TEXT1};">Predicted annual salary</strong><br>
            💡 <strong style="color:{TEXT1};">Personalised growth tips</strong><br>
            🗺️ <strong style="color:{TEXT1};">Step-by-step career roadmap</strong><br>
            📈 <strong style="color:{TEXT1};">Industry benchmarks & trends</strong><br>
            📱 <strong style="color:{TEXT1};">Send report to WhatsApp</strong>
          </div>
        </div>""", unsafe_allow_html=True)

    if st.button("🔍  Predict My Salary", key="predict_btn"):
        inp = {"experience_years":exp,"skills_count":skills,"certifications":cert,
               "job_title":job,"education_level":edu,"location":loc,
               "industry":ind,"company_size":company,"remote_work":remote}
        df = pd.DataFrame([inp])
        df["exp_squared"]    = df["experience_years"]**2
        df["skill_per_exp"]  = df["skills_count"]/(df["experience_years"]+1)
        df["cert_per_skill"] = df["certifications"]/(df["skills_count"]+1)
        df["seniority"]      = pd.cut(df["experience_years"],bins=[0,2,5,10,20],labels=["Fresher","Junior","Mid","Senior"])
        df = pd.get_dummies(df)
        df = df.reindex(columns=columns,fill_value=0)
        nc = [c for c in ["experience_years","skills_count","certifications","exp_squared","skill_per_exp","cert_per_skill"] if c in df.columns]
        if nc: df[nc] = scaler.transform(df[nc])
        salary = int(model.predict(df)[0])
        st.session_state.last_prediction = salary
        st.session_state.last_inputs     = inp

        sf  = f"₹{salary:,}"
        mon = f"₹{salary//12:,}"
        st.markdown(f"""
        <div class="result-hero">
          <div class="result-hero-label">Your Estimated Annual Salary</div>
          <div class="result-hero-amount">{sf}</div>
          <div class="result-hero-sub">≈ {mon} / month &nbsp;·&nbsp; Powered by K-Nearest Neighbors AI</div>
        </div>""", unsafe_allow_html=True)

        sen = "Fresher" if exp<=2 else ("Junior" if exp<=5 else ("Mid-Level" if exp<=10 else "Senior"))
        pot = f"₹{int(salary*1.35):,}"; pct = min(95,max(30,int(30+(salary/220000)*65)))
        m1,m2,m3,m4 = st.columns(4)
        with m1: st.markdown(f'<div class="metric-card"><div class="metric-label">Seniority</div><div class="metric-value" style="font-size:16px;">{sen}</div></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="metric-card"><div class="metric-label">Monthly</div><div class="metric-value" style="font-size:16px;">{mon}</div></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="metric-card"><div class="metric-label">Growth Potential</div><div class="metric-value" style="font-size:16px;">{pot}</div><div class="metric-sub">↑ 2–3 years</div></div>', unsafe_allow_html=True)
        with m4: st.markdown(f'<div class="metric-card"><div class="metric-label">Percentile</div><div class="metric-value" style="font-size:16px;">{pct}th</div></div>', unsafe_allow_html=True)

        st.markdown(f'<div style="background:{SUCCESS_BG};border:1px solid {SUCCESS_B};border-radius:12px;padding:14px 18px;margin-top:12px;"><span style="font-size:14px;color:#10b981;font-weight:700;">✅ Prediction saved!</span><span style="font-size:13px;color:{TEXT2};"> Go to 💡 Insights to get tips and send to WhatsApp.</span></div>', unsafe_allow_html=True)
        st.balloons()

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# INSIGHTS PAGE
# =========================
def show_insights():
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="page-title">💡 Career Insights</div>', unsafe_allow_html=True)
    if not st.session_state.last_prediction:
        st.markdown(f'<div style="text-align:center;padding:70px 20px;"><div style="font-size:56px;margin-bottom:16px;">💡</div><div style="font-size:20px;font-weight:800;color:{TEXT1};margin-bottom:8px;">Run a prediction first</div><div style="font-size:14px;color:{TEXT2};">Go to 🔍 Predict tab to get started.</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True); return

    inp=st.session_state.last_inputs; salary=st.session_state.last_prediction
    job=inp["job_title"]; exp=inp["experience_years"]; sc=inp["skills_count"]
    cert=inp["certifications"]; edu=inp["education_level"]; ind=inp["industry"]
    icon_map={"blue":"insight-icon-blue","green":"insight-icon-green","amber":"insight-icon-amber","rose":"insight-icon-rose"}

    st.markdown(f'<div class="card"><div class="card-title">🚀 How to Boost Your Salary</div>', unsafe_allow_html=True)
    for icon,title,desc,color in salary_boost_tips(job,exp,sc,cert,edu):
        st.markdown(f'<div class="insight-card"><div class="insight-icon {icon_map[color]}">{icon}</div><div><div class="insight-title">{title}</div><div class="insight-desc">{desc}</div></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    ca,cb = st.columns(2,gap="large")
    with ca:
        top_skills = SKILLS_BY_ROLE.get(job,SKILLS_BY_ROLE["Other"])[:6]
        boosts     = ["+₹8K–15K","+₹10K–20K","+₹6K–12K","+₹12K–25K","+₹5K–10K","+₹15K–30K"]
        st.markdown(f'<div class="card"><div class="card-title">🛠️ Top Skills to Learn</div>', unsafe_allow_html=True)
        for i,(sk,b) in enumerate(zip(top_skills,boosts)):
            pct=90-i*10
            st.markdown(f'<div class="compare-bar-wrap"><div class="compare-bar-label"><span style="font-size:13px;font-weight:500;color:{TEXT1};">{sk}</span><span class="trend-up">{b}/yr</span></div><div class="compare-bar-track"><div class="compare-bar-fill" style="width:{pct}%;background:linear-gradient(90deg,{ACCENT},{ACCENT2});"></div></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with cb:
        trend = INDUSTRY_TRENDS.get(ind,INDUSTRY_TRENDS["Other"])
        st.markdown(f'<div class="card"><div class="card-title">📈 Industry Trends — {ind}</div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px;"><div class="metric-card"><div class="metric-label">Growth</div><div class="metric-value">{trend["growth"]}</div><div class="metric-sub">↑ YoY</div></div><div class="metric-card"><div class="metric-label">Demand</div><div class="metric-value" style="font-size:15px;">{trend["demand"]}</div></div><div class="metric-card"><div class="metric-label">Top Pay</div><div class="metric-value" style="font-size:15px;">{trend["top_pay"]}</div></div><div class="metric-card"><div class="metric-label">Outlook</div><div class="metric-value" style="font-size:15px;">{trend["outlook"]}</div></div></div><div style="background:{ACCENT_SOFT};border-radius:12px;padding:12px 14px;border:1px solid {ACCENT_BORDER};"><div style="font-size:12px;color:{ACCENT};font-weight:700;margin-bottom:4px;">💡 Key Insight</div><div style="font-size:12px;color:{TEXT2};line-height:1.6;">Growing <strong style="color:{TEXT1};">{trend["growth"]}</strong>/yr. Top talent earns <strong style="color:{TEXT1};">{trend["top_pay"]}</strong>. Strong time to upskill and negotiate.</div></div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="card"><div class="card-title">⚡ What-If Salary Simulator</div><p style="font-size:13px;color:{TEXT2};margin-bottom:16px;">Drag sliders to see the salary impact of each improvement.</p>', unsafe_allow_html=True)
    s1,s2,s3 = st.columns(3)
    with s1:
        xe=st.slider("+Experience yrs",0,10,2,key="sim_exp"); se=int(salary*(1+xe*0.055))
        st.markdown(f'<div class="metric-card"><div class="metric-label">+{xe} yrs exp</div><div class="metric-value">₹{se:,}</div><div class="metric-sub trend-up">+₹{se-salary:,}</div></div>', unsafe_allow_html=True)
    with s2:
        xs=st.slider("+Skills",0,10,3,key="sim_skills"); ss=int(salary*(1+xs*0.028))
        st.markdown(f'<div class="metric-card"><div class="metric-label">+{xs} skills</div><div class="metric-value">₹{ss:,}</div><div class="metric-sub trend-up">+₹{ss-salary:,}</div></div>', unsafe_allow_html=True)
    with s3:
        xc=st.slider("+Certifications",0,5,1,key="sim_cert"); sc_=int(salary*(1+xc*0.04))
        st.markdown(f'<div class="metric-card"><div class="metric-label">+{xc} certs</div><div class="metric-value">₹{sc_:,}</div><div class="metric-sub trend-up">+₹{sc_-salary:,}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="wa-card">
      <div class="wa-title">📱 Send Insights to WhatsApp</div>
      <div class="wa-desc">
        Get your complete career insights report — salary prediction, growth tips, skill roadmap, and industry trends — delivered directly to your WhatsApp. Enter your number below and click the button.
      </div>
    </div>""", unsafe_allow_html=True)

    wa_col1, wa_col2 = st.columns([2,1], gap="medium")
    with wa_col1:
        wa_number = st.text_input(
            "📞 WhatsApp Number (with country code)",
            placeholder="e.g. 919876543210  (91 for India)",
            key="wa_number",
            help="Enter your number with country code, no + or spaces. Example: 919876543210"
        )
    with wa_col2:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("📤 Generate WhatsApp Link", key="wa_btn"):
            if not wa_number or not wa_number.strip().isdigit():
                st.error("Please enter a valid number (digits only, with country code).")
            else:
                msg     = build_whatsapp_message(inp, salary)
                encoded = urllib.parse.quote(msg)
                wa_url  = f"https://wa.me/{wa_number.strip()}?text={encoded}"
                st.session_state["wa_link"]  = wa_url
                st.session_state["wa_ready"] = True

    if st.session_state.get("wa_ready"):
        wa_url = st.session_state.get("wa_link","")
        st.markdown(f"""
        <div style="background:{SUCCESS_BG};border:1px solid {SUCCESS_B};border-radius:14px;padding:18px 20px;margin-top:12px;">
          <div style="font-size:14px;font-weight:700;color:#10b981;margin-bottom:8px;">✅ WhatsApp link ready!</div>
          <div style="font-size:13px;color:{TEXT2};margin-bottom:14px;line-height:1.6;">
            Click the button below to open WhatsApp with your pre-filled career insights report.
            It will open WhatsApp Web or the app on your device.
          </div>
          <div class="wa-btn"><a href="{wa_url}" target="_blank">📱 Open WhatsApp & Send Report</a></div>
          <div style="margin-top:12px;font-size:11px;color:{TEXT3};">ℹ️ Opens WhatsApp with your full report pre-filled. Just press Send!</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# ROADMAP PAGE
# =========================
def show_roadmap():
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="page-title">🗺️ Career Roadmap</div>', unsafe_allow_html=True)
    if not st.session_state.last_inputs:
        st.markdown(f'<div style="text-align:center;padding:70px;"><div style="font-size:56px;margin-bottom:16px;">🗺️</div><div style="font-size:20px;font-weight:800;color:{TEXT1};margin-bottom:8px;">Run a prediction first</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True); return

    inp=st.session_state.last_inputs; job=inp["job_title"]; exp=inp["experience_years"]
    steps=ROADMAP_BY_ROLE.get(job,ROADMAP_BY_ROLE["Other"])
    cs=0 if exp<=2 else (1 if exp<=5 else (2 if exp<=10 else (3 if exp<=15 else 4)))
    sr=["₹40K–70K","₹70K–1.1L","₹1.1L–1.6L","₹1.6L–2.0L","₹2.0L+"]; er=["0–2 yrs","2–5 yrs","5–10 yrs","10–15 yrs","15+ yrs"]

    cr,ci = st.columns([3,2],gap="large")
    with cr:
        st.markdown(f'<div class="card"><div class="card-title">🗺️ Career Path — {job}</div>', unsafe_allow_html=True)
        for i,step in enumerate(steps):
            if i<cs:    dot,badge,btxt="step-dot-done","badge-done","✓ Completed"
            elif i==cs: dot,badge,btxt="step-dot-curr","badge-current","📍 You are here"
            else:       dot,badge,btxt="step-dot-next","badge-future",f"Next · {er[i]}"
            st.markdown(f'<div class="roadmap-step"><div class="step-dot {dot}">{i+1}</div><div><div class="step-title">{step}</div><div class="step-sub">{er[i]} &nbsp;·&nbsp; {sr[i]}</div><span class="step-badge {badge}">{btxt}</span></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with ci:
        curr=steps[cs]; nxt=steps[min(cs+1,len(steps)-1)]; sk=SKILLS_BY_ROLE.get(job,SKILLS_BY_ROLE["Other"])[:4]
        st.markdown(f'<div class="card" style="background:{ACCENT_SOFT};border-color:{ACCENT_BORDER};margin-bottom:12px;"><div class="card-title">🎯 Your Next Goal</div><div style="font-size:18px;font-weight:800;color:{TEXT1};margin-bottom:8px;font-family:\'Plus Jakarta Sans\',sans-serif;">{nxt}</div><div style="font-size:13px;color:{TEXT2};line-height:1.6;">Currently at <strong style="color:{TEXT1};">{curr}</strong>. Build 1–2 impactful projects, master the skills below, and apply for senior roles.</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card"><div class="card-title">🛠️ Skills for Next Level</div>', unsafe_allow_html=True)
        for s in sk: st.markdown(f'<span class="pill">{s}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card"><div class="card-title">📅 Estimated Timeline</div><div style="font-size:13px;color:{TEXT2};line-height:2.4;">🟣 <strong style="color:{TEXT1};">Now:</strong> {steps[cs]}<br>🟢 <strong style="color:{TEXT1};">1–2 yrs:</strong> {steps[min(cs+1,len(steps)-1)]}<br>🔵 <strong style="color:{TEXT1};">3–5 yrs:</strong> {steps[min(cs+2,len(steps)-1)]}<br>⭐ <strong style="color:{TEXT1};">5+ yrs:</strong> {steps[-1]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# DASHBOARD PAGE
# =========================
def show_dashboard():
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="page-title">📊 Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">Platform statistics and salary growth trends.</div>', unsafe_allow_html=True)
    m1,m2,m3,m4 = st.columns(4)
    with m1: st.markdown(f'<div class="metric-card"><div class="metric-label">Total Users</div><div class="metric-value">10K+</div><div class="metric-sub">↑ Growing daily</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card"><div class="metric-label">Predictions Made</div><div class="metric-value">50K+</div><div class="metric-sub">↑ This month</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card"><div class="metric-label">Model Accuracy</div><div class="metric-value">95%</div><div class="metric-sub">↑ KNN Model</div></div>', unsafe_allow_html=True)
    with m4: st.markdown(f'<div class="metric-card"><div class="metric-label">Job Roles Covered</div><div class="metric-value">120+</div><div class="metric-sub">↑ Updated 2026</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    cd = pd.DataFrame({"Experience":[0,1,2,3,4,5,6,7,8,9,10],"Salary":[20000,26000,34000,44000,58000,72000,92000,115000,138000,158000,175000]})
    c1,c2 = st.columns(2,gap="large")
    with c1:
        st.subheader("📈 Salary Growth by Experience")
        st.line_chart(cd,x="Experience",y="Salary",height=280)
    with c2:
        st.subheader("🌊 Cumulative Salary Trend")
        st.area_chart(cd.set_index("Experience"),height=280)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# COMPARE PAGE
# =========================
def show_compare():
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="page-title">⚖️ Compare Yourself</div>', unsafe_allow_html=True)
    if not st.session_state.last_prediction:
        st.markdown(f'<div style="text-align:center;padding:70px;"><div style="font-size:56px;margin-bottom:16px;">⚖️</div><div style="font-size:20px;font-weight:800;color:{TEXT1};margin-bottom:8px;">Run a prediction first</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True); return

    salary=st.session_state.last_prediction; inp=st.session_state.last_inputs; job=inp["job_title"]
    base=max(40000,salary-random.randint(10000,20000))
    top25=int(salary*1.22); top10=int(salary*1.48); top5=int(salary*1.75); mx=top5
    bm=[("Entry Level (0–2 yrs)",int(base*0.6),"#94a3b8"),("Mid Level (3–6 yrs)",int(base*0.85),"#0ea5e9"),
        ("📍 Your Salary",salary,ACCENT),("Top 25%",top25,ACCENT2),("Top 10%",top10,"#7c3aed"),("Top 5% — Elite",top5,"#9333ea")]
    c1,c2 = st.columns([3,2],gap="large")
    with c1:
        st.markdown(f'<div class="card"><div class="card-title">📊 Market Benchmarks — {job}</div>', unsafe_allow_html=True)
        for label,val,color in bm:
            pct=int((val/mx)*100); iy="Your Salary" in label
            yb=f"background:{ACCENT_SOFT};border-radius:10px;padding:10px 12px;border:1px solid {ACCENT_BORDER};" if iy else ""
            st.markdown(f'<div class="compare-bar-wrap" style="{yb}"><div class="compare-bar-label"><span style="font-size:13px;font-weight:{"700" if iy else "500"};color:{ACCENT if iy else TEXT1};">{label}</span><span style="font-size:13px;font-weight:700;color:{ACCENT if iy else TEXT1};">₹{val:,}</span></div><div class="compare-bar-track"><div class="compare-bar-fill" style="width:{pct}%;background:{color};"></div></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
     pr = min(95, max(25, int(30 + (salary / top5) * 65)))
     gap = max(0, top10 - salary)

     upskill_msg = "" if pr >= 90 else " Upskill to break into the top 10%!"
     st.markdown(
        f'<div class="card" style="text-align:center;margin-bottom:14px;">'
        f'<div class="card-title">🎯 Your Market Position</div>'
        f'<div style="font-size:52px;font-weight:900;background:linear-gradient(135deg,{ACCENT},{ACCENT2});'
        f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;'
        f'font-family:\'Plus Jakarta Sans\',sans-serif;">{pr}th</div>'
        f'<div style="font-size:13px;color:{TEXT2};margin-top:4px;">percentile in your field</div>'
        f'<div style="font-size:13px;color:{TEXT2};margin-top:12px;line-height:1.6;">'
        f'You earn more than <strong style="color:{TEXT1};">{pr}%</strong> of similar professionals.{upskill_msg}'
        f'</div></div>',
        unsafe_allow_html=True
    )

     gap_value = "Already there! 🎉" if gap == 0 else f"₹{gap:,}"
     gap_msg = "You've cracked the top 10% — exceptional!" if gap == 0 else "Add 2–3 high-demand skills and apply for senior roles to close this gap in 1–2 years."
     st.markdown(
        f'<div class="card"><div class="card-title">💰 Gap to Top 10%</div>'
        f'<div style="font-size:22px;font-weight:800;color:{ACCENT};font-family:\'Plus Jakarta Sans\',sans-serif;">{gap_value}</div>'
        f'<div style="font-size:13px;color:{TEXT2};margin-top:8px;line-height:1.6;">{gap_msg}</div></div>',
        unsafe_allow_html=True
    )
st.markdown('</div>', unsafe_allow_html=True)

# =========================
# LEADERBOARD PAGE
# =========================
def show_leaderboard():
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="page-title">🏆 Leaderboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">Top predicted salaries across all SalaryIQ users.</div>', unsafe_allow_html=True)
    if st.session_state.last_prediction:
        s=st.session_state.last_prediction
        j=st.session_state.last_inputs.get("job_title","Professional") if st.session_state.last_inputs else "Professional"
        e=st.session_state.last_inputs.get("experience_years",0) if st.session_state.last_inputs else 0
        st.markdown(f'<div style="background:{ACCENT_SOFT};border:1.5px solid {ACCENT_BORDER};border-radius:16px;padding:18px 22px;margin-bottom:22px;display:flex;align-items:center;justify-content:space-between;"><div><div style="font-size:10px;color:{ACCENT};font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Your Best Prediction</div><div style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:20px;font-weight:800;color:{TEXT1};">{st.session_state.username} <span style="font-size:13px;color:{TEXT2};font-weight:400;">· {j} · {e} yrs</span></div></div><div style="text-align:right;"><div style="font-size:10px;color:{ACCENT};font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Predicted</div><div style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:22px;font-weight:900;color:{ACCENT};">₹{s:,}</div></div></div>', unsafe_allow_html=True)
    lb=[{"name":"Rahul S.","job":"AI Engineer","exp":8,"salary":195000},
        {"name":"Priya M.","job":"Data Scientist","exp":6,"salary":175000},
        {"name":"Arjun K.","job":"Cloud Engineer","exp":10,"salary":168000},
        {"name":"Sneha R.","job":"Software Engineer","exp":7,"salary":155000},
        {"name":"Vikram T.","job":"DevOps Engineer","exp":9,"salary":148000},
        {"name":"Meera J.","job":"Product Manager","exp":8,"salary":142000},
        {"name":"Kiran P.","job":"ML Engineer","exp":5,"salary":135000}]
    medals=["🥇","🥈","🥉"]; rcls=["gold","silver","bronze"]
    st.markdown(f'<div class="card"><div class="card-title">🏆 Top Earners — This Month</div>', unsafe_allow_html=True)
    for i,e in enumerate(lb):
        m=medals[i] if i<3 else f"#{i+1}"; c=rcls[i] if i<3 else ""
        st.markdown(f'<div class="lb-row {c}"><div class="lb-rank">{m}</div><div style="flex:1;"><div class="lb-name">{e["name"]}</div><div class="lb-role">{e["job"]} &nbsp;·&nbsp; {e["exp"]} yrs exp</div></div><div class="lb-salary">₹{e["salary"]:,}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# ENTRY POINT
# =========================

# CASE 1: Public Home Page
if not st.session_state.logged_in and st.session_state.show_public_home:

    st.sidebar.markdown(f'<div style="padding:20px 14px 8px;"><div style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:18px;font-weight:900;color:{TEXT1};margin-bottom:4px;">💼 SalaryIQ</div><div style="font-size:12px;color:{TEXT2};">AI-Powered Career Intelligence</div></div>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<div style="height:1px;background:{DIVIDER};margin:8px 0 12px;"></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="theme-sb" style="padding:0 14px 8px;">', unsafe_allow_html=True)
    if st.sidebar.button(TOGGLE_LBL, key="pub_theme"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<div style="height:1px;background:{DIVIDER};margin:8px 0 12px;"></div>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<div style="padding:0 14px;font-size:12px;color:{TEXT2};line-height:1.8;">✅ 95% Accuracy<br>⚡ Instant Results<br>📱 WhatsApp Reports<br>🗺️ Career Roadmaps<br>📊 Industry Benchmarks</div>', unsafe_allow_html=True)

    st.markdown(f'<div style="background:{HERO_BG};padding:18px 28px;border-radius:16px;text-align:center;font-family:\'Plus Jakarta Sans\',sans-serif;font-size:26px;font-weight:900;color:#fff;margin-top:16px;margin-bottom:24px;box-shadow:0 8px 32px rgba(99,102,241,0.3);">💼 SalaryIQ — Know Your Worth</div>', unsafe_allow_html=True)

    show_home()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{CARD_BG};border:1px solid {CARD_BORDER};border-radius:20px;padding:32px;text-align:center;margin-bottom:24px;box-shadow:{GLOW};">
      <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:22px;font-weight:900;color:{TEXT1};margin-bottom:8px;">Ready to know your true salary? 🚀</div>
      <div style="font-size:14px;color:{TEXT2};margin-bottom:24px;">Create a free account or log in to get your personalised salary prediction instantly.</div>
    </div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        st.markdown('<div class="login-cta">', unsafe_allow_html=True)
        if st.button("🔐 Login / Sign Up", key="goto_login_btn"):
            st.session_state.show_public_home = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# CASE 2: Auth Page
elif not st.session_state.logged_in and not st.session_state.show_public_home:

    st.sidebar.markdown('<div class="theme-sb" style="padding:16px 14px 8px;">', unsafe_allow_html=True)
    if st.sidebar.button(TOGGLE_LBL, key="auth_theme"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<div style="height:1px;background:{DIVIDER};margin:8px 14px;"></div>', unsafe_allow_html=True)

    st.sidebar.markdown('<div style="padding:4px 14px 8px;">', unsafe_allow_html=True)
    if st.sidebar.button("← Back to Home", key="back_home_btn"):
        st.session_state.show_public_home = True
        st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div style="background:{HERO_BG};padding:18px 28px;border-radius:16px;text-align:center;font-family:\'Plus Jakarta Sans\',sans-serif;font-size:26px;font-weight:900;color:#fff;margin-top:16px;margin-bottom:24px;box-shadow:0 8px 32px rgba(99,102,241,0.3);">💼 SalaryIQ — Know Your Worth</div>', unsafe_allow_html=True)

    menu = st.sidebar.radio("", ["🔐 Login", "📝 Sign Up"], label_visibility="collapsed")
    if "Login" in menu:
        show_login()
    else:
        show_signup()

# CASE 3: Logged In — Full Dashboard (no Home tab)
else:
    try:
        model, scaler, columns = load_model()
        model_loaded = True
    except:
        model_loaded = False

    if "wa_ready" not in st.session_state:
        st.session_state["wa_ready"] = False

    show_sidebar()
    show_topbar()
    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

    tab = st.session_state.active_tab

    # Guard: if somehow active_tab is still "home" from an old session, redirect to predict
    if tab == "home":
        st.session_state.active_tab = "predict"
        tab = "predict"
        st.rerun()

    if   tab == "predict":
        if model_loaded: show_predict(model, scaler, columns)
        else: st.error("⚠️ Model files not found. Please add knn_model.pkl, scaler.pkl, columns.pkl.")
    elif tab == "insights":    show_insights()
    elif tab == "roadmap":     show_roadmap()
    elif tab == "dashboard":   show_dashboard()
    elif tab == "compare":     show_compare()
    elif tab == "leaderboard": show_leaderboard()

# FOOTER
st.markdown(f'<div class="footer">💼 SalaryIQ Pro &nbsp;·&nbsp; Made with ❤️ using Streamlit &nbsp;·&nbsp; AI-Powered Career Intelligence</div>', unsafe_allow_html=True)
