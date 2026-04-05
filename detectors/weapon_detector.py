from ultralytics import YOLO
import config
import os
import sys

class WeaponDetector:

    def __init__(self):
        # path to YOLO-World model (downloads automatically if missing)
        model_path = config.WEAPON_MODEL_PATH

        print(f"[*] Initializing Weapon Detection Engine: {model_path}")

        try:
            # load YOLO-World model
            self.model = YOLO(model_path)
            
            # Set custom classes dynamic detection
            # Note: Only YOLO-World models support set_classes
            if hasattr(self.model, 'set_classes'):
                print(f"[*] Setting open-vocabulary monitoring targets: {config.WEAPON_CLASSES}")
                self.model.set_classes(config.WEAPON_CLASSES)
            else:
                print("[!] Warning: model does not appear to be YOLO-World. 'set_classes' skipped.")
                
        except Exception as e:
            print(f"[!] Error loading weapon model: {e}")
            # Fallback or re-raise
            raise e

    def detect(self, frame):
        try:
            results = self.model(frame, conf=config.CONFIDENCE_THRESHOLD, verbose=False)

            detections = []

            for result in results:
                if not hasattr(result, 'boxes'): continue
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
        except Exception as e:
            print(f"[!] Detection error: {e}")
            return []