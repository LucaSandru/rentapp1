# update_city_scores.py

import requests, time, json
from urllib.parse import quote
from collections import defaultdict

CITIES = [
    "Paris", "Rome", "Kyoto", "Istanbul", "Barcelona",
    "Bali", "Maldives", "Santorini", "Tulum", "Maui",
    "Ibiza", "Berlin", "Miami", "Bangkok", "Rio de Janeiro",
    "Tokyo", "Bangkok", "Naples", "New Orleans", "Lisbon",
    "Cape Town", "Reykjavik", "Vienna", "Prague", "Seville"
]

CATEGORIES = {
    "Historic Wonders": ['historic', 'tourism=museum'],
    "Peaceful Escapes": ['leisure=park', 'natural=beach'],
    "Vibrant Nights": ['amenity=bar', 'amenity=nightclub', 'amenity=pub'],
    "Culinary Delights": ['amenity=restaurant', 'amenity=cafe', 'amenity=food_court'],
    "Work & Remote Life": ['amenity=coworking_space', 'amenity=cafe'],
    "Cities of Love": ['tourism=viewpoint', 'tourism=attraction', 'natural=water']
}

OUTPUT_FILE = "backend/data/top5_by_category.json"

HEADERS = {
    "User-Agent": "rent-app-city-ranker-bot"
}


def wikidata_info(city):
    q = f'''
    SELECT ?pop ?area ?coord WHERE {{
      ?c rdfs:label "{city}"@en;
         wdt:P1082 ?pop;
         wdt:P2046 ?area;
         wdt:P625 ?coord.
    }} LIMIT 1
    '''
    r = requests.get("https://query.wikidata.org/sparql",
                     headers={"Accept": "application/sparql-results+json"},
                     params={"query": q})
    d = r.json()["results"]["bindings"]
    if not d:
        return None
    b = d[0]
    return {
        "population": float(b["pop"]["value"]),
        "area_km2": float(b["area"]["value"]),
        "coord": b["coord"]["value"]
    }


def overpass_count(city, tag_expr):
    overpass = f"""
    [out:json][timeout:60];
    area["name"="{city}"]["boundary"="administrative"]->.a;
    (
      node[{tag_expr}](area.a);
      way[{tag_expr}](area.a);
      relation[{tag_expr}](area.a);
    );
    out count;
    """
    r = requests.post("https://overpass-api.de/api/interpreter", data=overpass.encode("utf-8"), headers=HEADERS)
    j = r.json()
    return j["elements"][0]["tags"]["total"] if j.get("elements") else 0


def normalize_scores(scores):
    max_val = max(scores.values()) or 1
    return {k: round((v / max_val) * 9 + 1) for k, v in scores.items()}  # Scale to 1–10


def main():
    all_scores = defaultdict(dict)

    for city in CITIES:
        print(f"\n🔍 Processing: {city}")
        wd = wikidata_info(city)
        if not wd:
            print(f"❌ Skipped {city}: no Wikidata")
            continue

        for cat, tags in CATEGORIES.items():
            total = 0
            for tag in tags:
                print(f"  - Fetching {tag}...")
                try:
                    count = overpass_count(city, tag)
                    total += int(count)
                    time.sleep(1.5)  # Be kind to Overpass
                except Exception as e:
                    print(f"    ⚠️ Failed {tag}: {e}")
            all_scores[cat][city] = total

    final_output = {}
    for cat, scores in all_scores.items():
        print(f"\n📊 Ranking: {cat}")
        norm = normalize_scores(scores)
        top5 = sorted(norm.items(), key=lambda x: x[1], reverse=True)[:5]
        final_output[cat] = [
            {"city": city, "score": score} for city, score in top5
        ]

    with open(OUTPUT_FILE, "w") as f:
        json.dump(final_output, f, indent=2)

    print(f"\n✅ Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
