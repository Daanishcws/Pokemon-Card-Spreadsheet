import gspread
from google.oauth2.service_account import Credentials
import requests
import datetime
import logging

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
    collection_sheet = sheet.worksheet("Collection")
    card_details_sheet = sheet.worksheet("Card Details")
    try:
        search_results_sheet = sheet.worksheet("Search Results")
    except gspread.exceptions.WorksheetNotFound:
        search_results_sheet = sheet.add_worksheet(title="Search Results", rows="100", cols="12")
except Exception as e:
    logger.error(f"Error opening Google Sheets: {e}")
    raise

# Function to fetch card details from the Pokémon TCG API
def fetch_card_details(query):
    headers = {
        "X-Api-Key": "YOUR_API_KEY_HERE"  # Ensure this is your correct API key
    }
    
    try:
        api_url = f"https://api.pokemontcg.io/v2/cards?q={query}"
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data['data']:
            return data['data']
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching card details from API for query {query}: {e}")
    
    logger.warning(f"No data found for query: {query}")
    return None

# Read data from the collection sheet
try:
    collection_data = collection_sheet.get_all_records()
    logger.info(f"Headers: {collection_data[0].keys()}")
except Exception as e:
    logger.error(f"Error reading collection sheet: {e}")
    raise

# Process search status first
for row_number, row in enumerate(collection_data, start=2):  # start=2 to account for header row
    try:
        logger.info(f"Processing row {row_number}: {row}")
        status = row['Status'].lower()
        if status == 'search':
            card_name = row['Card Name'].strip()
            unique_id = row.get('Unique Identifier', '').strip()
            query = f'id:"{unique_id}"' if unique_id else f'name:"{card_name}"'
            cards = fetch_card_details(query)
            if cards:
                # Clear previous search results
                search_results_sheet.clear()
                search_results_sheet.append_row([
                    "Card Name", "Set Name", "Card Number", "Rarity", "Type", "Subtype",
                    "Average Sell Price", "Image URL", "Unique Identifier", "TCGPlayer URL"
                ])
                # Add matching cards to the temporary search results sheet
                for card_details in cards:
                    new_row = [
                        card_details.get('name', ''),
                        card_details.get('set', {}).get('name', ''),
                        card_details.get('number', ''),
                        card_details.get('rarity', ''),
                        card_details.get('types', [''])[0],
                        card_details.get('subtypes', [''])[0],
                        card_details.get('cardmarket', {}).get('prices', {}).get('averageSellPrice', ''),
                        card_details.get('images', {}).get('small', ''),
                        card_details.get('id', ''),  # Using the unique identifier
                        card_details.get('tcgplayer', {}).get('url', '')
                    ]
                    search_results_sheet.append_row(new_row)

                # Prompt user to select the correct card
                print(f"Search results for '{card_name}' are available in the 'Search Results' sheet.")
                selected_card_ids = input("Enter the unique identifiers of the cards you want to select (comma-separated): ").strip().split(',')

                for card_id in selected_card_ids:
                    card_details = next((card for card in cards if card['id'] == card_id), None)
                    if card_details:
                        new_row = [
                            card_name,
                            card_details.get('set', {}).get('name', ''),
                            card_details.get('number', ''),
                            card_details.get('rarity', ''),
                            card_details.get('types', [''])[0],
                            card_details.get('subtypes', [''])[0],
                            card_details.get('cardmarket', {}).get('prices', {}).get('averageSellPrice', ''),
                            card_details.get('images', {}).get('small', ''),
                            datetime.datetime.now().strftime("%Y-%m-%d"),
                            row['Condition'],
                            row['Location'],
                            card_details.get('id', ''),  # Using the unique identifier
                            card_details.get('tcgplayer', {}).get('url', '')
                        ]
                        card_details_sheet.append_row(new_row)
                        # Update status to fetched in the collection sheet
                        collection_sheet.update_cell(row_number, 3, 'fetched')
                        logger.info(f"Updated card details for {card_name} ({card_id})")
                    else:
                        logger.warning(f"No card details found for ID: {card_id}")

                # Clear the search results sheet after processing
                search_results_sheet.clear()
                search_results_sheet.append_row([
                    "Card Name", "Set Name", "Card Number", "Rarity", "Type", "Subtype",
                    "Average Sell Price", "Image URL", "Unique Identifier", "TCGPlayer URL"
                ])
                logger.info(f"Cleared search results for '{card_name}'")

    except Exception as e:
        logger.error(f"Error processing row {row_number}: {e}")

# Process other statuses
for row_number, row in enumerate(collection_data, start=2):  # start=2 to account for header row
    try:
        logger.info(f"Processing row {row_number}: {row}")
        status = row['Status'].lower()
        if status == 'pending':
            card_name = row['Card Name'].strip()
            card_number = row['Card Number'].strip()
            unique_id = row.get('Unique Identifier', '').strip()
            query = f'id:"{unique_id}"' if unique_id else f'name:"{card_name}" number:"{card_number}"'
            cards = fetch_card_details(query)
            if cards:
                card_details = next((card for card in cards if card['id'] == unique_id or card['number'] == card_number), None)
                if card_details:
                    new_row = [
                        card_name,
                        card_details.get('set', {}).get('name', ''),
                        card_details.get('number', ''),
                        card_details.get('rarity', ''),
                        card_details.get('types', [''])[0],
                        card_details.get('subtypes', [''])[0],
                        card_details.get('cardmarket', {}).get('prices', {}).get('averageSellPrice', ''),
                        card_details.get('images', {}).get('small', ''),
                        datetime.datetime.now().strftime("%Y-%m-%d"),
                        row['Condition'],
                        row['Location'],
                        card_details.get('id', ''),  # Using the unique identifier
                        card_details.get('tcgplayer', {}).get('url', '')
                    ]
                    card_details_sheet.append_row(new_row)
                    # Update status to fetched in the collection sheet
                    collection_sheet.update_cell(row_number, 3, 'fetched')
                    logger.info(f"Updated card details for {card_name} ({card_number})")
                else:
                    logger.warning(f"No card details found for {card_name} ({card_number}) or ID: {unique_id}")

    except Exception as e:
        logger.error(f"Error processing row {row_number}: {e}")

print("Card details updated successfully.")
