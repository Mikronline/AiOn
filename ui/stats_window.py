import os
import datetime
import re
from tkinter import Toplevel, Text, END, Button
from collections import Counter
from config import NOTES_DIR


class StatsWindow(Toplevel):
    def __init__(self, master, bg_color, fg_color):
        super().__init__(master)
        self.title("📊 Statystyki")
        self.configure(bg=bg_color)
        self.geometry("650x600")

        self.bg_color = bg_color
        self.fg_color = fg_color

        self.text_widget = Text(self, wrap="word", bg=bg_color, fg=fg_color,
                                font=("Helvetica", 11), padx=10, pady=10, borderwidth=0)
        self.text_widget.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        self.refresh_button = Button(self, text="🔄 Odśwież statystyki", bg=bg_color, fg=fg_color,
                                     command=self.refresh_stats, relief="groove", font=("Helvetica", 10))
        self.refresh_button.pack(pady=(0, 10))

        self.display_stats()

    def refresh_stats(self):
        self.text_widget.delete("1.0", END)
        self.display_stats()

    def display_stats(self):
        files = [f for f in os.listdir(NOTES_DIR) if f.endswith(".txt")]
        total_notes = len(files)
        word_counts, char_counts, all_words, dates = [], [], [], []

        for filename in files:
            path = os.path.join(NOTES_DIR, filename)
            try:
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()
                    words = re.findall(r'\b\w+\b', content.lower())
                    word_counts.append(len(words))
                    char_counts.append(len(content))
                    all_words.extend(words)

                    match = re.match(r"(\d{4}-\d{2}-\d{2})", filename)
                    if match:
                        dates.append(match.group(1))
            except:
                continue

        # Analiza danych
        unique_days = set(dates)
        word_freq = Counter(all_words)
        top_words = word_freq.most_common(5)

        day_activity = Counter()
        for d in dates:
            try:
                dt = datetime.datetime.strptime(d, "%Y-%m-%d")
                day_name = dt.strftime("%A")
                day_activity[day_name] += 1
            except:
                continue

        keywords = ["ważne", "pilne", "jutro", "praca", "szkoła", "termin", "zadanie"]
        keyword_hits = {k: all_words.count(k) for k in keywords if k in all_words}

        avg_words = round(sum(word_counts) / total_notes, 1) if total_notes else 0
        avg_chars = round(sum(char_counts) / total_notes, 1) if total_notes else 0
        best_day = day_activity.most_common(1)[0][0] if day_activity else "Brak danych"

        # 📄 Podstawowe
        self.insert_title("📄 Podstawowe statystyki")
        self.insert_line(f"• Liczba notatek: {total_notes}")
        self.insert_line(f"• Średnia liczba słów: {avg_words}")
        self.insert_line(f"• Średnia liczba znaków: {avg_chars}")
        self.insert_line(f"• Unikalne dni z notatkami: {len(unique_days)}")

        # 🧠 Analiza
        self.insert_title("\n🧠 Analiza treści")
        if top_words:
            for i, (word, count) in enumerate(top_words, 1):
                self.insert_line(f"• {i}. „{word}” – {count} razy")
        else:
            self.insert_line("• Brak wystarczających danych do analizy słów.")

        if keyword_hits:
            self.insert_line("\n📌 Wykryte słowa kluczowe:")
            for k, v in keyword_hits.items():
                self.insert_line(f"   - „{k}”: {v} wystąpień")

        # 📅 Aktywność
        self.insert_title("\n📅 Aktywność tygodnia")
        self.insert_line(f"• Najaktywniejszy dzień tygodnia: {best_day}")
        for day, count in sorted(day_activity.items()):
            self.insert_line(f"   - {day}: {count} notatek")

        # 💡 Podsumowanie
        self.insert_title("\n💡 Podsumowanie")
        if total_notes == 0:
            self.insert_line("• Brak danych – zacznij pisać notatki, aby zobaczyć statystyki.")
        elif avg_words < 5:
            self.insert_line("• Twoje notatki są bardzo krótkie – może warto pisać więcej?")
        elif avg_words > 30:
            self.insert_line("• Brawo! Tworzysz bardzo treściwe notatki.")
        else:
            self.insert_line("• Notujesz w idealnych proporcjach – tak trzymaj!")

        if keyword_hits:
            self.insert_line("• Pojawiają się pilne tematy – zajrzyj do najnowszych notatek.")

    def insert_title(self, text):
        self.text_widget.insert(END, f"{text}\n", "bold")
        self.text_widget.tag_configure("bold", font=("Helvetica", 11, "bold"))

    def insert_line(self, text):
        self.text_widget.insert(END, f"{text}\n")
