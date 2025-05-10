import os
import threading
from PIL import Image
from pystray import Icon, Menu, MenuItem

class AiOnTrayIcon:
    def __init__(self, root, icon_path, on_restore, on_quit):
        self.root = root
        self.icon_path = icon_path
        self.on_restore = on_restore
        self.on_quit = on_quit
        self.icon = None

    def setup_tray(self):
        """Tworzy ikonę w zasobniku systemowym."""
        if not os.path.exists(self.icon_path):
            print("[TrayIcon] Ikona nie istnieje.")
            return

        if not self.root or not self.root.winfo_exists():
            print("[TrayIcon] Root GUI nie istnieje.")
            return

        try:
            image = Image.open(self.icon_path)
            menu = Menu(
                MenuItem("🔙 Pokaż AiOn", self.restore),
                MenuItem("❌ Zamknij", self.quit_app)
            )

            self.icon = Icon("AiOn", image, "AiOn działa w tle", menu)

            def run_icon():
                try:
                    self.icon.run()
                except Exception as e:
                    print(f"[TrayIcon Thread Error] {e}")

            threading.Thread(target=run_icon, daemon=True).start()
        except Exception as e:
            print(f"[Tray error] Nie udało się uruchomić tray ikony: {e}")

    def restore(self, icon=None, item=None):
        if self.root and self.root.winfo_exists():
            self.root.after(0, self._restore_ui)

    def quit_app(self, icon=None, item=None):
        try:
            if self.icon:
                self.icon.stop()
            if self.root:
                self.root.quit()
        except Exception as e:
            print(f"[Tray error] Zamknięcie aplikacji nie powiodło się: {e}")

    def _restore_ui(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
