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
    # Replace 'your_credentials_file.json' with the path to your credentials file
    creds = Credentials.from_service_account_file('your_credentials_file.json', scopes=scope)
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
        # Replace 'your_api_key' with your actual API key
        "X-Api-Key": "your_api_key"
    }
    try:
        api_url = f"https://api.pokemontcg.io/v2/cards?q={query}"
        logger.info(f"Fetching card details with query: {query}")
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if 'data' in data and data['data']:
            logger.info(f"Received data for query {query}: {data['data']}")
            return data['data']
        else:
            logger.warning(f"No data in API response for query: {query}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching card details from API for query {query}: {e}")
    
    logger.warning(f"No data found for query: {query}")
    return None

# Read data from the collection sheet
try:
    collection_data = collection_sheet.get_all_records(empty2zero=False, head=1)
    logger.info(f"Headers: {collection_data[0].keys()}")
except Exception as e:
    logger.error(f"Error reading collection sheet: {e}")
    raise

# Helper function to safely strip strings
def safe_strip(value):
    return str(value).strip() if isinstance(value, str) else value

# Function to process search results
def process_search_results(card_name, cards, row_number):
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
                collection_data[row_number - 2]['Condition'],  # Adjust for zero-indexing
                collection_data[row_number - 2]['Location'],  # Adjust for zero-indexing
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

# Process search status first
for row_number, row in enumerate(collection_data, start=2):  # start=2 to account for header row
    try:
        status = safe_strip(row['Status']).lower()
        if status == 'search':
            card_name = safe_strip(row['Card Name'])
            if not card_name:
                logger.warning(f"Card name is empty for row {row_number}")
                continue
            query = f'name:"{card_name}"'
            cards = fetch_card_details(query)
            if cards:
                process_search_results(card_name, cards, row_number)
            else:
                logger.warning(f"No cards found for {card_name}")
    except Exception as e:
        logger.error(f"Error processing row {row_number}: {e}")

# Process other statuses
for row_number, row in enumerate(collection_data, start=2):  # start=2 to account for header row
    try:
        status = safe_strip(row['Status']).lower()
        if status == 'pending':
            unique_id = safe_strip(row.get('Unique Identifier', ''))
            card_name = safe_strip(row['Card Name'])
            card_number = safe_strip(row.get('Card Number', ''))
            
            if unique_id:
                query = f'id:"{unique_id}"'
                logger.info(f"Processing card with unique ID: {unique_id} in row {row_number}")
            elif card_name and card_number:
                query = f'name:"{card_name}" number:"{card_number}"'
                logger.info(f"Processing card: {card_name} {card_number} in row {row_number}")
            else:
                logger.warning(f"Card name or card number is empty for row {row_number}")
                continue

            cards = fetch_card_details(query)
            if cards:
                logger.debug(f"Found cards: {cards}")
                if unique_id:
                    card_details = next((card for card in cards if card['id'] == unique_id), None)
                else:
                    card_number_str = str(card_number)
                    card_details = next((card for card in cards if str(card['number']) == card_number_str), None)
                
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
                    logger.info(f"Updated card details for {card_name} ({unique_id if unique_id else card_number})")
                else:
                    logger.warning(f"No card details found for {card_name} ({unique_id if unique_id else card_number}) in the filtered results")
            else:
                logger.warning(f"No cards found for {card_name} ({unique_id if unique_id else card_number})")
    except Exception as e:
        logger.error(f"Error processing row {row_number}: {e}")

print("Card details updated successfully.")
