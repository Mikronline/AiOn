import os
import json
import datetime
from plyer import notification
from config import CALENDAR_DIR, NOTES_DIR, BASE_DIR

CACHE_PATH = BASE_DIR / "reminder_cache.json"


def sprawdz_powiadomienia_kalendarza():
    """Sprawdza wydarzenia z kalendarza na dziś i jutro."""
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)

    os.makedirs(CALENDAR_DIR, exist_ok=True)

    for file in os.listdir(CALENDAR_DIR):
        if not file.endswith(".txt"):
            continue
        try:
            date_str = file.replace(".txt", "")
            event_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            if event_date in (today, tomorrow):
                with open(CALENDAR_DIR / file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if content:
                    kiedy = "Dzisiaj" if event_date == today else "Jutro"
                    notification.notify(
                        title=f"📅 Przypomnienie ({kiedy})",
                        message=content[:100] + ("..." if len(content) > 100 else ""),
                        timeout=10
                    )
        except Exception as e:
            print(f"[notifier] Błąd przy kalendarzu: {e}")


def sprawdz_powiadomienia_notatek():
    """Analizuje dzisiejsze notatki pod kątem ważnych słów i przypomina."""
    keywords = ["jutro", "ważne", "zrób", "termin", "spotkanie", "przypomnij", "pilne"]
    today = datetime.date.today()
    os.makedirs(NOTES_DIR, exist_ok=True)

    # Wczytaj cache (unikaj ponownych powiadomień)
    cache = {}
    if CACHE_PATH.exists():
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            pass

    zmodyfikowano = False

    for file in os.listdir(NOTES_DIR):
        if not file.endswith(".txt"):
            continue

        path = NOTES_DIR / file
        mod_time = os.path.getmtime(path)
        mod_date = datetime.datetime.fromtimestamp(mod_time).date()

        if mod_date != today:
            continue
        if file in cache and cache[file] == mod_time:
            continue  # już przypomniano

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip().lower()
            if not content or len(content) < 5:
                continue

            if any(kw in content for kw in keywords):
                notification.notify(
                    title="🧠 Wykryto ważną notatkę",
                    message=content[:100] + ("..." if len(content) > 100 else ""),
                    timeout=10
                )
                cache[file] = mod_time
                zmodyfikowano = True
        except Exception as e:
            print(f"[notifier] Błąd notatek: {e}")

    if zmodyfikowano:
        try:
            with open(CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump(cache, f)
        except Exception as e:
            print(f"[notifier] Nie zapisano cache: {e}")
