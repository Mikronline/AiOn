import os
import datetime
import tkinter as tk
from tkinter import messagebox, Menu, colorchooser, Toplevel, Label

from config import (
    wczytaj_config, zapisz_config, ukryj_plik_konfig,
    NOTES_DIR, CALENDAR_DIR
)

from ui.notes_window import open_notes_window
from ui.analyzer_window import open_analyzer_window
from ui.calendar_window import open_calendar_window
from ui.tutorial import TutorialWindow
from ui.stats_window import StatsWindow
from ui.week_activity_window import WeekActivityWindow

from utils.notifier import sprawdz_powiadomienia_kalendarza, sprawdz_powiadomienia_notatek
from utils.splash import show_welcome_tip
from utils.welcome import show_welcome_intro
from utils.suggestions import daj_sugestie


class AiOnApp:
    def __init__(self, root):
        self.root = root
        self.config = wczytaj_config()

        self.bg_color = self.config.get("kolor_tla", "#000000")
        self.fg_color = self.config.get("kolor_tekstu", "#00ff00")

        self.setup_root_window()
        self.setup_main_interface()
        self.setup_menu()

        ukryj_plik_konfig()
        self.root.after(1000, self.update_time)

        self.config["launch_count"] = self.config.get("launch_count", 0) + 1
        zapisz_config(self.config)

        if self.config.get("first_launch", True):
            self.first_time_setup()
        else:
            self.uruchom_powiadomienia_i_powitania()

    # --- Układ głównego okna i przycisków ---

    def setup_root_window(self):
        self.root.title("AiOn")
        self.root.wm_attributes("-topmost", 1)
        self.root.minsize(220, 120)

        width, height = 450, 200
        x = self.root.winfo_screenwidth() - width - 10
        y = self.root.winfo_screenheight() - height - 70
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_main_interface(self):
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(expand=True, fill="both")

        self.button_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.button_frame.pack()

        # Układ przycisków w formie piramidy
        self.color_button = self.utworz_przycisk_na_srodku("⚙ Ustawienia", self.toggle_settings_menu, row=0, col=1, width=20, top=True)
        self.notes_button = self.utworz_przycisk("📝 Notatki dzienne", self.open_notes, 1, 0, width=16)
        self.analyzer_button = self.utworz_przycisk("📊 Analizator danych", self.open_analyzer, 1, 1, width=18)
        self.calendar_button = self.utworz_przycisk("📅 Kalendarz", self.open_calendar, 1, 2, width=16)
        dolny_frame = tk.Frame(self.button_frame, bg=self.bg_color)
        dolny_frame.grid(row=2, column=0, columnspan=3)

        self.week_button = tk.Button(dolny_frame, text="📅 Aktywność tyg.",
                                     command=self.open_week_activity, width=18,
                                     bg=self.bg_color, fg=self.fg_color)
        self.week_button.pack(side="left", padx=10, pady=5)

        self.stats_button = tk.Button(dolny_frame, text="🔍 Statystyki",
                                      command=self.open_stats, width=18,
                                      bg=self.bg_color, fg=self.fg_color)
        self.stats_button.pack(side="left", padx=10, pady=5)

        self.time_label = tk.Label(self.main_frame, font=("Helvetica", 12), bg=self.bg_color, fg=self.fg_color)
        self.time_label.pack(pady=5)

        self.main_frame.bind("<Configure>", self.center_widgets)
        self.root.bind("<Configure>", self.center_widgets)

    def utworz_przycisk(self, tekst, akcja, rzad, kolumna, width=12):
        btn = tk.Button(self.button_frame, text=tekst, command=akcja,
                        bg=self.bg_color, fg=self.fg_color, width=width)
        btn.grid(row=rzad, column=kolumna, padx=5, pady=5)
        return btn

    def utworz_przycisk_na_srodku(self, tekst, akcja, row, col, width=16, top=False):
        btn = tk.Button(self.button_frame, text=tekst, bg=self.bg_color, fg=self.fg_color,
                        font=("Helvetica", 10), relief="raised", width=width)
        if top:
            btn.bind("<Button-1>", akcja)
        else:
            btn.config(command=akcja)
        btn.grid(row=row, column=col, pady=(5, 10))
        return btn

    # --- Menu ustawień i kolory ---

    def setup_menu(self):
        self.color_menu = Menu(self.root, tearoff=0, bg=self.bg_color, fg=self.fg_color)
        self.color_menu.add_command(label="🎨 Kolor tła", command=self.change_bg_color)
        self.color_menu.add_command(label="🔤 Kolor tekstu", command=self.change_fg_color)
        self.color_menu.add_separator()
        self.color_menu.add_command(label="💾 Zapisz ustawienia kolorów", command=self.save_colors)
        self.color_menu.add_separator()

        self.notify_var = tk.BooleanVar(value=self.config.get("notify_from_notes", True))
        self.color_menu.add_checkbutton(label="🔔 Przypomnienia z notatek",
                                        variable=self.notify_var,
                                        command=self.toggle_notify_from_notes)

        self.reopen_var = tk.BooleanVar(value=self.config.get("reopen_last_window", True))
        self.color_menu.add_checkbutton(
            label="📂 Otwieraj ostatnio używane okno przy starcie",
            variable=self.reopen_var,
            command=self.toggle_reopen_last_window
        )

        self.color_menu.add_separator()
        self.color_menu.add_command(label="📘 Uruchom samouczek ponownie", command=self.show_tutorial)

        self.settings_visible = False

    def toggle_reopen_last_window(self):
        self.config["reopen_last_window"] = self.reopen_var.get()
        zapisz_config(self.config)

    def change_bg_color(self):
        kolor = colorchooser.askcolor(title="Wybierz kolor tła")[1]
        if kolor:
            self.bg_color = kolor
            self.apply_colors()

    def change_fg_color(self):
        kolor = colorchooser.askcolor(title="Wybierz kolor tekstu")[1]
        if kolor:
            self.fg_color = kolor
            self.apply_colors()

    def apply_colors(self):
        for widget in [
            self.root, self.main_frame, self.button_frame,
            self.notes_button, self.analyzer_button, self.calendar_button,
            self.week_button, self.stats_button, self.color_button, self.time_label
        ]:
            try:
                widget.configure(bg=self.bg_color, fg=self.fg_color)
            except:
                pass
        try:
            self.color_menu.configure(bg=self.bg_color, fg=self.fg_color)
        except:
            pass

    def save_colors(self):
        self.config["kolor_tla"] = self.bg_color
        self.config["kolor_tekstu"] = self.fg_color
        zapisz_config(self.config)
        messagebox.showinfo("Zapisano", "Ustawienia kolorów zostały zapisane!")

    def toggle_settings_menu(self, event):
        if self.settings_visible:
            self.color_menu.unpost()
        else:
            x = event.widget.winfo_rootx()
            y = event.widget.winfo_rooty() + event.widget.winfo_height()
            self.color_menu.post(x, y)
        self.settings_visible = not self.settings_visible

    def center_widgets(self, event=None):
        self.button_frame.place(relx=0.5, rely=0.4, anchor="center")
        self.time_label.place(relx=0.5, rely=0.8, anchor="center")

    def update_time(self):
        teraz = datetime.datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=teraz)
        self.root.after(1000, self.update_time)

    # --- Otwieranie okien ---

    def open_notes(self):
        open_notes_window(self.root, self.bg_color, self.fg_color)
        self.config["last_opened_window"] = "notes"
        zapisz_config(self.config)

    def open_analyzer(self):
        open_analyzer_window(self.root, self.bg_color, self.fg_color)
        self.config["last_opened_window"] = "analyzer"
        zapisz_config(self.config)

    def open_calendar(self):
        open_calendar_window(self.root, self.bg_color, self.fg_color)
        self.config["last_opened_window"] = "calendar"
        zapisz_config(self.config)

    def open_stats(self):
        StatsWindow(self.root, self.bg_color, self.fg_color)
        self.config["last_opened_window"] = "stats"
        zapisz_config(self.config)

    def open_week_activity(self):
        WeekActivityWindow(self.root, self.bg_color, self.fg_color)

    def show_tutorial(self):
        TutorialWindow(self.root, self.bg_color, self.fg_color)

    # --- Pierwsze uruchomienie i startowe efekty WOW ---

    def first_time_setup(self):
        self.config["run_in_background"] = messagebox.askyesno("Praca w tle", "Czy chcesz, aby AiOn działał w tle?")
        self.config["run_on_startup"] = messagebox.askyesno("Autostart", "Czy chcesz, aby AiOn uruchamiał się z systemem?")
        self.config["first_launch"] = False
        self.config["Show Tutorial"] = True
        self.config["welcome_shown"] = False

        zapisz_config(self.config)
        self.root.after(300, lambda: show_welcome_intro(self.root, self.bg_color, self.fg_color, self.show_tutorial))
        self.root.after(9000, self.pokaz_sugestie)

    def uruchom_powiadomienia_i_powitania(self):
        self.root.after(1000, sprawdz_powiadomienia_kalendarza)
        self.root.after(3000,
                        lambda: sprawdz_powiadomienia_notatek() if self.config.get("notify_from_notes", True) else None)
        self.root.after(5000, lambda: show_welcome_tip(self.root, self.bg_color, self.fg_color))

        if not self.config.get("welcome_shown", False):
            self.config["welcome_shown"] = True
            zapisz_config(self.config)
            self.root.after(7000,
                            lambda: show_welcome_intro(self.root, self.bg_color, self.fg_color, self.show_tutorial))

        if self.config.get("reopen_last_window", True):
            self.root.after(10000, self.otworz_ostatnie_okno)

    def otworz_ostatnie_okno(self):
        ostatnie = self.config.get("last_opened_window")
        if ostatnie == "notes":
            self.open_notes()
        elif ostatnie == "analyzer":
            self.open_analyzer()
        elif ostatnie == "calendar":
            self.open_calendar()
        elif ostatnie == "stats":
            self.open_stats()

    def pokaz_sugestie(self):
        sugestia = daj_sugestie()
        okno = Toplevel(self.root)
        okno.title("💡 Sugestia AiOn")
        okno.geometry("400x200")
        okno.configure(bg=self.bg_color)
        okno.attributes("-topmost", True)

        x = (okno.winfo_screenwidth() - 400) // 2
        y = (okno.winfo_screenheight() - 200) // 2
        okno.geometry(f"+{x}+{y}")

        label = Label(okno, text=sugestia, bg=self.bg_color, fg=self.fg_color,
                      font=("Helvetica", 12), wraplength=360, justify="center")
        label.pack(expand=True, pady=30)

    def toggle_notify_from_notes(self):
        self.config["notify_from_notes"] = self.notify_var.get()
        zapisz_config(self.config)
