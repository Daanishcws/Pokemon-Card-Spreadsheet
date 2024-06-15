"""
Author: Daanish Ali
Description: This script fetches detailed card information from the Pokémon TCG API and updates a Google Sheets document.
"""

import os
import time
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

def fetch_card_details(card_name, card_number):
    base_url = "https://api.pokemontcg.io/v2/cards"
    query = f'name:"{card_name}" number:"{card_number}"'
    headers = {'X-Api-Key': POKEMON_TCG_API_KEY}

    response = requests.get(f'{base_url}?q={query}', headers=headers)
    if response.status_code == 200:
        data = response.json().get('data', [])
        if data:
            return data[0]
        else:
            fallback_response = requests.get(f'{base_url}?q=name:"{card_name}"', headers=headers)
            if fallback_response.status_code == 200:
                return fallback_response.json().get('data', [])
    return None

def update_sheet(row, card_details):
    sheet.update_cell(row, 6, card_details.get('id', ''))
    sheet.update_cell(row, 1, card_details.get('name', ''))
    sheet.update_cell(row, 2, card_details.get('set', {}).get('name', ''))
    sheet.update_cell(row, 3, card_details.get('number', ''))
    sheet.update_cell(row, 4, card_details.get('rarity', ''))
    sheet.update_cell(row, 5, card_details.get('types', [''])[0])
    sheet.update_cell(row, 7, card_details.get('images', {}).get('small', ''))
    sheet.update_cell(row, 8, time.strftime("%Y-%m-%d"))
    sheet.update_cell(row, 9, 'Good')
    sheet.update_cell(row, 10, 'Binder 1')

def main():
    records = sheet.get_all_records()
    for i, record in enumerate(records):
        row = i + 2
        card_name = record['Card Name']
        card_number = record['Card Number']
        status = record['Status']

        if status in ('pending', 'search'):
            try:
                logger.info(f'Processing row {row}: {record}')
                card_details = fetch_card_details(card_name, card_number)
                if card_details:
                    update_sheet(row, card_details)
                    logger.info(f'Updated card details for {card_name} ({card_number})')
                else:
                    logger.warning(f'No details found for {card_name} ({card_number})')
            except Exception as e:
                logger.error(f'Error processing row {row}: {e}')
            time.sleep(1)  # Avoid hitting the API rate limit

if __name__ == '__main__':
    main()
