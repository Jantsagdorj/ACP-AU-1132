import requests
import json
from datetime import datetime
import csv

class CryptoAPIClient:
    """Handles API requests to CoinGecko."""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {'x-cg-demo-api-key': self.api_key}
    
    def fetch_crypto_prices(self, coin_ids, vs_currencies='usd'):
        """Fetches cryptocurrency prices from CoinGecko API."""
        url = 'https://api.coingecko.com/api/v3/simple/price'
        params = {
            'ids': ','.join(coin_ids),
            'vs_currencies': vs_currencies
        }
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e} - {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        return None


class DataSaver:
    """Saves raw cryptocurrency data to a JSON file."""
    
    @staticmethod
    def save_raw_data(data, filename='crypto_prices.json'):
        """Saves data with a timestamp to a JSON file."""
        timestamp = datetime.now().isoformat()
        entry = {'timestamp': timestamp, 'data': data}
        
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
        print(f"Data saved to {filename}")


class CSVConverter:
    """Converts JSON data to CSV format."""
    
    @staticmethod
    def convert_json_to_csv(input_file='crypto_prices.json', output_file='crypto_prices.csv'):
        """Converts JSONL to structured CSV."""
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            
            csv_writer = csv.writer(outfile)
            csv_writer.writerow(['timestamp', 'coin', 'price_usd'])  # Header
            
            for line in infile:
                entry = json.loads(line)
                timestamp = entry['timestamp']
                data = entry['data']
                
                for coin, price_info in data.items():
                    price = price_info.get('usd', '')
                    csv_writer.writerow([timestamp, coin, price])
        
        print(f"Converted JSONL to CSV and saved as {output_file}")


if __name__ == "__main__":
    # Initialize API client
    api_client = CryptoAPIClient(api_key='CG-m3EirGq9th7mL7JNhVHTbRnA')
    
    # Fetch data
    coins = ['bitcoin', 'ethereum', 'dogecoin']
    data = api_client.fetch_crypto_prices(coins)
    
    if data:
        print("Fetched data:", data)
        DataSaver.save_raw_data(data)  # Save to JSON
        CSVConverter.convert_json_to_csv()  # Convert to CSV
    else:
        print("Failed to fetch data.")