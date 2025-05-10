import os
import calendar
from datetime import datetime, date
from tkinter import Toplevel, Frame, Label, Button, Text, messagebox

from config import CALENDAR_DIR
from utils.file_manager import ensure_directory, read_text_file, write_text_file


def open_calendar_window(root, bg_color, fg_color):
    def edytuj_wydarzenie(day_date):
        event_window = Toplevel(calendar_window, bg=bg_color)
        event_window.title(f"Wydarzenie: {day_date}")
        event_window.geometry("300x200")

        Label(event_window, text=f"Wydarzenie na {day_date}", bg=bg_color, fg=fg_color).pack(pady=5)
        entry = Text(event_window, height=5, bg=bg_color, fg=fg_color)
        entry.pack(padx=10, pady=10, fill="both", expand=True)
        entry.focus_set()

        ensure_directory(CALENDAR_DIR)
        filepath = CALENDAR_DIR / f"{day_date}.txt"
        if filepath.exists():
            entry.insert("1.0", read_text_file(filepath))

        def zapisz():
            content = entry.get("1.0", "end")
            result = write_text_file(filepath, content)
            if result is not True:
                messagebox.showerror("Błąd", result)
            else:
                event_window.destroy()

        Button(event_window, text="Zapisz", command=zapisz,
               bg=fg_color, fg=bg_color).pack(pady=5)

    def update_calendar(year):
        for widget in calendar_frame.winfo_children():
            widget.destroy()

        miesiace = {
            1: "Styczeń", 2: "Luty", 3: "Marzec", 4: "Kwiecień",
            5: "Maj", 6: "Czerwiec", 7: "Lipiec", 8: "Sierpień",
            9: "Wrzesień", 10: "Październik", 11: "Listopad", 12: "Grudzień"
        }

        dni_tygodnia = ["Pn", "Wt", "Śr", "Cz", "Pt", "Sb", "Nd"]

        for month in range(1, 13):
            month_frame = Frame(calendar_frame, bg=bg_color, bd=2, relief="solid")
            month_frame.grid(row=(month - 1) // 3, column=(month - 1) % 3, padx=10, pady=10)

            Label(month_frame, text=miesiace[month], font=("Helvetica", 12, "bold"),
                  bg=bg_color, fg=fg_color).grid(row=0, column=0, columnspan=7, pady=(0, 5))

            for i, day in enumerate(dni_tygodnia):
                Label(month_frame, text=day, font=("Helvetica", 9, "bold"),
                      bg=bg_color, fg=fg_color, width=3).grid(row=1, column=i)

            for r, week in enumerate(calendar.Calendar(firstweekday=0).monthdatescalendar(year, month), start=2):
                for c, day in enumerate(week):
                    if day.month == month:
                        is_today = (day == date.today())
                        Button(month_frame, text=str(day.day), width=3,
                               fg=bg_color if is_today else fg_color,
                               bg=fg_color if is_today else bg_color,
                               relief="flat", borderwidth=0,
                               command=lambda d=day: edytuj_wydarzenie(d)).grid(row=r, column=c, padx=1, pady=1)

    def change_year(delta):
        nonlocal year
        year += delta
        year_label.config(text=str(year))
        update_calendar(year)

    calendar_window = Toplevel(root)
    calendar_window.title("Kalendarz")
    calendar_window.configure(bg=bg_color)

    year = datetime.now().year

    top_frame = Frame(calendar_window, bg=bg_color)
    top_frame.pack(pady=10)

    Button(top_frame, text="<<", command=lambda: change_year(-1),
           bg=bg_color, fg=fg_color, width=3).pack(side="left", padx=5)

    year_label = Label(top_frame, text=str(year), font=("Helvetica", 14, "bold"),
                       bg=bg_color, fg=fg_color)
    year_label.pack(side="left", padx=5)

    Button(top_frame, text=">>", command=lambda: change_year(1),
           bg=bg_color, fg=fg_color, width=3).pack(side="left", padx=5)

    calendar_frame = Frame(calendar_window, bg=bg_color)
    calendar_frame.pack()

    update_calendar(year)
