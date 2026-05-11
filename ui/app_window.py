import os
import datetime
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from tkinter import messagebox, Menu, colorchooser, Toplevel, Label
import customtkinter as ctk
import threading
import time
from plyer import notification

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
from utils.font_manager import wczytaj_czcionki

class AiOnApp:
    def __init__(self, root):
        self.root = root
        self.config = wczytaj_config()

        self.bg_color = self.config.get("kolor_tla", "#000000")
        self.fg_color = self.config.get("kolor_tekstu", "#00ff00")

        self.font = self.config.get("font", "Helvetica")
        self.font_size = self.config.get("font_size", 10)

        self.setup_root_window()
        self.setup_menu()
        self.setup_main_interface()

        ukryj_plik_konfig()
        self.root.after(0, self.update_time)

        self.config["launch_count"] = self.config.get("launch_count", 0) + 1
        zapisz_config(self.config)

        if self.config.get("first_launch", True):
            self.first_time_setup()
        else:
            self.uruchom_powiadomienia_i_powitania()
        self.apply_fonts()

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

        width, height = 450, 200

        x = self.root.winfo_screenwidth() - width - 10
        y = self.root.winfo_screenheight() - height - 70

        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.awadakadavra()
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(expand=True, fill="both")

        self.button_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.button_frame.pack()

        # Układ przycisków w formie piramidy
        self.color_button = self.utworz_przycisk_na_srodku("⚙ Ustawienia", self.toggle_settings_menu, row=0, col=1, width=20, top=True)
        self.notes_button = self.utworz_przycisk("📝 Notatki dzienne", self.open_notes, 1, 0, width=16)
        self.analyzer_button = self.utworz_przycisk("📊 Analizator danych", self.open_analyzer, 1, 1, width=18)
        self.calendar_button = self.utworz_przycisk("📅 Kalendarz", self.open_calendar, 1, 2, width=16)
        self.dolny_frame = tk.Frame(self.button_frame, bg=self.bg_color)
        self.dolny_frame.grid(row=2, column=0, columnspan=3)

        self.week_button = tk.Button(self.dolny_frame, text="📅 Aktywność tyg.", command=self.open_week_activity, width=18, bg=self.bg_color, fg=self.fg_color)
        self.week_button.pack(side="left", padx=10, pady=5)

        self.zegar = ctk.CTkButton(self.dolny_frame, text="", font=(self.font, self.font_size), command=self.zegar_menu, fg_color=self.bg_color, text_color=self.fg_color, border_width=1, width=30, height=30, corner_radius=15, border_spacing=0)
        self.zegar.pack(side="left", padx=10, pady=5)

        self.stats_button = tk.Button(self.dolny_frame, text="🔍 Statystyki", command=self.open_stats, width=18, bg=self.bg_color, fg=self.fg_color)
        self.stats_button.pack(side="left", padx=10, pady=5)


        self.main_frame.bind("<Configure>", self.center_widgets)

        self.create_clock_label(self.main_frame)

    def awadakadavra(self):
        try:
            for widget in [
                self.main_frame
            ]:
                try:
                    widget.destroy()
                except:
                    pass
        except:
            pass

    def create_clock_label(self, parent):
        self.clock_label = ctk.CTkLabel(
        parent,
        text="",
        font=("Helvetica", 14, "bold"),
        text_color=self.fg_color,
        fg_color="transparent"
    )

        self.clock_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-5)

    # ---------------- STOPER ----------------

    def start_stopwatch(self):
        if self.stopwatch_running:
            return

        self.stopwatch_running = True

        def run():
            start_time = time.time() - self.stopwatch_time
            while self.stopwatch_running:
                self.stopwatch_time = time.time() - start_time
                mins, secs = divmod(int(self.stopwatch_time), 60)
                hours, mins = divmod(mins, 60)

                # WAŻNE: tkinter thread safety
                self.root.after(0, lambda:
                    self.stopwatch_label.configure(
                        text=f"{hours:02}:{mins:02}:{secs:02}"
                    )
                )

                time.sleep(1)

        threading.Thread(target=run, daemon=True).start()


    def stop_stopwatch(self):
        self.stopwatch_running = False


    def reset_stopwatch(self):
        self.stopwatch_running = False
        self.stopwatch_time = 0
        self.stopwatch_label.configure(text="00:00:00")


    # ---------------- ALARM ----------------

    def set_alarm(self):
        try:
            czas = self.alarm_entry.get()
            godzina, minuta = map(int, czas.split(":"))

            def wait_for_alarm():
                while True:
                    now = datetime.datetime.now()
                    if now.hour == godzina and now.minute == minuta:
                        notification.notify(
                            title="⏰ Alarm AiOn",
                            message="Czas minął!",
                            timeout=10
                        )
                        break
                    time.sleep(20)

            threading.Thread(target=wait_for_alarm, daemon=True).start()
            messagebox.showinfo("Alarm", "Alarm ustawiony!")

        except Exception:
            messagebox.showerror("Błąd", "Podaj czas w formacie HH:MM")
        
    def zegar_menu(self):
        self.awadakadavra()

        width, height = 450, 200
        x = self.root.winfo_screenwidth() - width - 10
        y = self.root.winfo_screenheight() - height - 70
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(expand=True, fill="both")

        self.stopwatch_running = False
        self.stopwatch_time = 0

        # --- TYTUŁ ---
        ctk.CTkLabel(
            self.main_frame,
            text="⏱️ Zegar",
            text_color=self.fg_color,
            font=(self.font, self.font_size, "bold")
        ).pack(pady=5)

        # --- GŁÓWNY UKŁAD ---
        content_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        content_frame.pack(expand=True)

        left_frame = tk.Frame(content_frame, bg=self.bg_color)
        left_frame.pack(side="left", padx=20)

        ctk.CTkLabel(
            left_frame,
            text="⏱️ Stoper",
            text_color=self.fg_color,
            font=(self.font, self.font_size, "bold")
        ).pack(pady=5)

        self.stopwatch_label = ctk.CTkLabel(
            left_frame,
            text="00:00:00",
            text_color=self.fg_color,
            font=(self.font, self.font_size)
        )
        self.stopwatch_label.pack(pady=5)

        stoper_frame = tk.Frame(left_frame, bg=self.bg_color)
        stoper_frame.pack()

        for txt, cmd in [
            ("▶", self.start_stopwatch),
            ("⏸", self.stop_stopwatch),
            ("⏹", self.reset_stopwatch),
        ]:
            ctk.CTkButton(
                stoper_frame,
                text=txt,
                width=40,
                height=30,
                command=cmd,
                fg_color=self.bg_color,
                text_color=self.fg_color,
                border_width=1,
                font=(self.font, self.font_size)
            ).pack(side="left", padx=3)

        right_frame = tk.Frame(content_frame, bg=self.bg_color)
        right_frame.pack(side="left", padx=20)

        ctk.CTkLabel(
            right_frame,
            text="⏰ Alarm",
            text_color=self.fg_color,
            font=(self.font, self.font_size, "bold")
        ).pack(pady=5)

        self.alarm_entry = ctk.CTkEntry(
            right_frame,
            width=120,
            height=28,
            fg_color=self.bg_color,
            text_color=self.fg_color,
            border_width=1,
            font=(self.font, self.font_size)
        )
        self.alarm_entry.pack(pady=5)

        ctk.CTkButton(
            right_frame,
            text="Ustaw",
            height=30,
            command=self.set_alarm,
            fg_color=self.bg_color,
            text_color=self.fg_color,
            border_width=1,
            font=(self.font, self.font_size)
        ).pack(pady=5)

        ctk.CTkButton(
            self.main_frame,
            text="⬅ Powrót",
            height=30,
            command=self.setup_main_interface,
            fg_color=self.bg_color,
            text_color=self.fg_color,
            border_width=1,
            font=(self.font, self.font_size)
        ).pack(pady=5)

        self.create_clock_label(self.main_frame)

    def utworz_przycisk(self, tekst, akcja, rzad, kolumna, width=12):
        btn = tk.Button(self.button_frame, text=tekst, command=akcja, bg=self.bg_color, fg=self.fg_color, width=width)
        btn.grid(row=rzad, column=kolumna, padx=5, pady=5)
        return btn

    def utworz_przycisk_na_srodku(self, tekst, akcja, row, col, width=16, top=False):
        btn = tk.Button(self.button_frame, text=tekst, bg=self.bg_color, fg=self.fg_color,
                        font=(self.font, self.font_size), relief="raised", width=width)
        if top:
            btn.bind("<Button-1>", akcja)
        else:
            btn.config(command=akcja)
        btn.grid(row=row, column=col, pady=(5, 10))
        return btn

    # --- Menu ustawień i kolory ---

    def setup_menu(self):
        self.color_menu = Menu(self.root, tearoff=0, bg=self.bg_color, fg=self.fg_color, activebackground=self.fg_color, activeforeground=self.bg_color, selectcolor=self.fg_color, font=(self.font, self.font_size))
        self.color_menu.add_command(label="🎨 Kolor tła", command=self.change_bg_color)
        self.color_menu.add_command(label="🔤 Kolor tekstu", command=self.change_fg_color)
        self.color_menu.add_command(label="💾 Zapisz ustawienia kolorów", command=self.save_colors)
        self.color_menu.add_separator()
        self.color_menu.add_command(label="🔡 Wybierz czcionkę", command=self.choose_font)
        self.color_menu.add_command(label="🔢 Wybierz rozmiar czcionki", command=self.choose_font_size)
        self.color_menu.add_command(label="📝 Zapisz ustawienia czcionek", command=self.save_font_settings)
        self.color_menu.add_separator()

        self.notify_var = tk.BooleanVar(value=self.config.get("notify_from_notes", True))
        self.color_menu.add_checkbutton(label="🔔 Przypomnienia z notatek",
                                        variable=self.notify_var,
                                        command=self.toggle_notify_from_notes)

        self.reopen_var = tk.BooleanVar(value=self.config.get("reopen_last_window", True))
        self.color_menu.add_checkbutton(
            label="📂 Otwieraj ostatnio używane okno przy starcie",
            variable=self.reopen_var,
            command=self.toggle_reopen_last_window)

        self.color_menu.add_separator()
        self.color_menu.add_command(label="📘 Uruchom samouczek ponownie", command=self.show_tutorial, activebackground=self.fg_color, activeforeground=self.bg_color)

        self.settings_visible = False

    def choose_font(self):
        fonts = wczytaj_czcionki()

        win = tk.Toplevel(self.root)
        win.title("Wybierz czcionkę")
        win.geometry("300x400")
        win.configure(bg=self.bg_color)

        listbox = tk.Listbox(win, font=(self.font, self.font_size))
        listbox.pack(fill="both", expand=True, padx=10, pady=10)

        for f in fonts:
            listbox.insert("end", f)

        def select(event=None):
            selected = listbox.get("active")
            if selected:
                self.font = selected
                self.config["font"] = selected
                zapisz_config(self.config)
                self.apply_fonts()
                self.update_all_fonts()
                win.destroy()

        tk.Button(win, text="Zastosuj", command=select).pack(pady=10)

    def choose_font_size(self):
        win = tk.Toplevel(self.root)
        win.title("Wybierz rozmiar czcionki")
        win.geometry("250x150")
        win.configure(bg=self.bg_color)

        tk.Label(
            win,
            text="Rozmiar czcionki:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=(self.font, self.font_size)
        ).pack(pady=10)

        size_var = tk.IntVar(value=self.font_size)

        spinbox = tk.Spinbox(
            win,
            from_=8,
            to=40,
            textvariable=size_var,
            font=(self.font, self.font_size),
            width=10
        )
        spinbox.pack(pady=10)

        def apply_size():
            self.font_size = size_var.get()
            self.apply_fonts()
            self.update_all_fonts()
            win.destroy()

        tk.Button(
                win,
                text="Zastosuj",
                command=apply_size,
                bg=self.bg_color,
                fg=self.fg_color
        ).pack(pady=10)

    def save_font_settings(self):
        self.config["font"] = self.font
        self.config["font_size"] = self.font_size

        zapisz_config(self.config)

        messagebox.showinfo(
            "Zapisano",
            "Ustawienia czcionek zostały zapisane!"
        )

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
        self.root.configure(bg=self.bg_color)
        self.main_frame.configure(bg=self.bg_color)
        self.button_frame.configure(bg=self.bg_color)
        self.dolny_frame.configure(bg=self.bg_color)
        for widget in [
            self.notes_button, self.analyzer_button, self.calendar_button,
            self.week_button, self.stats_button, self.color_button, self.color_menu, self.zegar
        ]:
            try:
                widget.configure(selectcolor=self.fg_color, activebackground=self.fg_color, activeforeground=self.bg_color, bg=self.bg_color, fg=self.fg_color)
            except:
                try:
                    widget.configure(bg=self.bg_color, fg=self.fg_color)
                except:
                    try:
                      widget.configure(fg_color=self.bg_color, text_color=self.fg_color, border_color=self.fg_color)
                    except:
                        pass

    def apply_fonts(self):
        base_font = (self.font, self.font_size)

        # tkinter global font
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family=self.font, size=self.font_size)

        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(family=self.font, size=self.font_size)

        fixed_font = tkfont.nametofont("TkFixedFont")
        fixed_font.configure(family=self.font, size=self.font_size)

        # ttk
        style = ttk.Style()
        style.configure(".", font=base_font)
        style.configure("Treeview", font=(self.font, self.font_size))

        # customtkinter
        ctk.set_appearance_mode("dark")

        self.root.option_add("*Font", (self.font, self.font_size))

    def apply_ctk_fonts(self, widget=None):
        if widget is None:
            widget = self.root

        try:
            if hasattr(widget, "configure"):
                widget.configure(font=(self.font, self.font_size))
        except:
            pass

        for child in widget.winfo_children():
            self.apply_ctk_fonts(child)

    def update_all_fonts(self, widget=None):
        for widget in [
            self.notes_button, self.analyzer_button, self.calendar_button,
            self.week_button, self.stats_button, self.color_button, self.color_menu, self.zegar
        ]:
            try:
                widget.configure(font=(self.font, self.font_size))
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

    def update_time(self):
        teraz = datetime.datetime.now().strftime("%H:%M:%S")
        try:
            self.clock_label.configure(text=teraz)
        except:
            pass
        self.root.after(1000, self.update_time)

    # --- Otwieranie okien ---

    def open_notes(self):
        open_notes_window(self.root, self.bg_color, self.fg_color, self.font, self.font_size)
        self.config["last_opened_window"] = "notes"
        zapisz_config(self.config)

    def open_analyzer(self):
        open_analyzer_window(self.root, self.bg_color, self.fg_color, self.font, self.font_size)
        self.config["last_opened_window"] = "analyzer"
        zapisz_config(self.config)

    def open_calendar(self):
        open_calendar_window(self.root, self.bg_color, self.fg_color, self.font, self.font_size)
        self.config["last_opened_window"] = "calendar"
        zapisz_config(self.config)

    def open_stats(self):
        StatsWindow(self.root, self.bg_color, self.fg_color, self.font, self.font_size)
        self.config["last_opened_window"] = "stats"
        zapisz_config(self.config)

    def open_week_activity(self):
        WeekActivityWindow(self.root, self.bg_color, self.fg_color, self.font, self.font_size)

    def show_tutorial(self):
        TutorialWindow(self.root, self.bg_color, self.fg_color, self.font, self.font_size)

    # --- Pierwsze uruchomienie ---

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
        self.root.after(5000, lambda: show_welcome_tip(self.root, self.bg_color, self.fg_color, self.font, self.font_size))

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