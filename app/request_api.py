from datetime import datetime, timedelta
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import requests
import time
import FreeSimpleGUI as sg
from . import score_handler as sch
from . import csv_handler as tbl
from . import keystore
import json
import csv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

cmc_listing_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
cmc_info_url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info'
cmc_quote_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
cmc_rate_limit = '10' 

cg_search_url = 'https://api.coingecko.com/api/v3/search'
cg_rate_limit = 10

def api_request(api_key, api_choice, currency_choice, progress_callback=None):
    if api_choice == '1':
        headings, data, filepath = api_request_cmc(api_key, currency_choice, progress_callback)
        return headings, data, filepath
    elif api_choice == '2':
        headings, data, filepath = api_request_cg(api_key, currency_choice, progress_callback)
        return headings, data, filepath

def classify_search_query(query):
    query = query.strip()

    if query.isdigit():
        return "rank"     # request through ranking
    elif len(query) <= 6 and query.isupper():
        return "symbol"   # request though symbol
    else:
        return "name"     # request through name

def search_cmc(api_key, search_query, currency_choice):
    # rank, symbol, name
    query_type = classify_search_query(search_query)
    print('query_type', query_type)

    if query_type == 'symbol':
        parameters = {'symbol': search_query, 'convert': currency_choice}
    elif query_type == 'name':
        parameters = {'slug': search_query, 'convert': currency_choice}
    elif query_type == 'rank':
        sg.popup_error("Search by rank isn't supported via CoinMarketCap API. Try name or symbol.")
        return []
    
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }
    session = Session()
    session.headers.update(headers)

    try:
        output = []
        response = requests.get(cmc_quote_url, headers=headers, params=parameters)
        data = response.json()
        if 'data' in data and search_query in data['data']:
            # dict of metadata
            coin = data['data'][search_query]

            ranking = coin['cmc_rank']
            name = coin['name']
            symbol = coin['symbol']
            price = f'{coin['quote'][currency_choice]['price']:,.2f}'
            volume_1h = f'{coin['quote'][currency_choice]['percent_change_1h']:,.2f}'
            volume_24h = f'{coin['quote'][currency_choice]['percent_change_24h']:,.2f}'
            volume_7d = f'{coin['quote'][currency_choice]['percent_change_7d']:,.2f}'
            market_cap = f'{coin['quote'][currency_choice]['market_cap']:,.2f}'

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

            output.append({
                '#': ranking,
                'Name': name,
                'Current Price': price,
                '1h%': volume_1h,
                '24h%': volume_24h,
                '7d%': volume_7d,
                'Market Cap': market_cap,
                'Logo': logo,
                'Symbol': symbol,
                'Description': description,
                'Creation Date': date_added,
                'Website': website,
                'Source Code': source_code
            })
            output_with_scores = sch.evaluate_cryptos(output, currency_choice)
            output_list = list(output_with_scores[0].values())
            return [output_list]
        else:
            logger.warning(f"No data found for query {search_query} in CoinMarketCap")
            return None

    except Exception as e:
        logger.error(f"Error fetching data from CoinMarketCap API: {e}")
        return None
    
