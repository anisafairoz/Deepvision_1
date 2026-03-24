from ultralytics import YOLO
import config


class PersonDetector:

    def __init__(self):
        # load YOLO model for person detection
        self.model = YOLO("yolov8n.pt")

    def detect(self, frame):

        results = self.model(frame, conf=config.CONFIDENCE_THRESHOLD)

        detections = []

        for result in results:
            for box in result.boxes:

                cls = int(box.cls[0])

                # COCO class id for person = 0
                if cls == 0:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    conf = float(box.conf[0])

                    detections.append({
                        "bbox": [x1, y1, x2, y2],
                        "confidence": conf,
                        "class": "person"
                    })

        return detections