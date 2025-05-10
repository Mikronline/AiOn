import os
import glob
import datetime
from tkinter import Toplevel, Label, Button, Frame, filedialog, messagebox, scrolledtext, END
from config import NOTES_DIR


def open_notes_window(root, bg_color, fg_color):
    note_win = Toplevel(root, bg=bg_color)
    note_win.title("Notatki dzienne")
    note_win.geometry("600x500")
    note_win.minsize(500, 400)

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    os.makedirs(NOTES_DIR, exist_ok=True)

    Label(note_win, text=f"Dzisiaj: {today}", font=("Helvetica", 12),
          bg=bg_color, fg=fg_color).pack(pady=5)

    text_area = scrolledtext.ScrolledText(note_win, wrap="word",
                                          font=("Helvetica", 10),
                                          bg=bg_color, fg=fg_color)
    text_area.pack(expand=True, fill='both')
    text_area.focus_set()

    last_note_path = get_last_note_path(NOTES_DIR)
    if last_note_path:
        try:
            with open(last_note_path, 'r', encoding='utf-8') as file:
                text_area.insert(END, file.read())
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można otworzyć notatki: {e}")

    button_frame = Frame(note_win, bg=bg_color)
    button_frame.pack(pady=5)

    Button(button_frame, text="Zapisz notatkę",
           command=lambda: save_note(text_area),
           bg=bg_color, fg=fg_color).grid(row=0, column=0, padx=5)

    Button(button_frame, text="Otwórz notatkę",
           command=lambda: open_note(text_area),
           bg=bg_color, fg=fg_color).grid(row=0, column=1, padx=5)


def get_last_note_path(directory):
    txt_files = glob.glob(os.path.join(directory, "*.txt"))
    return max(txt_files, key=os.path.getmtime) if txt_files else None


def save_note(text_area):
    content = text_area.get("1.0", END).strip()
    if not content:
        messagebox.showwarning("Pusta notatka", "Nie można zapisać pustej notatki.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             initialdir=NOTES_DIR,
                                             filetypes=[("Pliki tekstowe", "*.txt")])
    if file_path:
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
        except Exception as e:
            messagebox.showerror("Błąd zapisu", f"Nie udało się zapisać notatki: {e}")


def open_note(text_area):
    file_path = filedialog.askopenfilename(initialdir=NOTES_DIR,
                                           filetypes=[("Text Files", "*.txt")])
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text_area.delete("1.0", END)
                text_area.insert("1.0", file.read())
        except Exception as e:
            messagebox.showerror("Błąd otwierania", f"Nie udało się otworzyć pliku: {e}")
