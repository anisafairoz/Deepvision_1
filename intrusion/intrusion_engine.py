import config

class IntrusionEngine:

    def check_intrusion(self, tracks):

        events = []

        for track in tracks:

            if track["class"] in config.WEAPON_CLASSES:
                events.append({
                    "type": "weapon",
                    "track": track
                })

        return events