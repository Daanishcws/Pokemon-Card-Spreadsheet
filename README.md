# PokéCard Price Updater

This repository contains a set of Python scripts to manage and update your Pokémon card collection. The scripts use the Pokémon TCG API to fetch and update card details and prices in a Google Sheets document. This README provides detailed instructions on setting up and using the scripts.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Fetching Card Details](#fetching-card-details)
  - [Updating Card Prices](#updating-card-prices)
- [Scripts Overview](#scripts-overview)
  - [fetch_card_details.py](#fetch_card_detailspy)
  - [update_card_prices.py](#update_card_pricespy)
- [Troubleshooting](#troubleshooting)
- [Credits](#credits)

## Prerequisites

Before you begin, ensure you have met the following requirements:

- You have Python 3.x installed on your machine.
- You have a Google Cloud project with the Google Sheets API enabled.
- You have a Pokémon TCG API key. You can get one from [Pokémon TCG Developer Portal](https://dev.pokemontcg.io/dashboard).

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/pokecard-price-updater.git
cd pokecard-price-updater
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```
## Configuration

1. Google Sheets API Credentials:

- Follow the instructions on Google Cloud Platform to create a service account and download the credentials JSON file.
- Save the JSON file in the project directory and rename it to `credentials.json`.
  
2. Environment Variables:

Create a `.env` file in the project directory and add the following variables:
```bash
POKEMON_TCG_API_KEY=your_pokemon_tcg_api_key
GOOGLE_SHEETS_CREDENTIALS=credentials.json
SHEET_NAME=Pokecard List
```
## Usage
### Fetching Card Details
The `fetch_card_details.py` script fetches detailed information about cards listed in your Google Sheets document. Cards marked with the status `pending` or `search` will be processed.

To run the script:
```bash
python fetch_card_details.py
```
### Updating Card Prices
The update_card_prices.py script updates the prices of cards in your Google Sheets document. It uses unique identifiers to fetch the latest prices from the Pokémon TCG API.

To run the script:
```bash
python update_card_prices.py
```
## Scripts Overview

### fetch_card_details.py
Description
This script reads the card details from the Google Sheets document, fetches additional information from the Pokémon TCG API, and updates the sheet with the fetched details.

- Input: Google Sheets with card details (name, number, status, etc.)
- Output: Updated Google Sheets with detailed card information.
  
### update_card_prices.py
Description
This script updates the prices of cards in the Google Sheets document using their unique identifiers. It fetches the latest prices from the Pokémon TCG API and updates the sheet.

- Input: Google Sheets with card details (including unique identifiers)
- Output: Updated Google Sheets with the latest card prices.
  
## Troubleshooting
Common Issues

-Quota Exceeded:
   - If you encounter quota exceeded errors, try reducing the number of API requests by batching updates or adding delays between requests.

-Authentication Errors:
   - Ensure your credentials.json file is correctly configured and the service account has the necessary permissions to access the Google Sheets API.
   
Debugging Tips
- Use logging to trace issues. The scripts include detailed logging to help you debug any issues that arise during execution.

## Credits
- Google Sheets API: Google Developers
- Pokémon TCG API: Pokémon TCG Developers
- Python Packages: `gspread`, `oauth2client`, `requests`

## Donations
If you find this project useful and would like to support its development, [please consider donating](https://www.paypal.com/paypalme/Daanishcws). Your support is greatly appreciated!

## Detailed Instructions for Scripts
### fetch_card_details.py
Description
This script is designed to fetch detailed information about Pokémon cards listed in your Google Sheets document. Cards marked with the status `pending` or `search` will be processed and updated with the detailed card information fetched from the Pokémon TCG API.

Workflow
1. Read Data: Reads card details from the specified Google Sheets document.
2. Fetch Details: For each card marked as `pending` or `search`, it queries the Pokémon TCG API.
3. Update Sheet: Updates the Google Sheets document with the fetched details, including images, card set, rarity, and other relevant information.
   
Usage

Run the script using the following command:
```bash
python fetch_card_details.py
```
### update_card_prices.py
Description
This script updates the prices of Pokémon cards listed in your Google Sheets document. It uses unique identifiers for each card to fetch the latest prices from the Pokémon TCG API and updates the sheet accordingly.

Workflow
1. Read Data: Reads card details from the specified Google Sheets document.
2. Fetch Prices: For each card with a unique identifier, it queries the Pokémon TCG API to get the latest price information.
3. Update Prices: Updates the price column in the Google Sheets document with the fetched prices, without altering other card details.
Usage
Run the script using the following command:
```bash
python update_card_prices.py
```
## Handling API Limits
Both scripts include mechanisms to handle API rate limits and quota restrictions. If a quota limit is exceeded, the scripts will wait and retry the request after a specified delay. This ensures that the scripts can complete their tasks even when the API usage is high.

## Error Handling
The scripts are designed to log detailed error messages to help you identify and resolve issues quickly. If an error occurs, the scripts will log the error message and continue processing the remaining cards.

## Conclusion
This project aims to streamline the management of your Pokémon card collection by automating the process of fetching detailed card information and updating prices. By following the setup and usage instructions provided in this README, you should be able to efficiently manage your card collection and keep it up-to-date with the latest market prices.

For any issues or questions, feel free to open an issue on the GitHub repository or contact the project maintainers.

Happy collecting!
