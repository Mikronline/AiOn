import os
from utils.resource_path import resource_path

def wczytaj_czcionki():
    try:
        with open(resource_path("assets/fonts.txt"), "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return ["Helvetica", "Arial", "Calibri"]