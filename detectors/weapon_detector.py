from ultralytics import YOLO
import config
import os

class WeaponDetector:

    def __init__(self):

        # get project root directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # path to weapon model
        model_path = os.path.join(base_dir, "models", "weapon_model.pt")

        print("Loading model from:", model_path)

        # load YOLO model
        self.model = YOLO(model_path)

    def detect(self, frame):

        results = self.model(frame, conf=config.CONFIDENCE_THRESHOLD)

        detections = []

        for result in results:
            for box in result.boxes:

                # bounding box
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                # confidence
                conf = float(box.conf[0])

                # class id
                cls_id = int(box.cls[0])

                # convert class id → class name
                label = self.model.names[cls_id]

                detections.append({
                    "bbox": [x1, y1, x2, y2],
                    "confidence": conf,
                    "class": label
                })

        return detections