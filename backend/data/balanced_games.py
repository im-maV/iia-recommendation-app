import os, json, re, random
import ijson
from collections import defaultdict



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEST_FILE_PATH = os.path.join(BASE_DIR, "50_games.json")
SRC_FILE_PATH = os.path.join(BASE_DIR, "games.json")

# ── Vocabulário de características ────────────────────────────────────────
VALID_GENRES      = {"Survival Horror", "RPG", "Shooter",
                     "Simulation", "Survival", "Souls-like"}
VALID_PERSPECTIVES = {"First-Person", "Third Person", "2D"}
VALID_CATEGORIES  = {"Singleplayer", "Co-op", "Multiplayer"}

# ── Extração do limite inferior de estimated_owners ───────────────────────
# ex.: "2000000 - 5000000" → 2_000_000
def parse_owners(owners_str: str) -> int:
    try:
        return int(owners_str.split("-")[0].strip().replace(",", ""))
    except:
        return 0

# ── Normalização: mantém 1 valor por característica ───────────────────────
def normalize_game(game: dict, owners: int) -> dict | None:
    tags    = list(game.get("tags", []))
    genre   = next((g for g in tags if g in VALID_GENRES),       None)
    persp   = next((p for p in tags if p in VALID_PERSPECTIVES),  None)
    cat     = next((c for c in tags if c in VALID_CATEGORIES),   None)

    if not (genre and persp and cat):
        return None

    return {
        "id":          game["id"],
        "name":        game["name"],
        "genre":       genre,
        "perspective": persp,
        "category":    cat,
        "owners":      owners,          # usado para seleção, descartado depois
        "recommendations": game.get("recommendations", 0)
    }

# ── PASSO 1: filtrar games.json e salvar games_filtered.json ──────────────
def filter_games(src=SRC_FILE_PATH, dst="games_filtered.json"):
    with open(src, "r", encoding="utf-8") as f_in, \
         open(dst, "w", encoding="utf-8") as f_out:

        objects = ijson.kvitems(f_in, "")
        f_out.write("[\n")
        first = True

        for app, raw in objects:
            owners  = parse_owners(raw.get("estimated_owners", "0"))
            game    = {**raw, "id": app}
            normed  = normalize_game(game, owners)
            if not normed:
                continue

            if not first:
                f_out.write(",\n")
            first = False
            json.dump(normed, f_out, ensure_ascii=False)

        f_out.write("\n]")
    print("Filtrado salvo em", dst)

# ── PASSO 2: selecionar 50 jogos (40 populares + 10 variados) ─────────────
def build_balanced_dataset(src="games_filtered.json",
                            dst="50_games.json",
                            total=50,
                            popular_threshold=500_000):

    with open(src, encoding="utf-8") as f:
        games = json.load(f)

    print(f"Jogos válidos disponíveis: {len(games)}")

    half = int(total // 1.2)  # 40 aprox

    # ── 40 populares: ordena por owners desc, amostra por gênero ──────────
    popular = [g for g in games if g["owners"] >= popular_threshold]
    popular.sort(key=lambda x: x["owners"], reverse=True)

    # amostragem estratificada dentro dos populares
    pop_by_genre = defaultdict(list)
    for g in popular:
        pop_by_genre[g["genre"]].append(g)

    selected_popular = []
    genres = list(pop_by_genre.keys())
    per_genre = half // len(genres)

    for genre in genres:
        selected_popular.extend(pop_by_genre[genre][:per_genre])

    # completa até 25 se algum gênero tiver poucos jogos populares
    if len(selected_popular) < half:
        used_ids = {g["id"] for g in selected_popular}
        extras   = [g for g in popular if g["id"] not in used_ids]
        selected_popular.extend(extras[:half - len(selected_popular)])

    # ── 25 variados: todos os não-populares, amostragem estratificada ─────
    used_ids   = {g["id"] for g in selected_popular}
    remaining  = [g for g in games if g["id"] not in used_ids]

    rem_by_genre = defaultdict(list)
    for g in remaining:
        rem_by_genre[g["genre"]].append(g)

    selected_random = []
    for genre in rem_by_genre:
        pool = rem_by_genre[genre]
        random.shuffle(pool)
        selected_random.extend(pool[:per_genre])

    if len(selected_random) < half:
        used_ids2 = {g["id"] for g in selected_random}
        extras2   = [g for g in remaining if g["id"] not in used_ids2]
        random.shuffle(extras2)
        selected_random.extend(extras2[:half - len(selected_random)])

    # ── Combina e remove coluna auxiliar 'owners' do JSON final ───────────
    final = selected_popular[:half] + selected_random[:half]
    final = final[:total]

    for g in final:
        g.pop("owners", None)
        g.pop("recommendations", None)

    with open(dst, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    print(f"Salvos {len(final)} jogos em {dst}")
    print(f"  Populares : {len(selected_popular[:half])}")
    print(f"  Variados  : {len(selected_random[:half])}")
    return final

# ── Execução ──────────────────────────────────────────────────────────────
if os.path.exists(SRC_FILE_PATH):
    filter_games()

final_games = build_balanced_dataset(popular_threshold=500_000)

print("\nAmostra dos 5 primeiros:")
for g in final_games[:5]:
    print(g)


with open(DEST_FILE_PATH, 'w', encoding='utf-8') as f:
    l = len(final_games)
    f.write('[\n')
    for i in range(l):
        json.dump(final_games[i], f, ensure_ascii=False)
        if i != l-1:
            f.write(',\n')
    f.write('\n]')