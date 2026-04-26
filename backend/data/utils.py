import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_allgames():
    result = []
    file_path = os.path.join(BASE_DIR, "50_games.json")

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            result = json.load(f)
    else:
        print("arquivo NÃO encontrado:", file_path)

    return result