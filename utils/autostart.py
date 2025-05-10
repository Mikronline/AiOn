import os
import sys
from pathlib import Path

try:
    import win32com.client
except ImportError:
    print("[autostart] Brak modułu win32com.client – autostart niedostępny na tym systemie.")
    win32com = None

def add_to_autostart():
    if win32com is None or not hasattr(sys, "frozen"):
        return  # Tylko dla .exe i gdy win32com dostępny

    startup_folder = Path(os.getenv("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    exe_path = Path(sys.executable)
    shortcut_path = startup_folder / "AiOn.lnk"

    if shortcut_path.exists():
        return  # Skrót już istnieje

    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = str(exe_path)
        shortcut.WorkingDirectory = str(exe_path.parent)
        shortcut.IconLocation = str(exe_path)
        shortcut.save()
        print("[autostart] Dodano do autostartu.")
    except Exception as e:
        print(f"[autostart] Błąd przy dodawaniu do autostartu: {e}")
