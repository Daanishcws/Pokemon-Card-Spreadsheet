# Pokémon Card Collection Script

This script fetches details about your Pokémon card collection from the Pokémon TCG API and updates a Google Sheet with the information. It includes card details such as type, subtype, rarity, price, and more.

## Table of Contents
- [Requirements](#requirements)
- [Setup](#setup)
- [API Setup](#api-setup)
- [Google Sheets Setup](#google-sheets-setup)
- [Google Cloud Console Setup](#google-cloud-console-setup)
- [Running the Script](#running-the-script)
- [Closing the Virtual Environment](#closing-the-virtual-environment)
- [Credits](#credits)

## Requirements

- Python 3.x
- Google Sheets API credentials
- Required Python packages: `gspread`, `oauth2client`, `requests`

## Setup

### 1. Install Python Packages

Open your terminal or command prompt and install the required packages:

```sh
pip install gspread oauth2client requests

```
## API Setup

1. Go to this website and sign up to get access to the API: https://dev.pokemontcg.io

## Google Sheets Setup

1. **Create a Google Sheet**:
   - Name it "Pokecard List".

2. **Create Sheets in the Google Sheet**:
   - **Collection**: 
     - Columns: `Card Name`, `Card Number`, `Status`
     - Input your card information here.

   - **Card Details**:
     - Columns: `Card Name`, `Set`, `Number`, `Rarity`, `Type`, `Subtype`, `Price`, `Image URL`, `Date Added`
   
   - **Statistics**:
     - Use this sheet for tracking metrics about your card collection (optional).

**Example Input in "Collection" Sheet**:

| Card Name | Card Number | Status  |
|-----------|-------------|---------|
| Pikachu   | 58/102      | Pending |
| Charizard | 4/102       | Pending |
| Bulbasaur | 44/102      | Fetched |

## Google Cloud Console Setup

1. **Create a Project**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project.

2. **Enable Google Sheets API**:
   - Go to the API library in the Google Cloud Console.
   - Search for "Google Sheets API" and enable it.

3. **Create Service Account Credentials**:
   - Go to the "Credentials" section.
   - Create a new service account.
   - Grant the service account access to the "Editor" role.
   - Create and download the JSON key file. Name it `credentials.json`.

4. **Share the Google Sheet**:
   - Share the Google Sheet with the service account email (found in the `credentials.json` file).

## Running the Script

### 1. Activate Virtual Environment

#### On macOS/Linux:

```sh
source myenv/bin/activate
```

On Windows:

```sh
myenv\Scripts\activate
```
2. Navigate to Project Directory
   
```sh
cd /path/to/your/project
```

3. Run the Script

```sh
python update_sheet.py
```
4. Script to update prices

```sh
python update_prices.py
```

## Closing the Virtual Environment
Deactivate the Virtual Environment: 
```sh
Deactivate
```

## Credits
- Google Sheets API: Google Developers
- Pokémon TCG API: Pokémon TCG Developers
- Python Packages: `gspread`, `oauth2client`, `requests`

