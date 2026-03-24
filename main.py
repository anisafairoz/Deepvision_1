import cv2

import config

from detectors.weapon_detector import WeaponDetector
from detectors.person_detector import PersonDetector
from detectors.ensemble_detector import EnsembleDetector

from tracking.tracker import Tracker
from intrusion.intrusion_engine import IntrusionEngine

from alerts.alert_engine import trigger_alert
from utils.drawing_utils import draw_detections


weapon_detector = WeaponDetector()
person_detector = PersonDetector()

ensemble = EnsembleDetector(weapon_detector, person_detector)

tracker = Tracker()

intrusion_engine = IntrusionEngine()


cap = cv2.VideoCapture(config.STREAM_URL)

while True:

    ret, frame = cap.read()
    

    if not ret:
        break

    detections = ensemble.detect(frame)

    tracks = tracker.update(detections)

    intrusion_events = intrusion_engine.check_intrusion(tracks)

    for event in intrusion_events:
        trigger_alert(frame, event)

    draw_detections(frame, tracks)

    cv2.imshow("AI Surveillance System", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break


cap.release()
cv2.destroyAllWindows()