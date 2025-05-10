import os
import datetime
import tkinter as tk
from collections import defaultdict
from config import NOTES_DIR


class WeekActivityWindow:
    def __init__(self, root, bg_color, fg_color):
        self.bg_color = bg_color
        self.fg_color = fg_color

        self.window = tk.Toplevel(root)
        self.window.title("📅 Tygodniowa aktywność")
        self.window.geometry("420x330")
        self.window.configure(bg=bg_color)
        self.window.resizable(False, False)

        self.utworz_interfejs()
        self.wyswietl_podsumowanie()

    def utworz_interfejs(self):
        """Tworzy elementy graficzne okna."""
        tytul = tk.Label(self.window,
                         text="📅 Twoja aktywność w tym tygodniu",
                         font=("Helvetica", 13, "bold"),
                         bg=self.bg_color,
                         fg=self.fg_color)
        tytul.pack(pady=10)

        self.text_box = tk.Text(
            self.window,
            wrap="word",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Helvetica", 10),
            height=14,
            width=48,
            borderwidth=0
        )
        self.text_box.pack(padx=10, pady=5)

    def wyswietl_podsumowanie(self):
        """Generuje i wyświetla tygodniowe statystyki."""
        tekst = self.generuj_podsumowanie()
        self.text_box.insert("1.0", tekst)
        self.text_box.config(state="disabled")

    def generuj_podsumowanie(self):
        """Zwraca sformatowany tekst z aktywnością tygodniową."""
        today = datetime.date.today()
        start_tygodnia = today - datetime.timedelta(days=today.weekday())

        daty_tygodnia = [
            (start_tygodnia + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(7)
        ]
        dni_tygodnia = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]

        aktywnosc = defaultdict(int)

        # Przeskanuj pliki notatek
        if os.path.exists(NOTES_DIR):
            for plik in os.listdir(NOTES_DIR):
                if plik.endswith(".txt"):
                    try:
                        sciezka = os.path.join(NOTES_DIR, plik)
                        modyfikacja = datetime.date.fromtimestamp(os.path.getmtime(sciezka)).strftime("%Y-%m-%d")
                        if modyfikacja in daty_tygodnia:
                            aktywnosc[modyfikacja] += 1
                    except:
                        continue

        linie = []
        for i, data in enumerate(daty_tygodnia):
            liczba = aktywnosc[data]
            linie.append(f"📌 {dni_tygodnia[i]} ({data}): {liczba} notatek")

        suma = sum(aktywnosc.values())
        srednia = suma / 7

        linie.append("\n📊 Średnia dzienna liczba notatek: {:.2f}".format(srednia))
        linie.append("✅ Regularność: {}".format("Dobra" if srednia >= 1 else "Niska"))

        return "\n".join(linie)
