class Tracker:

    def __init__(self):
        self.next_id = 0

    def update(self, detections):

        tracks = []

        for det in detections:
            track = det.copy()

            track["id"] = self.next_id
            self.next_id += 1

            tracks.append(track)

        return tracks