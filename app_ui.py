import streamlit as st
import cv2
import pandas as pd
import sqlite3
import os
import time
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

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

st.set_page_config(page_title="DeepVision SOC", layout="wide", page_icon="🛡️")

# Custom CSS for the SOC dashboard look
st.markdown("""
<style>
.alert-card {
    background-color: #1E232E;
    border-left: 5px solid #EAB308;
    padding: 10px 15px;
    margin-bottom: 10px;
    border-radius: 4px;
    color: white;
    font-size: 0.9em;
}
.alert-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
}
.alert-badge {
    background-color: #EAB308;
    color: black;
    font-weight: bold;
    font-size: 0.75em;
    padding: 2px 6px;
    border-radius: 4px;
}
.alert-time {
    color: #9CA3AF;
    font-size: 0.8em;
}
.alert-desc {
    margin-bottom: 8px;
    color: #D1D5DB;
}


/* Make Tabs look darker/cleaner */
div.stTabs [data-baseweb="tab-list"] {
    gap: 20px;
}
div.stTabs [data-baseweb="tab"] {
    height: 40px;
    white-space: pre-wrap;
    background-color: transparent;
    color: #9CA3AF;
}
div.stTabs [aria-selected="true"] {
    color: white;
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_models():
    init_db()
    w_det = WeaponDetector()
    p_det = PersonDetector()
    ens = EnsembleDetector(w_det, p_det)
    trk = Tracker()
    ie = IntrusionEngine()
    return ens, trk, ie

ensemble, tracker, intrusion_engine = load_models()

DB_PATH = "events.db"

def load_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(DB_PATH)
        # Fetching only the last 2000 records to keep the dashboard fast and reactive
        df = pd.read_sql_query("SELECT * FROM detections ORDER BY timestamp DESC LIMIT 2000", conn)
        conn.close()
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            # Sort back to ascending for time-series charts
            df = df.sort_values('timestamp')
        return df
    except Exception as e:
        return pd.DataFrame()

# Header
st.markdown("<h2 style='text-align: left;'>🛡️ DeepVision <span style='float: right; font-size: 0.5em; font-weight: normal; color: #9CA3AF; line-height:3em;'>Security Operations Center</span></h2>", unsafe_allow_html=True)
st.markdown("---")

# Layout
col_main, col_alerts = st.columns([2.3, 1])

with col_main:
    # 1. Live Feed Section
    top_col1, top_col2 = st.columns([1, 1])
    with top_col1:
        st.markdown("**Live Surveillance Feed**")
    with top_col2:
        st.markdown('<div style="text-align: right;"><span style="background-color: red; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; margin-right: 10px;">REC 🔴</span></div>', unsafe_allow_html=True)

    video_placeholder = st.empty()
    status_text = st.empty()
    
    # 2. Activity Insights (KPIs + Real-time Graphs)
    st.markdown("---")
    st.subheader("Activity Insights")
    
    kpi_cols = st.columns(3)
    kpi_total = kpi_cols[0].empty()
    kpi_suspicious = kpi_cols[1].empty()
    kpi_latest = kpi_cols[2].empty()
    
    graph_col1, graph_col2 = st.columns(2)
    with graph_col1:
        st.write("📈 **Detection Frequency**")
        freq_chart_placeholder = st.empty()
    with graph_col2:
        st.write("📊 **Class Distribution**")
        dist_chart_placeholder = st.empty()

    # 3. Spatial Analysis (Heatmap)
    st.markdown("---")
    st.subheader("Spatial Analysis")
    heat_placeholder = st.empty()

    # 4. Historical Analysis (Detailed Large Charts)
    st.markdown("---")
    st.subheader("Detailed Historical Reports")
    
    st.write("🗓️ **Weekly Intrusion Trends**")
    weekly_chart_placeholder = st.empty()
    
    st.write("🔍 **Suspicious Category Breakdown**")
    category_chart_placeholder = st.empty()

with col_alerts:
    st.markdown("⚠️ **Recent Alerts**")
    alerts_container = st.container(height=650)
    alerts_placeholder = alerts_container.empty()

# Sidebar Controls
start_btn = st.sidebar.button("Start Application (Grant Camera Permission)")
stop_btn = st.sidebar.button("Stop Application")

if "run" not in st.session_state:
    st.session_state.run = False

if start_btn:
    st.session_state.run = True

if stop_btn:
    st.session_state.run = False
    st.rerun()

def build_heat_grid(df):
    """Convert x,y coordinates into a 3x4 grid mapping density."""
    if df.empty:
        return np.zeros((3, 4))
    
    x_max = max(df['x_center'].max(), 640)
    y_max = max(df['y_center'].max(), 480)
    
    df['x_bin'] = pd.cut(df['x_center'], bins=[0, x_max*0.25, x_max*0.5, x_max*0.75, x_max*2], labels=[0,1,2,3], include_lowest=True, right=False)
    # y axis logic goes from top to bottom locally (0 at top) but plotly heatmap plots (0,0) at bottom left.
    # To map "Zone C" at top, "Zone A" at bottom like in image:
    df['y_bin'] = pd.cut(df['y_center'], bins=[0, y_max*0.33, y_max*0.66, y_max*2], labels=[2, 1, 0], include_lowest=True, right=False)
    
    grid = np.zeros((3, 4))
    for _, row in df.iterrows():
        try:
            r = int(row['y_bin'])
            c = int(row['x_bin'])
            grid[r, c] += 1
        except:
            pass
    return grid

def update_dashboard_ui():
    """Fetches latest DB data and updates all dashboard placeholders."""
    curr_time = time.time()
    df = load_data()
    if not df.empty:
        # 1. KPIs
        total_detections = len(df)
        suspicious_df = df[df['is_intrusion'] == 1]
        suspicious_alerts = len(suspicious_df)
        
        kpi_total.metric("TOTAL DETECTIONS", total_detections)
        kpi_suspicious.metric("SUSPICIOUS ALERTS", suspicious_alerts)
        if not suspicious_df.empty:
            latest_time = suspicious_df.iloc[-1]['timestamp'].strftime("%H:%M:%S")
            kpi_latest.metric("LATEST INTRUSION", latest_time)
        else:
            kpi_latest.metric("LATEST INTRUSION", "N/A")

        # 2. Detection Frequency (Line Chart)
        df['minute'] = df['timestamp'].dt.floor('Min')
        freq_df = df.groupby('minute').size().reset_index(name='count')
        fig_freq = px.line(freq_df, x='minute', y='count', height=300)
        fig_freq.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        freq_chart_placeholder.plotly_chart(fig_freq, use_container_width=True, key=f"freq_{curr_time}")

        # 3. Class Distribution (Pie Chart)
        class_dist = df['class_name'].value_counts().reset_index()
        class_dist.columns = ['class', 'count']
        fig_dist = px.pie(class_dist, names='class', values='count', height=300)
        fig_dist.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        dist_chart_placeholder.plotly_chart(fig_dist, use_container_width=True, key=f"dist_{curr_time}")

        # 4. Activity Grid Heatmap (Larger)
        grid_data = build_heat_grid(df)
        fig_hm = go.Figure(data=go.Heatmap(
            z=grid_data,
            y=["Zone A", "Zone B", "Zone C"],
            x=["Q1", "Q2", "Q3", "Q4"], 
            colorscale="Viridis",
            showscale=True
        ))
        fig_hm.update_layout(margin=dict(l=0, r=0, t=20, b=20), height=300)
        heat_placeholder.plotly_chart(fig_hm, use_container_width=True, key=f"heat_{curr_time}")
        
        # 5. Weekly Chart (Full Width, Larger)
        df['date'] = df['timestamp'].dt.date
        weekly_df = df[df['is_intrusion'] == 1].groupby('date').size().reset_index(name='Alerts')
        weekly_df = weekly_df.tail(14) # Show last 2 weeks if available
        fig_bar = px.bar(weekly_df, x='date', y='Alerts', height=400, color_discrete_sequence=['#EAB308'])
        fig_bar.update_layout(margin=dict(l=0, r=0, t=20, b=20))
        weekly_chart_placeholder.plotly_chart(fig_bar, use_container_width=True, key=f"week_{curr_time}")
        
        # 6. Detailed Category Breakdown (Full Width, Larger)
        if suspicious_alerts > 0:
            cat_df = suspicious_df['class_name'].value_counts().reset_index()
            cat_df.columns = ['Weapon Class', 'Detections Found']
            fig_pie_detail = px.pie(cat_df, names='Weapon Class', values='Detections Found', height=400, hole=0.5,
                                    title="Distribution of Suspicious Objects Detected")
            fig_pie_detail.update_traces(textinfo='percent+label')
            category_chart_placeholder.plotly_chart(fig_pie_detail, use_container_width=True, key=f"cat_{curr_time}")
        
        # Build Alerts Feed (Top 10)
        intrusions = df[df['is_intrusion'] == 1].sort_values(by='timestamp', ascending=False).head(10)
        html_feed = ""
        for _, row in intrusions.iterrows():
            time_str = row['timestamp'].strftime("%I:%M %p").lower()
            desc = f"Detected associated activity. Suspicious profile match for: {row['class_name'].title()}"
            html_feed += f"""
            <div class="alert-card">
                <div class="alert-header">
                    <span class="alert-badge">SUSPICIOUS</span>
                    <span class="alert-time">{time_str}</span>
                </div>
                <div class="alert-desc">{desc}</div>
            </div>
            """
        alerts_placeholder.markdown(html_feed, unsafe_allow_html=True)

if st.session_state.run:
    # Initialize Video Capture
    cap = cv2.VideoCapture(config.STREAM_URL)
    last_stat_update = 0
    frame_count = 0
    cached_detections = []

    while cap.isOpened() and st.session_state.run:
        ret, frame = cap.read()
        if not ret:
            status_text.warning("Video stream ended or cannot be read.")
            break
            
        # Processing with Frame Skipping
        frame_count += 1
        if frame_count % 3 == 1:
            cached_detections = ensemble.detect(frame)
            
        tracks = tracker.update(cached_detections)
        intrusion_events = intrusion_engine.check_intrusion(tracks)
        intrusion_track_ids = {event["track"]["id"] for event in intrusion_events}
        
        # Logging (Throttle logs)
        if frame_count % 3 == 1:
            for track in tracks:
                log_detection(
                    class_name=track["class"],
                    confidence=track["confidence"],
                    bbox=track["bbox"],
                    is_intrusion=(track["id"] in intrusion_track_ids)
                )
            
        for event in intrusion_events:
            trigger_alert(frame, event)

        draw_detections(frame, tracks)
        
        # Render Video
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
        
        # Dashboard Updates (Every 1.5s)
        curr_time = time.time()
        if (curr_time - last_stat_update) > 1.5:
            update_dashboard_ui()
            last_stat_update = curr_time

    cap.release()
else:
    status_text.info("Camera Stream Paused. Please click 'Start Application' in the sidebar.")
    # Show dashboard even when paused
    update_dashboard_ui()
