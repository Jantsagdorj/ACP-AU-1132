# processor.py
import json
import csv

def convert_jsonl_to_csv(input_file='crypto_prices.json', output_file='data/rates.csv'):
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        
        csv_writer = csv.writer(outfile)
        csv_writer.writerow(['timestamp', 'coin', 'price_usd'])  # CSV header
        
        for line in infile:
            entry = json.loads(line)
            timestamp = entry['timestamp']
            data = entry['data']
            
            for coin, price_info in data.items():
                price = price_info.get('usd', '')
                csv_writer.writerow([timestamp, coin, price])
    
    print(f" Converted JSONL to CSV and saved as {output_file}")

if __name__ == "__main__":
    convert_jsonl_to_csv()
