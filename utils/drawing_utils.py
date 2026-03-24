import cv2

def draw_detections(frame, tracks):

    for track in tracks:

        x1, y1, x2, y2 = track["bbox"]

        # convert to int for OpenCV
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        label = track["class"]
        track_id = track["id"]
        conf = track["confidence"]

        text = f"{label} {conf:.2f} ID:{track_id}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

        cv2.putText(
            frame,
            text,
            (x1, y1-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0,255,0),
            2
        )