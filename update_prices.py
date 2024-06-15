import gspread
from google.oauth2.service_account import Credentials
import requests
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Authenticate and connect to Google Sheets
try:
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file('pokecards-425917-d7dcaba85e3b.json', scopes=scope)
    client = gspread.authorize(creds)
except Exception as e:
    logger.error(f"Error during Google Sheets authentication: {e}")
    raise

# Open the Google Sheet
try:
    sheet = client.open("Pokecard List")
    card_details_sheet = sheet.worksheet("Card Details")
except Exception as e:
    logger.error(f"Error opening Google Sheets: {e}")
    raise

# Function to fetch card details from the Pokémon TCG API
def fetch_card_details_by_id(card_id):
    headers = {
        "X-Api-Key": "YOUR_API_KEY_HERE"  # Ensure this is your correct API key
    }
    
    try:
        api_url = f"https://api.pokemontcg.io/v2/cards/{card_id}"
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if 'data' in data:
            return data['data']
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching card details from API for ID {card_id}: {e}")
    
    logger.warning(f"No data found for ID: {card_id}")
    return None

# Read data from the card details sheet
try:
    card_details_data = card_details_sheet.get_all_records()
    logger.info(f"Headers: {card_details_data[0].keys()}")
except Exception as e:
    logger.error(f"Error reading card details sheet: {e}")
    raise

# Function to update the sheet
def update_sheet_with_retries(sheet, row_number, col, value, retries=5):
    for attempt in range(retries):
        try:
            sheet.update_cell(row_number, col, value)
            return
        except gspread.exceptions.APIError as e:
            if '429' in str(e):
                logger.warning(f"Rate limit exceeded. Retrying in 30 seconds... (Attempt {attempt + 1} of {retries})")
                time.sleep(30)
            else:
                raise e
    logger.error(f"Failed to update cell after {retries} attempts.")

# Define column indices for updating prices
price_col = 7  # Column index for the price

# Process each card in the card details sheet
for row_number, row in enumerate(card_details_data, start=2):  # start=2 to account for header row
    try:
        logger.info(f"Processing row {row_number}: {row}")
        card_id = row.get('unique identifier', '').strip() if isinstance(row.get('unique identifier', ''), str) else ''
        if card_id:
            card_details = fetch_card_details_by_id(card_id)
            if card_details:
                # Extract prices from the API response
                cardmarket_prices = card_details.get('cardmarket', {}).get('prices', {})
                tcgplayer_prices = card_details.get('tcgplayer', {}).get('prices', {})
                
                price = cardmarket_prices.get('averageSellPrice', tcgplayer_prices.get('normal', {}).get('mid', ''))

                # Update the Card Details sheet with the latest prices
                if price:
                    update_sheet_with_retries(card_details_sheet, row_number, price_col, price)
                logger.info(f"Updated price for card ID {card_id}")
            else:
                logger.warning(f"No card details found for ID: {card_id}")
        else:
            logger.warning(f"No unique identifier found for row {row_number}")

    except Exception as e:
        logger.error(f"Error processing row {row_number}: {e}")

print("Card prices updated successfully.")
