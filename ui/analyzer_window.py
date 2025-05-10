import os
import datetime
import random
from tkinter import (
    Toplevel, Frame, Button, messagebox,
    filedialog, scrolledtext, END, Label
)
from tkinter import ttk
from config import NOTES_DIR


def open_analyzer_window(root, bg_color, fg_color, force_reload=False):
    os.makedirs(NOTES_DIR, exist_ok=True)

    wybrane_pliki = list(filedialog.askopenfilenames(
        initialdir=NOTES_DIR,
        title="Wybierz notatki do analizy",
        filetypes=[("Pliki tekstowe", "*.txt")]
    ))

    if not wybrane_pliki:
        messagebox.showinfo("Brak danych", "Nie wybrano żadnych plików.")
        return

    okno = Toplevel(root, bg=bg_color)
    okno.title("📊 Analizator danych")
    okno.geometry("900x700")

    ścieżki = []
    ostatni_zaznaczony = {"item": None}
    dane_początkowe = []
    stan_sortowania = {"Nazwa": 0, "Data": 0, "Podsumowanie": 0}

    def pobierz_dane():
        return [tree.item(child)["values"] for child in tree.get_children()]

    def zaktualizuj_drzewo(dane):
        for dziecko in tree.get_children():
            tree.delete(dziecko)
        for wiersz in dane:
            tree.insert("", "end", values=wiersz)

    def sortuj_kolumne(kolumna):
        dane = pobierz_dane()

        for c in tree["columns"]:
            tree.heading(c, text=c)

        stan_sortowania[kolumna] = (stan_sortowania[kolumna] + 1) % 3

        if stan_sortowania[kolumna] == 0:
            zaktualizuj_drzewo(dane_początkowe)
        else:
            odwrotnie = stan_sortowania[kolumna] == 2
            indeks = tree["columns"].index(kolumna)
            if kolumna == "Data":
                dane.sort(key=lambda x: datetime.datetime.strptime(x[indeks], "%Y-%m-%d"), reverse=odwrotnie)
            else:
                dane.sort(key=lambda x: str(x[indeks]).lower(), reverse=odwrotnie)
            zaktualizuj_drzewo(dane)

        for c in tree["columns"]:
            strzałka = ""
            if stan_sortowania[c] == 1:
                strzałka = " ▲"
            elif stan_sortowania[c] == 2:
                strzałka = " ▼"
            tree.heading(c, text=c + strzałka)

    frame_przyciski = Frame(okno, bg=bg_color)
    frame_przyciski.pack(pady=10)

    tree = ttk.Treeview(okno)
    tree["columns"] = ("Nazwa", "Data", "Podsumowanie")
    tree.column("#0", width=0, stretch=False)
    tree.column("Nazwa", anchor="w", width=200)
    tree.column("Data", anchor="center", width=150)
    tree.column("Podsumowanie", anchor="w", width=500)

    for col in tree["columns"]:
        tree.heading(col, text=col, command=lambda c=col: sortuj_kolumne(c))

    tree.pack(fill="x", padx=10, pady=10)

    styl = ttk.Style()
    styl.theme_use("default")
    styl.configure("Treeview",
                   background=bg_color,
                   foreground=fg_color,
                   fieldbackground=bg_color,
                   rowheight=25)
    styl.map("Treeview", background=[("selected", fg_color)])

    pełny_tekst = scrolledtext.ScrolledText(okno, wrap="word", font=("Helvetica", 10),
                                            bg=bg_color, fg=fg_color)
    pełny_tekst.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    Button(frame_przyciski, text="📂 Dodaj notatki",
           command=lambda: dodaj_notatki(tree, ścieżki, pełny_tekst, bg_color, fg_color),
           bg=bg_color, fg=fg_color, font=("Helvetica", 10, "bold")).pack(side="left", padx=10)

    Button(frame_przyciski, text="🗑️ Usuń zaznaczoną",
           command=lambda: usuń_z_drzewa(tree, ścieżki),
           bg=bg_color, fg=fg_color, font=("Helvetica", 10, "bold")).pack(side="left", padx=10)

    Button(frame_przyciski, text="🧠 Wykryj zadania",
           command=lambda: wykryj_zadania(wybrane_pliki, bg_color, fg_color),
           bg=bg_color, fg=fg_color, font=("Helvetica", 10, "bold")).pack(side="left", padx=10)

    dodaj_do_drzewa(tree, wybrane_pliki, ścieżki)
    dane_początkowe.extend(pobierz_dane())

    def kliknięcie_drzewa(event):
        item = tree.identify_row(event.y)
        if not item:
            tree.selection_remove(tree.selection())
            pełny_tekst.delete("1.0", END)
            ostatni_zaznaczony["item"] = None
            return

        if ostatni_zaznaczony["item"] == item:
            tree.selection_remove(item)
            pełny_tekst.delete("1.0", END)
            ostatni_zaznaczony["item"] = None
        else:
            tree.selection_set(item)
            ostatni_zaznaczony["item"] = item
            index = tree.index(item)
            try:
                with open(ścieżki[index], "r", encoding="utf-8") as f:
                    pełny_tekst.delete("1.0", END)
                    pełny_tekst.insert("end", f.read())
            except Exception as e:
                pełny_tekst.delete("1.0", END)
                pełny_tekst.insert("end", f"[Błąd odczytu pliku: {e}]")

    tree.bind("<ButtonRelease-1>", kliknięcie_drzewa)


