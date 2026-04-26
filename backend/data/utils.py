import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_most_popular():
    "Obtém os 10 jogos mais populares e categorizados a partir do dataset."
    file_path = os.path.join(BASE_DIR, "50_games.json")

    if not os.path.exists(file_path):
        print("arquivo NÃO encontrado:", file_path)
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        games = json.load(f)

    # Lista com os IDs dos 10 jogos mais populares e categorizados
    games_ids = [
        "730",  # Counter-Strike 2
        "1245620",  # ELDEN RING
        "1966720",  # Lethal Company
        "578080",  # PUBG: BATTLEGROUNDS
        "1091500",  # Cyberpunk 2077
        "105600",  # Terraria
        "271590",  # Grand Theft Auto V Legacy
        "2050650",  # Resident Evil 4
        "550",  # Left 4 Dead 2
        "4000",  # Garry's Mod
    ]

    result = [game for game in games if game["id"] in games_ids]
    return result
