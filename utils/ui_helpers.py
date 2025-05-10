import tkinter as tk

def apply_colors(app):
    """Nakłada aktualne kolory tła i tekstu na wszystkie widżety."""
    widgets = [
        app.root, app.main_frame, app.button_frame,
        app.notes_button, app.analyzer_button, app.calendar_button,
        app.stats_button, app.week_button, app.color_button, app.time_label
    ]

    for widget in widgets:
        try:
            widget.configure(bg=app.bg_color, fg=app.fg_color)
        except tk.TclError:
            pass

    try:
        app.color_menu.configure(bg=app.bg_color, fg=app.fg_color)
    except:
        pass

def center_widgets(app, event=None):
    """Pozycjonuje główne elementy na środku okna."""
    app.button_frame.place(relx=0.5, rely=0.4, anchor="center")
    app.time_label.place(relx=0.5, rely=0.8, anchor="center")

def toggle_settings_menu(app, event):
    """Pokazuje lub ukrywa menu ustawień po kliknięciu ⚙."""
    if app.settings_visible:
        app.color_menu.unpost()
    else:
        x = event.widget.winfo_rootx()
        y = event.widget.winfo_rooty() + event.widget.winfo_height()
        app.color_menu.post(x, y)
    app.settings_visible = not app.settings_visible
