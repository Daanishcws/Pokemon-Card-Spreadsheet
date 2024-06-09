import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import time

# Function to fetch updated price from Pokémon TCG API
def fetch_updated_price(api_key, unique_id):
    name, set_name, card_number = unique_id.split('-')
    headers = {
        'X-Api-Key': api_key
    }
    query = f'name:"{name}" set.name:"{set_name}" number:"{card_number}"'
    url = f'https://api.pokemontcg.io/v2/cards?q={query}'
    response = requests.get(url, headers=headers)
    data = response.json().get('data', [])
    if data:
        return data[0].get('cardmarket', {}).get('prices', {}).get('averageSellPrice', 'N/A')
    return 'N/A'

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open the Google Sheet
spreadsheet = client.open("Pokecard List")

# Fetch the card details from the "Card Details" sheet
details_sheet = spreadsheet.worksheet("Card Details")
cards = details_sheet.get_all_records()

# Fetch and update prices for each card
api_key = 'YOUR_API_KEY_HERE'  # Replace with your API key
for index, card in enumerate(cards):
    unique_id = card['Unique ID']
    updated_price = fetch_updated_price(api_key, unique_id)
    details_sheet.update_cell(index + 2, 8, updated_price)  # Update the price

    # Adding delay to avoid hitting the quota limit
    time.sleep(1)

print("Prices updated successfully!")
