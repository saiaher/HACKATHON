"""
GovLENS AI Fraud Detection System - Smart India Hackathon 2026
Dataset -> SQLite -> Streamlit -> Explainable Fraud Detection -> Alerts/Investigation

Run:
    pip install -r requirements.txt
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime

import database as db
import fraud_engine as fe
import visualizations as viz

st.set_page_config(page_title="GovLENS - MPLAD Fraud Detection", page_icon="🛡️", layout="wide",
                    initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root{
  --bg:#EEF2FA; --surface:#FFFFFF; --border:#E1E7F3; --border-soft:#EBEFF8;
  --ink:#0F172A; --ink-soft:#5B6472; --ink-mute:#98A1B3;
  --brand:#4338CA; --brand2:#6D5EF5; --accent:#0FB5AE;
  --danger:#E11D48; --danger-bg:#FDE7EC;
  --warn:#D97706; --warn-bg:#FEF2DC;
  --ok:#059669; --ok-bg:#E1F7EE;
  --r-sm:10px; --r-md:14px; --r-lg:18px;
  --shadow: 0 1px 2px rgba(15,23,42,.04), 0 4px 14px rgba(15,23,42,.05);
}

html, body, [class*="css"] { font-family:'Inter',sans-serif; color:var(--ink); font-size:14px; }
.stApp{ background:
    radial-gradient(1100px 480px at 8% -8%, #E4E9FC 0%, rgba(228,233,252,0) 60%),
    radial-gradient(900px 420px at 100% 0%, #DFF6F3 0%, rgba(223,246,243,0) 55%),
    var(--bg); }

/* kill default streamlit whitespace */
div.block-container{ padding-top:.6rem !important; padding-bottom:1.2rem !important; max-width:1320px; }
div[data-testid="stVerticalBlock"]{ gap:.55rem !important; }
div[data-testid="stHorizontalBlock"]{ gap:.7rem !important; }
div[data-testid="stVerticalBlockBorderWrapper"]{ gap:0 !important; }
.element-container{ margin-bottom:0 !important; }
div[data-testid="stMarkdownContainer"] > p{ margin-bottom:.3rem; }
header[data-testid="stHeader"]{ background:transparent; height:0; }
div[data-testid="stAppViewBlockContainer"]{ padding-top:.6rem; }
hr{ margin:.6rem 0 !important; border-color:var(--border) !important; }

h1,h2,h3{ color:var(--ink); font-weight:800; letter-spacing:-.01em; }
h3{ margin:.2rem 0 .4rem 0 !important; font-size:15.5px !important; text-transform:uppercase; letter-spacing:.03em; color:var(--ink-soft); }
.stCaption, [data-testid="stCaptionContainer"]{ margin-top:-4px; }

/* ---------- Sidebar: dark, dense ---------- */
section[data-testid="stSidebar"]{ background:#0B1120; border-right:none; width:242px !important; }
section[data-testid="stSidebar"] > div{ padding-top:.8rem; }
section[data-testid="stSidebar"] *{ color:#CBD3E6 !important; }
section[data-testid="stSidebar"] .stSelectbox label{ color:#6B7590 !important; font-size:10.5px !important; font-weight:700 !important; text-transform:uppercase; letter-spacing:.06em; }
section[data-testid="stSidebar"] div[data-baseweb="select"] > div, section[data-testid="stSidebar"] div[role="combobox"]{ background:#161D30 !important; background-color:#161D30 !important; border-color:#232B42 !important; border-radius:10px !important; }
section[data-testid="stSidebar"] div[data-baseweb="select"] span, section[data-testid="stSidebar"] div[data-baseweb="select"] div{ color:#FFFFFF !important; }

.brand{ display:flex; align-items:center; gap:9px; padding:2px 6px 16px; }
.brand .mark{ width:34px; height:34px; border-radius:10px; background:linear-gradient(135deg,var(--brand2),var(--accent)); display:flex; align-items:center; justify-content:center; font-size:17px; }
.brand .txt .name{ font-weight:800; font-size:15.5px; color:#FFFFFF !important; line-height:1.1; }
.brand .txt .tag{ font-size:10px; color:#6B7590 !important; font-weight:700; letter-spacing:.05em; }

section[data-testid="stSidebar"] div[role="radiogroup"]{ display:flex; flex-direction:column; gap:2px; }
section[data-testid="stSidebar"] div[role="radiogroup"] label{
    width:100%; display:flex; flex-direction:row; align-items:center; gap:10px;
    padding:9px 12px; border-radius:10px; margin:0; cursor:pointer; transition:.12s ease; }
section[data-testid="stSidebar"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p{
    white-space:pre-line; font-size:13.5px; font-weight:600; margin:0; }
section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child{ display:none; }
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover{ background:#151C30; }
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked){
    background:linear-gradient(90deg,rgba(109,94,245,.22),rgba(109,94,245,.02)); box-shadow:inset 2px 0 0 var(--brand2); }
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) p{ color:#FFFFFF !important; }
.sb-foot{ margin-top:14px; padding:10px 12px; background:#141B2E; border-radius:10px; font-size:11px; color:#6B7590 !important; line-height:1.5; }

/* ---------- Topbar ---------- */
.topbar{ display:flex; align-items:center; justify-content:space-between; padding:14px 20px;
    background:linear-gradient(90deg,#0B1120 0%,#1B2340 100%); border-radius:var(--r-lg); margin-bottom:12px; }
.topbar .t h1{ color:#fff; font-size:19px; margin:0; }
.topbar .t p{ color:#9AA4C0; font-size:12px; margin:2px 0 0; font-weight:500; }
.live-chip{ display:flex; align-items:center; gap:6px; background:rgba(15,181,174,.14); border:1px solid rgba(15,181,174,.35);
    padding:5px 12px; border-radius:999px; color:#5EEAD4 !important; font-size:11.5px; font-weight:700; }
.live-dot{ width:7px; height:7px; border-radius:50%; background:#2DD4BF; box-shadow:0 0 0 3px rgba(45,212,191,.25); }

/* ---------- Metric cards ---------- */
.mrow{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:6px; }
.mcard{ background:var(--surface); border:1px solid var(--border); border-radius:var(--r-md); padding:14px 16px;
    box-shadow:var(--shadow); display:flex; flex-direction:column; gap:2px; }
.mcard .top{ display:flex; align-items:center; justify-content:space-between; }
.mcard .chip{ width:30px; height:30px; border-radius:9px; display:flex; align-items:center; justify-content:center; font-size:14px; }
.mcard .lbl{ font-size:11px; color:var(--ink-mute); font-weight:700; text-transform:uppercase; letter-spacing:.04em; }
.mcard .val{ font-size:24px; font-weight:900; color:var(--ink); line-height:1.15; }
.mcard .sub{ font-size:11px; font-weight:700; }
.chip-a{ background:#EEF0FF; color:var(--brand2); } .chip-b{ background:#E4FBF9; color:var(--accent); }
.chip-c{ background:var(--danger-bg); color:var(--danger); } .chip-d{ background:var(--warn-bg); color:var(--warn); }

/* ---------- Section card wrapper ---------- */
.panel{ background:var(--surface); border:1px solid var(--border); border-radius:var(--r-lg); padding:14px 16px; box-shadow:var(--shadow); }

/* ---------- Expanders ---------- */
div[data-testid="stExpander"]{ border-radius:var(--r-md) !important; border:1px solid var(--border) !important;
    box-shadow:var(--shadow); overflow:hidden; background:var(--surface); }
div[data-testid="stExpander"] summary{ font-weight:650; font-size:13.5px; padding:2px 0; }
div[data-testid="stExpander"] summary:hover{ color:var(--brand); }

/* ---------- Buttons ---------- */
.stButton > button{ border-radius:9px; font-weight:700; font-size:13px; border:none; padding:8px 16px;
    background:linear-gradient(135deg,var(--brand2),var(--brand)); color:#fff; box-shadow:0 2px 6px rgba(67,56,202,.3); }
.stButton > button:hover{ filter:brightness(1.08); color:#fff; }
.stDownloadButton > button{ border-radius:9px; font-weight:700; font-size:13px; border:1px solid var(--border); background:#fff; color:var(--brand); }

/* ---------- Inputs ---------- */
.stTextInput input, .stTextArea textarea{ background:#fff !important; border-radius:9px !important; border:1.5px solid var(--border) !important; font-size:13.5px !important; min-height:40px !important; color:var(--ink) !important; }
div[data-testid="stSelectbox"] > div, div[data-testid="stSelectbox"] > div > div,
div[data-testid="stSelectbox"] div[data-baseweb="select"], div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
div[data-testid="stSelectbox"] div[role="combobox"], div[data-testid="stSelectbox"] div[aria-haspopup="listbox"]{
    background-color:#FFFFFF !important; background:#FFFFFF !important; }
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
div[data-testid="stSelectbox"] div[role="combobox"]{
    border:1.5px solid var(--border) !important; border-radius:9px !important; min-height:40px !important;
    box-shadow:0 1px 2px rgba(15,23,42,.03) !important; }
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover,
div[data-testid="stSelectbox"] div[role="combobox"]:hover{ border-color:var(--brand2) !important; }
div[data-testid="stSelectbox"] svg{ fill:var(--ink-soft) !important; }
div[data-testid="stSelectbox"] span, div[data-testid="stSelectbox"] div{ color:var(--ink) !important; font-weight:600 !important; }
div[data-baseweb="popover"]{ z-index:9999 !important; }
ul[data-baseweb="menu"]{ background:#fff !important; border:1px solid var(--border) !important; box-shadow:0 8px 24px rgba(15,23,42,.14) !important; border-radius:10px !important; padding:4px !important; }
ul[data-baseweb="menu"] li{ color:var(--ink) !important; font-size:13px !important; font-weight:600 !important; border-radius:7px !important; }
ul[data-baseweb="menu"] li:hover{ background:var(--border-soft) !important; }
ul[data-baseweb="menu"] li[aria-selected="true"]{ background:#EEF0FF !important; color:var(--brand) !important; font-weight:700 !important; }
label{ font-size:12px !important; color:var(--ink) !important; font-weight:700 !important; margin-bottom:4px !important; }

/* ---------- Evidence / na / pill ---------- */
.evidence-box{ background:var(--warn-bg); border-left:3px solid var(--warn); padding:9px 13px; border-radius:9px; margin:5px 0; font-size:13px; }
.data-na{ color:var(--ink-mute); font-style:italic; }
.pill{ display:inline-block; padding:3px 11px; border-radius:999px; font-weight:800; font-size:11px; color:#fff; }

/* ---------- Table ---------- */
.gt{ width:100%; border-collapse:collapse; }
.gt th{ color:var(--ink-mute); font-size:10.5px; text-transform:uppercase; letter-spacing:.05em; text-align:left;
    padding:6px 10px; border-bottom:1px solid var(--border); font-weight:800; }
.gt td{ padding:9px 10px; font-size:13px; border-bottom:1px solid var(--border-soft); color:var(--ink-soft); }
.gt tr:last-child td{ border-bottom:none; } .gt tr:hover td{ background:#F8F9FD; }
.gt td:first-child{ font-weight:700; color:var(--ink); }

/* ---------- Risk bars ---------- */
.rrow{ margin-bottom:12px; } .rrow:last-child{ margin-bottom:0; }
.rrow .top{ display:flex; justify-content:space-between; font-weight:700; font-size:13px; }
.rtrack{ background:#EEF0F5; border-radius:6px; height:7px; margin-top:5px; overflow:hidden; }
.rfill{ height:7px; border-radius:6px; }
</style>
""", unsafe_allow_html=True)

