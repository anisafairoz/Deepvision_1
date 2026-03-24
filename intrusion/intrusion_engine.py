class IntrusionEngine:

    def check_intrusion(self, tracks):

        events = []

        for track in tracks:

            if track["class"] in ["Gun", "Knife", "Pistol", "rifle","Grenade"]:
                events.append({
                    "type": "weapon",
                    "track": track
                })

            if track["class"] == "person":
                events.append({
                    "type": "intruder",
                    "track": track
                })

        return events