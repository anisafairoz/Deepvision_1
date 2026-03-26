from ultralytics import YOLO
import config
import os

class WeaponDetector:

    def __init__(self):
        # path to YOLO-World model (downloads automatically if missing)
        model_path = config.WEAPON_MODEL_PATH

        print("Loading Zero-Shot YOLO-World model from:", model_path)

        # load YOLO-World model
        self.model = YOLO(model_path)
        
        # Set custom classes dynamic detection
        print("Setting open-vocabulary classes:", config.WEAPON_CLASSES)
        self.model.set_classes(config.WEAPON_CLASSES)

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

                # convert class id -> class name
                label = self.model.names[cls_id]

                detections.append({
                    "bbox": [x1, y1, x2, y2],
                    "confidence": conf,
                    "class": label
                })

        return detections