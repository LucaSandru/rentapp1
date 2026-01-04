import os
import json
import pandas as pd
from datetime import datetime
import traceback

EXCHANGE_FILE = "data/exchange_rates.json"
OUTPUT_FILE = "data/average_prices.json"
CITIES_FILE = "frontend/js/cities.json"
CSV_FOLDER = "data"

def normalize(s):
    return s.strip().lower().replace("é", "e").replace("’", "'")

def load_exchange_rates():
    if not os.path.exists(EXCHANGE_FILE):
        print("❌ Missing exchange rates file.")
        return {}
    with open(EXCHANGE_FILE, "r") as f:
        return json.load(f).get("rates", {})

def main():
    print("⚙️  Starting price generation...")

    exchange_rates = load_exchange_rates()
    if not exchange_rates:
        print("❌ No exchange rates loaded.")
        return

    with open(CITIES_FILE, "r", encoding="utf-8") as f:
        city_meta = {normalize(c["city"]): c for c in json.load(f)}

    result = {}

    for filename in os.listdir(CSV_FOLDER):
        if not filename.endswith(".csv"):
            continue

        city_id = filename.replace(".csv", "").lower()
        file_path = os.path.join(CSV_FOLDER, filename)

        try:
            print(f"📄 Processing: {city_id}")
            df = pd.read_csv(file_path)

            if "price" not in df.columns or "accommodates" not in df.columns:
                raise ValueError("Missing required columns")

            df = df.dropna(subset=["price", "accommodates"])
            df["price"] = df["price"].replace('[\$,€]', '', regex=True).str.replace(',', '', regex=False)
            df["price"] = pd.to_numeric(df["price"], errors="coerce")
            df = df.dropna(subset=["price"])
            df = df[(df["accommodates"] > 0) & (df["price"] < 80000)]

            meta = city_meta.get(normalize(city_id))
            currency = meta.get("currency", "EUR") if meta else "EUR"
            rate = exchange_rates.get(currency, 1.0)

            if currency != "EUR":
                df["price"] = df["price"] / rate

            df["price_per_person"] = df["price"] / df["accommodates"]
            mean = round(df["price_per_person"].mean(), 2)

            result[city_id] = mean
            print(f"✅ {city_id}: €{mean} per person")

        except Exception as e:
            print(f"❌ Error with {city_id}: {e}")
            traceback.print_exc()
            result[city_id] = None

    # Save result
    with open(OUTPUT_FILE, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "prices": result
        }, f)

    print(f"✅ Done. Saved {len(result)} cities → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
