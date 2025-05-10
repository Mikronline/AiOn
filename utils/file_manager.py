import os
from pathlib import Path


def ensure_directory(path):
    """Tworzy folder, jeśli nie istnieje."""
    os.makedirs(path, exist_ok=True)


def read_text_file(path):
    """Odczytuje zawartość pliku tekstowego."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"[Błąd odczytu pliku: {e}]"


def write_text_file(path, content):
    """Zapisuje treść do pliku tekstowego."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.strip())
        return True
    except Exception as e:
        return f"[Błąd zapisu pliku: {e}]"


def get_latest_txt_file(path):
    """Zwraca najnowszy plik .txt z folderu."""
    files = list(Path(path).glob("*.txt"))
    return max(files, key=lambda f: f.stat().st_mtime) if files else None


def list_txt_files(path):
    """Zwraca listę plików .txt z folderu."""
    return list(Path(path).glob("*.txt"))
