from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import joblib
import numpy as np
import os
import json
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
import pandas as pd
import requests
import threading
import subprocess
import sys





def maybe_update_prices():
    def run():
        try:
            cache_path = os.path.join("data", "average_prices.json")

            # If no cache → run script
            if not os.path.exists(cache_path):
                print("📁 Cache missing. Running price generator...")
                subprocess.run([sys.executable, "backend/scripts/generate_average_prices.py"])
                print("✅ Generated prices (no cache)")
                return

            # If cache exists → check timestamp
            with open(cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)

            ts_str = cache.get("timestamp")
            if not ts_str:
                raise ValueError("Missing timestamp")

            ts = datetime.fromisoformat(ts_str)
            age = datetime.now() - ts

            if age > timedelta(hours=24):
                print(f"⏳ Cache is {age}. Updating in background...")
                subprocess.run([sys.executable, "backend/scripts/generate_average_prices.py"])
                print("✅ Generated prices (updated)")
            else:
                print(f"🟢 Cache is fresh ({age}). No need to update.")

        except Exception as e:
            print("❌ Error in background price updater:", e)

    # Run in background thread so FastAPI launches instantly
    threading.Thread(target=run, daemon=True).start()



app = FastAPI()
maybe_update_prices()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 Serve frontend folder
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))
# Serve static files (CSS, JS, images, HTML pages)
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Serve index.html on root
@app.get("/")
def read_index():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

# Serve predict.html explicitly
@app.get("/predict.html")
def serve_predict_page():
    return FileResponse(os.path.join(frontend_dir, "predict.html"))


# Get absolute base path of this file (backend/)
base_path = os.path.dirname(__file__)
model_dir = os.path.join(base_path, "api", "models")

# Load model
model_path = os.path.join(model_dir, "florence_model.pkl")
model = joblib.load(model_path)

# Load feature columns and default values
with open(os.path.join(model_dir, "feature_columns.json"), "r") as f:
    feature_columns = json.load(f)

with open(os.path.join(model_dir, "feature_defaults.json"), "r") as f:
    feature_defaults = json.load(f)

# Input model: optional user fields only
class RequiredInput(BaseModel):
    accommodates: int
    bedrooms: float
    bathrooms: float
    room_type_Private_room: Optional[int] = 0
    room_type_Entire_home_apt: Optional[int] = 0
    neighbourhood_cleansed_Centro_Storico: Optional[int] = 0
    property_type_Apartment: Optional[int] = 0

class AdvancedInput(BaseModel):
    beds: Optional[float] = None
    review_scores_rating: Optional[float] = None
    number_of_reviews: Optional[float] = None
    review_scores_cleanliness: Optional[float] = None
    review_scores_location: Optional[float] = None
    instant_bookable: Optional[int] = None
    reviews_per_month: Optional[float] = None
    amenities_count: Optional[int] = None

class CombinedInput(RequiredInput, AdvancedInput):
    pass

@app.get("/about")
def read_about():
    return FileResponse(os.path.join(frontend_dir, "about.html"))




@app.post("/predict")
def predict_price(data: CombinedInput):
    print("🎯 FastAPI validation passed. Reached predict route.")
    try:
        user_input = data.dict(exclude_unset=True)
        print("✅ Received input:", user_input)

        user_input["beds_per_person"] = user_input.get("beds", 1) / user_input.get("accommodates", 1)
        user_input["reviews_density"] = user_input.get("number_of_reviews", 1) / (user_input.get("reviews_per_month", 0.1))

        # Fill in missing features
        # Define features that are derived or required for the model
        derived_or_safe_defaults = ["beds_per_person", "reviews_density", "instant_bookable", "review_scores_rating", "number_of_reviews", "reviews_per_month", "review_scores_cleanliness", "review_scores_location", "amenities_count"]

        full_input = []

        for col in feature_columns:
            if col in user_input:
                full_input.append(user_input[col])
            elif col in derived_or_safe_defaults:
                full_input.append(feature_defaults.get(col, 0))  # Use a safe default
            else:
                full_input.append(0)  # For everything else, default to zero


        print("✅ Feature vector length:", len(full_input))
        print("✅ First 5 values:", full_input[:5])

        X = np.array([full_input])
        prediction_log = model.predict(X)[0]
        prediction = np.expm1(prediction_log)

        print("✅ Prediction result:", prediction)

        return {"estimated_price": float(round(prediction, 2))}

    except Exception as e:
        import traceback
        traceback.print_exc()
        print("❌ ERROR in /predict:", str(e))
        return {"error": str(e)}


