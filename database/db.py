import sqlite3
import datetime
import os

DB_PATH = "events.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            class_name TEXT,
            confidence REAL,
            x_center REAL,
            y_center REAL,
            is_intrusion BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

def log_detection(class_name, confidence, bbox, is_intrusion=False):
    x1, y1, x2, y2 = bbox
    x_center = (x1 + x2) / 2.0
    y_center = (y1 + y2) / 2.0
    
    # Use Local System Time
    local_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO detections (timestamp, class_name, confidence, x_center, y_center, is_intrusion)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (local_time, class_name, confidence, x_center, y_center, is_intrusion))
    conn.commit()
    conn.close()
