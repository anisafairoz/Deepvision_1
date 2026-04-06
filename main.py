import os
import sys

if __name__ == "__main__":
    print("Launching DeepVision Engine (FastAPI)...")
    # Launching the backend API
    os.system(f"{sys.executable} -m uvicorn server:app --host 0.0.0.0 --port 8000")
