import os
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "activity.log")

# Create dir if needed
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log(text: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {text}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