# ================================================================
# DATA LAYER (cached; computed once and reused everywhere)
# ================================================================

db.init_db()

if "data_version" not in st.session_state:
    st.session_state.data_version = 0


@st.cache_data(show_spinner=False)
def load_data(_version):
    raw_df = db.load_projects_df()
    scored_df, breakdowns = fe.compute_all_risks(raw_df)
    return scored_df, breakdowns


def get_data():
    return load_data(st.session_state.data_version)


def refresh_data():
    db.reload_from_dataset()
    st.session_state.data_version += 1
    load_data.clear()


def fmt_lakh(v):
    if v is None:
        return "Data not available"
    if v >= 10000000:
        return f"₹{v/10000000:.2f} Cr"
    return f"₹{v/100000:.2f} L"


def fmt_date(d):
    if pd.isna(d):
        return "Data not available"
    return d.strftime("%d-%b-%Y")


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_drive_image(share_url: str):
    """Server-side fetch + validation of a Google Drive-hosted image.
    Returns raw bytes only if a real image was retrieved, else None.
    (st.image on a raw URL doesn't detect failures — the browser just
    shows a broken icon — so we fetch and verify here instead.)"""
    if not share_url or "/d/" not in share_url:
        return None
    try:
        file_id = share_url.split("/d/")[1].split("/")[0]
    except IndexError:
        return None
    if not file_id:
        return None

    candidates = [
        f"https://drive.google.com/uc?export=view&id={file_id}",
        f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000",
    ]
    for url in candidates:
        try:
            resp = requests.get(url, timeout=6, allow_redirects=True)
            content_type = resp.headers.get("Content-Type", "")
            if resp.status_code == 200 and content_type.startswith("image/"):
                return BytesIO(resp.content)
        except requests.RequestException:
            continue
    return None


