import os
import random
import datetime
from config import NOTES_DIR

def daj_sugestie():
    """Zwraca kontekstową sugestię na start aplikacji."""
    sugestie = [
        "🧠 Czas na notatkę dnia – krótki wpis lepszy niż żaden!",
        "📅 Sprawdź kalendarz – może o czymś zapomniałeś?",
        "📊 Zajrzyj do statystyk i sprawdź swoją regularność.",
        "🎨 Zmień kolory interfejsu – świeży wygląd, świeży umysł!",
        "🔍 Użyj wykrywania zadań, by nic nie umknęło.",
        "📘 Przypomnij sobie samouczek – zawsze dostępny w ustawieniach."
    ]

    try:
        today = datetime.date.today().strftime("%Y-%m-%d")
        if os.path.exists(NOTES_DIR):
            today_notes = [f for f in os.listdir(NOTES_DIR) if f.startswith(today)]
            if not today_notes:
                sugestie.insert(0, "✍️ Nie masz jeszcze dzisiejszej notatki. Czas coś zapisać!")
    except:
        pass

    return random.choice(sugestie)
