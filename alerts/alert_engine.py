import os
import cv2
import datetime

try:
    from alerts.telegram_alert import send_telegram
except ImportError:
    from telegram_alert import send_telegram

SNAPSHOT_DIR = "alerts/snapshots"
if not os.path.exists(SNAPSHOT_DIR):
    os.makedirs(SNAPSHOT_DIR)

def save_snapshot(frame, bbox, class_name):
    """
    Crops the frame to the detected object and saves it as a forensic archive.
    Returns the relative path to the saved image.
    """
    try:
        ih, iw, _ = frame.shape
        x1, y1, x2, y2 = [int(v) for v in bbox]
        
        # Add a 10% padding for context, clipped to image boundaries
        pad_w = int((x2 - x1) * 0.1)
        pad_h = int((y2 - y1) * 0.1)
        
        rx1 = max(0, x1 - pad_w)
        ry1 = max(0, y1 - pad_h)
        rx2 = min(iw, x2 + pad_w)
        ry2 = min(ih, y2 + pad_h)
        
        cropped = frame[ry1:ry2, rx1:rx2]
        
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{ts}_{class_name}.jpg"
        filepath = os.path.join(SNAPSHOT_DIR, filename)
        
        cv2.imwrite(filepath, cropped)
        return filepath
    except Exception as e:
        print(f"[!] Alert Engine: Failed to save snapshot: {e}")
        return None

def trigger_alert(frame, event):
    """
    Triggers visual and remote alerts for detected security events.
    'event' contains track and type information.
    """
    track = event.get("track", {})
    class_name = track.get("class", "unknown")
    conf = track.get("confidence", 0.0)
    bbox = track.get("bbox", [0, 0, 0, 0])
    
    # Save a forensic snapshot of just the detected object
    snapshot_path = save_snapshot(frame, bbox, class_name)
    
    msg = f"🛡️ DeepVision ALERT: {class_name.upper()} detected with {conf:.2f} confidence!"
    if snapshot_path:
        msg += f" [Snapshot: {snapshot_path}]"
        
    print(f"[*] {msg}")

    # Send remote notification
    try:
        send_telegram(msg)
    except Exception as e:
        print(f"[!] Alert Engine: Failed to send Telegram notification: {e}")
    
    return snapshot_path