def na(v, suffix=""):
    if v is None or v == "" or (isinstance(v, float) and pd.isna(v)):
        return '<span class="data-na">Data not available</span>'
    return f"{v}{suffix}"


# ================================================================
# SESSION STATE
# ================================================================
if "user_role" not in st.session_state:
    st.session_state.user_role = "ministry"
if "user_district" not in st.session_state:
    st.session_state.user_district = None
if "selected_project_id" not in st.session_state:
    st.session_state.selected_project_id = None


# ================================================================
# PROJECT DETAIL / INVESTIGATION VIEW
# ================================================================
def show_project_detail(project_id, df, breakdowns):
    row = df[df["project_id"] == project_id]
    if row.empty:
        st.error("Project not found.")
        return
    p = row.iloc[0]
    b = breakdowns[project_id]

    if st.button("← Back"):
        st.session_state.selected_project_id = None
        st.rerun()

    st.markdown(f"## 🔍 {p['project_id']} — {p['project_type']}")
    st.markdown(f"{b['color']} **{b['risk_level']} RISK — {b['total_score']}/100**")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📋 Project Information")
        st.markdown(f"**Project ID:** {p['project_id']}  \n"
                    f"**State:** {p['state']}  \n"
                    f"**District:** {p['district']}  \n"
                    f"**Project Type:** {p['project_type']}  \n"
                    f"**Contractor:** {p['contractor']}  \n"
                    f"**MP:** {p['mp_name']}  \n"
                    f"**Status:** {p['status']}", unsafe_allow_html=True)

        st.markdown("### 💰 Financial Information")
        st.markdown(f"**Sanctioned Amount:** {fmt_lakh(p['sanctioned_amount'])}  \n"
                    f"**Released Amount:** {fmt_lakh(p['released_amount'])} ({p['released_pct']:.0f}% of sanctioned)  \n"
                    f"**Expenditure:** {fmt_lakh(p['expenditure'])} ({p['expenditure_pct']:.0f}% of released)")

        st.markdown("### 🕒 Timeline")
        st.markdown(f"**Start Date:** {fmt_date(p['start_date'])}  \n"
                    f"**Expected Completion:** {fmt_date(p['completion_date'])}  \n"
                    f"**Estimated Progress (time-based):** {p['est_completion_pct']:.0f}%  \n"
                    f"**Delay:** {p['delay_days']} days" if p['delay_days'] else "**Delay:** None recorded")

        st.markdown("### 📍 Location")
        if p["gps_lat"] is not None:
            st.markdown(f"**Latitude, Longitude:** {p['gps_lat']:.4f}, {p['gps_lon']:.4f}")
            st.map(pd.DataFrame({"lat": [p["gps_lat"]], "lon": [p["gps_lon"]]}), size=20)
        else:
            st.markdown('<span class="data-na">GPS data not available</span>', unsafe_allow_html=True)

        st.markdown("### 🖼️ Field Image Verification")
        st.caption("Dataset provides a single project image field (no separate before/after pair), so before/after comparison is unavailable.")
        img_bytes = fetch_drive_image(p["image_url"]) if p["image_url"] else None
        if img_bytes:
            st.image(img_bytes, caption="Project field image", use_container_width=True)
        else:
            st.info("Image verification unavailable — field image required or inaccessible.")

        st.markdown("### ❓ Why is this project suspicious?")
        reasons = fe.top_reasons(b, n=6)
        if not reasons:
            st.success("No significant anomalies detected for this project.")
        else:
            for label, score, reason in reasons:
                st.markdown(f'<div class="evidence-box"><b>{label}</b> (+{score:.0f} pts): {reason}</div>', unsafe_allow_html=True)

        st.markdown(f"**Recommended Action:** {fe.recommended_action(b)}")

    with col2:
        st.plotly_chart(viz.gauge_chart(b["total_score"]), use_container_width=True, key=f"detail_gauge_{project_id}")
        st.plotly_chart(viz.risk_breakdown_chart(b), use_container_width=True, key=f"detail_bar_{project_id}")

        st.markdown("### 🕵️ Investigation Workflow")
        current = db.get_investigation_status(project_id)
        st.caption(f"Current status: **{current['status']}**" + (f" (updated {current['updated_at']})" if current['updated_at'] else ""))
        new_status = st.selectbox("Update status", db.VALID_STATUSES,
                                   index=db.VALID_STATUSES.index(current["status"]) if current["status"] in db.VALID_STATUSES else 0,
                                   key=f"status_{project_id}")
        notes = st.text_area("Officer notes", value=current["notes"], key=f"notes_{project_id}", height=80)
        if st.button("💾 Save Investigation Status", key=f"save_{project_id}", use_container_width=True):
            db.set_investigation_status(project_id, new_status, notes)
            st.success(f"Status saved: {new_status}")
            st.rerun()

        st.markdown("### 📄 Report")
        report_text = build_report_text(p, b, current)
        st.download_button("⬇️ Download Risk Assessment Report", report_text,
                            file_name=f"{project_id}_risk_report.txt", use_container_width=True,
                            key=f"report_{project_id}")