def search_coingecko(api_key, search_query, currency_choice):
    cg_api_key = api_key or keystore.load_api_key('CoinGecko', 'CGKEY')
    if not cg_api_key:
        logger.error("No CoinGecko API key found")
        return None

    params = {'query': search_query, 'x_cg_demo_api_key': cg_api_key}
    try:
        output = []
        response = make_coingecko_request(cg_search_url, params)
        search_data = response.json()
        coins = search_data.get('coins', [])
        
        # Find the first coin where query matches name or symbol (case-insensitive)
        query_lower = search_query.lower()
        matching_coin = next(
            (coin for coin in coins 
             if query_lower in coin.get('name', '').lower() or query_lower in coin.get('symbol', '').lower()),
            None
        )

        if not matching_coin:
            logger.warning(f"No matching coin found for query {search_query} in CoinGecko")
            return None

        coin_id = matching_coin['id']
        cg_coin_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        coin_response = make_coingecko_request(cg_coin_url, {'x_cg_demo_api_key': cg_api_key})
        coin_data = coin_response.json()

        name = coin_data.get('name', 'N/A')
        symbol = coin_data.get('symbol', 'N/A').upper()
        price = coin_data.get('market_data', {}).get('current_price', {}).get(currency_choice.lower(), 'N/A')
        volume_1h = coin_data.get('market_data', {}).get('price_change_percentage_1h_in_currency', {}).get(currency_choice.lower(), 'N/A')
        volume_24h = coin_data.get('market_data', {}).get('price_change_percentage_24h_in_currency', {}).get(currency_choice.lower(), 'N/A')
        volume_7d = coin_data.get('market_data', {}).get('price_change_percentage_7d_in_currency', {}).get(currency_choice.lower(), 'N/A')
        market_cap = coin_data.get('market_data', {}).get('market_cap', {}).get(currency_choice.lower(), 'N/A')
        ranking = coin_data.get('market_cap_rank', 'N/A')
        logo = coin_data.get('image', {}).get('large', 'N/A')
        description = coin_data.get('description', {}).get('en', 'N/A').split('.')[0] if coin_data.get('description', {}).get('en') else 'N/A'
        homepage_links = coin_data.get('links', {}).get('homepage', [])
        website = homepage_links[0] if homepage_links and homepage_links[0] else 'N/A'
        github_links = coin_data.get('links', {}).get('repos_url', {}).get('github', [])
        source_code = github_links[0] if github_links and github_links[0] else 'N/A'
        creation_date = coin_data.get('genesis_date', 'N/A')

        output.append({
            '#': ranking,
            'Name': name,
            'Current Price': f"{price:,.2f}",
            '1h%': f"{volume_1h:,.2f}",
            '24h%': f"{volume_24h:,.2f}",
            '7d%': f"{volume_7d:,.2f}",
            'Market Cap': f"{float(market_cap):,.2f}",
            'Logo': logo,
            'Symbol': symbol,
            'Description': description,
            'Creation Date': creation_date,
            'Website': website,
            'Source Code': source_code
        })
        output_with_scores = sch.evaluate_cryptos(output, currency_choice)
        output_list = list(output_with_scores[0].values())
        return [output_list]
    except Exception as e:
        logger.error(f"Error fetching data from CoinGecko API: {e}")
        return None

def api_request_cmc(api_key, currency_choice, progress_callback=None):
    if progress_callback:
        progress_callback(1, "Initializing CoinMarketCap request...")
    
    parameters = {
        'start': '1',
        'limit': cmc_rate_limit,
        'convert': currency_choice
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }
    session = Session()
    session.headers.update(headers)

    try:
        if progress_callback:
            progress_callback(3, "Fetching cryptocurrency listings...")
        
        response = session.get(cmc_listing_url, params=parameters)
        response.raise_for_status()
        cmc_listing_data = response.json()
        cmc_coins = cmc_listing_data.get('data', [])

        output = []
        total_coins = len(cmc_coins)
        
        for idx, coin in enumerate(cmc_coins):
            if progress_callback:
                progress = 5 + int((idx / total_coins) * 50)
                progress_callback(progress, f"Fetching details for {coin['name']}...")
            
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
                continue

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
            time.sleep(1)  # Avoid rate limits

            output.append({
                '#': ranking,
                'Name': name,
                'Current Price': f"{price:,.2f}",
                '1h%': f"{volume_1h:,.2f}",
                '24h%': f"{volume_24h:,.2f}",
                '7d%': f"{volume_7d:,.2f}",
                'Market Cap': f"{float(market_cap):,.2f}",
                'Logo': logo,
                'Symbol': symbol,
                'Description': description,
                'Creation Date': date_added,
                'Website': website,
                'Source Code': source_code
            })

        if progress_callback:
            progress_callback(50, "Evaluating cryptocurrency scores...")
            
        output_with_scores = sch.evaluate_cryptos(output, currency_choice, progress_callback)
        logger.info(f'Fetched {len(output_with_scores)} coins from CoinMarketCap')
        
        if progress_callback:
            progress_callback(98, "Saving data to file...")
            
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filepath = f'app/assets/data/CMC_crypto_extended_{timestamp}.csv'

        tbl.export_to_csv(output_with_scores, filepath)
        headings, data = tbl.read_csv(filepath)
        
        if progress_callback:
            progress_callback(100, "Complete!")
            
        return headings, data, filepath

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        logger.error(f"Request failed: {e}")
        sg.popup(f"Request failed: {e}")
        return None, None, None
    except KeyError as ke:
        logger.error(f"KeyError: {ke}")
        return sg.popup(f"Response missing key: {ke}")