def dodaj_do_drzewa(tree, pliki, ścieżki):
    wstępy = [
        "W tym dniu zrobiłeś:", "Twoje działania obejmowały:", "Zrealizowane zadania:",
        "Notatka zawierała:", "Tego dnia zapisałeś:", "Treść tego dnia to:"
    ]

    for ścieżka in pliki:
        nazwa = os.path.basename(ścieżka)
        ścieżki.append(ścieżka)
        data = datetime.datetime.fromtimestamp(os.path.getmtime(ścieżka)).strftime("%Y-%m-%d")
        try:
            with open(ścieżka, "r", encoding="utf-8") as f:
                zawartość = f.read().strip()
        except Exception as e:
            zawartość = f"[Błąd odczytu pliku: {e}]"

        wstęp = random.choice(wstępy)
        podsumowanie = f"{wstęp} {zawartość[:80]}{'...' if len(zawartość) > 80 else ''}"
        tree.insert("", "end", values=(nazwa, data, podsumowanie))


def dodaj_notatki(tree, ścieżki, tekst, bg_color, fg_color):
    nowe = filedialog.askopenfilenames(initialdir=NOTES_DIR,
                                       title="Dodaj kolejne notatki",
                                       filetypes=[("Pliki tekstowe", "*.txt")])
    if not nowe:
        return
    unikalne = [f for f in nowe if f not in ścieżki]
    dodaj_do_drzewa(tree, unikalne, ścieżki)


def usuń_z_drzewa(tree, ścieżki):
    zaznaczone = tree.focus()
    if zaznaczone:
        indeks = tree.index(zaznaczone)
        tree.delete(zaznaczone)
        if indeks < len(ścieżki):
            del ścieżki[indeks]


def wykryj_zadania(pliki, bg_color, fg_color):
    słowa_kluczowe = ["ważne", "jutro", "do zrobienia", "spotkanie", "projekt", "termin", "egzamin", "zadanie"]
    znalezione = []

    for plik in pliki:
        try:
            with open(plik, "r", encoding="utf-8") as f:
                zawartość = f.read().lower()
                linie = zawartość.splitlines()
                for linia in linie:
                    if any(kw in linia for kw in słowa_kluczowe):
                        znalezione.append((os.path.basename(plik), linia.strip()))
        except:
            continue

    popup = Toplevel()
    popup.title("🧠 Wykryte zadania")
    popup.configure(bg=bg_color)
    popup.geometry("600x400")

    Label(popup, text="Zadania wykryte na podstawie słów kluczowych:",
          bg=bg_color, fg=fg_color, font=("Helvetica", 12, "bold")).pack(pady=10)

    if znalezione:
        pole = scrolledtext.ScrolledText(popup, wrap="word", font=("Helvetica", 10),
                                         bg=bg_color, fg=fg_color)
        pole.pack(fill="both", expand=True, padx=10, pady=10)
        for plik, linia in znalezione:
            pole.insert("end", f"📁 {plik}: {linia}\n")
    else:
        Label(popup, text="Nie wykryto żadnych zadań. ✨",
              bg=bg_color, fg=fg_color, font=("Helvetica", 11)).pack(pady=20)
