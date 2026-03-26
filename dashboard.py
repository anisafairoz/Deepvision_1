import streamlit as st
import pandas as pd
import sqlite3
import datetime
import os
import plotly.express as px

DB_PATH = "events.db"
BACKGROUND_IMG = "background.jpg"

st.set_page_config(page_title="DeepVision Dashboard", layout="wide", page_icon="📈")

def load_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM detections", conn)
        conn.close()
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        return pd.DataFrame()

st.title("🛡️ DeepVision AI Analytics")

df = load_data()

if df.empty:
    st.warning("No data found. Ensure the video stream is running.")
else:
    # --- KPIs ---
    st.subheader("Activity Insights")
    col1, col2, col3 = st.columns(3)
    
    total_detections = len(df)
    intrusions = df[df['is_intrusion'] == 1]
    total_intrusions = len(intrusions)
    
    col1.metric("Total Detections", total_detections)
    col2.metric("Intrusion Alerts", total_intrusions)
    
    if not intrusions.empty:
        latest = intrusions.iloc[-1]['timestamp']
        col3.metric("Latest Intrusion", latest.strftime("%H:%M:%S"))
    else:
        col3.metric("Latest Intrusion", "None")

    st.markdown("---")
    
    # --- Layout ---
    row1_c1, row1_c2 = st.columns([1, 1])
    
    with row1_c1:
        st.subheader("Detections Over Time")
        # Time series grouping by minute
        df['minute'] = df['timestamp'].dt.floor('Min')
        time_series = df.groupby('minute').size().reset_index(name='count')
        if not time_series.empty:
            fig_ts = px.line(time_series, x='minute', y='count', title='Detection Frequency')
            st.plotly_chart(fig_ts, use_container_width=True)
            
    with row1_c2:
        st.subheader("Detected Objects Distribution")
        class_dist = df['class_name'].value_counts().reset_index()
        class_dist.columns = ['class', 'count']
        if not class_dist.empty:
            fig_pie = px.pie(class_dist, names='class', values='count', title='Class Distribution')
            st.plotly_chart(fig_pie, use_container_width=True)
            
    st.markdown("---")
    
    st.subheader("Detection Heatmap")
    
    if os.path.exists(BACKGROUND_IMG):
        st.image(BACKGROUND_IMG, caption="Live Feed Reference", width=640)
    
    if not df.empty:
        # Create a heat map using 2D histogram
        fig_heat = px.density_heatmap(
            df, x='x_center', y='y_center', 
            nbinsx=30, nbinsy=30, 
            color_continuous_scale="Viridis",
            title="Spatial Density of Detections (X, Y Image Coordinates)"
        )
        # Invert Y axis to match image coordinates (origin at top-left)
        fig_heat.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_heat, use_container_width=True)