def make_coingecko_request(url, params, retries=3, backoff_factor=2):
    """Make a CoinGecko API request with retry logic for rate limits."""
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            if response.status_code == 429:
                wait_time = backoff_factor ** attempt
                logger.warning(f"Rate limit hit for {url}. Retrying after {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"HTTP error for {url}: {e}")
                raise
        except requests.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            raise
    raise Exception(f"Failed to fetch {url} after {retries} attempts")

def api_request_cg(api_key, currency_choice, progress_callback=None):
    if progress_callback:
        progress_callback(1, "Initializing CoinGecko request...")
        
    cg_api_key = api_key or keystore.load_api_key('CoinGecko', 'CGKEY')
    if not cg_api_key:
        logger.error("No CoinGecko API key found in settings.cfg")
        sg.popup("No CoinGecko API key found. Please save it in settings.cfg.")
        return None, None, None

    vs_currency = currency_choice.lower()
    cg_market_url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': vs_currency,
        'order': 'market_cap_desc',
        'per_page': cg_rate_limit,
        'page': 1,
        'sparkline': 'false',
        'price_change_percentage': '1h,24h,7d',
        'x_cg_demo_api_key': cg_api_key
    }

    try:
        if progress_callback:
            progress_callback(3, "Fetching cryptocurrency listings...")
            
        market_data = make_coingecko_request(cg_market_url, params).json()
        output = []
        total_coins = len(market_data)

        for idx, coin in enumerate(market_data, start=1):
            if progress_callback:
                progress = 5 + int((idx / total_coins) * 50)
                progress_callback(progress, f"Fetching details for {coin['name']}...")
                
            coin_id = coin['id']
            name = coin['name']
            symbol = coin['symbol']
            price = coin['current_price']
            market_cap = coin.get('market_cap', 'N/A')
            volume_1h = coin.get('price_change_percentage_1h_in_currency', 'N/A')
            volume_24h = coin.get('price_change_percentage_24h_in_currency', 'N/A')
            volume_7d = coin.get('price_change_percentage_7d_in_currency', 'N/A')
            logo = coin.get('image', 'N/A')

            # Detailed metadata
            cg_coin_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            cg_coin_info = make_coingecko_request(cg_coin_url, {'x_cg_demo_api_key': cg_api_key}).json()

            description = cg_coin_info.get('description', {}).get('en', '').split('.')[0] if cg_coin_info.get('description', {}).get('en') else 'N/A'
            homepage_links = cg_coin_info.get('links', {}).get('homepage', [])
            website = homepage_links[0] if homepage_links and homepage_links[0] else 'N/A'
            github_links = cg_coin_info.get('links', {}).get('repos_url', {}).get('github', [])
            source_code = github_links[0] if github_links and github_links[0] else 'N/A'
            creation_date = cg_coin_info.get('genesis_date', 'N/A')

            output.append({
                '#': idx,
                'Name': name,
                'Current Price': f"{price:,.2f}",
                '1h%': f"{volume_1h:,.2f}" if isinstance(volume_1h, (float, int)) else 'N/A',
                '24h%': f"{volume_24h:,.2f}" if isinstance(volume_24h, (float, int)) else 'N/A',
                '7d%': f"{volume_7d:,.2f}" if isinstance(volume_7d, (float, int)) else 'N/A',
                f'Market Cap': f"{float(market_cap):,.2f}" if isinstance(market_cap, (float, int)) else 'N/A',
                'Logo': logo,
                'Symbol': symbol.upper(),
                'Description': description,
                'Creation Date': creation_date,
                'Website': website,
                'Source Code': source_code
            })

            time.sleep(2)  # Respect CoinGecko demo rate limits (~30 req/min)

        if progress_callback:
            progress_callback(50, "Evaluating cryptocurrency scores...")
            
        output_with_scores = sch.evaluate_cryptos(output, currency_choice, progress_callback)
        logger.info(f'Fetched {len(output_with_scores)} coins from CoinGecko')
        
        if progress_callback:
            progress_callback(98, "Saving data to file...")
            
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filepath = f'app/assets/data/CG_crypto_extended_{timestamp}.csv'

        tbl.export_to_csv(output_with_scores, filepath)
        headings, data = tbl.read_csv(filepath)
        
        if progress_callback:
            progress_callback(100, "Complete!")
            
        return headings, data, filepath

    except requests.RequestException as e:
        logger.error(f"CoinGecko request failed: {e}")
        sg.popup(f"CoinGecko request failed: {e}")
        return None, None, None

