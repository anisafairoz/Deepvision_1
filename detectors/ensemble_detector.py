class EnsembleDetector:

    def __init__(self, weapon_detector, person_detector):

        self.weapon_detector = weapon_detector
        self.person_detector = person_detector

    def detect(self, frame):

        weapon_detections = self.weapon_detector.detect(frame)

        person_detections = self.person_detector.detect(frame)

        return weapon_detections + person_detections