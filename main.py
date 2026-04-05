import os
import sys

if __name__ == "__main__":
    print("Launching DeepVision Unified Dashboard...")
    # Using streamlit run to boot the core UI
    os.system(f"{sys.executable} -m streamlit run app_ui.py")
