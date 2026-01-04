# RentellyWorld – Smart 'Airbnb-like' Price Predictor

**RentellyWorld** is a full-stack machine learning web application that predicts the estimated price of an Airbnb rental based on key listing features (like bedrooms, bathrooms, reviews, etc.), trained on real data from various cities around the world.

This project is designed to help *travelers* make smarter booking decisions and *hosts* ensure their listings are competitively priced.

---

## Features

- Predict rental prices in various cities (starting with Florence)  
- Smart, data-backed estimates trained on real Airbnb listings  
- Interactive and professional UI with globe/city selector and search  
- Clean separation of backend (FastAPI) and frontend (HTML/CSS/JS)  
- Currency converter support with live exchange rates (using API)
- Log-transformed regression model for higher accuracy  
- Modular and extendable for new cities or models

---

## Technologies Used

### a) Frontend
- HTML5, CSS3 (custom styling)
- JavaScript (modular, dynamic search, globe interaction)
- `globe.gl` for interactive 3D city visualization (for globe deployment on the main web page)

### b) Backend
- **FastAPI** for the REST API
- **Joblib** for model loading
- **Pandas**, **NumPy** for preprocessing
- **Scikit-learn** & **LightGBM** for ML model training
- Live exchange rate fetching from [frankfurter.app](https://www.frankfurter.app) - interactive API

---

## How It Works

1. The user selects a city or types it in the search bar.
2. User is redirected to `/predict.html?city=YourCity`.
3. A form appears where user can input features (e.g., number of beds, reviews).
4. The backend processes the input, adds derived features, and uses a trained model (e.g., for Florence) to predict the log-price (for a higher accuracy).
5. The prediction is reverse-transformed (coming back from log-price accuracy) and displayed as an estimated price (user can choose type of currency)

---

## Model Training

- Notebook: `notebooks/fixed_train_florence.ipynb` - example for Florence
- Model trained on log-transformed prices (`log_price = np.log1p(price)`)
- Final MAE (Mean Absolute Error): ~**2.66** (log scale)
- Default values for missing features are precomputed and stored in:
  - `feature_columns.json`
  - `feature_defaults.json`

---

## Project Structure

RentApp/
├── backend/
│ ├── main.py # FastAPI server
│ ├── api/models/ # ML models + metadata
│ └── scripts/ # Scripts to update prices, etc.
├── frontend/
│ ├── index.html # Landing page
│ ├── predict.html # Prediction UI
│ ├── js/ # Interactive JS (globe, search)
│ └── css/style.css # Main styling
├── notebooks/
│ └── fixed_train_florence.ipynb
├── data/
│ ├── cities.json # Metadata for cities
│ ├── average_prices.json # Cached price per city
│ └── exchange_rates.json # Cached FX data
