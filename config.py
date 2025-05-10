import os
import json
import ctypes
import stat
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

# Główne ścieżki
BASE_DIR = Path(os.path.abspath(os.path.dirname(__file__)))
CONFIG_PATH = BASE_DIR / "aion_config.json"
CALENDAR_DIR = BASE_DIR / "calendar"
NOTES_DIR = BASE_DIR / "notes"

# Domyślne ustawienia
DEFAULT_CONFIG = {
    "kolor_tla": "#000000",
    "kolor_tekstu": "#ffffff",
    "samouczek_ukończony": False,
    "first_launch": True,
    "run_in_background": False,
    "run_on_startup": False,
    "Show Tutorial": True,
    "launch_count": 0,
    "notify_from_notes": True,
    "welcome_shown": False,
    "last_opened_window": None,
    "reopen_last_window": True
}

def ukryj_plik_konfig():
    """Ukrywa plik konfiguracyjny w systemie Windows."""
    if os.name == "nt" and CONFIG_PATH.exists():
        try:
            ctypes.windll.kernel32.SetFileAttributesW(str(CONFIG_PATH), 0x02)
        except Exception as e:
            print(f"[config.py] Nie udało się ukryć pliku: {e}")

def wczytaj_config():
    """Wczytuje plik konfiguracyjny lub tworzy nowy."""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
            for key, val in DEFAULT_CONFIG.items():
                config.setdefault(key, val)
        except json.JSONDecodeError:
            _przywroc_uszkodzony_config()
            config = DEFAULT_CONFIG.copy()
    else:
        config = DEFAULT_CONFIG.copy()
        zapisz_config(config)
    return config

def zapisz_config(config):
    """Zapisuje konfigurację do pliku."""
    try:
        if CONFIG_PATH.exists():
            os.chmod(CONFIG_PATH, stat.S_IWRITE)
            ctypes.windll.kernel32.SetFileAttributesW(str(CONFIG_PATH), 0x80)

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        ukryj_plik_konfig()
    except Exception as e:
        print(f"[config.py] Błąd zapisu konfiguracji: {e}")

def _przywroc_uszkodzony_config():
    """Przywraca domyślną konfigurację w razie błędu odczytu."""
    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning(
        "Uszkodzony plik konfiguracyjny",
        "Wykryto uszkodzony plik konfiguracyjny.\nZostał on przywrócony do wartości domyślnych."
    )
    root.destroy()
    zapisz_config(DEFAULT_CONFIG.copy())