def is_valid_cmc_api_key(api_key):
    url = cmc_listing_url
    try:
        headers = {'X-CMC_PRO_API_KEY': api_key}
        response = requests.get(url, headers=headers)
        return response.status_code == 200
    except Exception:
        return False

def is_valid_cg_api_key(api_key):
    url = 'https://api.coingecko.com/api/v3/ping'
    try:
        response = make_coingecko_request(url, {'x_cg_demo_api_key': api_key})
        return response.status_code == 200
    except Exception:
        return False

def cg_get_historical_price(coin_id, date_str, currency):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/history"
    try:
        cg_api_key = keystore.load_api_key('CoinGecko', 'CGKEY')
        if not cg_api_key:
            logger.error("No CoinGecko API key found for historical price")
            return 'N/A'
        response = make_coingecko_request(url, {'date': date_str, 'x_cg_demo_api_key': cg_api_key})
        data = response.json()
        return data['market_data']['current_price'].get(currency.lower(), 'N/A')
    except Exception:
        return 'N/A'

def get_api_choice(imagepath):
    api_choice = 'CoinMarketCap' if imagepath == 'app/assets/images/CMC.png' else 'CoinGecko'
    return api_choice

def fetch_next_cryptocurrencies(offset, api_key, api_choice, currency_choice, progress_callback=None):
    try:
        if api_choice == '1':
            return fetch_cmc_next_cryptocurrencies(api_key, offset, currency_choice, progress_callback)
        else:
            return fetch_cg_next_cryptocurrencies(offset, currency_choice, progress_callback)
    except Exception as e:
        logger.error(f"Error fetching next cryptocurrencies: {e}")
        sg.popup(f"Error fetching next cryptocurrencies: {e}")
        return []

def fetch_cmc_next_cryptocurrencies(api_key, offset, currency_choice, progress_callback=None):
    if progress_callback:
        progress_callback(1, "Initializing CoinMarketCap request...")
        
    currency = currency_choice
    parameters = {
        'start': str(offset + 1),
        'limit': cmc_rate_limit,
        'convert': currency
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }
    session = Session()
    session.headers.update(headers)

    try:
        if progress_callback:
            progress_callback(3, "Fetching cryptocurrency listings...")
            
        response = session.get(cmc_listing_url, params=parameters)
        response.raise_for_status()
        cmc_listing_data = response.json()
        cmc_coins = cmc_listing_data.get('data', [])

        output = []
        total_coins = len(cmc_coins)

        for idx, coin in enumerate(cmc_coins):
            if progress_callback:
                progress = 5 + int((idx / total_coins) * 50)
                progress_callback(progress, f"Fetching details for {coin['name']}...")
                
            ranking = coin['cmc_rank']
            name = coin['name']
            symbol = coin['symbol']
            price = coin['quote'][currency_choice]['price']
            volume_1h = coin['quote'][currency_choice]['percent_change_1h']
            volume_24h = coin['quote'][currency_choice]['percent_change_24h']
            volume_7d = coin['quote'][currency_choice]['percent_change_7d']
            market_cap = coin['quote'][currency_choice]['market_cap']

            coin_id = coin['id']
            info_response = session.get(cmc_info_url, params={'id': coin_id})
            info_response.raise_for_status()
            info_data = info_response.json()

            if 'data' not in info_data:
                logger.warning(f"No 'data' in response for coin ID {coin_id}")
                continue

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
            time.sleep(1)

            output.append({
                '#': ranking,
                'Name': name,
                'Current Price': f"{price:,.2f}",
                '1h%': f"{volume_1h:,.2f}",
                '24h%': f"{volume_24h:,.2f}",
                '7d%': f"{volume_7d:,.2f}",
                f'Market Cap': f"{float(market_cap):,.2f}",
                'Logo': logo,
                'Symbol': symbol,
                'Description': description,
                'Creation Date': date_added,
                'Website': website,
                'Source Code': source_code
            })

        if progress_callback:
            progress_callback(50, "Evaluating cryptocurrency scores...")
            
        output_with_scores = sch.evaluate_cryptos(output, currency_choice, progress_callback)
        
        if progress_callback:
            progress_callback(100, "Complete!")
            
        return output_with_scores

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        logger.error(f"Request failed: {e}")
        return []
    except KeyError as ke:
        logger.error(f"KeyError: {ke}")
        return []

