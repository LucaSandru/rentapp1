import subprocess
import webbrowser
import sys
import time
import urllib.request
import json


# ✅ Step 1: Run average price generator once before server starts
try:
    print("✅ Done generating average prices.")
except Exception as e:
    print("❌ Failed to generate average prices:", e)


def wait_for_predict_ready(url, timeout=90):
    start = time.time()
    test_data = {
    "accommodates": 2,
    "bedrooms": 1,
    "bathrooms": 1,
    "price": 100,
    "room_type_Private_room": 1,
    "room_type_Entire_home_apt": 0,
    "neighbourhood_cleansed_Centro_Storico": 0,
    "property_type_Apartment": 1,
    "beds": 1,
    "number_of_reviews": 1,
    "reviews_per_month": 1
}


    while time.time() - start < timeout:
        try:
            req = urllib.request.Request(
                url + "/predict",
                data=json.dumps(test_data).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req) as res:
                if res.status == 200:
                    return True
        except Exception as e:
            print("⏳ Waiting for /predict to be ready...")
            time.sleep(1)
    return False

port = 8000
url = f"http://127.0.0.1:{port}"

# Start FastAPI server
process = subprocess.Popen([
    sys.executable, "-m", "uvicorn",
    "backend.main:app",
    "--reload",
    "--port", str(port)
])
# Wait until the /predict endpoint works
if wait_for_predict_ready(url):
    print("✅ Server is fully ready. Opening browser...")
    webbrowser.open(f"{url}/")
    print("🌐 You can now visit the app in your browser.")
else:
    print("❌ Server failed to start or /predict not ready.")
    process.kill()
    sys.exit(1)

# Wait for server process to stay alive
try:
    process.wait()
except KeyboardInterrupt:
    print("🛑 Shutting down...")
    process.kill()

print(f"⏳ Launching FastAPI...")

# Wait for /predict to be ready (model must be loaded)
def wait_for_about_ready(url, timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url + "/about") as res:
                if res.status == 200:
                    return True
        except:
            time.sleep(1)
    return False

if wait_for_predict_ready(url) and wait_for_about_ready(url):
    print("✅ Server and /about are fully ready. Opening browser...")
    webbrowser.open(f"{url}/")
else:
    print("❌ Server failed to start or /about not ready.")
