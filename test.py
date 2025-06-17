from datetime import datetime, timedelta
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import requests
import time
import FreeSimpleGUI as sg
import json
import csv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

cmc_listing_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
cmc_info_url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info'
cmc_quote_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

def search_via_api(api_key, query, currency_choice, filepath):
    url = cmc_quote_url
    print('hi')
    parameters = {
        'symbol': query,
        'convert': currency_choice
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }
    session = Session()
    session.headers.update(headers)
    try:
        response = requests.get(url, headers=headers, params=parameters)
        data = response.json()
        if 'data' in data and query in data['data']:
            coin = data['data'][query]

            ranking = coin['cmc_rank']
            name = coin['name']
            symbol = coin['symbol']
            price = coin['quote'][currency_choice]['price']
            volume_1h = coin['quote'][currency_choice]['percent_change_1h']
            volume_24h = coin['quote'][currency_choice]['percent_change_24h']
            volume_7d = coin['quote'][currency_choice]['percent_change_7d']
            market_cap = coin['quote'][currency_choice]['market_cap']

            # Metadata
            coin_id = coin['id']
            info_response = session.get(cmc_info_url, params={'id': coin_id})
            info_response.raise_for_status()
            info_data = info_response.json()

            if 'data' not in info_data:
                logger.warning(f"No 'data' in response for coin ID {coin_id}")

            coin_info = info_data['data'].get(str(coin_id), {})

            date_added = coin_info.get('date_added', 'N/A')
            if date_added != 'N/A':
                try:
                    date_added = datetime.strptime(date_added, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")
                except ValueError:
                    date_added = 'N/A'
            description = coin_info.get('description', 'N/A')
            logo = coin_info.get('logo', 'N/A')
            website_list = coin_info.get('urls', {}).get('website', [])
            website = website_list[0] if website_list else 'N/A'
            source_code_list = coin_info.get('urls', {}).get('source_code', [])
            source_code = source_code_list[0] if source_code_list else 'N/A'
            output_tuple = (
                str(ranking),
                name,
                f"{price:,.2f}",
                f"{volume_1h:,.2f}",
                f"{volume_24h:,.2f}",
                f"{volume_7d:,.2f}",
                f"{float(market_cap):,.2f}",
                logo,
                symbol,
                description,
                date_added,
                website,
                source_code
            )
            return output_tuple
        
    except Exception as e:
        print(f"Error fetching data from API: {e}")
        return None
    
api_key = 'e28cbf9a-5c08-452e-8099-fa7f832262a3' 
print(search_via_api(api_key, 'ETH', 'USD', './data/temp.csv'))