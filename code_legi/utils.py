import json
from datetime import datetime

def load_articles(json_path="data/articles_circu.json"):
    """Charge les articles depuis le fichier JSON."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def filter_articles(
    articles,
    search_all=None,
    date_debut_min=None,
    date_debut_max=None,
    sort_by=None,
    ascending=True
):
    # Filtre global sur code, titre, numéro d'article, texte
    if search_all:
        search_all = search_all.lower()
        articles = [
            a for a in articles
            if search_all in str(a.get("code", "")).lower()
            or search_all in str(a.get("titre", "")).lower()
            or search_all in str(a.get("article", "")).lower()
            or search_all in str(a.get("texte", "")).lower()
        ]

    # Filtrer par date_debut
    if date_debut_min or date_debut_max:
        filtered = []
        for a in articles:
            try:
                date_debut = datetime.strptime(a["date_debut"], "%Y-%m-%d")
                if date_debut_min and date_debut < date_debut_min:
                    continue
                if date_debut_max and date_debut > date_debut_max:
                    continue
                filtered.append(a)
            except:
                continue
        articles = filtered

    # Tri par date si demandé
    def parse_date(article, field):
        try:
            return datetime.strptime(article[field], "%Y-%m-%d")
        except Exception:
            return datetime.min if ascending else datetime.max

    if sort_by in ("date_debut", "date_fin"):
        articles.sort(key=lambda a: parse_date(a, sort_by), reverse=not ascending)

    return articles