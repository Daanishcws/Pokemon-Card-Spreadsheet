import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import time
from datetime import datetime

# Function to fetch card data from Pokémon TCG API
def fetch_card_details(api_key, name, card_number):
    headers = {
        'X-Api-Key': api_key
    }
    number = card_number.split('/')[0].lstrip('0')  # Remove leading zeros
    query = f'name:"{name}" number:"{number}"'
    url = f'https://api.pokemontcg.io/v2/cards?q={query}'
    response = requests.get(url, headers=headers)
    return response.json().get('data', [])

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open the Google Sheet
spreadsheet = client.open("Pokecard List")

# Fetch the card names, card numbers, and statuses from the "Collection" sheet
collection_sheet = spreadsheet.worksheet("Collection")
cards = collection_sheet.get_all_records()

# Create or open the "Card Details" sheet
try:
    details_sheet = spreadsheet.worksheet("Card Details")
except gspread.exceptions.WorksheetNotFound:
    details_sheet = spreadsheet.add_worksheet(title="Card Details", rows="1000", cols="20")

# Clear existing data in the "Card Details" sheet
details_sheet.clear()

# Prepare to update the "Card Details" sheet with card details
headers = ['Unique ID', 'Card Name', 'Set', 'Number', 'Rarity', 'Type', 'Subtype', 'Price', 'Image URL', 'Date Added']
details_sheet.append_row(headers)

# Fetch and write details for each card
api_key = 'YOUR_API_KEY_HERE'  # Replace with your API key
for index, card in enumerate(cards):
    card_name = card['Card Name']
    card_number = card['Card Number']
    status = card['Status']
    error_column = len(card) + 1

    if status.lower() == "pending":
        card_details = fetch_card_details(api_key, card_name, card_number)
        if card_details:
            card_detail = card_details[0]
            name = card_detail.get('name')
            set_name = card_detail.get('set', {}).get('name')
            card_number = card_detail.get('number')
            rarity = card_detail.get('rarity')
            types = ', '.join(card_detail.get('types', []))
            subtypes = ', '.join(card_detail.get('subtypes', []))
            prices = card_detail.get('cardmarket', {}).get('prices', {}).get('averageSellPrice', 'N/A')
            image_url = card_detail.get('images', {}).get('large')
            date_added = datetime.now().strftime('%Y-%m-%d')
            unique_id = f"{name}-{set_name}-{card_number}"
            row = [unique_id, name, set_name, card_number, rarity, types, subtypes, prices, image_url, date_added]
            details_sheet.append_row(row)
            collection_sheet.update_cell(index + 2, 3, "Fetched")
            collection_sheet.update_cell(index + 2, error_column, "")
        else:
            collection_sheet.update_cell(index + 2, error_column, "Card not found")
        time.sleep(1)

print("Google Sheet updated successfully!")
