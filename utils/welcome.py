import tkinter as tk
import datetime

DNI_TYGODNIA = [
    "poniedziałek", "wtorek", "środa", "czwartek", "piątek", "sobota", "niedziela"
]

MIESIĄCE = [
    "stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca",
    "lipca", "sierpnia", "września", "października", "listopada", "grudnia"
]

def show_welcome_intro(root, bg_color, fg_color, on_start_callback=None):
    """Wyświetla ekran powitalny z datą i przyciskiem rozpoczęcia."""
    now = datetime.datetime.now()
    dzien_tygodnia = DNI_TYGODNIA[now.weekday()]
    dzien = now.day
    miesiac = MIESIĄCE[now.month - 1]
    rok = now.year

    tekst = (
        f"Cześć! 👋\n\n"
        f"Dzisiaj jest {dzien_tygodnia}, {dzien} {miesiac} {rok}.\n"
        f"Miło Cię widzieć w AiOn – Twoim osobistym asystencie codzienności.\n\n"
        f"Zaraz pokażemy Ci szybki samouczek. Gotowy? 🚀"
    )

    win = tk.Toplevel(root)
    win.title("Witamy w AiOn!")
    win.configure(bg=bg_color)
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()

    # Wycentrowanie
    width, height = 540, 300
    x = (win.winfo_screenwidth() - width) // 2
    y = (win.winfo_screenheight() - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

    tk.Label(win, text=tekst, bg=bg_color, fg=fg_color,
             font=("Helvetica", 12), justify="center", wraplength=500).pack(padx=20, pady=(40, 20))

    def rozpocznij():
        if on_start_callback:
            on_start_callback()
        win.destroy()

    tk.Button(win, text="🚀 Rozpocznij przygodę", command=rozpocznij,
              bg=fg_color, fg=bg_color, font=("Helvetica", 11, "bold"), width=22).pack(pady=10)

    win.protocol("WM_DELETE_WINDOW", rozpocznij)
