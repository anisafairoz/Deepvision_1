STREAM_URL = 0   
WEAPON_MODEL_PATH = "yolov8s-world.pt"
CONFIDENCE_THRESHOLD = 0.4 # Increased for better reliability
PERSON_MODEL_PATH = "yolov8n.pt"

ALERT_COOLDOWN = 10

# Real-world weapon classes for YOLO-World zero-shot detection
WEAPON_CLASSES = [
    "pistol", "handgun", "revolver", "rifle", "assault rifle", 
    "shotgun", "sniper", "knife", "machete", "sword", "dagger", 
    "grenade", "pipe bomb", "rocket launcher", "baseball bat", 
    "crowbar", "brass knuckles"
]