import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from plyer import notification

from ui.app_window import AiOnApp
from utils.tray_icon import AiOnTrayIcon
from utils.notifier import (
    sprawdz_powiadomienia_kalendarza,
    sprawdz_powiadomienia_notatek
)
from utils.autostart import add_to_autostart

ICON_PATH = os.path.join("assets", "aion.ico")

def main():
    root = tk.Tk()

    if os.name == "nt" and os.path.exists(ICON_PATH):
        root.iconbitmap(ICON_PATH)

    app = AiOnApp(root)

    tray = AiOnTrayIcon(
        root=root,
        icon_path=ICON_PATH,
        on_restore=lambda: root.deiconify(),
        on_quit=lambda: root.quit()
    )

    def hide_window():
        """Zamyka lub minimalizuje do tła w zależności od ustawień."""
        if not app.config.get("run_in_background", False):
            if messagebox.askokcancel("Zamknąć aplikację?", "Czy chcesz zakończyć działanie AiOn?"):
                root.destroy()
            return

        if root.winfo_exists():
            root.withdraw()
            tray.setup_tray()
            notification.notify(
                title="AiOn działa w tle",
                message="Kliknij ikonę w zasobniku, aby wrócić.",
                timeout=5
            )

    root.protocol("WM_DELETE_WINDOW", hide_window)

    # Powiadomienia przy starcie
    if app.config.get("notify_from_notes", True):
        root.after(2000, sprawdz_powiadomienia_kalendarza)
        root.after(3000, sprawdz_powiadomienia_notatek)

    # Autostart tylko dla .exe
    if app.config.get("run_on_startup", False):
        root.after(1000, add_to_autostart)

    root.mainloop()

if __name__ == "__main__":
    main()
