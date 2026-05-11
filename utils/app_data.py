import os

APP_NAME = "AiOn"

APP_DATA_DIR = os.path.join(
    os.getenv("APPDATA"),
    APP_NAME
)

NOTES_DIR = os.path.join(APP_DATA_DIR, "notes")
CALENDAR_DIR = os.path.join(APP_DATA_DIR, "calendar")
CONFIG_FILE = os.path.join(APP_DATA_DIR, "aion_config.json")

os.makedirs(NOTES_DIR, exist_ok=True)
os.makedirs(CALENDAR_DIR, exist_ok=True)