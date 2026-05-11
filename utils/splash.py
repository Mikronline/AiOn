import os
import tkinter as tk
import datetime
from config import CALENDAR_DIR, NOTES_DIR


def show_welcome_tip(root, bg_color, fg_color, font, font_size):
    """Wyświetla okno z podpowiedzią dnia na podstawie kalendarza i notatek."""
    today = datetime.date.today()
    messages = []

    # Sprawdź wydarzenia z kalendarza
    if os.path.exists(CALENDAR_DIR):
        for file in os.listdir(CALENDAR_DIR):
            if file.endswith(".txt"):
                try:
                    date_str = file.replace(".txt", "")
                    event_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                    if event_date == today:
                        with open(CALENDAR_DIR / file, "r", encoding="utf-8") as f:
                            content = f.read().strip()
                        if content:
                            messages.append(f"📅 Dziś: {content[:80]}{'...' if len(content) > 80 else ''}")
                except:
                    continue

    # Sprawdź ważne słowa w notatkach
    keywords = ["jutro", "ważne", "zrób", "termin", "spotkanie", "przypomnij", "do zrobienia", "pilne"]
    if os.path.exists(NOTES_DIR):
        for file in os.listdir(NOTES_DIR):
            if file.endswith(".txt"):
                try:
                    with open(NOTES_DIR / file, "r", encoding="utf-8") as f:
                        content = f.read().strip().lower()
                    if any(k in content for k in keywords):
                        messages.append(f"🧠 W notatkach: {content[:80]}{'...' if len(content) > 80 else ''}")
                        break
                except:
                    continue

    if not messages:
        messages.append("🌞 Dziś dobry moment, by zaplanować coś nowego!")

    # Wyświetl popup
    tip = tk.Toplevel(root)
    tip.title("AiOn – Asystent dnia")
    tip.configure(bg=bg_color)
    tip.geometry("350x150+100+100")
    tip.attributes("-topmost", True)
    tip.resizable(False, False)

    label = tk.Label(tip, text="🔔 Codzienne przypomnienie:", font=("Helvetica", 11, "bold"),
                     bg=bg_color, fg=fg_color)
    label.pack(pady=(10, 5))

    for msg in messages:
        tk.Label(tip, text=msg, font=(font, font_size),
                 bg=bg_color, fg=fg_color, wraplength=300, justify="left").pack(anchor="w", padx=20)

    tip.after(8000, tip.destroy)
