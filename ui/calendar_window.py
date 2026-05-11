import calendar
from datetime import datetime, date
import customtkinter as ctk
from tkinter import Toplevel, Frame, Label, Text, messagebox
from config import CALENDAR_DIR
from utils.file_manager import ensure_directory, read_text_file, write_text_file


def open_calendar_window(root, bg_color, fg_color, font, font_size):

    event_cache = {}

    miesiace = {
        1: "Styczeń", 2: "Luty", 3: "Marzec", 4: "Kwiecień",
        5: "Maj", 6: "Czerwiec", 7: "Lipiec", 8: "Sierpień",
        9: "Wrzesień", 10: "Październik", 11: "Listopad", 12: "Grudzień"
    }

    miesiace_lista = list(miesiace.values())

    def load_event(filepath):
        if filepath in event_cache:
            return event_cache[filepath]

        if filepath.exists():
            content = read_text_file(filepath)
            event_cache[filepath] = content
            return content
        return ""

    def edytuj_wydarzenie(day_date):
        event_window = Toplevel(calendar_window, bg=bg_color)
        event_window.title(f"Wydarzenie: {day_date}")
        event_window.geometry("300x200")

        Label(event_window, text=f"Wydarzenie na {day_date}",
              bg=bg_color, fg=fg_color).pack(pady=5, font=(font, font_size))

        entry = Text(event_window, height=5, bg=bg_color, fg=fg_color, font=(font, font_size))
        entry.pack(padx=10, pady=10, fill="both", expand=True)
        entry.focus_set()

        ensure_directory(CALENDAR_DIR)
        filepath = CALENDAR_DIR / f"{day_date}.txt"

        entry.insert("1.0", load_event(filepath))

        def zapisz():
            content = entry.get("1.0", "end")
            result = write_text_file(filepath, content)

            if result is not True:
                messagebox.showerror("Błąd", result)
            else:
                event_cache[filepath] = content
                event_window.destroy()

        ctk.CTkButton(event_window, text="Zapisz",
               command=zapisz,
               fg_color=fg_color, text_color=bg_color, hover_color=bg_color[0]+bg_color[1]+fg_color[2]+bg_color[3]+fg_color[4]+bg_color[5]+fg_color[6], border_width=1, font=(font, font_size)).pack(pady=5)

    def update_calendar(year, month):
        for widget in calendar_frame.winfo_children():
            widget.destroy()

        dni_tygodnia = ["Pn", "Wt", "Śr", "Cz", "Pt", "Sb", "Nd"]

        ctk.CTkLabel(calendar_frame,
                     text=f"{miesiace[month]} {year}",
                     font=(font, font_size, "bold"),
                     text_color=fg_color,
                     fg_color="transparent").grid(row=0, column=0, columnspan=7, pady=5)

        for i, day in enumerate(dni_tygodnia):
            ctk.CTkLabel(calendar_frame,
                         text=day,
                         text_color=fg_color,
                         fg_color="transparent",
                         font=(font, font_size)
                         ).grid(row=1, column=i)

        cal = calendar.Calendar(firstweekday=0)

        for r, week in enumerate(cal.monthdatescalendar(year, month), start=2):
            for c, day in enumerate(week):
                if day.month == month:
                    is_today = (day == date.today())

                    ctk.CTkButton(
                        calendar_frame,
                        text=str(day.day),
                        width=35,
                        height=35,
                        fg_color=fg_color if is_today else "transparent",
                        text_color=bg_color if is_today else fg_color,
                        hover_color=bg_color[0]+bg_color[1]+fg_color[2]+bg_color[3]+fg_color[4]+bg_color[5]+fg_color[6],
                        border_width=1,
                        font=(font, font_size),
                        command=lambda d=day: edytuj_wydarzenie(d)
                    ).grid(row=r, column=c, padx=2, pady=2)

    def change_month(delta):
        nonlocal current_month, year

        current_month += delta

        while current_month > 12:
            current_month -= 12
            year += 1
        while current_month < 1:
            current_month += 12
            year -= 1

        refresh_controls()
        update_calendar(year, current_month)

    def set_month(choice):
        nonlocal current_month
        current_month = miesiace_lista.index(choice) + 1
        update_calendar(year, current_month)

    def set_year(event=None):
        nonlocal year
        try:
            year = int(year_entry.get())
            update_calendar(year, current_month)
        except ValueError:
            pass

    def refresh_controls():
        month_menu.set(miesiace[current_month])
        year_entry.delete(0, "end")
        year_entry.insert(0, str(year))

    calendar_window = Toplevel(root)
    calendar_window.title("Kalendarz")
    calendar_window.configure(bg=bg_color, bd=10)

    year = datetime.now().year
    current_month = datetime.now().month

    top_frame = Frame(calendar_window, bg=bg_color)
    top_frame.pack(pady=10)

    ctk.CTkButton(top_frame, text="<<",
           command=lambda: change_month(-12),
           fg_color=bg_color, text_color=fg_color, width=3, hover_color=bg_color[0]+bg_color[1]+fg_color[2]+bg_color[3]+fg_color[4]+bg_color[5]+fg_color[6], border_width=1, font=(font, font_size)).pack(side="left", padx=2)

    ctk.CTkButton(top_frame, text="<",
           command=lambda: change_month(-1),
           fg_color=bg_color, text_color=fg_color, width=3, hover_color=bg_color[0]+bg_color[1]+fg_color[2]+bg_color[3]+fg_color[4]+bg_color[5]+fg_color[6], border_width=1, font=(font, font_size)).pack(side="left", padx=2)

    month_menu = ctk.CTkOptionMenu(top_frame,
                                   values=miesiace_lista,
                                   command=set_month,
                                   text_color=bg_color,
                                   fg_color=fg_color,
                                   dropdown_fg_color=bg_color,
                                   dropdown_text_color=fg_color,
                                   dropdown_hover_color=bg_color[0]+bg_color[1]+fg_color[2]+bg_color[3]+fg_color[4]+bg_color[5]+fg_color[6],
                                   button_color=fg_color,
                                   button_hover_color=bg_color[0]+fg_color[1]+fg_color[2]+bg_color[3]+fg_color[4]+bg_color[5]+bg_color[6],
                                   font=(font, font_size))
    month_menu.pack(side="left", padx=5)

    year_entry = ctk.CTkEntry(top_frame, width=60, fg_color=bg_color, text_color=fg_color, border_width=1, font=(font, font_size))
    year_entry.pack(side="left", padx=5)
    year_entry.bind("<Return>", set_year)

    ctk.CTkButton(top_frame, text=">",
           command=lambda: change_month(1),
           fg_color=bg_color, text_color=fg_color, width=3, hover_color=bg_color[0]+bg_color[1]+fg_color[2]+bg_color[3]+fg_color[4]+bg_color[5]+fg_color[6], border_width=1,font=(font, font_size)).pack(side="left", padx=2)

    ctk.CTkButton(top_frame, text=">>",
           command=lambda: change_month(12),
           fg_color=bg_color, text_color=fg_color, width=3, hover_color=bg_color[0]+bg_color[1]+fg_color[2]+bg_color[3]+fg_color[4]+bg_color[5]+fg_color[6], border_width=1, font=(font, font_size)).pack(side="left", padx=2)

    calendar_frame = ctk.CTkFrame(calendar_window, fg_color=bg_color[0]+bg_color[1]+fg_color[2]+bg_color[3]+fg_color[4]+bg_color[5]+fg_color[6], border_width=1)
    calendar_frame.pack()

    refresh_controls()
    update_calendar(year, current_month)