def build_report_text(p, b, investigation):
    lines = [
        "AI-ASSISTED PROJECT RISK ASSESSMENT REPORT",
        "(Not an official government document)",
        "=" * 55,
        f"Project ID: {p['project_id']}",
        f"Project Type: {p['project_type']}",
        f"State / District: {p['state']} / {p['district']}",
        f"Contractor: {p['contractor']}",
        f"MP: {p['mp_name']}",
        f"Status: {p['status']}",
        "",
        "FINANCIAL",
        f"Sanctioned: {fmt_lakh(p['sanctioned_amount'])}",
        f"Released: {fmt_lakh(p['released_amount'])} ({p['released_pct']:.0f}%)",
        f"Expenditure: {fmt_lakh(p['expenditure'])} ({p['expenditure_pct']:.0f}% of released)",
        "",
        "TIMELINE",
        f"Start: {fmt_date(p['start_date'])}   Expected Completion: {fmt_date(p['completion_date'])}",
        f"Estimated Progress (time-based): {p['est_completion_pct']:.0f}%   Delay: {p['delay_days']} days",
        "",
        f"RISK SCORE: {b['total_score']}/100  ({b['risk_level']})",
        f"  Rule-based score: {b['rule_score']}   ML anomaly contribution: {b['ml_contribution']}",
        "",
        "DETECTED ISSUES / EVIDENCE",
    ]
    for label, score, reason in fe.top_reasons(b, n=6):
        lines.append(f"  - {label} (+{score:.0f} pts): {reason}")
    lines += [
        "",
        f"Recommended Action: {fe.recommended_action(b)}",
        "",
        f"Investigation Status: {investigation['status']}",
        f"Officer Notes: {investigation['notes'] or 'None'}",
        "",
        f"Generated: {datetime.now().strftime('%d-%b-%Y %H:%M')}",
    ]
    return "\n".join(lines)


