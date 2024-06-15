"""
Author: Daanish Ali
Description: This script updates card prices from the Pokémon TCG API and updates a Google Sheets document.
"""

import os
import logging
import gspread
from google.oauth2.service_account import Credentials
import requests
from dotenv import load_dotenv

load_dotenv()

# Constants
GOOGLE_SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'path_to_credentials.json')
SHEET_NAME = os.getenv('SHEET_NAME', 'Pokecard List')
POKEMON_TCG_API_KEY = os.getenv('POKEMON_TCG_API_KEY', 'your_pokemon_tcg_api_key')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file(GOOGLE_SHEETS_CREDENTIALS, scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

def fetch_card_price(unique_identifier):
    base_url = f"https://api.pokemontcg.io/v2/cards/{unique_identifier}"
    headers = {'X-Api-Key': POKEMON_TCG_API_KEY}

    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        data = response.json().get('data', {})
        if data:
            return data.get('tcgplayer', {}).get('prices', {}).get('normal', {}).get('market', None)
    return None

def update_price_in_sheet(row, price):
    sheet.update_cell(row, 7, price)

def main():
    records = sheet.get_all_records()
    for i, record in enumerate(records):
        row = i + 2
        unique_identifier = record['Unique Identifier']

        if unique_identifier:
            try:
                logger.info(f'Processing row {row}: {record}')
                price = fetch_card_price(unique_identifier)
                if price is not None:
                    update_price_in_sheet(row, price)
                    logger.info(f'Updated price for card with ID {unique_identifier}')
                else:
                    logger.warning(f'No price found for card with ID {unique_identifier}')
            except Exception as e:
                logger.error(f'Error processing row {row}: {e}')
            time.sleep(1)  # Avoid hitting the API rate limit

if __name__ == '__main__':
    main()