@app.get("/top-cities")
def get_top_cities():
    with open("data/top5_by_category.json", "r") as f:
        return JSONResponse(content=json.load(f))

from fastapi.responses import JSONResponse


EXCHANGE_CACHE_FILE = "data/exchange_rates.json"
EXCHANGE_TTL_HOURS = 6

def get_exchange_rates():
    from datetime import datetime, timedelta
    import requests

    fallback_rates = {
        "ARS": 950.0,
        "CLP": 980.0,
        "TWD": 35.0
    }

    # ✅ Check cache first
    if os.path.exists(EXCHANGE_CACHE_FILE):
        with open(EXCHANGE_CACHE_FILE, "r") as f:
            cache = json.load(f)
            ts = datetime.fromisoformat(cache.get("timestamp", "2000-01-01"))
            if datetime.now() - ts < timedelta(hours=EXCHANGE_TTL_HOURS):
                print("📦 Using cached exchange rates")

                # ✅ Inject missing fallback currencies into cached rates
                merged_rates = {**fallback_rates, **cache.get("rates", {})}
                return merged_rates

    # 🔁 Fetch from API
    try:
        print("🌐 Fetching exchange rates from frankfurter.app")
        res = requests.get("https://api.frankfurter.app/latest?from=EUR", timeout=10)
        res.raise_for_status()
        data = res.json()

        rates = data.get("rates", {})
        if not isinstance(rates, dict):
            raise ValueError("Invalid rates format")

        # ✅ Inject fallback rates if not present
        for k, v in fallback_rates.items():
            if k not in rates:
                print(f"⚠️ Injecting fallback for {k}: {v}")
                rates[k] = v

        # 💾 Cache result
        with open(EXCHANGE_CACHE_FILE, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "rates": rates
            }, f)

        print("✅ Fetched and saved exchange rates")
        return rates

    except Exception as e:
        print("❌ Failed to fetch exchange rates:", e)

        # Fallback to last cache if possible
        if os.path.exists(EXCHANGE_CACHE_FILE):
            try:
                with open(EXCHANGE_CACHE_FILE, "r") as f:
                    cache = json.load(f)
                    rates = cache.get("rates", {})
                    for k, v in fallback_rates.items():
                        if k not in rates:
                            print(f"⚠️ Injecting fallback for {k} in stale cache")
                            rates[k] = v
                    return rates
            except Exception as fallback_error:
                print("❌ Stale cache is broken:", fallback_error)

        raise HTTPException(status_code=500, detail="Failed to fetch exchange rates")




@app.get("/average-prices")
def serve_cached_prices():
    import os
    import json
    from fastapi.responses import JSONResponse

    file_path = os.path.join("data", "average_prices.json")

    if not os.path.exists(file_path):
        print("❌ File missing:", file_path)
        return JSONResponse(
            content={"error": "average_prices.json not found"},
            status_code=503
        )

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        prices = data.get("prices")
        if not isinstance(prices, dict):
            raise ValueError("Missing or invalid 'prices' key in file")

        return JSONResponse(content=prices)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={"error": f"Error loading average_prices.json: {str(e)}"},
            status_code=500
        )




@app.get("/exchange-last-updated")
def exchange_last_updated():
    import os
    import json
    from datetime import datetime

    EXCHANGE_CACHE_FILE = "data/exchange_rates.json"

    if os.path.exists(EXCHANGE_CACHE_FILE):
        with open(EXCHANGE_CACHE_FILE, "r") as f:
            cache = json.load(f)
            ts = cache.get("timestamp")
            if ts:
                return {"timestamp": ts}

    return {"timestamp": None}



@app.get("/exchange-rates")
def get_exchange_rates_file():
    file_path = os.path.join("data", "exchange_rates.json")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Exchange rates file not found")

    with open(file_path, "r") as f:
        data = json.load(f)
        return JSONResponse(content=data)



'''@app.get("/{full_path:path}")
def catch_all(full_path: str):
    return FileResponse(os.path.join(frontend_dir, "index.html"))'''




