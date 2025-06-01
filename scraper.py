# scraper.py
import requests
import json
import os

def get_currency_data():
    url = "https://api.coingecko.com/api/v3/exchange_rates"
    try:
        response = requests.get(url)
        response.raise_for_status()  # raise error if not 200
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"❌ Error fetching data: {e}")
        return None

def save_raw_data(data, filename="data/raw_rates.json"):
    os.makedirs("data", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Data saved to {filename}")

if __name__ == "__main__":
    print("📡 Fetching currency data...")
    data = get_currency_data()
    if data:
        save_raw_data(data)