def fetch_cg_next_cryptocurrencies(offset, currency_choice, progress_callback=None):
    if progress_callback:
        progress_callback(1, "Initializing CoinGecko request...")
        
    cg_api_key = keystore.load_api_key('CoinGecko', 'CGKEY')
    if not cg_api_key:
        logger.error("No CoinGecko API key found in settings.cfg")
        sg.popup("No CoinGecko API key found. Please save it in settings.cfg.")
        return []

    cg_market_url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': currency_choice.lower(),
        'order': 'market_cap_desc',
        'per_page': cg_rate_limit,
        'page': (offset // cg_rate_limit) + 1,
        'sparkline': 'false',
        'price_change_percentage': '1h,24h,7d',
        'x_cg_demo_api_key': cg_api_key
    }

    try:
        if progress_callback:
            progress_callback(3, "Fetching cryptocurrency listings...")
            
        market_data = make_coingecko_request(cg_market_url, params).json()
        output = []
        total_coins = len(market_data)

        for idx, coin in enumerate(market_data, start=offset + 1):
            if progress_callback:
                progress = 5 + int((idx / total_coins) * 50)
                progress_callback(progress, f"Fetching details for {coin['name']}...")
                
            coin_id = coin['id']
            name = coin['name']
            symbol = coin['symbol']
            price = coin['current_price']
            market_cap = coin.get('market_cap', 'N/A')
            volume_1h = coin.get('price_change_percentage_1h_in_currency', 'N/A')
            volume_24h = coin.get('price_change_percentage_24h_in_currency', 'N/A')
            volume_7d = coin.get('price_change_percentage_7d_in_currency', 'N/A')
            logo = coin.get('image', 'N/A')

            cg_coin_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            cg_coin_info = make_coingecko_request(cg_coin_url, {'x_cg_demo_api_key': cg_api_key}).json()

            description = cg_coin_info.get('description', {}).get('en', '').split('.')[0] if cg_coin_info.get('description', {}).get('en') else 'N/A'
            homepage_links = cg_coin_info.get('links', {}).get('homepage', [])
            website = homepage_links[0] if homepage_links and homepage_links[0] else 'N/A'
            github_links = cg_coin_info.get('links', {}).get('repos_url', {}).get('github', [])
            source_code = github_links[0] if github_links and github_links[0] else 'N/A'
            creation_date = cg_coin_info.get('genesis_date', 'N/A')

            output.append({
                '#': idx,
                'Name': name,
                'Current Price': f"{price:,.2f}",
                '1h%': f"{volume_1h:,.2f}" if isinstance(volume_1h, (float, int)) else 'N/A',
                '24h%': f"{volume_24h:,.2f}" if isinstance(volume_24h, (float, int)) else 'N/A',
                '7d%': f"{volume_7d:,.2f}" if isinstance(volume_7d, (float, int)) else 'N/A',
                f'Market Cap': f"{float(market_cap):,.2f}" if isinstance(market_cap, (float, int)) else 'N/A',
                'Logo': logo,
                'Symbol': symbol.upper(),
                'Description': description,
                'Creation Date': creation_date,
                'Website': website,
                'Source Code': source_code
            })

            time.sleep(2)

        if progress_callback:
            progress_callback(50, "Evaluating cryptocurrency scores...")
        output_with_scores = sch.evaluate_cryptos(output, currency_choice, progress_callback)
        
        if progress_callback:
            progress_callback(100, "Complete!")
            
        return output_with_scores

    except requests.RequestException as e:
        logger.error(f"CoinGecko request failed: {e}")
        sg.popup(f"CoinGecko request failed: {e}")
        return []