# ================================================================
# DASHBOARD (stat cards + anomalies table + risk bars — no charts)
# ================================================================
def show_dashboard(df, breakdowns):
    st.subheader("📊 Dashboard")

    total = len(df)
    high = int((df["risk_level"] == "HIGH").sum())
    medium = int((df["risk_level"] == "MEDIUM").sum())
    low = int((df["risk_level"] == "LOW").sum())
    flagged = high + medium
    total_sanctioned = df["sanctioned_amount"].sum()
    at_risk = df.loc[df["risk_level"] == "HIGH", "sanctioned_amount"].sum()

    st.markdown(f"""<div class="mrow">
    <div class="mcard"><div class="top"><span class="lbl">Total Projects</span><span class="chip chip-a">📁</span></div><div class="val">{total}</div></div>
    <div class="mcard"><div class="top"><span class="lbl">Total Sanctioned</span><span class="chip chip-b">💰</span></div><div class="val">{fmt_lakh(total_sanctioned)}</div></div>
    <div class="mcard"><div class="top"><span class="lbl">Flagged Projects</span><span class="chip chip-c">🚨</span></div><div class="val">{flagged}</div><div class="sub" style="color:var(--danger);">Requires attention</div></div>
    <div class="mcard"><div class="top"><span class="lbl">Amount at Risk (High)</span><span class="chip chip-d">⚠️</span></div><div class="val">{fmt_lakh(at_risk)}</div></div>
    </div>""", unsafe_allow_html=True)

    colL, colR = st.columns([2, 1])

    with colL:
        st.markdown("### 🚨 Recent Anomalies")
        inv_all = db.get_all_investigation_status()
        alerts_df = df[df["risk_level"].isin(["HIGH", "MEDIUM"])].sort_values("risk_score", ascending=False).head(8)
        if alerts_df.empty:
            st.success("✅ No flagged projects")
        else:
            rows_html = ""
            for _, p in alerts_df.iterrows():
                b = breakdowns[p["project_id"]]
                status = inv_all.get(p["project_id"], {}).get("status", "Detected")
                badge_color = "var(--danger)" if b["risk_level"] == "HIGH" else "var(--warn)"
                rows_html += f"""<tr>
                    <td>{p['project_id']}</td><td>{p['district']}, {p['state']}</td>
                    <td>{fmt_lakh(p['sanctioned_amount'])}</td>
                    <td><span class="pill" style="background:{badge_color};">{b['total_score']}</span></td>
                    <td>{status}</td></tr>"""
            st.markdown(f"""<div class="panel"><table class="gt">
            <tr><th>Project ID</th><th>Location</th><th>Amount</th><th>Risk</th><th>Status</th></tr>
            {rows_html}</table></div>""", unsafe_allow_html=True)

    with colR:
        st.markdown("### Risk Distribution")
        bars = ""
        for label, count, color in [("High Risk", high, "var(--danger)"), ("Medium Risk", medium, "var(--warn)"), ("Low Risk", low, "var(--ok)")]:
            pct = (count / total * 100) if total else 0
            bars += f"""<div class="rrow"><div class="top"><span>{label}</span><span>{count}</span></div>
            <div class="rtrack"><div class="rfill" style="background:{color};width:{pct}%;"></div></div></div>"""
        st.markdown(f'<div class="panel">{bars}</div>', unsafe_allow_html=True)

    st.markdown("### 🤖 AI Detection Engine")
    st.caption("Rule-based checks (Financial, Cost, Timeline, Ghost Project Risk, Contractor) combined with an "
               "Isolation Forest anomaly model continuously score every project in the dataset. See the Analytics "
               "page for full charts, or open a project in Projects List / Alerts for the explainable breakdown.")


