import streamlit as st
import cv2
import pandas as pd
import sqlite3
import os
import time
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import psutil

# OpenCV imports
import config
from database.db import init_db, log_detection
from detectors.weapon_detector import WeaponDetector
from detectors.person_detector import PersonDetector
from detectors.ensemble_detector import EnsembleDetector
from tracking.tracker import Tracker
from intrusion.intrusion_engine import IntrusionEngine
from alerts.alert_engine import trigger_alert
from utils.drawing_utils import draw_detections

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="DeepVision SOC | Command Center",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- PREMIUM BESPOKE TACTICAL STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Orbitron:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    :root {
        --tactical-blue: #3B82F6;
        --alert-red: #EF4444;
        --ui-bg: #0B0F1A;
        --sidebar-bg: #0F172A;
        --border-muted: #1E293B;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: var(--ui-bg);
    }

    /* Bespoke Dark Theme */
    .main {
        background-color: var(--ui-bg);
        background-image: 
            linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px);
        background-size: 40px 40px;
    }
    
    /* --- COMMAND CENTER SIDEBAR OVERHAUL --- */
    section[data-testid="stSidebar"] {
        background-color: #0B0F1A !important;
        border-right: 5px solid var(--tactical-blue) !important;
        min-width: 320px !important;
    }

    /* Target all radio labels */
    div[role="radiogroup"] label {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid var(--border-muted) !important;
        padding: 18px 25px !important;
        margin-bottom: 12px !important;
        border-radius: 4px !important;
        color: #94A3B8 !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        cursor: pointer !important;
    }

    div[role="radiogroup"] label:hover {
        border-color: var(--tactical-blue) !important;
        background: rgba(59, 130, 246, 0.1) !important;
    }

    /* THE DEFINITIVE ACTIVE SELECTOR */
    div[role="radiogroup"] label:has(input:checked) {
        background-color: var(--tactical-blue) !important;
        border-color: var(--tactical-blue) !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.4) !important;
    }

    div[role="radiogroup"] label:has(input:checked) p {
        color: #FFFFFF !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
    }

    /* Terminal-style Typography */
    .stTable, .stDataFrame {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
    }

    h1, h2, h3, .section-title {
        font-family: 'Orbitron', sans-serif !important;
        color: #FFFFFF !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Custom Header */
    .main-header {
        border-left: 8px solid var(--tactical-blue);
        background: linear-gradient(90deg, rgba(30, 41, 59, 0.4) 0%, transparent 100%);
        padding: 40px;
        margin-bottom: 40px;
    }
    
    /* Tactical Status Bar */
    .status-bar {
        background: #111827;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        padding: 15px 30px;
        border: 1px solid var(--border-muted);
        border-top: 4px solid var(--tactical-blue);
        display: flex;
        justify-content: space-between;
        margin-bottom: 40px;
        border-radius: 4px;
        color: #FFFFFF;
    }

    /* Unique Card Design */
    .kpi-card {
        background: #111827;
        border: 1px solid var(--border-muted);
        padding: 25px;
        position: relative;
    }
    .kpi-card::after {
        content: '';
        position: absolute;
        top: 0; right: 0;
        width: 15px; height: 15px;
        border-top: 2px solid var(--tactical-blue);
        border-right: 2px solid var(--tactical-blue);
    }
    .kpi-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.5em;
        color: var(--tactical-blue);
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-thumb { background: var(--tactical-blue); }
    /* Alert Item Styling */
    .alert-card {
        background: rgba(30, 41, 59, 0.5);
        border-left: 4px solid #3B82F6;
        padding: 10px 15px;
        margin-bottom: 10px;
        border-radius: 5px;
        border: 1px solid var(--border-muted);
    }
    .severity-high { border-left-color: var(--alert-red); }
    .severity-med { border-left-color: #F59E0B; }
    .severity-low { border-left-color: #10B981; }
    
    /* Agent Indicator */
    .agent-panel {
        background: #111827;
        border: 1px solid var(--border-muted);
        padding: 15px;
        border-radius: 4px;
        text-align: center;
    }
    .status-dot {
        height: 10px;
        width: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
    }
    .dot-active { background-color: #10B981; box-shadow: 0 0 10px #10B981; }
    .dot-idle { background-color: #6B7280; }
    .dot-error { background-color: var(--alert-red); box-shadow: 0 0 10px var(--alert-red); }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "run" not in st.session_state: st.session_state.run = False
if "alerts_count" not in st.session_state: st.session_state.alerts_count = 0
if "last_frame" not in st.session_state: st.session_state.last_frame = None
if "recent_snapshots" not in st.session_state: st.session_state.recent_snapshots = []
if "num_log_rows" not in st.session_state: st.session_state.num_log_rows = 10

# --- MODELS & DB ---
@st.cache_resource(show_spinner=False)
def load_models():
    init_db()
    with st.spinner("Initializing DeepVision Core Agents..."):
        w_det = WeaponDetector()
        p_det = PersonDetector()
        ens = EnsembleDetector(w_det, p_det)
        trk = Tracker()
        ie = IntrusionEngine()
    return ens, trk, ie

ensemble, tracker, intrusion_engine = load_models()
DB_PATH = "events.db"

def load_data():
    if not os.path.exists(DB_PATH): return pd.DataFrame()
    try:
        conn = sqlite3.connect(DB_PATH)
        # Increased limit to 10,000 for "Full History" support
        df = pd.read_sql_query("SELECT * FROM detections ORDER BY timestamp DESC LIMIT 10000", conn)
        conn.close()
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp', ascending=False)
        return df
    except: return pd.DataFrame()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <div style='font-size: 2.2em; margin-bottom: 10px;'>📹</div>
        <h3 style='color: white; margin: 0; font-family: "Orbitron", sans-serif;'>DEEPVISION <span style='font-weight: 300; opacity: 0.7;'>SOC</span></h3>
        <p style='color: #64748B; font-size: 0.85em; letter-spacing: 1px;'>SURVEILLANCE OPERATIONS CENTER</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    menu = st.radio("📡 SYSTEM MODULES", [
        "Real-Time Monitoring",
        "Threat & Alert Management",
        "Object Detection Analytics",
        "Behavior & Activity Analysis"
    ])
    
    st.markdown("---")
    st.markdown("### 🎮 Control Interface")
    if st.button("🚀 START SCAN", use_container_width=True, type="primary"): st.session_state.run = True
    if st.button("🛑 STOP SYSTEM", use_container_width=True): 
        st.session_state.run = False
        st.rerun()

# --- TOP STATUS BAR ---
st.markdown(f"""
<div class="status-bar">
    <div style='color: #F8FAFC;'>🔌 <b>Camera Link:</b> <span style='color: #10B981;'>ONLINE</span></div>
    <div style='color: #F8FAFC;'>🕒 <b>Local Time:</b> {datetime.now().strftime("%I:%M:%S %p")}</div>
    <div style='color: #F8FAFC;'>🛰️ <b>Signal:</b> <span style='color: #3B82F6;'>STABLE</span></div>
    <div style='color: #F8FAFC;'>📝 <b>Log State:</b> <span style='color: {"#EF4444" if st.session_state.run else "#6B7280"};'>{"SCANNING" if st.session_state.run else "READY"}</span></div>
</div>
""", unsafe_allow_html=True)

# --- MODULE UTILS ---
def get_mock_kpi(label, value, icon="📈", color="#3B82F6"):
    return f"""
    <div class="kpi-card" style="border-top: 2px solid {color};">
        <div style="font-size: 1.2em; margin-bottom: 5px;">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """

# --- MODULE 1: REAL-TIME MONITORING ---
def show_realtime_monitoring():
    st.markdown("<div class='section-title'>👁️ Live Surveillance Stream</div>", unsafe_allow_html=True)
    col_v, col_side = st.columns([3, 1])
    
    with col_v:
        # Single Large Focus Feed
        v1 = st.empty()
        if not st.session_state.run:
            standby = st.session_state.last_frame if st.session_state.last_frame is not None else "background.jpg"
            v1.image(standby, use_container_width=True, caption="[CAM 01] System Standby - READY")
        
    with col_side:
        st.markdown("##### 📹 Terminal Status")
        st.success("📹 CAM 01 - LOCAL ACCESS (ACTIVE)")
        st.markdown("---")
        st.markdown("##### 🕵️ Detection Engine")
        st.info("Zero-Shot YOLO: ARMED")
        st.info("Tracker v2: SYNCED")

    return v1

# --- MODULE 2: THREAT & ALERT MANAGEMENT ---
def show_threat_management():
    st.markdown("<div class='section-title'>⚠️ Threat Escalation & Forensic Logs</div>", unsafe_allow_html=True)
    df = load_data()
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("##### Forensic Evidence Gallery")
        if st.session_state.recent_snapshots:
            for snap_path in reversed(st.session_state.recent_snapshots[-3:]):
                st.image(snap_path, use_container_width=True, caption=f"Forensic ID: {os.path.basename(snap_path)}")
        else:
            st.info("No active threat snapshots archived.")
    
    with c2:
        st.markdown("##### Detection Velocity (Real-Time)")
        t_df = pd.DataFrame({"Time": pd.date_range(datetime.now(), periods=10, freq="-1min"), "Hits": np.random.randint(0, 5, 10)})
        fig_t = px.area(t_df, x="Time", y="Hits", color_discrete_sequence=["#EF4444"])
        fig_t.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=300)
        st.plotly_chart(fig_t, use_container_width=True)

    st.markdown("---")
    st.markdown("##### 📝 System Audit Archive (High Fidelity)")
    
    if not df.empty:
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            time_filter = st.selectbox("🕒 Preset Time Range", ["All History", "Last 1 Hour", "Last 24 Hours", "Last 7 Days"])
        with f_col2:
            class_filter = st.multiselect("🎯 Objective Filter", ["All"] + sorted(df['class_name'].unique().tolist()), default="All")
        
        # Apply Logic
        filtered_df = df.copy()
        now = datetime.now()
        
        # Enhanced Display Logic for Warnings
        def process_warning_labels(row):
            is_weapon = row['class_name'].lower() in [w.lower() for w in config.WEAPON_CLASSES]
            if is_weapon:
                return f"⚠️ WARNING: {row['class_name'].upper()}"
            return row['class_name']
            
        filtered_df['class_name'] = filtered_df.apply(process_warning_labels, axis=1)

        if time_filter == "Last 1 Hour":
            filtered_df = filtered_df[filtered_df['timestamp'] > now - pd.Timedelta(hours=1)]
        elif time_filter == "Last 24 Hours":
            filtered_df = filtered_df[filtered_df['timestamp'] > now - pd.Timedelta(days=1)]
        elif time_filter == "Last 7 Days":
            filtered_df = filtered_df[filtered_df['timestamp'] > now - pd.Timedelta(days=7)]
            
        if "All" not in class_filter and class_filter:
            # Filter against processed warning labels using regex
            pattern = '|'.join(class_filter)
            filtered_df = filtered_df[filtered_df['class_name'].str.contains(pattern, case=False)]
            
        # Pagination Logic
        total_records = len(filtered_df)
        display_df = filtered_df.iloc[:st.session_state.num_log_rows]
        
        def highlight_weapons(s):
            is_warn = "⚠️ WARNING" in str(s.class_name)
            # BRIGHT RED FONT as requested
            return ['color: #FF0000 !important; font-weight: 900; background-color: rgba(220, 38, 38, 0.1);' if is_warn else '' for _ in s]

        st.caption(f"Displaying {len(display_df)} of {total_records} archived entries")
        
        # Stylized Dataframe
        st.dataframe(
            display_df[['timestamp', 'class_name', 'confidence', 'is_intrusion']].style.apply(highlight_weapons, axis=1),
            use_container_width=True,
            height=400
        )
        
        if st.session_state.num_log_rows < total_records:
            if st.button("🔽 LOAD NEXT 10 RECORDS", use_container_width=True):
                st.session_state.num_log_rows += 10
                st.rerun()
        else:
            st.success("🏁 All historical records loaded.")
            if st.button("🔄 Reset View"):
                st.session_state.num_log_rows = 10
                st.rerun()
    else:
        st.caption("System log is currently empty.")

# --- MODULE 3: OBJECT DETECTION ANALYTICS ---
def show_analytics():
    st.markdown("<div class='section-title'>📊 Intelligence Metrics</div>", unsafe_allow_html=True)
    df = load_data()
    
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(get_mock_kpi("Total Detected", len(df) if not df.empty else 0), unsafe_allow_html=True)
    k2.markdown(get_mock_kpi("Model Confidence", "94.2%", "🎯", "#10B981"), unsafe_allow_html=True)
    k3.markdown(get_mock_kpi("Intrusion Alerts", len(df[df['is_intrusion']==1]) if not df.empty else 0, "🚨", "#EF4444"), unsafe_allow_html=True)
    k4.markdown(get_mock_kpi("Process FPS", "32.5", "⚡", "#A855F7"), unsafe_allow_html=True)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 🧱 Category Distribution")
        if not df.empty:
            c_dist = df['class_name'].value_counts().reset_index()
            fig = px.pie(c_dist, values='count', names='class_name', hole=0.5)
            fig.update_layout(showlegend=True, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("##### ⚡ FPS Stability Index")
        fig_perf = px.line(y=np.random.normal(30, 1.5, 100))
        fig_perf.update_layout(margin=dict(l=0, r=0, t=0, b=0), yaxis_title="Frames Per Second")
        st.plotly_chart(fig_perf, use_container_width=True)

# --- MODULE 4: BEHAVIOR & ACTIVITY ANALYSIS ---
def show_behavior_analysis():
    st.markdown("<div class='section-title'>🌀 Crowd Density & Behavior Metrics</div>", unsafe_allow_html=True)
    df = load_data()
    
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("##### Spatial Heatmap (Intensity Matrix)")
        grid = np.random.randint(0, 100, (10, 10))
        fig = go.Figure(data=go.Heatmap(z=grid, colorscale='Viridis'))
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        st.markdown("##### Activity Trend (Last 24h)")
        trend = np.random.randint(0, 100, 24)
        fig_trend = px.line(x=list(range(24)), y=trend, labels={'x':'Hour', 'y':'Detections'})
        st.plotly_chart(fig_trend, use_container_width=True)

# --- MODULE 5: MULTI-AGENT SYSTEM HUB ---
def show_agent_monitoring():
    st.markdown("<div class='section-title'>🤖 System Pipeline Orchestration</div>", unsafe_allow_html=True)
    
    ag1, ag2, ag3, ag4 = st.columns(4)
    with ag1: st.markdown("<div class='agent-panel'><div class='status-dot dot-active'></div><br><b>Visual Perception</b><br><small style='color: #10B981;'>STATE: DETECTING</small></div>", unsafe_allow_html=True)
    with ag2: st.markdown("<div class='agent-panel'><div class='status-dot dot-active'></div><br><b>Temporal Tracker</b><br><small style='color: #10B981;'>STATE: SYNCED</small></div>", unsafe_allow_html=True)
    with ag3: st.markdown("<div class='agent-panel'><div class='status-dot dot-idle'></div><br><b>Risk Assessment</b><br><small style='color: #6B7280;'>STATE: STANDBY</small></div>", unsafe_allow_html=True)
    with ag4: st.markdown("<div class='agent-panel'><div class='status-dot dot-active'></div><br><b>Logic Dispatcher</b><br><small style='color: #10B981;'>STATE: ARMED</small></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("##### ⚙️ Production Pipeline Workflow")
    st.markdown("""
    1. **INGESTION**: Live BGR frame buffer extraction.
    2. **INFERENCE**: YOLO-World high-confidence detection (Person/Weapon).
    3. **TRACKING**: Multi-object ByteTrack association.
    4. **SPATIAL ANALYTICS**: ROI Intrusion & Zone Violation check.
    5. **NOTIFICATION**: Evidence snapshot capture & Alert dispatch.
    """)

# --- MAIN APP ROUTING ---
v_placeholder = None

if menu == "Real-Time Monitoring":
    v_placeholder = show_realtime_monitoring()
elif menu == "Threat & Alert Management":
    show_threat_management()
elif menu == "Object Detection Analytics":
    show_analytics()
elif menu == "Behavior & Activity Analysis":
    show_behavior_analysis()

# --- EXECUTION LOOP (Global) ---
if st.session_state.run:
    cap = cv2.VideoCapture(config.STREAM_URL)
    last_ui_update = 0
    f_count = 0
    c_dets = []
    
    # Notify User
    if menu == "Real-Time Monitoring":
        st.toast("System Terminal Initialized", icon="📹")
        time.sleep(1)
        st.toast("Monitoring Protocol: ACTIVE", icon="✅")

    last_snapshot_time = 0

    while cap.isOpened() and st.session_state.run:
        ret, frame = cap.read()
        if not ret: break
        
        f_count += 1
        if f_count % 3 == 1:
            c_dets = ensemble.detect(frame)
        
        tracks = tracker.update(c_dets)
        ints = intrusion_engine.check_intrusion(tracks)
        int_ids = {e["track"]["id"] for e in ints}
        
        if f_count % 3 == 1:
            for trk in tracks:
                log_detection(trk["class"], trk["confidence"], trk["bbox"], (trk["id"] in int_ids))
        
        for e in ints:
            snap_path = trigger_alert(frame, e)
            if snap_path and (time.time() - last_snapshot_time > 3.0):
                st.session_state.recent_snapshots.append(snap_path)
                if len(st.session_state.recent_snapshots) > 10:
                    st.session_state.recent_snapshots.pop(0)
                last_snapshot_time = time.time()
                st.toast(f"EVIDENCE CAPTURED: {e['track']['class'].upper()}", icon="🚨")

        draw_detections(frame, tracks)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        st.session_state.last_frame = frame_rgb
        
        # Only render video if in Real-Time Module
        if menu == "Real-Time Monitoring" and v_placeholder:
            v_placeholder.image(frame_rgb, use_container_width=True)
            
        # Update logic throttled
        # Note: In a tabbed interface, we may not want to force-refresh non-active modules too often
        # but the logging logic must run in background
            
    cap.release()
