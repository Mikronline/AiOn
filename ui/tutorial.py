import os
import json
from tkinter import Toplevel, Label, Button, Frame, DoubleVar, Scale
from PIL import Image, ImageTk
from config import CONFIG_PATH, zapisz_config, ukryj_plik_konfig
from utils.resource_path import resource_path


class TutorialWindow:
    def __init__(self, root, bg_color, fg_color, font, font_size):
        self.root = root
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.font = font
        self.font_size = font_size

        self.slides = self.definiuj_slajdy()
        self.current_slide = 0

        self.okno = Toplevel(root)
        self.okno.title("AiOn – Samouczek")
        self.okno.configure(bg=bg_color)
        self.okno.resizable(True, True)
        self.okno.transient(root)
        self.okno.grab_set()
        self.center_window()

        self.okno.grid_rowconfigure(1, weight=1)
        self.okno.grid_columnconfigure(0, weight=1)

        self.slide_image_label = Label(self.okno, bg=bg_color)
        self.slide_image_label.grid(row=0, column=0, pady=20)

        self.scale_var = DoubleVar(value=1.0)
        self.scale_slider = Scale(
            self.okno, from_=0.5, to=1.5, resolution=0.1,
            orient="horizontal", label="Skaluj obrazek",
            variable=self.scale_var,
            command=lambda _: self.pokaż_slajd(self.current_slide),
            bg=bg_color, fg=fg_color,
            highlightbackground=bg_color
        )
        self.scale_slider.grid(row=1, column=0, pady=(0, 5))

        self.slide_text = Label(self.okno, text="", wraplength=700,
                                bg=bg_color, fg=fg_color, font=(font, font_size),
                                justify="center")
        self.slide_text.grid(row=1, column=0, sticky="n", pady=(10, 5))

        self.dot_frame = Frame(self.okno, bg=bg_color)
        self.dot_frame.grid(row=2, column=0, pady=(0, 5))

        self.btn_frame = Frame(self.okno, bg=bg_color)
        self.btn_frame.grid(row=3, column=0, pady=10)

        self.dots = []
        for i in range(len(self.slides)):
            dot = Label(self.dot_frame, text="●", font=(font, font_size),
                        fg=fg_color if i == 0 else "gray", bg=bg_color)
            dot.pack(side="left", padx=2)
            self.dots.append(dot)

        self.prev_btn = Button(self.btn_frame, text="◀ Poprzedni", command=self.poprzedni_slajd,
                               bg="#444", fg="white", font=(font, font_size, "bold"), width=12)
        self.prev_btn.pack(side="left", padx=10)

        self.next_btn = Button(self.btn_frame, text="Dalej ▶", command=self.następny_slajd,
                               bg="#0f0", fg="black", font=(font, font_size, "bold"), width=12)
        self.next_btn.pack(side="left", padx=10)

        self.pokaż_slajd(0)

    def definiuj_slajdy(self):
        return [
            {
                "image": "assets/img/step1.png",
                "text": "🎨 Witaj w AiOn! Dostosuj interfejs – kliknij ⚙️, by zmienić kolory lub zmienić czcionkę i ponownie uruchomić ten samouczek."
            },
            {
                "image": "assets/img/step2.png",
                "text": "📝 Notatki dzienne to miejsce na zadania, pomysły i przemyślenia. Zapisuj lub przeglądaj poprzednie wpisy."
            },
            {
                "image": "assets/img/step3.png",
                "text": "📊 Analizator danych pozwala sortować, przeszukiwać i czytać notatki. Kliknij 🧠, by wykryć ważne informacje."
            },
            {
                "image": "assets/img/step4.png",
                "text": "📅 Kalendarz roczny umożliwia szybki przegląd miesięcy. Kliknij dzień, by zapisać wydarzenie."
            },
            {
                "image": "assets/img/step5.png",
                "text": "⏰ Zapisane wydarzenia przypomną Ci o sobie, gdy nadejdzie czas – dziś lub jutro!"
            },
            {
                "image": "assets/img/step6.png",
                "text": "📆 Aktywność tygodniowa pokazuje, jak często notujesz każdego dnia tygodnia. To świetny sposób na budowanie nawyków!"
            },
            {
                "image": "assets/img/step7.png",
                "text": "🔍 Statystyki dają Ci wgląd w aktywność: liczba notatek, najczęstsze słowa, regularność i więcej!"
            },
            {
                "image": "assets/img/step8.png",
                "text": "🕛 Kliknij ikonę zegara, aby przejść do narzędzi czasu – stopera i alarmu."
            },
            {
                "image": "assets/img/step9.png",
                "text": "⏱️ Stoper umożliwia dokładne mierzenie czasu – idealny do zadań i treningów."
            },
            {
                "image": "assets/img/step10.png",
                "text": "⏰ Alarm pozwala ustawić godzinę powiadomienia, aby nie przegapić ważnych wydarzeń."
            }
        ]

    def center_window(self, width=800, height=600):
        x = (self.okno.winfo_screenwidth() - width) // 2
        y = (self.okno.winfo_screenheight() - height) // 2
        self.okno.geometry(f"{width}x{height}+{x}+{y}")

    def pokaż_slajd(self, index):
        self.current_slide = index
        slide = self.slides[index]

        try:
            img = Image.open(resource_path(slide["image"]))
            scale = self.scale_var.get()

            max_width, max_height = 500, 300
            img_ratio = img.width / img.height
            target_ratio = max_width / max_height

            if img_ratio > target_ratio:
                base_width = min(img.width, max_width)
                base_height = int(base_width / img_ratio)
            else:
                base_height = min(img.height, max_height)
                base_width = int(base_height * img_ratio)

            img = img.resize((int(base_width * scale), int(base_height * scale)), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            self.slide_image_label.configure(image=photo)
            self.slide_image_label.image = photo
            self.slide_image_label.config(text="")
        except Exception as e:
            self.slide_image_label.configure(image="", text="[Błąd ładowania obrazu]",
                                             fg=self.fg_color, bg=self.bg_color, font=(self.font, self.font_size))
            print(f"Błąd ładowania obrazu: {e}")

        self.slide_text.config(text=slide["text"])
        self.prev_btn.config(state="normal" if index > 0 else "disabled")

        if index == len(self.slides) - 1:
            self.next_btn.config(text="Zakończ", command=self.zakończ_tutorial, font=(self.font, self.font_size))
        else:
            self.next_btn.config(text="Dalej ▶", command=self.następny_slajd, font=(self.font, self.font_size))

        for i, dot in enumerate(self.dots):
            dot.config(fg=self.fg_color if i == index else "gray", font=(self.font, self.font_size))

    def następny_slajd(self):
        if self.current_slide < len(self.slides) - 1:
            self.current_slide += 1
            self.pokaż_slajd(self.current_slide)

    def poprzedni_slajd(self):
        if self.current_slide > 0:
            self.current_slide -= 1
            self.pokaż_slajd(self.current_slide)

    def zakończ_tutorial(self):
        self.okno.destroy()
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
            config["samouczek_ukonczony"] = True
            zapisz_config(config)
        except Exception as e:
            print(f"Błąd zapisu tutorialu: {e}")
        ukryj_plik_konfig()