# ================================================================
# PROJECTS LIST
# ================================================================
def show_projects_list(df, breakdowns):
    st.subheader("📋 Projects List")
    st.markdown('<div class="panel">', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        state_f = st.selectbox("State", ["All"] + sorted(df["state"].unique().tolist()))
    with c2:
        district_f = st.selectbox("District", ["All"] + sorted(df["district"].unique().tolist()))
    with c3:
        type_f = st.selectbox("Project Type", ["All"] + sorted(df["project_type"].unique().tolist()))
    with c4:
        status_f = st.selectbox("Status", ["All"] + sorted(df["status"].unique().tolist()))

    c5, c6, c7 = st.columns(3)
    with c5:
        risk_f = st.selectbox("Risk Level", ["All", "HIGH", "MEDIUM", "LOW"])
    with c6:
        search_id = st.text_input("Search Project ID")
    with c7:
        search_contractor = st.text_input("Search Contractor")

    c8, c9 = st.columns(2)
    with c8:
        sort_by = st.selectbox("Sort by", ["Risk Score (desc)", "Sanctioned Amount (desc)", "Project ID"])
    st.markdown('</div>', unsafe_allow_html=True)

    filtered = df.copy()
    if state_f != "All":
        filtered = filtered[filtered["state"] == state_f]
    if district_f != "All":
        filtered = filtered[filtered["district"] == district_f]
    if type_f != "All":
        filtered = filtered[filtered["project_type"] == type_f]
    if status_f != "All":
        filtered = filtered[filtered["status"] == status_f]
    if risk_f != "All":
        filtered = filtered[filtered["risk_level"] == risk_f]
    if search_id:
        filtered = filtered[filtered["project_id"].str.contains(search_id, case=False, na=False)]
    if search_contractor:
        filtered = filtered[filtered["contractor"].str.contains(search_contractor, case=False, na=False)]

    if sort_by == "Risk Score (desc)":
        filtered = filtered.sort_values("risk_score", ascending=False)
    elif sort_by == "Sanctioned Amount (desc)":
        filtered = filtered.sort_values("sanctioned_amount", ascending=False)
    else:
        filtered = filtered.sort_values("project_id")

    st.markdown(f"**{len(filtered)} project(s) found**")

    for _, p in filtered.head(50).iterrows():
        b = breakdowns[p["project_id"]]
        with st.expander(f"{b['color']} {p['project_id']} — {p['project_type']} — {p['district']} — Risk: {b['total_score']}/100"):
            colA, colB = st.columns([3, 1])
            with colA:
                st.markdown(f"**Contractor:** {p['contractor']}  \n"
                            f"**Sanctioned:** {fmt_lakh(p['sanctioned_amount'])}  \n"
                            f"**Released:** {fmt_lakh(p['released_amount'])} ({p['released_pct']:.0f}%)  \n"
                            f"**Expenditure:** {fmt_lakh(p['expenditure'])}  \n"
                            f"**Estimated Progress:** {p['est_completion_pct']:.0f}%  \n"
                            f"**Status:** {p['status']}")
            with colB:
                if st.button("View Details", key=f"list_view_{p['project_id']}", use_container_width=True):
                    st.session_state.selected_project_id = p["project_id"]
                    st.rerun()


# ================================================================
# ALERTS
# ================================================================
def show_alerts(df, breakdowns):
    st.subheader("🚨 Alerts")

    alerts = df[df["risk_level"].isin(["HIGH", "MEDIUM"])].sort_values("risk_score", ascending=False)
    if alerts.empty:
        st.success("✅ No active alerts")
        return

    st.markdown(f"**{len(alerts)} project(s) flagged**")
    inv_all = db.get_all_investigation_status()

    for _, p in alerts.iterrows():
        b = breakdowns[p["project_id"]]
        status = inv_all.get(p["project_id"], {}).get("status", "Detected")
        with st.expander(f"{b['color']} {p['project_id']} — {b['risk_level']} ({b['total_score']}/100) — {status}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**Location:** {p['district']}, {p['state']}  \n**Type:** {p['project_type']}  \n**Contractor:** {p['contractor']}")
                for label, score, reason in fe.top_reasons(b, n=4):
                    st.markdown(f"❌ **{label}:** {reason}")
                st.markdown(f"**Recommended Action:** {fe.recommended_action(b)}")
            with col2:
                st.plotly_chart(viz.gauge_chart(b["total_score"]), use_container_width=True, key=f"alert_gauge_{p['project_id']}")
                if st.button("Investigate", key=f"alert_investigate_{p['project_id']}", use_container_width=True):
                    st.session_state.selected_project_id = p["project_id"]
                    st.rerun()


# ================================================================
# ANALYTICS
# ================================================================
def show_analytics(df, breakdowns):
    st.subheader("📈 Analytics")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(viz.risk_pie_chart(df), use_container_width=True)
    with col2:
        tchart = viz.timeline_chart(df)
        if tchart:
            st.plotly_chart(tchart, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(viz.bar_by(df, "project_type", "Projects by Type"), use_container_width=True)
    with col4:
        delayed = df[df["delay_days"] > 0]
        st.markdown(f"**⏱️ Delayed Projects: {len(delayed)} of {len(df)}**")
        if not delayed.empty:
            show = delayed[["project_id", "district", "contractor", "delay_days", "risk_score"]].sort_values("delay_days", ascending=False).head(10)
            show.columns = ["Project ID", "District", "Contractor", "Delay (days)", "Risk Score"]
            st.dataframe(show, use_container_width=True, hide_index=True)
        else:
            st.success("No delayed projects.")

    st.markdown("### 🗺️ Geographic Risk Distribution")
    gmap = viz.geo_map(df)
    if gmap:
        st.plotly_chart(gmap, use_container_width=True)
    else:
        st.info("No valid GPS coordinates available to plot.")

    st.markdown("### 🚨 Top 5 High-Risk Projects")
    top5 = df[df["risk_level"] == "HIGH"].sort_values("risk_score", ascending=False).head(5)
    if top5.empty:
        st.success("✅ No high-risk projects detected.")
    else:
        show = top5[["project_id", "project_type", "district", "state", "contractor", "risk_score"]].copy()
        show.columns = ["Project ID", "Type", "District", "State", "Contractor", "Risk Score"]
        st.dataframe(show, use_container_width=True, hide_index=True)


# ================================================================
# ABOUT
# ================================================================
def show_about():
    st.subheader("ℹ️ About GovLENS")
    st.markdown("""
GovLENS is an AI-assisted monitoring layer for MPLAD scheme projects, built for
Smart India Hackathon 2026. It combines **deterministic, explainable rule-based
checks** with an **unsupervised Isolation Forest anomaly model** to flag projects
for human review — it does not make final fraud determinations.

**Signals used:**
- Financial Anomaly — release vs. expenditure patterns
- Cost Anomaly — statistical comparison (median/IQR/z-score) against similar projects
- Timeline Anomaly — overdue and stagnant projects
- Ghost Project Risk Indicator — high fund release vs. low estimated physical progress
  *(this is a heuristic indicator, not real satellite verification)*
- Contractor Risk — historical performance across a contractor's project portfolio
- ML Anomaly Detection — Isolation Forest contribution on the combined feature set

All numbers on this dashboard are computed from the actual seeded dataset — no
random or fabricated project data is used at runtime.
""")


# ================================================================
# MAIN
# ================================================================
def main():
    st.markdown("""<div class="topbar"><div class="t"><h1>🛡️ GovLENS</h1>
    <p>AI Fraud Detection · MPLAD Scheme Monitoring · SIH 2026</p></div>
    <div class="live-chip"><span class="live-dot"></span>LIVE MONITORING</div></div>""", unsafe_allow_html=True)

    df, breakdowns = get_data()

    if df.empty:
        st.error("No project data found in the database.")
        return

    st.sidebar.markdown("""<div class="brand"><div class="mark">🛡️</div>
    <div class="txt"><div class="name">GovLENS</div><div class="tag">MPLAD MONITORING</div></div></div>""",
    unsafe_allow_html=True)

    role = st.sidebar.selectbox("Role", ["Ministry/Central Authority", "District Authority"], label_visibility="collapsed")
    st.session_state.user_role = "ministry" if role == "Ministry/Central Authority" else "district"

    if st.session_state.user_role == "district":
        districts = sorted(df["district"].unique().tolist())
        st.session_state.user_district = st.sidebar.selectbox("Select District", districts)
        view_df = df[df["district"] == st.session_state.user_district]
    else:
        view_df = df

    if st.session_state.user_role == "ministry":
        pages = ["📊\nDashboard", "📋\nProjects", "🚨\nAlerts", "📈\nAnalytics", "ℹ️\nAbout"]
    else:
        pages = ["📊\nDashboard", "📋\nProjects", "📈\nAnalytics", "ℹ️\nAbout"]
    page = st.sidebar.radio("Go to", pages, label_visibility="collapsed").split("\n")[1]

    st.sidebar.markdown('<div class="sb-foot">Rule-based + Isolation Forest scoring engine, computed live from the seeded MPLAD dataset.</div>', unsafe_allow_html=True)

    if st.session_state.selected_project_id:
        # detail view always uses full df so investigation/report has global context
        show_project_detail(st.session_state.selected_project_id, df, breakdowns)
        return

    if page == "Dashboard":
        show_dashboard(view_df, breakdowns)
    elif page == "Projects":
        show_projects_list(view_df, breakdowns)
    elif page == "Alerts":
        show_alerts(view_df, breakdowns)
    elif page == "Analytics":
        show_analytics(view_df, breakdowns)
    elif page == "About":
        show_about()


if __name__ == "__main__":
    main()